# AI Agent Guidelines & Architecture Guide

This repository contains **arunsrin's notes**, a personal digital garden and technical notebook built with **Hugo** and hosted on **Cloudflare Pages** at [https://www.arunsr.in](https://www.arunsr.in).

## 1. Core Principles & Philosophy
- **Performance & Zero Bloat:** Fast load times and 100/100 Lighthouse audit scores are top priorities. Do not introduce heavy frontend frameworks (React, Vue, lodash, jQuery) or render-blocking scripts. All client-side enhancements must use vanilla, deferred JavaScript and lightweight CSS.
- **Visual Identity:** Respect the light blue theme. The signature turquoise-to-sky-blue header gradient is `linear-gradient(#40E0D0, #2fa4e7 75%, #2c9ad9)`. Accent colors are `#0284c7` (light mode) and `#38bdf8` (dark mode).
- **Personality & Delight:** The site embraces subtle, playful Easter eggs (e.g., custom HTTP response headers like `x-lotr`, random fortunes in the footer, CSS animated emojis). Keep this playful spirit intact when adding features.
- **Digital Garden Structure:** Content is organized conceptually (Books, Games, Tech Notes, Research) rather than chronologically. Navigation is multi-column with collapsible section details and hierarchical breadcrumbs.
- **Preserve the Author's Voice & Prose:** Layout, templates, CSS, and structural architecture can be freely adapted and refactored by AI agents. However, **the writing itself must NOT be modified or rewritten**. The prose reflects the personal style, thoughts, and voice of the author (good or bad). Never attempt to "improve", "polish", or rewrite the text of notes, book reviews, or commentaries.

## 2. Directory Layout
- `home/`: Content directory (mounted to Hugo `content`). Markdown notes live here.
  - `home/css/extra.css`: Custom styling, animations, card grids, tables, and buttons.
  - `home/static/`: Static assets (`quotes.js`, `quotes.json`, self-hosted `iconify-icon.min.js`).
- `layouts/`: Hugo Go templates.
  - `layouts/_default/`: Base layout (`baseof.html`), single note (`single.html`), list view (`list.html`), and render hooks (`_markup/`).
  - `layouts/partials/`: Modular components (`header.html`, `footer.html`, `head.html`, `sidebar.html`, `toc.html`).
- `static_root/`: Mounted directly to the site root (`_headers`, `favicon.ico`). Cloudflare caching and security headers live in `static_root/_headers`.
- `scripts/`: Development and testing helper scripts.

## 3. Testing & Verification
Always test your changes locally before submitting or committing!

```bash
# Run the complete test suite (strict build, JSON validation, internal link audit)
./scripts/test.sh

# Or execute individual steps:
hugo --gc --minify --panicOnWarning          # Build with zero warnings
jq . public/index.json > /dev/null          # Validate search index
jq . public/static/quotes.json > /dev/null  # Validate quotes database

# Start local preview server (bind 0.0.0.0, port 1313)
hugo server --bind 0.0.0.0 --port 1313 -b http://localhost:1313/
```

## 4. Rules of Thumb for Changes
1. **Never commit breaking deprecations:** Hugo builds in CI use `--panicOnWarning`. Ensure all templates use modern Hugo APIs (e.g., `locale` instead of `languageCode`, `.Site.Language.Locale` instead of `.Site.LanguageCode`).
2. **Search Index Integrity:** The client search (`layouts/index.json`) loads on `Ctrl+K`. Keep it lean and ensure generated JSON stays strictly valid.
3. **DOM Execution Order:** Always wrap DOM queries in `document.addEventListener('DOMContentLoaded', ...)` when elements may be declared across different partials (e.g. `header.html` referencing `#sidebar-left`).
4. **Link Handling:** Internal links should use Hugo relative permalinks. External links are handled by `layouts/_default/_markup/render-link.html` which adds `target="_blank" rel="noopener noreferrer"` and an external indicator `↗`.
5. **Git Practices:** Create feature branches for larger sets of changes, make clean atomic commits with conventional commit messages, and test before opening pull requests.
6. **Sacred Prose Principle:** You can freely iterate on layout containers, HTML templates, CSS classes, and metadata. But do NOT alter the author's writing, phrasing, tone, or opinions in markdown content files.
