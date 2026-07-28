#!/usr/bin/env python3
"""Generate the 1200x630 Open Graph card for one or more guides.

    python3 scripts/og-card.py send-a-copy-of-your-passport-safely
    python3 scripts/og-card.py --all          # every guide missing a card

Writes assets/images/og/<slug>.png and <slug>.es.png, reading each title from
the guide's own front matter so the card and the page cannot drift.

A guide with no card falls back to the shared static/images/og.png, which works
but is generic — worth generating one for anything you expect to be shared.

Renders the card as HTML in Chromium and screenshots it, which keeps it in the
same visual family as the original hand-built set (dark ground, amber shield and
wordmark, big title, schematic redacted-document glyph, amber foot rule).
Requires Playwright.
"""
import argparse, html, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
GUIDES = ROOT / "content/guides"
OUT = ROOT / "assets/images/og"

TEMPLATE = """<!doctype html><html><head><meta charset=utf-8><style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:1200px;height:630px;background:#0F1115;
  font-family:Inter,-apple-system,'Segoe UI',Roboto,sans-serif;position:relative;overflow:hidden}
.glow{position:absolute;top:-190px;right:-150px;width:620px;height:620px;border-radius:50%;
  background:radial-gradient(circle,rgba(242,169,59,.13),rgba(242,169,59,0) 68%)}
.brand{position:absolute;top:52px;left:64px;display:flex;align-items:center;gap:14px}
.brand span{color:#F2F4F8;font-size:26px;font-weight:700;letter-spacing:-.2px}
h1{position:absolute;left:64px;top:170px;width:660px;color:#F2F4F8;font-size:__FS__px;
  font-weight:800;line-height:1.16;letter-spacing:-1.2px}
.doc{position:absolute;right:64px;top:205px;width:290px;height:196px;background:#1B1F27;
  border:1px solid #2C313B;border-radius:14px;padding:22px}
.row{display:flex;align-items:center;gap:16px}
.av{width:52px;height:52px;border-radius:50%;background:#2C313B;flex:none}
.lines{flex:1}
.l{height:11px;border-radius:6px;background:#2C313B;margin-bottom:9px}
.l.amber{background:#F2A93B;width:82%}
.l.short{width:58%}
.foot{margin-top:26px}
.foot .l{height:10px;margin-bottom:11px}
.foot .l:nth-child(3){width:72%}
.rule{position:absolute;left:0;bottom:0;width:100%;height:9px;background:#F2A93B}
</style></head><body>
<div class=glow></div>
<div class=brand>
  <svg viewBox="0 0 24 24" width="34" height="34"><path fill="#F2A93B"
    d="M12 2 4 5v6c0 5 3.4 8.6 8 11 4.6-2.4 8-6 8-11V5l-8-3Zm0 2.2 6 2.25V11c0 3.9-2.5 6.8-6 8.8C8.5 17.8 6 14.9 6 11V6.45L12 4.2Z"/></svg>
  <span>Anonymize my ID</span>
</div>
<h1>__TITLE__</h1>
<div class=doc>
  <div class=row><div class=av></div>
    <div class=lines><div class="l amber"></div><div class="l short"></div></div></div>
  <div class=foot><div class=l></div><div class=l></div><div class=l></div></div>
</div>
<div class=rule></div>
</body></html>"""


def title_of(path):
    m = re.search(r'^title: "(.*)"$', path.read_text(encoding="utf-8"), re.M)
    if not m:
        sys.exit(f"no title in {path}")
    return m.group(1)


def font_size(title):
    n = len(title)
    return 62 if n <= 34 else 55 if n <= 46 else 48 if n <= 58 else 43


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="*", help="guide slugs (without .md)")
    ap.add_argument("--all", action="store_true", help="every guide missing a card")
    args = ap.parse_args()

    slugs = args.slugs
    if args.all:
        slugs = sorted({p.stem for p in GUIDES.glob("*.md")
                        if not p.stem.startswith("_") and not p.stem.endswith(".es")
                        and not (OUT / f"{p.stem}.png").exists()})
        if not slugs:
            print("every guide already has a card.")
            return 0
    if not slugs:
        ap.error("pass one or more slugs, or --all")

    jobs = []
    for slug in slugs:
        for suffix, name in (("", f"{slug}.md"), (".es", f"{slug}.es.md")):
            src = GUIDES / name
            if not src.exists():
                sys.exit(f"missing {src}")
            jobs.append((OUT / f"{slug}{suffix}.png", title_of(src)))

    from playwright.sync_api import sync_playwright
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_context(viewport={"width": 1200, "height": 630}).new_page()
        for dest, title in jobs:
            doc = (TEMPLATE.replace("__TITLE__", html.escape(title))
                           .replace("__FS__", str(font_size(title))))
            page.set_content(doc, wait_until="load")
            page.screenshot(path=str(dest))
            print(f"  {dest.relative_to(ROOT)}  ({len(title)} chars)")
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
