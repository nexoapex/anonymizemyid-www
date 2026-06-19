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
themes/aegis/        layouts + assets/css (the theme)
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
  soon"), so platforms can launch one at a time.
- `baseURL` (top of `hugo.toml`) — the production domain.

## SEO & GEO

The site ships a full set of machine-readable signals for search engines and AI
answer engines:

- **`sitemap.xml`** + **`robots.txt`** — `robots.txt` explicitly welcomes AI
  crawlers (GPTBot, ClaudeBot, PerplexityBot, Google-Extended, Applebot, …) and
  points at the sitemap.
- **JSON-LD structured data** (`themes/aegis/layouts/partials/structured-data.html`)
  — `Organization` + `WebSite` everywhere, `SoftwareApplication` + `FAQPage` on
  the home page, `WebPage` + `BreadcrumbList` on inner pages.
- **`llms.txt`** + **`llms-full.txt`** — generated from the live content via Hugo
  output formats (`[outputs]` / `[outputFormats]` in `hugo.toml`).
- **Open Graph + Twitter** cards using `static/images/og.png` (1200×630).
- **Icons & PWA** — `favicon.svg`, `favicon.ico`, 16/32 px PNGs,
  `apple-touch-icon.png`, `icon-192/512.png` and `site.webmanifest` (generated
  from the brand mark with `rsvg-convert`).
- **`humans.txt`** and **`.well-known/security.txt`**.

> When you change the FAQ, edit it in **both** `layouts/index.html` (the visible
> `<details>`) and `partials/structured-data.html` (the `FAQPage` data) so the
> page and its structured data stay in sync.

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
