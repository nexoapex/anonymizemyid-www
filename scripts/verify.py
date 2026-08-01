#!/usr/bin/env python3
"""Load the built site in real Chromium under the exact production headers.

    hugo --gc --minify && python3 scripts/verify.py
    python3 scripts/verify.py --live      # against https://anonymizemyid.com

Requires Playwright (`pip install playwright && playwright install chromium`).

This exists because the two things most likely to break this site cannot be
caught by reading templates:

  1. The CSP is **hash-based**. An inline <style> or a `style="..."` attribute
     that is not in the hash list is silently blocked — no build error, no
     console warning unless you are listening for securitypolicyviolation.
     This has shipped broken once already, from a single style attribute.
  2. Google Analytics must make **zero network contact before consent**. It is
     injected only by assets/js/consent.js after an explicit Accept. Any change
     that puts a Google URL back into static markup reintroduces a real GDPR
     compliance gap, and looks fine in the template diff.

So: any change to head.html, main.css, cookie-consent.html or consent.js should
be run through this before pushing.
"""
import argparse, functools, http.server, pathlib, re, socketserver, sys, threading

ROOT = pathlib.Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
PORT = 8899
RELATED_LINKS = 5

PATHS = [
    "/", "/es/", "/guides/", "/es/guides/",
    "/guides/send-a-copy-of-your-passport-safely/",
    "/guides/how-to-redact-a-passport-or-id/",       # has the fieldmap diagram
    "/guides/dni-vs-passport-what-to-redact/",       # has a comparison table
    "/guides/how-to-watermark-a-copy-of-your-id/",
    # Spanish guides carry Spanish slugs (slug: in each .es.md); the English
    # paths they used to live at are 301s in netlify.toml, not pages.
    "/es/guides/que-es-la-mrz-zona-de-lectura-mecanica/",
    "/es/guides/puede-una-empresa-guardar-copia-del-dni/",
    "/about/", "/privacy/", "/terms/", "/contact/", "/imprint/",
]


def headers_from_netlify():
    toml = (ROOT / "netlify.toml").read_text(encoding="utf-8")
    return {
        "Content-Security-Policy": re.search(r'Content-Security-Policy = "(.*)"', toml).group(1),
        "Permissions-Policy": re.search(r'Permissions-Policy = "(.*)"', toml).group(1),
        "X-Content-Type-Options": "nosniff",
    }


def serve(extra_headers):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            for k, v in extra_headers.items():
                self.send_header(k, v)
            super().end_headers()

        def log_message(self, *a):
            pass

    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("127.0.0.1", PORT),
                                 functools.partial(Handler, directory=str(PUBLIC)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true",
                    help="check https://anonymizemyid.com instead of ./public")
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright

    srv = None
    if args.live:
        base = "https://anonymizemyid.com"
    else:
        if not PUBLIC.is_dir():
            sys.exit("public/ not found — run `hugo --gc --minify` first")
        srv = serve(headers_from_netlify())
        base = f"http://127.0.0.1:{PORT}"

    failures = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for path in PATHS:
            ctx = browser.new_context(viewport={"width": 390, "height": 844})
            page = ctx.new_page()
            errors, google, failed = [], [], []
            page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.on("requestfailed", lambda r: failed.append(r.url))
            page.on("request", lambda r: google.append(r.url)
                    if re.search(r"google|gstatic|doubleclick", r.url) else None)
            page.add_init_script("""
              window.__csp = [];
              document.addEventListener('securitypolicyviolation',
                e => window.__csp.push(e.violatedDirective + ' :: ' + e.blockedURI));
            """)
            page.goto(base + path, wait_until="networkidle")
            violations = page.evaluate("window.__csp || []")

            notes = []
            parts = [x for x in path.split("/") if x]
            if "guides" in parts and parts[-1] != "guides":
                if page.locator(".answer-box").count() != 1:
                    notes.append("missing the short-answer block")
                if page.locator(".takeaways li").count() < 3:
                    notes.append("fewer than 3 takeaways")
                # 4 topical (Hugo's [related] index) + 1 reserved rotation slot
                # that guarantees the low-overlap guides still get linked; see
                # layouts/guides/single.html.
                if page.locator("nav.related li").count() != RELATED_LINKS:
                    notes.append(f"related links != {RELATED_LINKS}")
                if page.locator(".author-card").count() != 1:
                    notes.append("missing the author card")
            if page.locator("h1").count() != 1:
                notes.append(f"h1 count = {page.locator('h1').count()}")
            if page.evaluate("document.documentElement.scrollWidth > window.innerWidth + 1"):
                notes.append("page scrolls horizontally at 390px")
            # WCAG 2.2 AA target size (24px), standalone controls only. The spec
            # exempts a target "in a sentence or its size is otherwise
            # constrained by the line-height of non-target text" — so rather
            # than maintain a list of classes, detect it structurally: if the
            # enclosing block holds meaningful text beyond the link's own label,
            # the link is inline prose and exempt.
            small = page.evaluate("""() => [...document.querySelectorAll('a,button')]
                .filter(el => {
                  const r = el.getBoundingClientRect();
                  if (!r.height || r.height >= 24) return false;
                  const block = el.closest('p,li,td,figcaption,dd,blockquote');
                  if (block) {
                    const own = el.textContent.trim().length;
                    if (block.textContent.trim().length > own + 2) return false;
                  }
                  return true;
                })
                .map(el => (el.innerText || el.tagName).trim().slice(0, 30))""")
            notes += [f"tap target under 24px: {t}" for t in small]

            # Structural a11y that also happens to be structural SEO. Each of
            # these was verified clean when added, so a hit means a regression.
            if not page.evaluate("document.documentElement.lang"):
                notes.append("no lang on <html>")
            if page.locator("main").count() != 1:
                notes.append(f"main landmark x{page.locator('main').count()}")
            if page.locator("a.skip-link").count() != 1:
                notes.append("no skip link (WCAG 2.4.1)")
            no_th = page.evaluate(
                "() => [...document.querySelectorAll('table')]"
                ".filter(t => !t.querySelector('th')).length")
            if no_th:
                notes.append(f"{no_th} table(s) with no <th>")
            unlabelled = page.evaluate(
                "() => [...document.querySelectorAll('input,select,textarea')]"
                ".filter(e => e.type !== 'hidden' && !e.labels?.length"
                " && !e.getAttribute('aria-label')).length")
            if unlabelled:
                notes.append(f"{unlabelled} unlabelled form control(s)")

            bad = violations or errors or google or failed or notes
            print(f"{'FAIL' if bad else 'ok  '} {path}")
            for label, items in (("csp", violations), ("console", errors),
                                 ("google-before-consent", google),
                                 ("request failed", failed), ("", notes)):
                for item in items:
                    print(f"       {label + ': ' if label else ''}{item}")
            if bad:
                failures.append(path)
            ctx.close()
        browser.close()

    if srv:
        srv.shutdown()
    print(f"\n{len(PATHS) - len(failures)}/{len(PATHS)} pages clean")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
