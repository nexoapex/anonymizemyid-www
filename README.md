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
- Store launch: set `appStoreUrl` / `playStoreUrl` and `comingSoon = false` to
  turn the "Coming soon" badges into live download links.
- `baseURL` (top of `hugo.toml`) — the production domain.

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
