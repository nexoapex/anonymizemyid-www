#!/usr/bin/env python3
"""Static SEO/GEO audit of the built site in ./public.

Run `hugo --gc --minify` first, then `python3 scripts/audit.py`. Exits non-zero
if anything is wrong, so it works as a pre-push check.

What it catches, in rough order of how much each has actually bitten us:

  * internal links that 301 (a path with no trailing slash, e.g. from
    `"/privacy" | relLangURL` — always use the page's own .RelPermalink)
  * SERP title > 60 chars, meta description outside 110-160
  * duplicate titles or descriptions across pages
  * hreflang alternates that are missing or not reciprocal
  * dead #fragment links
  * more than one <h1>, or a heading level jump (h2 -> h4)
  * missing canonical / x-default / robots meta
  * invalid JSON-LD, or Article/FAQPage missing a Google-required property
  * <img> with no alt or no width/height (the latter causes CLS)

NOTE: the built HTML is minified, so attributes are unquoted AND reordered.
Match on the attribute value, never on tag-prefix order — `<meta property=og:type`
silently matches nothing because the minifier may emit `<meta content=article
property=og:type>`.
"""
import collections, glob, json, os, re, sys, urllib.parse, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"

TITLE_MAX = 60
DESC_MIN, DESC_MAX = 110, 160
# URL segment the guide hub lives under, per language. English and Spanish share
# /guides/; German uses /ratgeber/. Add a segment here when a language renames
# the section in hugo.toml, or its guides drop out of the link-distribution check.
GUIDE_SECTIONS = ("guides", "ratgeber")


def first(pattern, text):
    m = re.search(pattern, text, re.S)
    return m.group(1) if m else ""


def check_external(pages):
    """HEAD every off-site URL the built pages point at, including the ones that
    only exist inside JSON-LD (Article.citation, Article.about/sameAs).

    Off by default and behind --external: it needs the network, so it is not
    something a pre-push check should depend on. Worth running whenever a guide
    gains a source, because a dead primary source is worse than none — it is a
    citation an answer engine cannot verify.
    """
    import concurrent.futures, urllib.error, urllib.request

    # Pull from href attributes and from parsed JSON-LD rather than regexing the
    # whole document: a bare URL regex has to guess where the URL stops, and
    # ".../Documento_Nacional_de_Identidad_(Spain)" ends in a character such a
    # regex almost always treats as a delimiter.
    def walk(node):
        if isinstance(node, str):
            if node.startswith("http"):
                yield node
        elif isinstance(node, dict):
            for v in node.values():
                yield from walk(v)
        elif isinstance(node, list):
            for v in node:
                yield from walk(v)

    urls = set()
    for html in pages.values():
        urls |= set(re.findall(r'href="(https?://[^"]+)"', html))
        urls |= set(re.findall(r"href=(https?://[^\s>]+)", html))
        for blob in re.findall(
                r"<script type=application/ld\+json>(.*?)</script>", html, re.S):
            try:
                urls |= set(walk(json.loads(blob)))
            except Exception:
                pass  # invalid JSON-LD is already reported by the main pass
    urls = sorted(u for u in urls if "anonymizemyid.com" not in u
                  and not u.startswith(("https://schema.org", "http://schema.org")))

    def head(url):
        req = urllib.request.Request(url, method="HEAD", headers={
            "User-Agent": "Mozilla/5.0 (compatible; anonymizemyid-audit/1.0)"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return url, r.status
        except urllib.error.HTTPError as e:
            # A host that dislikes HEAD, or a WAF that dislikes a non-browser
            # user agent, is not a dead link. The German federal sites
            # (bsi.bund.de, bfdi.bund.de) answer 400 to the UA above and 200 to
            # a browser one, so 400 belongs in this retry alongside 403/405.
            if e.code in (400, 403, 405):
                try:
                    with urllib.request.urlopen(urllib.request.Request(
                            url, headers={"User-Agent": "Mozilla/5.0"}), timeout=20) as r:
                        return url, r.status
                except Exception as exc:
                    return url, f"{e.code} then {exc}"
            return url, e.code
        except Exception as exc:
            return url, str(exc)

    bad = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        for url, status in pool.map(head, urls):
            # Any 2xx means the source is reachable. EUR-Lex answers its ELI
            # permalinks with 202, which the old `!= 200` reported as a broken
            # primary source on every guide that cites the GDPR.
            if not (isinstance(status, int) and 200 <= status < 300):
                bad.append(f"external {status}  {url}")
    print(f"external URLs checked: {len(urls)}")
    return bad


def main():
    if not PUBLIC.is_dir():
        sys.exit("public/ not found — run `hugo --gc --minify` first")

    pages = {}
    for f in glob.glob(str(PUBLIC / "**/*.html"), recursive=True):
        url = "/" + os.path.relpath(f, PUBLIC).replace("index.html", "")
        pages[url] = open(f, encoding="utf-8").read()

    on_disk = set(pages) | {
        "/" + os.path.relpath(f, PUBLIC)
        for f in glob.glob(str(PUBLIC / "**/*.*"), recursive=True)
    }

    issues = []
    titles, descs = collections.Counter(), collections.Counter()

    for url, html in pages.items():
        # /en/ is Hugo's alias stub for the root-served English home; 404 has no
        # canonical or hreflang by design. Neither is a real page.
        skip = url.endswith("404.html") or url.startswith("/en/")

        for href in set(re.findall(r'href="?([^"\s>]+)"?', html)):
            if href.startswith(("mailto:", "tel:", "#")):
                continue
            if href.startswith("http") and "anonymizemyid.com" not in href:
                continue
            target = href.replace("https://anonymizemyid.com", "") or "/"
            path, _, frag = target.partition("#")
            path = urllib.parse.unquote(path)
            if path and path not in on_disk and not path.endswith((".xml", ".txt")):
                issues.append(f"redirecting/broken link  {url} -> {href}")
            if frag and path in pages:
                if not re.search(rf'id="?{re.escape(frag)}"?[\s>]', pages[path]):
                    issues.append(f"dead anchor            {url} -> {href}")

        for img in re.findall(r"<img[^>]*>", html):
            if "alt=" not in img:
                issues.append(f"img without alt        {url}")
            if "width=" not in img or "height=" not in img:
                issues.append(f"img without dimensions {url}")

        # The social card is the one asset nothing else on the page references,
        # so a missing file is invisible until a link is shared and unfurls
        # blank. Both the per-guide cards and the per-language shared card are
        # picked by string interpolation in head.html, which cannot fail loudly.
        # The [\s>] guard keeps og:image:width and friends out.
        for tag in re.findall(r"<meta[^>]*>", html):
            if not re.search(r'(?:property|name)="?(?:og:image|twitter:image)"?[\s>]', tag):
                continue
            m = re.search(r'content="?(https://anonymizemyid\.com[^"\s>]+)', tag)
            if not m:
                continue
            path = urllib.parse.unquote(m.group(1).replace("https://anonymizemyid.com", ""))
            if path not in on_disk:
                issues.append(f"og:image missing       {url} -> {path}")

        for blob in re.findall(r"<script type=application/ld\+json>(.*?)</script>", html, re.S):
            try:
                graph = json.loads(blob).get("@graph", [])
            except Exception as exc:
                issues.append(f"invalid JSON-LD        {url}: {exc}")
                continue
            for node in graph:
                if node.get("@type") == "Article":
                    for req in ("headline", "image", "datePublished", "author",
                                "publisher", "mainEntityOfPage"):
                        if req not in node:
                            issues.append(f"Article missing {req}  {url}")
                if node.get("@type") == "FAQPage":
                    for q in node.get("mainEntity", []):
                        if not q.get("name") or not q.get("acceptedAnswer", {}).get("text"):
                            issues.append(f"incomplete FAQ entry   {url}")

        if skip:
            continue

        title = first(r"<title>(.*?)</title>", html)
        desc = first(r'<meta name=description content="?([^">]*)"?>', html)
        titles[title] += 1
        descs[desc] += 1

        if len(title) > TITLE_MAX:
            issues.append(f"title {len(title)} chars       {url}")
        if not DESC_MIN <= len(desc) <= DESC_MAX:
            issues.append(f"description {len(desc)} chars  {url}")
        if len(re.findall(r"<h1", html)) != 1:
            issues.append(f"h1 count != 1          {url}")
        if not re.search(r"<link rel=canonical", html):
            issues.append(f"no canonical           {url}")
        if not re.search(r'hreflang="?x-default', html):
            issues.append(f"no x-default           {url}")
        if not re.search(r"<meta name=robots", html):
            issues.append(f"no robots meta         {url}")

        levels = [int(x) for x in re.findall(r"<h([1-6])", html)]
        for a, b in zip(levels, levels[1:]):
            if b > a + 1:
                issues.append(f"heading jump h{a}->h{b}    {url}")
                break

        for lang, href in re.findall(
                r'<link rel=alternate hreflang="?([a-zA-Z-]+)"? href="?([^">]+)', html):
            if lang == "x-default":
                continue
            other = href.replace("https://anonymizemyid.com", "") or "/"
            if other not in pages:
                issues.append(f"hreflang target missing {url} -> {href}")
                continue
            back = [h.replace("https://anonymizemyid.com", "") or "/"
                    for _, h in re.findall(
                        r'<link rel=alternate hreflang="?([a-zA-Z-]+)"? href="?([^">]+)',
                        pages[other])]
            if url not in back:
                issues.append(f"hreflang not reciprocal {url} <-> {other}")

    if "--external" in sys.argv:
        issues += check_external(pages)

    issues += [f"duplicate title x{n}     {t[:50]}" for t, n in titles.items() if n > 1]
    issues += [f"duplicate description x{n} {d[:46]}" for d, n in descs.items() if n > 1]

    # Internal-link distribution: a guide nobody links to will not rank.
    links = collections.defaultdict(set)
    for url, html in pages.items():
        for href in set(re.findall(
                r'href="?(?:https://anonymizemyid\.com)?(/[^"\'\s>#?]*)', html)):
            if not href.endswith((".xml", ".txt", ".png", ".svg", ".ico",
                                  ".webmanifest", ".jpg", ".webp")):
                links[href].add(url)
    # The guide hub is not called "guides" in every language — German publishes
    # it at /de/ratgeber/ (see [languages.de.permalinks] in hugo.toml). Matching
    # only on "/guides/" silently dropped a whole language out of the
    # inbound-link distribution check, which is the one check that notices a
    # guide nothing links to.
    guides = [u for u in pages
              if any(f"/{s}/" in u for s in GUIDE_SECTIONS)
              and not any(u.endswith(f"{s}/") for s in GUIDE_SECTIONS)
              and not u.startswith("/en/")]
    inbound = {u: len(links.get(u, set()) - {u}) for u in guides}

    print(f"pages: {len(pages)}   guides: {len(guides)}")
    if inbound:
        print(f"guide inbound links: min={min(inbound.values())} "
              f"max={max(inbound.values())} mean={sum(inbound.values()) / len(inbound):.1f}")
        for u, n in sorted(inbound.items(), key=lambda kv: kv[1])[:3]:
            print(f"  fewest inbound: {n}  {u}")

    print(f"\nissues: {len(issues)}")
    for i in issues:
        print("  -", i)
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
