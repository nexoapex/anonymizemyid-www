#!/usr/bin/env python3
"""Recompute the CSP sha256 hashes from the built site.

    hugo --gc --minify && python3 scripts/csp-hashes.py [--write]

The site's Content-Security-Policy in netlify.toml is hash-based, because
Netlify headers are static and cannot carry a per-request nonce. That only
works because every inline <script> and <style> is byte-identical on every
page. If `main.css` or the inline language-redirect script in
partials/head.html changes, the hash changes, and a stale hash means the CSP
silently blocks the CSS or the script in production — no build error.

So this script asserts the invariant (exactly one distinct hash of each kind
across the whole site) and prints the current values. `--write` updates
netlify.toml in place.

Adding a NEW inline <script> means a NEW hash to add, not a swap of the
existing one. External files (assets/js/consent.js) need no hash — they are
covered by 'self'.
"""
import argparse, base64, collections, glob, hashlib, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
NETLIFY = ROOT / "netlify.toml"

STYLE = re.compile(r"<style[^>]*>(.*?)</style>", re.S)
# Inline scripts only: skip anything with a src, and skip JSON-LD data blocks.
SCRIPT = re.compile(
    r"<script(?![^>]*\bsrc=)(?![^>]*type=application/ld)[^>]*>(.*?)</script>", re.S)


def sha256(text):
    return "sha256-" + base64.b64encode(hashlib.sha256(text.encode()).digest()).decode()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="update netlify.toml in place")
    args = ap.parse_args()

    if not PUBLIC.is_dir():
        sys.exit("public/ not found — run `hugo --gc --minify` first")

    styles, scripts = collections.Counter(), collections.Counter()
    for f in glob.glob(str(PUBLIC / "**/*.html"), recursive=True):
        html = open(f, encoding="utf-8").read()
        for block in STYLE.findall(html):
            styles[sha256(block)] += 1
        for block in SCRIPT.findall(html):
            if block.strip():
                scripts[sha256(block)] += 1

    ok = True
    for label, counts in (("style-src", styles), ("script-src", scripts)):
        print(f"{label}: {len(counts)} distinct")
        for h, n in counts.items():
            print(f"  {n:>3} pages  '{h}'")
        if len(counts) != 1:
            ok = False
            print(f"  !! expected exactly 1 — an inline block is no longer "
                  f"byte-identical across pages, so no single hash can cover it")

    if not ok:
        return 1

    style, script = next(iter(styles)), next(iter(scripts))
    toml = NETLIFY.read_text(encoding="utf-8")
    live = re.findall(r"'(sha256-[A-Za-z0-9+/=]+)'", toml)
    stale = [h for h in (style, script) if h not in live]

    if not stale:
        print("\nnetlify.toml is up to date.")
        return 0

    print(f"\nnetlify.toml is STALE — missing: {', '.join(stale)}")
    if not args.write:
        print("re-run with --write to update it.")
        return 1

    for old in live:
        if old not in (style, script):
            replacement = style if old not in scripts else script
            toml = toml.replace(f"'{old}'", f"'{replacement}'")
    NETLIFY.write_text(toml, encoding="utf-8")
    print("netlify.toml updated. Now re-run scripts/verify.py in a real browser.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
