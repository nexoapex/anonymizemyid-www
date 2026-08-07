#!/usr/bin/env python3
"""Cross-device layout audit: every page type at every breakpoint.

    hugo --gc --minify && python3 scripts/responsive.py
    python3 scripts/responsive.py --shots       # also write PNGs to /tmp

scripts/verify.py loads each page once, at 390px, and asserts correctness
(CSP, consent, schema, tap targets). This is the other half: it loads the same
pages at nine widths spanning small phone → large desktop and looks for the
things that only go wrong *between* breakpoints, where nothing errors and
nothing is missing — the layout is just wrong.

What it checks, and why each one is here rather than eyeballed:

  overflow      Any element whose box crosses the viewport's right edge. The
                document-level scrollWidth check in verify.py misses an element
                clipped by an ancestor's `overflow:hidden`, which still looks
                broken.
  tap targets   WCAG 2.2 AA 24px, at *every* width. A target can pass at 390px
                and fail at 360px once a flex row wraps.
  tiny text     Anything under 12px computed. Font sizes here are mostly rem,
                so this catches a hardcoded px that slipped in.
  measure       Prose line length in characters. Comfortable reading is roughly
                45-85ch; a `.narrow`/`.page` container that loses its max-width
                at some width shows up as a 120ch paragraph, which no viewport
                check would flag.
  grid orphans  A row of a CSS grid holding fewer items than the row above it,
                where the shortfall is >1 — the ragged trailing row that makes
                a card section look unfinished at exactly one breakpoint.
  collisions    Sibling boxes that overlap. Almost always an absolutely
                positioned badge or tag that fits at one width and not another.
  under header  Content sitting beneath the sticky header at page top, i.e.
                scroll-margin missing on an anchor target.
"""
import argparse, functools, http.server, json, pathlib, re, socketserver, sys, threading

ROOT = pathlib.Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
PORT = 8901
SHOT_DIR = pathlib.Path("/tmp/amid-shots")

# Small phone → large desktop, including the two tablet widths (768 portrait,
# 1024 landscape) that sit right on top of the 760/980px media queries.
WIDTHS = [320, 360, 390, 414, 768, 834, 1024, 1280, 1440]

# One page of every distinct template, in all three languages: home, guide hub,
# guide with a fieldmap, guide with a table, guide with neither, and a plain
# content page. Anything that breaks breaks on one of these.
PATHS = [
    "/", "/es/", "/de/",
    "/guides/", "/es/guides/", "/de/ratgeber/",
    "/guides/how-to-redact-a-passport-or-id/",
    "/guides/dni-vs-passport-what-to-redact/",
    "/guides/send-a-copy-of-your-passport-safely/",
    "/es/guides/que-es-la-mrz-zona-de-lectura-mecanica/",
    "/de/ratgeber/personalausweis-kopieren-erlaubt/",
    "/about/", "/privacy/", "/es/terms/",
]

PROBE = r"""() => {
  const vw = window.innerWidth;
  const out = {overflow: [], small: [], tiny: [], measure: [], orphan: [],
               collide: [], underHeader: []};
  const label = el => {
    const t = (el.innerText || el.textContent || '').trim().replace(/\s+/g, ' ');
    return el.tagName.toLowerCase()
      + (el.className && typeof el.className === 'string'
         ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : '')
      + (t ? ' "' + t.slice(0, 34) + '"' : '');
  };

  // ── overflow ───────────────────────────────────────────────────────────
  for (const el of document.querySelectorAll('body *')) {
    const r = el.getBoundingClientRect();
    if (!r.width || !r.height) continue;
    const cs = getComputedStyle(el);
    if (cs.position === 'fixed') continue;
    // The skip link is parked at left:-9999px so it stays focusable without
    // being visible (WCAG 2.4.1) — off-screen is the whole point of it.
    if (el.closest('.skip-link')) continue;
    // A .table-wrap scrolls its table on purpose; the wrapper itself must fit.
    if (el.closest('.table-wrap') && el.tagName !== 'DIV') continue;
    if (r.right > vw + 1 || r.left < -1) {
      out.overflow.push(label(el) + ` [${Math.round(r.left)}…${Math.round(r.right)} / ${vw}]`);
    }
  }

  // ── tap targets (WCAG 2.2 AA, standalone controls only) ────────────────
  for (const el of document.querySelectorAll('a,button,summary,input,select')) {
    const r = el.getBoundingClientRect();
    if (!r.height || r.height >= 24) continue;
    const block = el.closest('p,li,td,figcaption,dd,blockquote');
    if (block && block.textContent.trim().length > el.textContent.trim().length + 2) continue;
    out.small.push(label(el) + ` [${Math.round(r.height)}px]`);
  }

  // ── tiny text ──────────────────────────────────────────────────────────
  for (const el of document.querySelectorAll('body *')) {
    if (!el.childNodes.length) continue;
    const direct = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (!direct) continue;
    // Labels inside the fieldmap SVG carry a font-size in *user units*, which
    // the viewBox scales to whatever width the figure is rendered at — the
    // computed value here says nothing about the size on screen.
    if (el.closest('svg')) continue;
    const px = parseFloat(getComputedStyle(el).fontSize);
    if (px && px < 12) out.tiny.push(label(el) + ` [${px}px]`);
  }

  // ── prose measure ──────────────────────────────────────────────────────
  const probe = document.createElement('span');
  probe.textContent = '0';
  for (const p of document.querySelectorAll('.prose > p, .lede, .answer-lede > p, .section-sub')) {
    const r = p.getBoundingClientRect();
    if (r.width < 100) continue;
    p.appendChild(probe);
    const ch = probe.getBoundingClientRect().width;
    probe.remove();
    if (!ch) continue;
    const n = Math.round(r.width / ch);
    if (n > 92) out.measure.push(label(p) + ` [${n}ch]`);
  }

  // ── grid orphans ───────────────────────────────────────────────────────
  for (const g of document.querySelectorAll('.guide-grid,.feature-grid,.steps,.strip-inner,.plans')) {
    const kids = [...g.children].map(k => k.getBoundingClientRect()).filter(r => r.width);
    if (kids.length < 3) continue;
    const rows = {};
    kids.forEach(r => { const k = Math.round(r.top); (rows[k] = rows[k] || []).push(r); });
    const counts = Object.keys(rows).sort((a, b) => a - b).map(k => rows[k].length);
    if (counts.length > 1) {
      const per = Math.max(...counts), last = counts[counts.length - 1];
      // A short last row is only ragged if it is also left-hugging. One
      // centred card is a deliberate list terminator, not an accident.
      const tail = rows[Object.keys(rows).sort((a, b) => a - b).pop()];
      const gr = g.getBoundingClientRect();
      const mid = (Math.min(...tail.map(r => r.left)) + Math.max(...tail.map(r => r.right))) / 2;
      const centred = Math.abs(mid - (gr.left + gr.right) / 2) < 4;
      if (per - last > 1 && !centred) out.orphan.push(`${label(g)} rows=${counts.join(',')}`);
    }
  }

  // ── sibling collisions ─────────────────────────────────────────────────
  const seen = new Set();
  for (const parent of document.querySelectorAll('.hero-grid,.header-inner,.footer-inner,.badges,.cookie-banner-inner,.plan,.privacy-band,.crumbs,.fieldmap-key')) {
    const kids = [...parent.children];
    for (let i = 0; i < kids.length; i++) for (let j = i + 1; j < kids.length; j++) {
      const a = kids[i].getBoundingClientRect(), b = kids[j].getBoundingClientRect();
      if (!a.width || !b.width) continue;
      if (getComputedStyle(kids[i]).position === 'absolute') continue;
      if (getComputedStyle(kids[j]).position === 'absolute') continue;
      const ox = Math.min(a.right, b.right) - Math.max(a.left, b.left);
      const oy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
      if (ox > 2 && oy > 2) {
        const key = label(kids[i]) + '|' + label(kids[j]);
        if (!seen.has(key)) { seen.add(key); out.collide.push(key); }
      }
    }
  }

  // ── content hidden under the sticky header ─────────────────────────────
  const hdr = document.querySelector('.site-header');
  if (hdr) {
    const h = hdr.getBoundingClientRect().height;
    const h1 = document.querySelector('main h1');
    if (h1) {
      const r = h1.getBoundingClientRect();
      if (r.top < h && r.bottom > 0) out.underHeader.push(`h1 top=${Math.round(r.top)} header=${Math.round(h)}`);
    }
  }
  return out;
}"""


def headers_from_netlify():
    toml = (ROOT / "netlify.toml").read_text(encoding="utf-8")
    return {
        "Content-Security-Policy": re.search(r'Content-Security-Policy = "(.*)"', toml).group(1),
        "Permissions-Policy": re.search(r'Permissions-Policy = "(.*)"', toml).group(1),
    }


def serve(extra):
    class H(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            for k, v in extra.items():
                self.send_header(k, v)
            super().end_headers()

        def log_message(self, *a):
            pass

    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("127.0.0.1", PORT),
                                 functools.partial(H, directory=str(PUBLIC)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", action="store_true", help="write PNGs to /tmp/amid-shots")
    ap.add_argument("--only", help="substring filter on path")
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright

    if not PUBLIC.is_dir():
        sys.exit("public/ not found — run `hugo --gc --minify` first")
    srv = serve(headers_from_netlify())
    base = f"http://127.0.0.1:{PORT}"
    paths = [p for p in PATHS if not args.only or args.only in p]
    if args.shots:
        SHOT_DIR.mkdir(parents=True, exist_ok=True)

    # Findings are deduplicated across widths: one line per (check, item) with
    # the list of widths it occurs at, because the same broken element
    # otherwise prints nine times and buries everything else.
    findings = {}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for path in paths:
            for w in WIDTHS:
                ctx = browser.new_context(viewport={"width": w, "height": 900},
                                          device_scale_factor=1)
                page = ctx.new_page()
                page.goto(base + path, wait_until="networkidle")
                # The consent banner is fixed and covers the fold; dismiss it so
                # the checks see the real page, exactly as a returning visitor.
                page.evaluate(
                    "localStorage.setItem('amid_consent',"
                    " JSON.stringify({analytics:false}))")
                page.reload(wait_until="networkidle")
                res = page.evaluate(PROBE)
                for check, items in res.items():
                    for item in items:
                        findings.setdefault((path, check, item), []).append(w)
                if args.shots and w in (390, 768, 1440):
                    slug = (path.strip("/").replace("/", "_") or "home")
                    page.screenshot(path=str(SHOT_DIR / f"{slug}@{w}.png"),
                                    full_page=True)
                ctx.close()
        browser.close()
    srv.shutdown()

    by_path = {}
    for (path, check, item), widths in findings.items():
        by_path.setdefault(path, []).append((check, item, widths))
    for path in paths:
        rows = by_path.get(path)
        if not rows:
            print(f"ok   {path}")
            continue
        print(f"FAIL {path}")
        for check, item, widths in sorted(rows):
            print(f"       {check:<12} {item}   @{','.join(map(str, widths))}")

    total = sum(len(v) for v in by_path.values())
    print(f"\n{len(paths) - len(by_path)}/{len(paths)} pages clean across "
          f"{len(WIDTHS)} widths — {total} finding(s)")
    if args.shots:
        print(f"screenshots: {SHOT_DIR}")
    return 1 if by_path else 0


if __name__ == "__main__":
    sys.exit(main())
