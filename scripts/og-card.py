#!/usr/bin/env python3
"""Generate the 1200x630 Open Graph cards.

    python3 scripts/og-card.py send-a-copy-of-your-passport-safely
    python3 scripts/og-card.py --all            # every card that is missing
    python3 scripts/og-card.py --all --force    # redraw everything (design change)
    python3 scripts/og-card.py --defaults       # just the shared per-language cards

Two kinds of card, one template:

  * **Per-guide** -> assets/images/og/<slug>[.<lang>].png, titled from the
    guide's own front matter so the card and the page cannot drift.
  * **Shared** -> static/images/og[.<lang>].png, used by the home page, the
    guides hub and the legal pages. These used to be a single hand-made English
    image served to every language, so a shared link to /de/ or /es/ unfurled in
    English; now there is one per language, drawn from that language's own
    tagline in hugo.toml.

The card shows a schematic identity document with a vertical amber seam down it:
left of the seam the sensitive fields are raw character marks, right of it they
are covered and the app's watermark is tiled over them. The two rows that stay
grey right through the seam are the ones you keep visible. That is the whole
product in one image, before a word is read - which matters because most of
these are seen at ~300px wide in a chat client.

Everything the card says in words is read from the site's own config
(hugo.toml taglines, i18n/<lang>.toml section names) rather than restated here,
so a copy change on the site cannot leave the cards behind. Only the artwork
strings - the document label and its four field labels - live in this file,
because nothing on the site renders them.

Renders the card as HTML in Chromium and screenshots it. Requires Playwright.
"""
import argparse, html, pathlib, re, sys, tomllib

ROOT = pathlib.Path(__file__).resolve().parent.parent
GUIDES = ROOT / "content/guides"
OUT = ROOT / "assets/images/og"
SHARED = ROOT / "static/images"

# Artwork-only strings: the document label and the four field labels drawn on
# the mock. Deliberately the document a reader of that language actually holds.
# The mock is a schematic wireframe - boxes and rules standing in for fields -
# never a facsimile of a real issued card.
ARTWORK = {
    "en": {
        "doclabel": "PASSPORT",
        "fields": ("Surname", "Given names", "Document No.", "Date of birth"),
        "feature": "100% on-device \u00b7 redact + watermark \u00b7 \u20ac4 once",
    },
    "es": {
        "doclabel": "DNI / PASAPORTE",
        "fields": ("Apellidos", "Nombre", "N\u00famero", "Fecha de nacimiento"),
        "feature": "100% en el dispositivo \u00b7 censura + marca de agua \u00b7 4 \u20ac una vez",
    },
    "de": {
        "doclabel": "PERSONALAUSWEIS",
        "fields": ("Name", "Vornamen", "Dokumentennr.", "Geburtsdatum"),
        "feature": "100 % auf dem Ger\u00e4t \u00b7 schw\u00e4rzen + Wasserzeichen \u00b7 einmalig 4 \u20ac",
    },
}

TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>OG card</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  html, body { width:1200px; height:630px; overflow:hidden; }
  body {
    background:#0F1115;
    color:#F2F4F8;
    font-family:-apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif;
    -webkit-font-smoothing:antialiased;
    display:flex; flex-direction:column;
    padding:28px 68px 0;
    position:relative;
  }

  /* warm lift behind the document */
  .glow {
    position:absolute; left:-140px; right:-140px; bottom:-90px; height:520px;
    background:radial-gradient(58% 100% at 52% 100%, rgba(242,169,59,.12), rgba(242,169,59,0) 72%);
    pointer-events:none;
  }

  /* ---------- masthead ---------- */
  .brand { flex:0 0 36px; display:flex; align-items:center; justify-content:space-between; position:relative; }
  .mark { display:flex; align-items:center; gap:11px; }
  .mark span { font-size:21px; font-weight:650; letter-spacing:-.005em; }
  .domain { font-size:15px; font-weight:500; letter-spacing:.025em; color:#9BA3AF; }
  .masthead-rule { flex:0 0 1px; background:#252A33; }

  /* ---------- title block ---------- */
  .lede { flex:0 0 auto; padding:20px 0 16px; position:relative; }
  .kicker { display:flex; align-items:center; gap:12px; height:22px; margin-bottom:10px; }
  .kicker i { display:block; width:30px; height:3px; border-radius:2px; background:#F2A93B; }
  .kicker span { font-size:14px; font-weight:700; letter-spacing:.2em; text-transform:uppercase; color:#F2A93B; }
  h1 {
    font-size:__FS__px; line-height:1.08; font-weight:700; letter-spacing:-.021em;
    max-width:1040px; overflow-wrap:break-word; text-wrap:balance;
    display:-webkit-box; -webkit-box-orient:vertical; -webkit-line-clamp:3; overflow:hidden;
  }
  /* default card: no section label at all — the title simply rises, the rail
     never survives as an orphaned amber dash. */
  body.is-default .kicker { display:none; }
  body.is-default .lede { padding-top:38px; }

  /* ---------- the document sheet ---------- */
  .doc {
    flex:1 1 auto; min-height:300px; position:relative;
    background:#1B1F27;
    border:1px solid #2C313B; border-bottom:0;
    border-radius:16px 16px 0 0;
    padding:22px 30px 0;
    overflow:hidden;
    display:flex; flex-direction:column;
  }

  /* the wipe seam: one continuous amber edge. Everything to its right has been
     processed; the kept rows run straight through it untouched. */
  .seam { position:absolute; left:729px; top:0; bottom:0; width:5px; background:#F2A93B; z-index:1; }
  /* the app's tiled watermark — only on the processed side of the seam */
  .wm {
    position:absolute; left:734px; right:0; top:0; bottom:0; z-index:4; pointer-events:none;
    background:repeating-linear-gradient(45deg, rgba(255,255,255,.05) 0 2px, rgba(255,255,255,0) 2px 22px);
  }

  /* ---------- sheet head ---------- */
  .docHead { flex:0 0 40px; display:flex; align-items:center; justify-content:space-between; position:relative; z-index:2; }
  .docLabel { display:flex; align-items:center; gap:12px; }
  .docLabel i { width:10px; height:10px; border-radius:2px; background:#F2A93B; display:block; flex:0 0 10px; }
  .docLabel span { font-size:22px; font-weight:700; letter-spacing:.075em; color:#F2F4F8; white-space:nowrap; }
  .gate { display:flex; align-items:center; gap:9px; border:1px solid #343B47; border-radius:999px;
          padding:7px 14px 7px 12px; color:#9BA3AF; font-size:16px; font-weight:700; letter-spacing:.06em; }
  .rule { flex:0 0 1px; background:#2C313B; margin-top:12px; position:relative; z-index:2; }

  /* ---------- field rows ---------- */
  .body { flex:1 1 auto; min-height:0; display:flex; align-items:center; gap:34px; padding:14px 0; position:relative; z-index:2; }

  .portrait { flex:0 0 132px; align-self:center; height:100%; max-height:200px; min-height:140px;
              border:1px solid #363D4A; border-radius:6px; background:#161A21; position:relative; }
  .portrait svg { position:absolute; left:50%; top:50%; transform:translate(-50%,-50%); }

  .rows { flex:1 1 auto; height:100%; max-height:200px; display:flex; flex-direction:column; justify-content:space-between; }
  .row { display:flex; align-items:center; gap:20px; height:30px; }
  .row label { flex:0 0 200px; font-size:13.5px; font-weight:600; letter-spacing:.12em; text-transform:uppercase;
               color:#A6AEBA; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
  .track { flex:1 1 auto; position:relative; height:30px; }

  /* kept fields: one continuous thin rule that runs straight through the seam,
     unchanged on both sides — "these four things, and nothing else" */
  .row.keep .track::before { content:""; position:absolute; left:0; right:0; top:10px; height:11px;
                             border-radius:2px; background:#4E5665; }
  /* sensitive fields: raw character marks up to the seam, then covered */
  .chars { position:absolute; left:0; top:8px; height:14px; width:50.97%; border-radius:1px;
           background:repeating-linear-gradient(90deg, #6E7788 0 10px, rgba(0,0,0,0) 10px 16px); }

  /* the cover: 2.5x the height of the marks it sits on, hard dark edge,
     drop shadow — it sits ON the sheet, it is not a highlighted field */
  .cover { position:absolute; top:1px; height:28px; left:50.97%; right:0; border-radius:4px;
           background:#F2A93B; box-shadow:0 3px 0 rgba(0,0,0,.38), inset 0 0 0 1.5px rgba(26,18,6,.22); }

  /* ---------- machine-readable zone ---------- */
  .mrz { flex:0 0 auto; border-top:1px solid #2C313B; padding-top:15px; position:relative; z-index:2; }
  .mrzRow { height:17px; border-radius:1px;
            background:repeating-linear-gradient(90deg, #5A6272 0 9px, rgba(0,0,0,0) 9px 15px); }
  .mrzRow + .mrzRow { margin-top:9px; }
  .mrz .cover { top:11px; height:51px; left:69.86%; right:0; border-radius:5px; }

  /* sheet ground below the MRZ, bleeding off the bottom edge: keeps the
     poster crop while holding the MRZ clear of client-side crops */
  .tail { flex:0 0 46px; }
</style>
</head>
<body>
  <div class="glow"></div>

  <div class="brand">
    <div class="mark">
      <svg viewBox="0 0 24 24" width="30" height="30"><path fill="#F2A93B" d="M12 2 4 5v6c0 5 3.4 8.6 8 11 4.6-2.4 8-6 8-11V5l-8-3Zm0 2.2 6 2.25V11c0 3.9-2.5 6.8-6 8.8C8.5 17.8 6 14.9 6 11V6.45L12 4.2Z"/></svg>
      <span>Anonymize my ID</span>
    </div>
    <div class="domain">anonymizemyid.com</div>
  </div>
  <div class="masthead-rule"></div>

  <div class="lede">
    <div class="kicker"><i></i><span>__EYEBROW__</span></div>
    <h1>__TITLE__</h1>
  </div>

  <div class="doc">
    <div class="seam"></div>

    <div class="docHead">
      <div class="docLabel"><i></i><span>__DOCLABEL__</span></div>
      <div class="gate">
        <svg width="25" height="18" viewBox="0 0 25 18" fill="none">
          <path d="M7 15h11a4 4 0 0 0 .5-8 5.6 5.6 0 0 0-10.6-1.3A4.4 4.4 0 0 0 7 15Z" stroke="#9BA3AF" stroke-width="1.6" stroke-linejoin="round"/>
          <path d="M3.5 17.2 21.5 1.2" stroke="#1B1F27" stroke-width="4.4"/>
          <path d="M3.5 17.2 21.5 1.2" stroke="#9BA3AF" stroke-width="1.6"/>
        </svg>
        <span>0 KB</span>
      </div>
    </div>
    <div class="rule"></div>

    <div class="body">
      <div class="portrait">
        <svg width="72" height="82" viewBox="0 0 74 84" fill="none">
          <circle cx="37" cy="28" r="17" stroke="#3F4655" stroke-width="2"/>
          <path d="M7 80c0-16.6 13.4-30 30-30s30 13.4 30 30" stroke="#3F4655" stroke-width="2"/>
        </svg>
      </div>

      <div class="rows">
        <div class="row keep"><label>__F1__</label><div class="track"></div></div>
        <div class="row keep"><label>__F2__</label><div class="track"></div></div>
        <div class="row hide"><label>__F3__</label><div class="track"><span class="chars"></span><span class="cover"></span></div></div>
        <div class="row hide"><label>__F4__</label><div class="track"><span class="chars"></span><span class="cover"></span></div></div>
      </div>
    </div>

    <div class="mrz">
      <div class="mrzRow"></div>
      <div class="mrzRow"></div>
      <span class="cover"></span>
    </div>

    <div class="tail"></div>
    <div class="wm"></div>
  </div>
</body>
</html>
"""


def site_strings():
    """Per-language tagline + section name, straight from the site's own config."""
    cfg = tomllib.loads((ROOT / "hugo.toml").read_text(encoding="utf-8"))
    out = {}
    for lang, block in cfg["languages"].items():
        i18n = tomllib.loads((ROOT / f"i18n/{lang}.toml").read_text(encoding="utf-8"))
        out[lang] = {
            "tagline": block.get("params", {}).get("tagline", ""),
            "eyebrow": i18n.get("guides_title", "").upper(),
        }
    return out


def title_of(path):
    m = re.search(r'^title: "(.*)"$', path.read_text(encoding="utf-8"), re.M)
    if not m:
        sys.exit(f"no title in {path}")
    return m.group(1)


def font_size(title):
    """Title size ladder.

    The document sheet below the title is the flexible element, so a taller
    title block simply shortens the sheet. The invariant that keeps the sheet
    reading as a document is `size * 1.08 * lines <= 195px`; the h1 is clamped
    to three lines so four is impossible. The 34px rung exists so a title past
    ~78 characters steps down rather than pushing the machine-readable zone off
    the bottom of the canvas.
    """
    n = len(title)
    return (62 if n <= 34 else 55 if n <= 46 else 48 if n <= 58
            else 43 if n <= 70 else 38 if n <= 78 else 34)


def variants(slug):
    """Every language file for a slug: <slug>.md plus <slug>.<lang>.md.

    Returns [(suffix, path)], where suffix is "" for the default language and
    ".<lang>" otherwise - the same naming partials/head.html looks the card up
    by. A slug that exists in only one language yields only that one.
    """
    out = []
    for path in sorted(GUIDES.glob(f"{slug}.*")):
        if path.suffix != ".md":
            continue
        rest = path.name[len(slug):-3]        # "" or ".de"
        out.append((rest, path))
    return out


def lang_of(suffix):
    return suffix[1:] if suffix else "en"


def render(jobs):
    """jobs: [(dest, title, lang, is_default)]"""
    from playwright.sync_api import sync_playwright
    strings = site_strings()
    OUT.mkdir(parents=True, exist_ok=True)
    SHARED.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_context(viewport={"width": 1200, "height": 630},
                                   device_scale_factor=1).new_page()
        for dest, title, lang, is_default in jobs:
            art = ARTWORK.get(lang, ARTWORK["en"])
            # On a shared card the eyebrow carries the value proposition instead
            # of a section name - it is the one card where nobody arrived from a
            # section and the pitch is the point.
            eyebrow = art["feature"] if is_default else strings[lang]["eyebrow"]
            doc = (TEMPLATE
                   .replace("__TITLE__", html.escape(title))
                   .replace("__EYEBROW__", html.escape(eyebrow))
                   .replace("__DOCLABEL__", html.escape(art["doclabel"]))
                   .replace("__FS__", str(font_size(title))))
            for i, f in enumerate(art["fields"], 1):
                doc = doc.replace(f"__F{i}__", html.escape(f))
            page.set_content(doc, wait_until="load")
            page.screenshot(path=str(dest))
            print(f"  {dest.relative_to(ROOT)}  ({len(title)} chars, {lang})")
        browser.close()


def default_jobs(force):
    """The shared card, one per language published in hugo.toml."""
    jobs = []
    for lang, s in site_strings().items():
        suffix = "" if lang == "en" else f".{lang}"
        dest = SHARED / f"og{suffix}.png"
        if force or not dest.exists():
            jobs.append((dest, s["tagline"], lang, True))
    return jobs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="*", help="guide slugs (without .md)")
    ap.add_argument("--all", action="store_true", help="every card that is missing")
    ap.add_argument("--defaults", action="store_true", help="only the shared cards")
    ap.add_argument("--force", action="store_true",
                    help="redraw cards that already exist (after a design change)")
    args = ap.parse_args()

    jobs = []
    if args.defaults:
        jobs = default_jobs(args.force or True)
    elif args.all:
        for src in sorted(GUIDES.glob("*.md")):
            if src.name.startswith("_"):
                continue
            slug = src.stem.split(".")[0]
            suffix = src.stem[len(slug):]
            dest = OUT / f"{slug}{suffix}.png"
            if args.force or not dest.exists():
                jobs.append((dest, title_of(src), lang_of(suffix), False))
        jobs += default_jobs(args.force)
        if not jobs:
            print("every card already exists (use --force to redraw).")
            return 0
    elif args.slugs:
        for slug in args.slugs:
            found = variants(slug)
            if not found:
                sys.exit(f"no guide file for {slug} in {GUIDES}")
            for suffix, src in found:
                jobs.append((OUT / f"{slug}{suffix}.png", title_of(src),
                             lang_of(suffix), False))
    else:
        ap.error("pass one or more slugs, or --all, or --defaults")

    render(jobs)
    return 0


if __name__ == "__main__":
    sys.exit(main())
