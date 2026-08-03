# anonymizemyid-www

The public marketing + legal website for **[Anonymize my ID](https://anonymizemyid.com)**
— a privacy-first, on-device ID/passport anonymizer by
**[Nexo Apex S.L.](https://nexoapex.com)**

Built with **Hugo** (from-scratch theme `aegis`, charcoal + amber, mobile-first).
The mobile app lives in a separate private repo.

## Develop

```bash
hugo server          # http://localhost:1313 (live reload)
hugo --gc --minify   # build static site to ./public
```

Requires Hugo **extended** ≥ 0.163.

## Structure

```
hugo.toml            site config + [languages.en|es|de] + shared [params]
i18n/                UI string tables — en/es/de.toml (one key per string)
content/             _index, privacy, terms, imprint, about, contact (+ .es.md/.de.md)
content/guides/      SEO/GEO content hub — _index + one Markdown file per guide (+ .es.md/.de.md)
themes/aegis/        layouts + assets/css (the theme)
  layouts/guides/    list.html (hub) + single.html (article) templates
  layouts/index.rsl.xml    RSL 1.0 AI-licensing terms -> /license.xml
  layouts/sitemap.xml      overrides Hugo's built-in template to add x-default
  layouts/_markup/render-table.html   wraps markdown tables for mobile scroll
  layouts/shortcodes/fieldmap.html    the passport field-map diagram
  partials/home-faq.html   single source for the home FAQ (page + schema, per language)
  partials/lang-switch.html   EN|ES switcher; head.html carries the redirect script
assets/images/og/    per-guide social cards (see scripts/og-card.py)
static/images/       favicon, shared og image, screenshots
scripts/             audit + verification tooling (see "Verify & audit")
netlify.toml         Netlify build settings, security headers, CSP
```

## Configure

All tunables are in `hugo.toml` under `[params]`:

- Product copy: `appName`, `tagline`, `price`, `freeUses`.
- Legal entity: `company`, `vat`, `address`, `phone`, `email`, `privacyEmail`.
- Store launch: set `appStoreUrl` / `playStoreUrl` to the real store links to
  turn each "Coming soon" badge into a live download button. Each badge flips
  independently as soon as its URL is set (leave it as `#` to stay "Coming
  soon"), so platforms can launch one at a time. `appStoreId` powers the iOS
  Safari smart-banner meta tag and the app's structured data. Both stores are
  live: iOS (`apps.apple.com/app/id6781656126`) and Google Play.
- `baseURL` (top of `hugo.toml`) — the production domain.
- Per-language copy lives under `[languages.en.params]` / `[languages.es.params]`
  (`tagline`, `description`, `price`, `priceNote`, `priceDisclaimer`); everything
  shared (brand, store URLs, legal entity) stays in the root `[params]`.

## Languages (EN + ES + DE)

The site is trilingual: **English** is the default, served at `/`; **Spanish** at
`/es/`; **German** at `/de/`. Adding a fourth language is: a `[languages.xx]`
block in `hugo.toml`, an `i18n/xx.toml`, and `*.xx.md` content files — the
templates read the language list rather than branching on it.

- **UI strings** are in `i18n/<lang>.toml` and used via `{{ i18n "key" }}`.
  Page text is translated by filename — `about.md` (EN) + `about.es.md` (ES) +
  `about.de.md` (DE).
- **Language detection & redirect** — a tiny inline script in `partials/head.html`
  reads the browser language (and any explicit choice saved by the switcher) and
  redirects, say, a de-preferring visitor from an English page to its German
  twin, using the page's own `hreflang` links. It only ever redirects **away
  from English** on its own, so a crawler (Accept-Language en, no stored choice)
  that lands on `/es/` or `/de/` indexes that URL instead of being bounced. The
  `EN|ES|DE` switcher (`partials/lang-switch.html`) stores the choice in
  `localStorage` so it sticks. **Editing this script changes the CSP hash** —
  see "Verify & audit".
- **hreflang + x-default** alternates are emitted for every page from
  `.AllTranslations`; English is `x-default`. A language may claim extra
  regional targets via `hreflangAlso` in its params: German declares `de-AT` and
  `de-CH` pointing at the same `/de/` URL, so a search in Vienna or Zurich
  resolves to the German edition rather than the English one. `head.html` and
  `layouts/sitemap.xml` both read that list, so the two can't disagree.
- **The German guide hub is at `/de/ratgeber/`**, not `/de/guides/` —
  `[languages.de.permalinks]` renames the section, because *Ratgeber* is the
  word German search actually uses. Build links from `site.GetPage "/guides"`
  and the page's own `.RelPermalink`, never a hand-built `/guides/` path.
- **The app screenshots stay English on purpose.**
  `assets/images/screens/app-home.png` is a real capture of the product, and the
  product is English-only — which every language's `app_lang_note` says out
  loud. Drawing a German or Spanish UI and presenting it as a screenshot would
  be a false product claim, and it would contradict the site's own copy. The
  before/after strip is likewise genuine app output over a US State Department
  **specimen** passport ("EP Exemplar Book", CANCELLED); replacing it with a
  synthetic German or Spanish document would look better targeted and stop being
  evidence. Per-language document artwork belongs in the OG cards and the
  `fieldmap` shortcode, which are ours to draw. If the hero should speak German,
  the fix is localising the app.
- **The German edition covers DACH, not just Germany.** Where the law differs,
  the guides carry the Austrian and Swiss position beside the German one, and
  five guides exist **only** in German because the query does: § 20 PAuswG,
  PostIdent/VideoIdent, Kleinanzeigen, SCHUFA, and Austria + Switzerland. A
  guide with no English twin is fine — Hugo pairs by filename and simply emits
  one alternate.

## SEO & GEO

The site ships a full set of machine-readable signals for search engines and AI
answer engines:

- **`sitemap.xml`** + **`robots.txt`** — `robots.txt` explicitly welcomes AI
  crawlers (GPTBot, ClaudeBot, PerplexityBot, Google-Extended, Applebot, …) and
  points at the sitemap and the licence.
- **JSON-LD structured data** (`themes/aegis/layouts/partials/structured-data.html`)
  — `Organization` (with `sameAs`, `contactPoint`, `ImageObject` logo) + `WebSite`
  everywhere; `SoftwareApplication` with an `AggregateOffer` over the real
  0–4 € range + `FAQPage` on the home page; `Article` + `BreadcrumbList` +
  `Person` on each guide, with optional `FAQPage` / `HowTo` from that guide's
  front matter; an `ItemList` of every guide on the hub; and the specific
  `AboutPage` / `ContactPage` / `PrivacyPolicy` / `TermsOfService` subtypes
  rather than a generic `WebPage`.
- **Short-answer blocks** — every guide carries `answer:` and `takeaways:` front
  matter, rendered above the fold as a "Short answer" card and published three
  ways: on the page, as `Article.abstract`, and into `llms.txt` /
  `llms-full.txt`. This is the passage an AI answer engine is meant to quote,
  so it is written deliberately rather than left to be summarised out of prose.
- **Content hub for SEO/GEO** (`content/guides/`) — plain-English guides written
  for high-intent queries and answer engines: question headings, comparison
  tables, per-article FAQs, claims linked to primary sources (ICAO 9303, GDPR,
  the EU AML directive, BOE), and a field-map diagram (`{{< fieldmap >}}`).
- **Internal linking** — the "Keep reading" block shows **five**: four from
  Hugo's `[related]` index over each guide's `keywords:`, plus **one reserved
  slot** filled from the rest of the hub rotated by the page's own weight.
  Keyword overlap is high enough that `[related]` used to fill every slot, so
  the rotation never ran and inbound links spread 3–18, starving the
  highest-intent pages (bank/KYC, hotel, employer). Reserving one of the four
  instead of adding a fifth is worse — it redistributes nothing and costs every
  page a topical link. Now 5–19, mean 8.9.
- **`Article.citation`** — the external primary sources are read out of each
  guide's *rendered body* (`findRE` over `.Content`, own-domain links dropped),
  so the provenance an answer engine sees cannot drift from the links actually
  in the prose. Adding a source to a guide is all it takes.
- **`Article.about`** — entity grounding. Each guide's existing (translated)
  `keywords:` are mapped to `Thing`s with a `sameAs` pointing at a canonical
  description, so an engine ties the page to an entity it already holds instead
  of resolving a bag of strings. Scenario guides whose keywords are situational
  ("landlords", "hosts") take the baseline *Identity document* entity rather
  than a stretched one.
- **Author E-E-A-T** — a named `Person` (`url`, `jobTitle`, `description`,
  `knowsAbout`, `sameAs`) plus a visible author card on every guide.
- **`hreflang`** alternates in the `<head>` for every page (`en`, `es`, and
  `x-default` → English), plus per-language `og:locale` / `og:locale:alternate`,
  mirrored as `xhtml:link` alternates in the sitemaps.
- **Translated slugs** — every `.es.md` and `.de.md` guide sets `slug:`, so
  Spanish pages live at `/es/guides/como-censurar-un-pasaporte-o-dni/` and
  German ones at `/de/ratgeber/ausweis-oder-reisepass-schwaerzen/` rather than
  the English path. `netlify.toml` 301s every old `/es/` URL (the German set was
  born with its own slugs, so it needs none). Translations still pair by
  filename, so `hreflang` and the OG cards are unaffected. **Adding a translated
  guide means adding a `slug:`** — and if you ever rename one, add the 301.
- **`llms.txt`** + **`llms-full.txt`** — generated per language (`/llms.txt`,
  `/es/llms.txt`, …) from the live content via Hugo output formats; both carry
  each guide's short answer, so an agent that only fetches `llms.txt` still
  gets the answer rather than a bare description.
- **`license.xml`** — [RSL 1.0](https://rslstandard.org/rsl) AI-licensing terms,
  permitting `search ai-input ai-train` with `payment type="attribution"`.
  Purely declarative and additive: `robots.txt` stays `Allow: /`, so a crawler
  that does not speak RSL is unaffected. Discoverable three ways (a `License:`
  directive in `robots.txt`, `<link rel="license">` in the head, and an HTTP
  `Link:` header). **To withdraw training rights, delete `ai-train` from the one
  `<permits>` line in `layouts/index.rsl.xml`** — nothing else changes.
- **Sitemaps** — a sitemap index at `/sitemap.xml` referencing the per-language
  `/en/sitemap.xml` and `/es/sitemap.xml`; `robots.txt` points at the index.
  `layouts/sitemap.xml` overrides Hugo's built-in template to add `x-default`.
- **Open Graph + Twitter** cards — all generated by `scripts/og-card.py`
  (1200×630), in two kinds: a per-guide card
  (`assets/images/og/<slug>[.<lang>].png`) and a shared per-language card
  (`static/images/og[.<lang>].png`) for the home page, the guides hub and the
  legal pages. **The shared card used to be one hand-made English image served
  to every language**, so a link to `/de/` or `/es/` unfurled in English with an
  English phone screenshot in it. Guides emit `og:type=article` with
  `article:published_time` / `modified_time` / `author` / `section` / `tag`.

  The card draws a schematic identity document with a vertical amber seam: left
  of the seam the sensitive fields are raw character marks, right of it they are
  covered and the app's watermark is tiled over them, while the two fields you
  keep visible run through unchanged. It reads as "sensitive fields covered"
  before a word is read, which is what matters — most of these are seen at
  ~300px wide in a chat client, where a title and a grey rectangle read as
  nothing at all. Everything in words comes from the site's own config (taglines
  from `hugo.toml`, section names from `i18n/<lang>.toml`) so a copy change
  cannot leave the cards behind; only the document label and its four field
  labels live in the script, because nothing on the site renders those.

  Two things in the template are load-bearing and not free to nudge: the seam is
  positioned at a fixed `left:729px` inside `.doc`, and the two cover widths
  (`50.97%` on the field tracks, `69.86%` on the MRZ) are derived from it. Change
  the sheet's padding and they stop lining up. The title ladder holds
  `size × 1.08 × lines ≤ 195px` so the document below never gets squeezed;
  the `<h1>` is clamped to three lines so a pathological title steps down a rung
  rather than pushing the machine-readable zone off the canvas.
- **IndexNow** — `static/f6ac9814062bc1ee81990d078bb1e23f.txt` is the key file.
  Covers Bing, Yandex and Copilot; Google does not participate.
- **Icons & PWA** — `favicon.svg`, `favicon.ico`, 16/32 px PNGs,
  `apple-touch-icon.png`, `icon-192/512.png` and `site.webmanifest` (generated
  from the brand mark with `rsvg-convert`).
- **`humans.txt`** and **`.well-known/security.txt`**.

> The home FAQ lives in one place — `themes/aegis/layouts/partials/home-faq.html`
> (a returning partial). Both the visible `<details>` in `layouts/index.html` and
> the `FAQPage` JSON-LD in `partials/structured-data.html` read from it, so the
> page and its structured data can't drift. Each guide's own FAQ works the same
> way, from its `faq:` front matter.
>
> **New guide?** Add `content/guides/<slug>.md` **and `<slug>.es.md` /
> `<slug>.de.md`** with `title`, `description`, `date`/`lastmod`, `weight`,
> `keywords`, `answer`, `takeaways`, and optional `faq:` / `howto:` (plus
> `slug:` on any non-English file). The hub, home teaser, sitemap, `llms.txt`,
> related-content index and Article/FAQ/HowTo structured data all pick it up
> with no template changes. Two things do **not** happen by themselves: run
> `python3 scripts/og-card.py <slug>` for its social cards — it generates one
> per language file that exists — and give it a `weight`, since guides are
> ordered by weight, not by date.
>
> German copy uses **„…“** quotes and the formal **Sie** throughout. An ASCII
> `"` closing a `„` inside front matter silently breaks the YAML parse — Hugo
> then reports a front-matter error for a line that looks perfectly fine.
>
> If the guide's body already opens with its own "Short answer:" line, rewrite
> that opening — the `answer:` card now sits directly above it.

## Verify & audit

Five scripts, all standalone (`scripts/verify.py` and `scripts/og-card.py` need
`pip install playwright && playwright install chromium`):

```bash
hugo --gc --minify
python3 scripts/audit.py            # static SEO audit; exits non-zero on any issue
python3 scripts/audit.py --external # ...plus HEAD every off-site URL (needs network)
python3 scripts/verify.py           # loads ./public in real Chromium under the prod headers
python3 scripts/verify.py --live    # same, against https://anonymizemyid.com
python3 scripts/csp-hashes.py --write   # recompute the CSP hashes after a CSS/inline-JS change
python3 scripts/og-card.py --all    # generate any missing OG cards
python3 scripts/og-card.py --all --force   # redraw all of them after a design change
python3 scripts/indexnow.py --new   # ping IndexNow with the URLs the last commit touched
```

`indexnow.py` runs **after** the deploy is live, not before — it announces URLs,
so submitting a page Netlify has not published yet just burns the submission.
Submit only what changed: the protocol treats resubmitting unchanged pages as
spam. It covers Bing (and therefore Copilot), Yandex and DuckDuckGo; Google does
not participate, so a new page still needs Search Console on that side.

**Read this before touching `main.css`, `partials/head.html`,
`partials/cookie-consent.html` or `assets/js/consent.js`:**

- The **CSP is hash-based**, because Netlify headers are static and cannot carry
  a per-request nonce. It only works because every inline `<style>`/`<script>`
  is byte-identical on every page. Change the CSS or the inline redirect script
  and the hash changes — a stale hash means the browser **silently blocks** the
  stylesheet in production, with no build error. `scripts/csp-hashes.py` asserts
  the invariant (exactly one distinct hash of each kind) and updates
  `netlify.toml`. A *new* inline `<script>` is a *new* hash, not a swap.
  Never use a `style="..."` attribute — it is blocked the same way.
  `--write` rewrites the hashes **inside each directive**; it used to guess
  which stale hash to replace and, for a changed *script*, wrote the
  stylesheet's hash into `script-src`. Always finish with `scripts/verify.py`,
  which loads the real pages under these headers and listens for
  `securitypolicyviolation` — that is what catches this class of mistake.
- **Google Analytics must make zero network contact before consent.** It is
  injected only by `assets/js/consent.js` after an explicit Accept; nothing
  Google-shaped may go back into static markup. `scripts/verify.py` asserts this
  on every page it loads.
- Build internal links from the page's own `.RelPermalink`, never
  `"/privacy" | relLangURL` — the latter drops the trailing slash and every hit
  then 301s. `scripts/audit.py` catches this.

## Deploy (Netlify, free tier)

1. Netlify → **Add new site → Import an existing project → GitHub →**
   `nexoapex/anonymizemyid-www`.
2. Build settings come from `netlify.toml` (Hugo, `public/`).
3. Add the custom domain `anonymizemyid.com` and enable HTTPS.

Any static host works too (Cloudflare Pages, GitHub Pages); just run
`hugo --gc --minify` and serve `public/`.

---

© Nexo Apex S.L. Site content and theme are proprietary. Screenshots are
generated from the app; no third-party assets are bundled in this repo.
