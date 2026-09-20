# Feature Specification: Bi-directional Backlinks & Unified Related Notes

## 1. User Story & Context
As a reader exploring arunsrin's digital garden, I want to see meaningful connections between notes — whether a note is explicitly referenced by another note ("Mentioned In"), directly links outward to another note ("Referenced"), or shares related intellectual themes and topics — combined into a single, cohesive **`🔗 Related Notes`** section at the bottom of each page.

## 2. Layout & Architectural Principles
1. **Single Unified Section (`🔗 Related Notes`):**
   - Instead of fragmented or empty "Mentioned In" blocks, all relational signals are unified into one card deck directly beneath note content (`layouts/_default/single.html`).
2. **Prioritized Relationship Badges:**
   - `Mentioned In` (score 500, turquoise badge): Notes that explicitly link to this note (backlinks), rendered with the contextual sentence excerpt where the mention occurs.
   - `Referenced` (score 400, sky-blue badge): Notes linked directly from within the current note's markdown body.
   - `#topic` (score 100 per tag, topic pill): Notes sharing focused, meaningful tags (e.g. `#devops`, `#monitoring`, `#psychology`, `#nabokov`).
   - `In this series` (score 50, series pill): Tightly scoped siblings in structured leaf categories (e.g. *Oxford - A Very Short Introduction Series*).
3. **Anti-Spurious Topic Isolation:**
   - Blanket bucket tags (`books`, `games`, `research`, `non-fiction`, `fiction`, `tech`) are strictly excluded from tag similarity calculations so unrelated notes (such as COVID-19 or Capitalism on Productivity) never match.
4. **100% Regular Content Coverage:**
   - 100% of regular content notes (57/57) surface between 2 and 5 high-signal recommendations.

## 3. Acceptance Criteria
1. **Backlink & Mention Discovery:**
   - Detect pages in `site.RegularPages` whose `.Content` links to the current page.
   - Extract plain-text contextual excerpt around the link (cleanly stripping icon shortcodes and markdown hashes).
2. **Outgoing Reference Discovery:**
   - Surface notes directly referenced by the current page.
3. **Topic Matching:**
   - Discover topic-related notes using enriched metadata tags without topic bleed.
4. **Clean Snippets:**
   - Zero unparsed icon syntax (`:material-*:`, `:simple-*:`, `:fontawesome-*:`) or heading hashes (`#`) in card snippets.
5. **Sacred Prose Principle:**
   - Zero modifications to the author's prose in markdown files. Frontmatter metadata tags are used for topic clustering.
6. **Zero Bloat & Cloudflare Safety:**
   - 100% build-time Hugo partial rendering; zero client-side render-blocking JS.
   - Zero inline event handlers (Cloudflare Rocket Loader safe).
7. **Automated Test Coverage:**
   - Integrated test suite in `scripts/test_related_notes.py` executed by `./scripts/test.sh` asserting 100% coverage, mention accuracy, reference accuracy, anti-spurious isolation, and clean formatting.
