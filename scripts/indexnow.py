#!/usr/bin/env python3
"""Submit URLs to IndexNow, so Bing, Copilot, Yandex and DuckDuckGo see a change
the same day instead of whenever they next crawl.

    python3 scripts/indexnow.py --new           # URLs added/changed in the last commit
    python3 scripts/indexnow.py --all           # every URL in the sitemaps
    python3 scripts/indexnow.py /guides/foo/ /es/guides/foo/
    python3 scripts/indexnow.py --all --dry-run

The key file (static/<key>.txt) is already deployed and must stay reachable at
the site root — that is how the endpoint proves the submission came from
someone who controls the domain. Nothing here is Google-facing: Google does not
participate in IndexNow, so a new page still needs Search Console (or simply
time) on that side. Bing's index is what Copilot and several AI answer engines
read from, which is why this is worth doing at all.

Only submit URLs that actually changed. The protocol treats repeated
submissions of unchanged pages as spam, and the penalty is being ignored.
"""
import argparse, glob, json, pathlib, re, subprocess, sys, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
HOST = "anonymizemyid.com"
ENDPOINT = "https://api.indexnow.org/IndexNow"

KEY_FILES = list((ROOT / "static").glob("*.txt"))
KEY = next((f.stem for f in KEY_FILES if re.fullmatch(r"[0-9a-f]{32}", f.stem)), None)


def sitemap_urls():
    """Every <loc> across the per-language sitemaps in ./public."""
    urls = set()
    for f in glob.glob(str(PUBLIC / "**/sitemap.xml"), recursive=True):
        text = pathlib.Path(f).read_text(encoding="utf-8")
        urls |= {u for u in re.findall(r"<loc>(.*?)</loc>", text) if not u.endswith(".xml")}
    return sorted(urls)


def changed_urls():
    """Guide/page URLs touched by the last commit, both languages.

    Maps content/guides/<slug>[.es].md back to its published URL rather than
    reading the sitemap, so a rename is submitted under the new path only.
    """
    diff = subprocess.run(
        ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
        cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    urls = set()
    for path in diff:
        m = re.fullmatch(r"content/(.+?)(\.es)?\.md", path)
        if not m:
            continue
        slug, es = m.group(1), m.group(2)
        slug = "" if slug == "_index" else slug.removesuffix("/_index")
        prefix = "/es" if es else ""
        urls.add(f"https://{HOST}{prefix}/{slug}{'/' if slug else ''}")
    return sorted(urls)


def submit(urls, dry_run=False):
    payload = {
        "host": HOST,
        "key": KEY,
        "keyLocation": f"https://{HOST}/{KEY}.txt",
        "urlList": urls,
    }
    for u in urls:
        print("  ", u)
    if dry_run:
        print(f"\ndry run — {len(urls)} URL(s) not submitted")
        return 0
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        # 200 accepted, 202 accepted but key still being validated. Both fine.
        print(f"\n{resp.status} {resp.reason} — {len(urls)} URL(s) submitted")
        return 0 if resp.status in (200, 202) else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("urls", nargs="*", help="paths or full URLs to submit")
    ap.add_argument("--all", action="store_true", help="every URL in the sitemaps")
    ap.add_argument("--new", action="store_true", help="URLs touched by the last commit")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not KEY:
        sys.exit("no IndexNow key file found in static/ (expected <32 hex chars>.txt)")

    if args.all:
        urls = sitemap_urls()
    elif args.new:
        urls = changed_urls()
    else:
        urls = [u if u.startswith("http") else f"https://{HOST}{u}" for u in args.urls]

    if not urls:
        print("nothing to submit")
        return 0
    if len(urls) > 10000:
        sys.exit("IndexNow accepts at most 10000 URLs per request")

    return submit(urls, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
