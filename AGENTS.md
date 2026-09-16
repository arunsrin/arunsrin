# AI Agent Guidelines & Architecture Guide

This repository contains **arunsrin's notes**, a personal digital garden and technical notebook built with **Hugo** and hosted on **Cloudflare Pages** at [https://www.arunsr.in](https://www.arunsr.in).

## 1. Core Principles & Philosophy
- **Performance & Zero Bloat:** Fast load times and 100/100 Lighthouse audit scores are top priorities. Do not introduce heavy frontend frameworks (React, Vue, lodash, jQuery) or render-blocking scripts. All client-side enhancements must use vanilla, deferred JavaScript and lightweight CSS.
- **Visual Identity:** Respect the light blue theme. The signature turquoise-to-sky-blue header gradient is `linear-gradient(#40E0D0, #2fa4e7 75%, #2c9ad9)`. Accent colors are `#0284c7` (light mode) and `#38bdf8` (dark mode).
- **Personality & Delight:** The site embraces subtle, playful Easter eggs (e.g., custom HTTP response headers like `x-lotr`, random fortunes in the footer, CSS animated emojis). Keep this playful spirit intact when adding features.
- **Digital Garden Structure:** Content is organized conceptually (Books, Games, Tech Notes, Research) rather than chronologically. Navigation is multi-column with collapsible section details and hierarchical breadcrumbs.
- **Preserve the Author's Voice & Prose:** Layout, templates, CSS, and structural architecture can be freely adapted and refactored by AI agents. However, **the writing itself must NOT be modified or rewritten**. The prose reflects the personal style, thoughts, and voice of the author (good or bad). Never attempt to "improve", "polish", or rewrite the text of notes, book reviews, or commentaries. *Amendment:* Simple search-and-replace operations for outdated factual/tooling names (e.g., replacing 'mkdocs' with 'hugo') are permitted.

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
The author is particularly strict about rigorous local testing first. Always test your changes locally and verify them on the local preview server. **NEVER commit or push changes to git until the author has tested locally and explicitly confirmed that things are fine.**

```bash
# Run the complete test suite (strict build, JSON validation, link audit, JS & Cloudflare safety)
./scripts/test.sh

# Or execute individual steps:
hugo --gc --minify --panicOnWarning          # Build with zero warnings
jq . public/index.json > /dev/null          # Validate search index
jq . public/static/quotes.json > /dev/null  # Validate quotes database
node scripts/test_js.js                     # Validate JS, Cloudflare caching & Rocket Loader safety

# Start local preview server (bind 0.0.0.0, port 1313)
hugo server --bind 0.0.0.0 --port 1313 -b http://localhost:1313/
```

## 4. Rules of Thumb for Changes
1. **Never commit breaking deprecations:** Hugo builds in CI use `--panicOnWarning` with Hugo v0.147.7 for exact parity with Cloudflare Pages' default build image. Ensure config uses modern Hugo settings (e.g., `locale` instead of `languageCode`), and templates maintain compatibility with Cloudflare Pages' Hugo runner (e.g., use `.Site.Language.Lang` rather than `.Site.Language.Locale` which was only introduced in v0.158+ and fails on older runners).
2. **Cloudflare Rocket Loader & Zero Inline Handlers:** NEVER use inline HTML event handlers (e.g., `onclick="..."`, `onchange="..."`, `onload="..."`). Cloudflare Rocket Loader is enabled on the domain and intercepts inline handlers, silently suppressing events until its async script queue completes. Always attach event listeners unobtrusively in JavaScript via `addEventListener()`.
3. **Static Asset Caching & Cache-Busting:** Never mark unhashed asset paths (like `/css/*` or `/static/*`) as `immutable` in `static_root/_headers` — browsers will permanently cache stale files on disk for up to a year. Use `stale-while-revalidate` for mutable static assets, and always add cache-busting query strings to external asset links in templates (e.g., `href="/css/extra.css?v={{ now.Unix }}"`). Prefer inlining critical, lightweight client styles and scripts (<2KB) directly in partials (`head.html`, `footer.html`) so they deploy atomically with page HTML.
4. **HTML Tag Balance in Markdown:** When using custom container blocks in markdown content (e.g. `<div class="grid cards" markdown>`), always ensure the matching closing `</div>` tag is present to prevent DOM nesting leaks.
5. **Search Index Integrity:** The client search (`layouts/index.json`) loads on `Ctrl+K`. Keep it lean and ensure generated JSON stays strictly valid.
6. **DOM Execution Order:** Always wrap DOM queries in `document.addEventListener('DOMContentLoaded', ...)` when elements may be declared across different partials (e.g. `header.html` referencing `#sidebar-left`).
7. **Link Handling:** Internal links should use Hugo relative permalinks. External links are handled by `layouts/_default/_markup/render-link.html` which adds `target="_blank" rel="noopener noreferrer"` and an external indicator `↗`.
8. **Git Worktrees, Practices & Confirmation Workflow:**
   - **Use Git Worktrees for Parallel Changes:** Implicitly use `git worktree` under `.worktrees/<feature-name>` (gitignored) instead of switching branches in the main working tree whenever making changes parallel to other ongoing tasks or to prevent background dev server (`hugo server`) disruption:
     ```bash
     # Create isolated worktree for a feature/fix
     git worktree add -b <feature-name> .worktrees/<feature-name> master
     
     # Test within worktree
     cd .worktrees/<feature-name> && ./scripts/test.sh
     
     # Cleanup after merge
     git worktree remove .worktrees/<feature-name>
     git branch -d <feature-name>
     ```
   - **CRITICAL Confirmation Workflow:** Never commit and push to remote until the author has tested and explicitly confirmed locally that things are fine. The workflow is: implement -> run `./scripts/test.sh` -> verify on preview server -> prompt author to test locally -> commit and push only upon explicit confirmation. Atomic commits with conventional commit messages.
9. **Sacred Prose Principle:** You can freely iterate on layout containers, HTML templates, CSS classes, and metadata. But do NOT alter the author's writing, phrasing, tone, or opinions in markdown content files. (Simple search/replace for outdated tooling names such as 'mkdocs' -> 'hugo' is permitted).
