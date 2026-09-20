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
  - `layouts/partials/`: Modular components (`header.html`, `footer.html`, `head.html`, `sidebar.html`, `toc.html`, `related-notes.html`).
- `static_root/`: Mounted directly to the site root (`_headers`, `favicon.ico`). Cloudflare caching and security headers live in `static_root/_headers`.
- `scripts/`: Development and testing helper scripts.

## 3. Testing & Verification
The author is particularly strict about rigorous local testing first. Always test your changes locally and verify them on the local preview server. **NEVER commit or push changes to git until the author has tested locally and explicitly confirmed that things are fine.**

```bash
# Run the complete test suite (strict build, JSON validation, link audit, JS & Cloudflare safety)
./scripts/test.ps1                           # Windows PowerShell
./scripts/test.sh                            # WSL / Linux / macOS

# Or execute individual steps:
hugo --gc --minify --panicOnWarning          # Build with zero warnings
jq . public/index.json | Out-Null            # Validate search index (PowerShell)
# or: jq . public/index.json > /dev/null     # (WSL / Bash)
jq . public/static/quotes.json | Out-Null    # Validate quotes database (PowerShell)
# or: jq . public/static/quotes.json > /dev/null # (WSL / Bash)
python scripts/check_links.py                # Cross-platform internal link audit
node scripts/test_js.js                      # Validate JS, Cloudflare caching & Rocket Loader safety
python scripts/test_related_notes.py         # Validate related notes, backlinks & anti-spurious isolation
node scripts/test_search.js                  # Validate search relevance scoring & highlighting

# Local preview servers (automatically managed by agent in background)
# Master baseline: http://localhost:1313/
hugo server --bind 0.0.0.0 --port 1313 -b http://localhost:1313/

# Active feature worktree preview: http://localhost:1314/
cd .worktrees/<feature-name> && hugo server --bind 0.0.0.0 --port 1314 -b http://localhost:1314/
```

## 4. Rules of Thumb for Changes
1. **Never commit breaking deprecations:** Hugo builds in CI use `--panicOnWarning` with Hugo v0.147.7 for exact parity with Cloudflare Pages' default build image. Ensure config uses modern Hugo settings (e.g., `locale` instead of `languageCode`), and templates maintain compatibility with Cloudflare Pages' Hugo runner (e.g., use `.Site.Language.Lang` rather than `.Site.Language.Locale` which was only introduced in v0.158+ and fails on older runners).
2. **Cloudflare Rocket Loader & Zero Inline Handlers:** NEVER use inline HTML event handlers (e.g., `onclick="..."`, `onchange="..."`, `onload="..."`). Cloudflare Rocket Loader is enabled on the domain and intercepts inline handlers, silently suppressing events until its async script queue completes. Always attach event listeners unobtrusively in JavaScript via `addEventListener()`.
3. **Static Asset Caching & Cache-Busting:** Never mark unhashed asset paths (like `/css/*` or `/static/*`) as `immutable` in `static_root/_headers` — browsers will permanently cache stale files on disk for up to a year. Use `stale-while-revalidate` for mutable static assets, and always add cache-busting query strings to external asset links in templates (e.g., `href="/css/extra.css?v={{ now.Unix }}"`). Prefer inlining critical, lightweight client styles and scripts (<2KB) directly in partials (`head.html`, `footer.html`) so they deploy atomically with page HTML.
4. **HTML Tag Balance in Markdown:** When using custom container blocks in markdown content (e.g. `<div class="grid cards" markdown>`), always ensure the matching closing `</div>` tag is present to prevent DOM nesting leaks.
5. **Search Index Integrity:** The client search (`layouts/index.json`) loads on `Ctrl+K`. Keep it lean and ensure generated JSON stays strictly valid.
6. **DOM Execution Order:** Always wrap DOM queries in `document.addEventListener('DOMContentLoaded', ...)` when elements may be declared across different partials (e.g. `header.html` referencing `#sidebar-left`).
7. **Link Handling:** Internal links should use Hugo relative permalinks. External links are handled by `layouts/_default/_markup/render-link.html` which adds `target="_blank" rel="noopener noreferrer"` and an external indicator `↗`.
8. **Git Worktrees ONLY & Automated Dual-Port Preview:**
   - **Always Pull Latest Master First:** Because multiple tasks and fixes proceed in parallel, agents MUST ALWAYS run `git pull origin master` in the root tree before branching or starting any new task.
   - **STRICTLY Use Git Worktrees & Dual-Port Preview (Never Switch Branches in Main Tree):** NEVER switch branches (`git checkout <branch>` or `git switch <branch>`) in the root repository tree. The main working tree must permanently remain on `master`. All feature development, bug fixes, refactoring, and experiments must strictly take place in an isolated worktree created under `.worktrees/<feature-name>`. The agent is strictly responsible for automatically spinning up and maintaining both servers in the background: master on port 1313 (`http://localhost:1313/`) and the active feature worktree on port 1314 (`http://localhost:1314/`). The author never needs to run or restart servers manually.
     ```bash
     # Always pull latest master before branching
     git pull origin master

     # Create isolated worktree for a feature/fix
     git worktree add -b <feature-name> .worktrees/<feature-name> master
     
     # Test and work exclusively within the worktree
     cd .worktrees/<feature-name>
     ./scripts/test.ps1     # PowerShell
     # or: ./scripts/test.sh # WSL / Bash
     
     # Preview servers are launched and maintained automatically by the agent
     # (:1313 for master baseline, :1314 for candidate feature)

     # Cleanup after merge to master
     git worktree remove .worktrees/<feature-name>
     git branch -d <feature-name>
     ```
   - **CRITICAL Confirmation Workflow:** Never commit and push to remote until the author has tested and explicitly confirmed locally that things are fine. The workflow is: implement -> run test suite (`./scripts/test.ps1` or `./scripts/test.sh`) inside worktree -> verify on preview server (port 1314) -> prompt author to test locally -> commit and push only upon explicit confirmation. Atomic commits with conventional commit messages.
9. **Sacred Prose Principle:** You can freely iterate on layout containers, HTML templates, CSS classes, and metadata. But do NOT alter the author's writing, phrasing, tone, or opinions in markdown content files. (Simple search/replace for outdated tooling names such as 'mkdocs' -> 'hugo' is permitted).
10. **Automated Test Mandate for New Code & CI Parity:** Whenever new code, templates, shortcodes, partials, CSS components, or JavaScript behaviors are introduced, Gimli and Legolas MUST author automated regression tests integrated into BOTH `./scripts/test.sh` and the GitHub Actions pipeline (`.github/workflows/ci.yml`) (e.g. dedicated test scripts under `scripts/test_*.py` or `scripts/test_*.js`). Features are never considered complete without automated assertions verifying: (a) structural presence across generated HTML, (b) functional correctness, (c) negative tests preventing unwanted regressions or spurious content, (d) coverage integrity across all affected pages, and (e) execution parity in GitHub CI on every PR and merge.
11. **Dynamic CI Test Discovery & Parity Enforcement (`scripts/test_ci_parity.py`):** GitHub Actions CI (`.github/workflows/ci.yml`) uses dynamic wildcard discovery (`scripts/test_*.py` and `scripts/test_*.js`). All new test suites created under `scripts/` are automatically executed by CI on every push and PR without requiring manual edits to `.github/workflows/*` (which prevents GitHub OAuth `workflow` scope push rejections). CI parity is strictly guarded by `scripts/test_ci_parity.py` (Step 10 in `./scripts/test.ps1` and `./scripts/test.sh`), which physically fails the local build if any test script in `scripts/` is not covered by CI. Never bypass CI parity.
12. **Windows Python UTF-8 Stdout Reconfiguration:** Windows PowerShell console defaults to `cp1252`. Python scripts that print Unicode symbols (e.g. checkmarks `\u2713` or emojis) will crash with `UnicodeEncodeError`. All Python test scripts (`scripts/test_*.py`) MUST include at the top:
    ```python
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    ```
13. **Stacking Contexts & Z-Index Discipline:** Never assign an integer `z-index` (e.g. `z-index: 1`) to top-level layout containers (`.layout-container`) containing fixed drawers or overlays. An integer `z-index` creates an isolated stacking context that traps high z-index descendants (like a mobile drawer at `z-index: 1200`) beneath root-level overlays (`z-index: 1150`). Layout containers must use `z-index: auto`.
14. **Minified HTML Assertion Robustness:** Hugo builds using `--minify` strip quotes from simple HTML attributes (e.g. `id=sidebar-overlay` and `class=sidebar-overlay`). Test assertions checking generated HTML in `public/` must use regex that accommodates optional quotes (e.g. `r'id=["\']?element-id["\'\s>]'`).
15. **Subagent Permission Minimization & The Interruption-Free Reviewer Principle:** Subagents should be granted the minimum tool privileges strictly required for their role. In particular, code review agents (like Elrond) must NOT be spawned with write/shell tools (`enable_write_tools: false`). Arbitrary shell commands (`git log`, `git diff`, `git status`, `Select-String`, `grep`, `cat`) executed by subagents trigger interactive Antigravity CLI permission prompts that disrupt the author. Instead:
    - The orchestrator (Gandalf) pre-gathers the git diff, commit history, and spec context and passes them directly in the subagent's prompt.
    - Review subagents inspect files exclusively via built-in read tools (`view_file`), which are inherently non-destructive and never prompt for permission.
    - Review subagents write and return their structured review verdict directly in their final response message to the orchestrator. The parent orchestrator (Gandalf) then posts the review comment to the GitHub PR using `gh pr comment`.

## 5. Backlog Management (Todoist Integration)
The backlog of website features, improvements, and maintenance tasks is tracked in Todoist under the project **`Site updates 🌐`** (ID: `6hWVfCmh7qC5P3HW`) using the `td` CLI (`@doist/todoist-cli`, setup per [Todoist AI guide](https://www.todoist.com/help/todoist/todoist-and-ai/use-todoist-in-gemini-spark-dEb9IBNVY#h_01M1B8SXGM1ZKPKS66P8SK1EMN)).

- **Actionable AI Tasks (`llm-task`):** Tasks designated for the agent to implement are tagged with the label `llm-task`.
- **Groomed & Execution-Ready (`next`):** Tasks in the backlog that have been reviewed, groomed, and explicitly approved by the author for execution are additionally tagged with the label `next`. The `/site-sprint` workflow strictly scopes tasks matching **both** labels (`llm-task` AND `next`).
- **Capturing New Ideas:** Whenever we discuss or conceive new ideas for the website, automatically create a corresponding task in `Site updates 🌐` with a detailed explanation and acceptance criteria in the description, tagged with `llm-task`:
  ```bash
  td task add "<Task Summary>" --project "Site updates 🌐" --labels "llm-task" --description "<Detailed explanation and acceptance criteria>"
  ```
- **Picking Up Backlog Tasks:** To check for pending tasks:
  ```bash
  # Check groomed tasks ready for sprint execution:
  td task list --project "Site updates 🌐" --filter "@llm-task & @next" --json

  # Or check full backlog status (groomed vs ungroomed) using the sprint helper:
  python scripts/site_sprint.py status
  ```

## 6. Multi-Agent Development Workflow (`/site-sprint`)
When you trigger the `/site-sprint` command (or ask to run an autonomous sprint), an end-to-end multi-agent pipeline is executed by **The Fellowship**:

1. **🧙‍♂️ Gandalf (The Strategist / Living Spec Custodian):**
   - Inspects the Todoist backlog (`python scripts/site_sprint.py pick-next`).
   - Analyzes codebase and architecture.
   - **Interactive Human Gate:** Asks clarifying implementation questions and design tradeoffs.
   - **Living Spec Ownership:** Once you explicitly sign off, writes the approved specification to `docs/specs/<feature-name>.md`. Throughout development and review iterations, Gandalf **continuously updates the specification** as requirements evolve or edge cases are uncovered, ensuring the spec remains the living source of truth.

2. **🔄 The Triad Recursive Loop (Gimli ⇄ Legolas ⇄ Elrond):**
   Steps 2, 3, and 4 form an autonomous recursive convergence loop that runs iteratively in the background until unanimous consensus is achieved:
   - **⚒️ Gimli (The Code Smith / Dev):** Works seamlessly in an isolated worktree (`.worktrees/<feature-name>`), crafting templates, styles, logic, and companion automated regression tests in strict compliance with `docs/specs/<feature-name>.md` and `AGENTS.md` (Sacred Prose, zero bloat, vanilla JS, Cloudflare safety, test coverage).
   - **🏹 Legolas (The Sharp-Eyed Scout / QA & Spec Compliance Enforcer):** Executes the strict test suite (`./scripts/test.ps1` / `./scripts/test.sh`) inside the worktree. Audits that all new code has passing regression tests. If any failure occurs, sends targeted bug reports back to Gimli; repeats until 100% green.
   - **🧝‍♂️ Elrond (The Wise Arbiter / Adversarial Code Reviewer & Chronicle Custodian):** Operates as an adversarial auditor governed by `REVIEW.md` ("assume code is broken until proven bulletproof"). Audits the green diff with fresh eyes across 10 strict review gates (CI parity, stacking contexts, event delegation, Rocket Loader safety, encoding, minification, sacred prose, zero bloat, negative testing, and subagent permission hygiene) in a zero-interruption read-only context (`enable_write_tools: false`) using `view_file`.
     - **Recursive Trigger:** If Elrond flags feedback or requests changes (`🔴 Request Changes`), it **automatically triggers Gimli** to update code and tests, **Gimli's update triggers Legolas** to re-test, and **Legolas's green run triggers Elrond** to re-review.
     - Codifies session friction, gotchas, and annoyances permanently into `AGENTS.md`, `SKILL.md`, and `REVIEW.md`.
     - The Triad loop repeats until **unanimous consensus** is reached (all tests green + Elrond grants `🟢 Approved without reservations`).

3. **🧙‍♂️ Gandalf (Consensus Synthesis, Author Briefing & Gate):**
   - Confirms unanimous consensus among Gimli, Legolas, and Elrond.
   - Validates that `docs/specs/<feature-name>.md` is completely up to date with all architectural decisions and edge cases resolved during the Triad loop.
   - Commits atomically, pushes branch to origin, and posts Elrond's structured review directly to the PR via `gh pr comment`.
   - Automatically spins up and verifies background Hugo servers on :1313 (master baseline) and :1314 (candidate feature worktree).
   - Synthesizes a comprehensive briefing to the author: problem/solution summary, consensus confirmation, live URLs (`http://localhost:1313/` vs `http://localhost:1314/`), PR link, and concrete testing checklist asking for final sign-off.

4. **🚀 Human Sign-off, Merge & Cleanup:**
   - Author reviews live on :1314 vs :1313 and grants sign-off.
   - If author requests changes during review, the Triad loop iterates (Gimli -> Legolas -> Elrond) while Hugo LiveReload updates :1314 in real time.
   - Upon explicit author sign-off, Gandalf merges the PR via `gh pr merge`, pulls master in root repo, safely removes the worktree, and completes the Todoist task.
