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
hugo.toml            site config + [params] (price, store URLs, company details)
content/             _index, privacy, terms, imprint, about, contact (Markdown)
content/guides/      SEO/GEO content hub — _index + one Markdown file per guide
themes/aegis/        layouts + assets/css (the theme)
  layouts/guides/    list.html (hub) + single.html (article) templates
  partials/home-faq.html   single source for the home FAQ (page + schema)
static/images/       favicon, og image, screenshots
netlify.toml         Netlify build settings
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
- Language: English today. The config is i18n-ready (`defaultContentLanguage`,
  a weighted `[languages.en]`, and `hreflang` alternates wired into the
  `<head>`), so a `[languages.es]` can be added without restructuring.

## SEO & GEO

The site ships a full set of machine-readable signals for search engines and AI
answer engines:

- **`sitemap.xml`** + **`robots.txt`** — `robots.txt` explicitly welcomes AI
  crawlers (GPTBot, ClaudeBot, PerplexityBot, Google-Extended, Applebot, …) and
  points at the sitemap.
- **JSON-LD structured data** (`themes/aegis/layouts/partials/structured-data.html`)
  — `Organization` + `WebSite` everywhere; `SoftwareApplication` (iOS + Android)
  + `FAQPage` on the home page; `Article` + `BreadcrumbList` on each guide, with
  an optional `FAQPage` and `HowTo` driven by that guide's front matter
  (`faq:` / `howto:`); `WebPage` / `CollectionPage` on the other inner pages.
- **Content hub for SEO/GEO** (`content/guides/`) — plain-English guides written
  for high-intent queries and answer engines: clear question headings, concise
  citable passages, per-article FAQs, and internal links to the app and siblings.
- **`hreflang`** alternates in the `<head>` (English + `x-default` today;
  i18n-ready for a future Spanish edition).
- **`llms.txt`** + **`llms-full.txt`** — generated from the live content via Hugo
  output formats (`[outputs]` / `[outputFormats]` in `hugo.toml`); `llms.txt`
  lists the guides in their own section.
- **Open Graph + Twitter** cards using `static/images/og.png` (1200×630).
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
> **New guide?** Add `content/guides/<slug>.md` with `title`, `description`,
> `date`/`lastmod`, and optional `faq:` / `howto:` front matter. It is picked up
> automatically by the hub, the home teaser, the sitemap, `llms.txt` and the
> Article/FAQ/HowTo structured data — no template changes needed.

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
