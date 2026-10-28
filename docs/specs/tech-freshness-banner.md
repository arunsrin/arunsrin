# Feature Specification: Outdated Content Freshness Callout Banner for Tech Notes

## 1. Overview & Context

In a technical digital garden, notes covering rapidly evolving tools, command-line interfaces, APIs, and frameworks (e.g., Kubernetes, Linux, Docker, OpenSSL) drift over time. Commands and flags that worked seamlessly several years ago may be deprecated or behave differently in current releases.

To provide clear expectations for readers without altering or rewriting the author's original prose (preserving the **Sacred Prose Principle**), this feature introduces a polite, automated build-time advisory banner at the top of technical notes that have not been modified in more than 2 years (>730 days).

---

## 2. Technical Architecture & Component Design

### 2.1 Hugo Template Logic (`layouts/partials/freshness-banner.html`)

A dedicated partial is included in `layouts/_default/single.html` directly before the page content:

```html
{{/* Content freshness advisory banner for technical notes */}}
{{ if and (eq .Section "tech") .IsPage }}
  {{ $warningEnabled := default true .Params.freshness_warning }}
  {{ if $warningEnabled }}
    {{ $lastmod := .Lastmod }}
    {{ if $lastmod.IsZero }}
      {{ $lastmod = .Date }}
    {{ end }}
    {{ if not $lastmod.IsZero }}
      {{ $ageSeconds := sub now.Unix $lastmod.Unix }}
      {{/* 730 days * 86400 seconds/day = 63072000 seconds (2 years) */}}
      {{ if gt $ageSeconds 63072000 }}
        {{ $days := div $ageSeconds 86400 }}
        {{ $years := div $days 365 }}
        <aside class="freshness-banner" role="note" aria-label="Content freshness advisory">
          <span class="freshness-banner-icon" aria-hidden="true">⏳</span>
          <div class="freshness-banner-body">
            <strong>Advisory:</strong> This technical reference was last updated over {{ $years }} years ago ({{ $lastmod.Format "Jan 2006" }}). Some CLI flags, APIs, or commands may have changed.
          </div>
        </aside>
      {{ end }}
    {{ end }}
  {{ end }}
{{ end }}
```

### 2.2 Integration in `layouts/_default/single.html`

In `layouts/_default/single.html`, the partial is invoked right above `.content`:
```html
  <div class="page-meta">
    ...
  </div>

  {{ partial "freshness-banner.html" . }}

  <div class="content">
    {{ .Content }}
  </div>
```

### 2.3 Visual Styling & Theme Harmony (`home/css/extra.css`)

The banner adheres strictly to the digital garden visual identity:
- **Soft warning amber/gold tint** with a subtle light-blue accent border (`var(--link-color)` or `#38bdf8`) to maintain continuity with the site header gradient.
- **Light mode:** Warm parchment/amber background (`rgba(245, 158, 11, 0.08)`), warm border (`rgba(245, 158, 11, 0.3)`), left accent border (`3px solid #0284c7`).
- **Dark mode:** Dark amber surface (`rgba(245, 158, 11, 0.12)`), text color adapted to `--text-color`, left accent border (`3px solid #38bdf8`).
- **Responsive & Accessible:** Clean flex layout, rounded corners, unobtrusive spacing, semantically marked as `<aside role="note">`.

```css
.freshness-banner {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  margin: 1.25rem 0 1.5rem 0;
  padding: 0.85rem 1rem;
  border-radius: 0.5rem;
  background-color: rgba(245, 158, 11, 0.08);
  border: 1px solid rgba(245, 158, 11, 0.25);
  border-left: 4px solid #0284c7;
  color: var(--text-color);
  font-size: 0.9rem;
  line-height: 1.5;
}

[data-theme="dark"] .freshness-banner {
  background-color: rgba(245, 158, 11, 0.12);
  border-color: rgba(245, 158, 11, 0.35);
  border-left-color: #38bdf8;
}

.freshness-banner-icon {
  font-size: 1.2rem;
  line-height: 1.2;
  flex-shrink: 0;
}

.freshness-banner-body {
  flex: 1;
}
```

---

## 3. Acceptance Criteria

1. **Section Isolation:** Banner renders strictly on notes residing in the `tech/` section. Notes in `books/`, `games/`, `posts/`, `other-interests/`, and root pages (`about.md`, `uses.md`, `now.md`) must never display the banner.
2. **Age Threshold (> 730 Days):** Banner is rendered exclusively when the note's `.Lastmod` (or `.Date`) is older than 730 days (> 2 years) relative to Hugo build time (`now`).
3. **Dynamic Time Formatting:** The copy dynamically displays the elapsed duration and month/year: e.g., `"over 3 years ago (Oct 2023)"`.
4. **Frontmatter Opt-Out:** If a note frontmatter specifies `freshness_warning: false`, the banner is suppressed regardless of age.
5. **Zero Client-Side JavaScript Runtime:** 100% build-time Go template logic. Zero client-side script overhead, zero impact on Lighthouse performance.
6. **Sacred Prose Preservation:** No markdown content or author prose is modified or rewritten.
7. **Automated Regression Testing:** Companion automated test suite authored in `scripts/test_freshness_banner.py` validating presence, absence, styling hooks, and opt-out behavior across generated pages in `public/`.
8. **Test Suite Parity:** `./scripts/test.ps1` and GitHub Actions CI pass cleanly with zero warnings (`--panicOnWarning`).
