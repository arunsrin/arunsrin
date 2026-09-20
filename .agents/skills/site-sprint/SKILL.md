---
name: site-sprint
description: "Autonomous multi-agent sprint cycle for arunsrin's notes: Gandalf (PM - interviews author & refines Todoist requirements) -> Gimli (Dev - crafts code in worktree) -> Legolas (QA - runs strict test suite with feedback loop) -> Elrond (Reviewer - independent code audit, PR review & retrospective rule codification) -> Gandalf (validates sign-off) -> Git push and Pull Request for human review. Trigger via `/site-sprint` or when asked to run a multi-agent sprint."
---

# Multi-Agent Development Sprint (`/site-sprint`)

This skill orchestrates an autonomous multi-agent feature sprint for **arunsrin's notes** ([https://www.arunsr.in](https://www.arunsr.in)).

```
  ┌──────────────────────────────────────────────┐
  │ 🧙‍♂️ Phase 1: Gandalf (The Strategist / PM)     │
  │ Queries Todoist backlog ('Site updates 🌐'), │
  │ interviews the author on implementation,     │
  │ and secures explicit human sign-off.         │
  └──────────────────────┬───────────────────────┘
                         │ (Human Sign-off)
                         ▼
  ┌──────────────────────────────────────────────┐
  │ ⚒️ Phase 2: Gimli (The Code Smith / Dev)     │
  │ Crafts feature inside isolated git worktree   │
  │ (.worktrees/<name>) in the background.       │
  └──────────────────────┬───────────────────────┘
                         │
                         ▼
  ┌──────────────────────────────────────────────┐
  │ 🏹 Phase 3: Legolas (The Scout / QA Tester)  │
  │ Runs ./scripts/test.sh; catches regressions; │
  │ loops feedback to Gimli until 100% green.    │
  └──────────────────────┬───────────────────────┘
                         │ (All tests pass)
                         ▼
  ┌──────────────────────────────────────────────┐
  │ 🧝‍♂️ Phase 4: Elrond (The Wise Arbiter / Review)│
  │ Independent code review with fresh eyes;     │
  │ codifies session lessons into AGENTS.md;     │
  │ posts review comments on PR for Gimli loop.  │
  └──────────────────────┬───────────────────────┘
                         │ (Review feedback resolved)
                         ▼
  ┌──────────────────────────────────────────────┐
  │ 🧙‍♂️ Phase 5: Gandalf (Final Validation Gate)  │
  │ Confirms diff matches signed-off criteria;   │
  │ manages dual-port servers & author briefing. │
  └──────────────────────┬───────────────────────┘
                         │
                         ▼
  ┌──────────────────────────────────────────────┐
  │ 🚀 Phase 6: Human Sign-off, Merge & Cleanup  │
  │ Author reviews live and gives sign-off;      │
  │ Gandalf merges PR, cleans worktree & closes. │
  └──────────────────────────────────────────────┘
```

---

## The Fellowship (Agent Personas)

1. 🧙‍♂️ **Gandalf (The Strategist / Living Spec Custodian):**
   - **Motto:** *"All we have to decide is what to do with the time that is given us."*
   - **Role:** Queries Todoist, analyzes architecture, interviews the human author with clarifying questions and design tradeoffs, authors `docs/specs/<feature-name>.md`, and **continuously maintains and updates the specification** as requirements evolve throughout development, iteration, and author review.
2. ⚒️ **Gimli (The Code Smith / Developer):**
   - **Motto:** *"Faithless is he that says farewell when the road darkens."*
   - **Role:** Works in the background inside an isolated worktree (`.worktrees/<name>`). Implements HTML, CSS, JS, and Hugo templates in **strict compliance** with `docs/specs/<feature-name>.md` and `AGENTS.md` (Sacred Prose, zero bloat, vanilla JS, Cloudflare safety, and mandatory automated test authoring).
3. 🏹 **Legolas (The Sharp-Eyed Scout / QA & Spec Compliance Enforcer):**
   - **Motto:** *"A red sun rises. Blood has been spilled this night... or a link was broken."*
   - **Role:** Ruthlessly tests the worktree with `./scripts/test.ps1` (PowerShell) or `./scripts/test.sh` (WSL). **Enforces spec compliance:** systematically verifies that every acceptance criterion in `docs/specs/<feature-name>.md` has companion automated regression tests that pass cleanly. Sends precise reproduction steps and error logs back to Gimli until zero defects remain.
4. 🧝‍♂️ **Elrond (The Wise Arbiter / Code Reviewer & Chronicle Custodian):**
   - **Motto:** *"The house of Elrond was a refuge for the weary and the oppressed, and a treasury of good counsel and wise lore."*
   - **Role:** Independently audits the codebase with a fresh pair of eyes before human review. Scrutinizes architectural elegance, edge cases, accessibility, visual hierarchy, and maintainability. Identifies session friction, annoyances, and pitfalls to codify as permanent rules in `AGENTS.md` and `SKILL.md`. Posts actionable code review comments directly on the GitHub PR for Gimli to iterate on.

---

## Sprint Execution Procedure

### Phase 1: Interactive Scoping & Human Sign-off (🧙‍♂️ Gandalf)

1. **Backlog Inspection:**
   Inspect Todoist for groomed tasks ready for execution:
   ```bash
   python scripts/site_sprint.py pick-next
   # or in WSL/Bash: ./scripts/site_sprint.py pick-next
   # or: td task list --project "Site updates 🌐" --filter "@llm-task & @next" --json
   ```
   - **Groomed Tasks (`llm-task` + `next`):** Pick the highest-priority task that has been reviewed and groomed by the author (tagged with both `llm-task` and `next`).
   - **If no groomed tasks are found:** Check `python scripts/site_sprint.py status`. Inform the author of any pending ungroomed AI tasks (`llm-task` only) awaiting their review and `next` tag, or audit digital garden notes/templates to propose new candidate tasks.
   - Do NOT pick or execute tasks that lack the `next` tag without explicit human instruction.

2. **Codebase & Architectural Analysis:**
   Inspect related files, templates, styles, and data structures. Identify potential tradeoffs, UX choices, or edge cases.

3. **Interactive Human Interview & Sign-off Gate:**
   - Present the proposed feature, approach, and options to the author.
   - Ask clarifying implementation questions (e.g. design preferences, content sources, scope limits).
   - **CRITICAL GATE:** Do NOT dispatch background agents until the human author answers and explicitly confirms/signs off (e.g. "Proceed", "Looks good", or specific direction).

4. **Generate Feature-Specific Specification (`docs/specs/<feature-name>.md`):**
   Once sign-off is received, author `docs/specs/<feature-name>.md` (e.g. `docs/specs/bi-directional-backlinks.md`). Specs are uniquely named by feature so they permanently accumulate in `master` as living architecture documentation and avoid git merge overwrites. The spec must contain:
   - User Story & Context
   - Numbered, verifiable Acceptance Criteria
   - Core Guardrails from [AGENTS.md](../../AGENTS.md) (Sacred Prose, zero bloat, light blue visual theme, Rocket Loader safety).

---

### Phase 2: Background Code Crafting (⚒️ Gimli)

1. **Always Pull Latest Master & Isolated Worktree Creation:**
   Ensure the main repository tree permanently stays on `master` and incorporate any parallel merges before branching:
   ```bash
   git pull origin master
   git worktree add -b <feature-name> .worktrees/<feature-name> master
   ```

2. **Implementation:**
   Gimli implements all requirements specified in `docs/specs/<feature-name>.md` within `.worktrees/<feature-name>`:
   - Clean, lightweight vanilla JS (no frameworks).
   - Responsive styling adhering to the light blue gradient theme.
   - No modification to existing author prose in markdown files.
   - Tags properly closed and balanced.

3. **Mandatory Companion Automated Test Authoring & CI Parity:**
   Whenever new code, templates, shortcodes, partials, CSS components, or JavaScript behaviors are introduced, Gimli MUST author corresponding automated regression tests and wire them into BOTH `./scripts/test.ps1` / `./scripts/test.sh` and the GitHub Actions CI workflow (`.github/workflows/ci.yml`) (e.g. dedicated test scripts under `scripts/test_*.py` or `scripts/test_*.js`).
   *Test Authoring Criteria:*
   - **New Templates / Partials:** Assert presence of generated DOM elements, correct CSS class hooks, and zero template execution errors across pages.
   - **Content & Taxonomy Logic:** Assert coverage integrity across notes, relationship accuracy, and include negative tests preventing spurious matches or topic leaks.
   - **Client-Side Scripts:** Assert event listener correctness, Rocket Loader compatibility (zero inline handlers), and state persistence.
   - **CI Parity:** Every test run locally in `./scripts/test.ps1` / `./scripts/test.sh` must also run in GitHub Actions on every PR and merge.
   - **Zero Untested Features:** A feature is NEVER considered complete without accompanying automated test coverage.

---

### Phase 3: Background QA Verification Loop (🏹 Legolas)

1. **Automated Test Run & Test Coverage Audit:**
   Legolas audits that automated regression tests exist for all newly introduced code in the diff, and executes the strict test suite inside the worktree:
   ```bash
   python scripts/site_sprint.py run-tests .worktrees/<feature-name>
   # or: cd .worktrees/<feature-name> && ./scripts/test.ps1 (PowerShell) / ./scripts/test.sh (WSL)
   ```
   If new code lacks companion automated tests in the test suite, Legolas rejects the build and instructs Gimli to author tests before certifying approval.

2. **Automated Feedback Loop:**
   - **On Any Failure (Exit code != 0 or missing test coverage):**
     1. Legolas captures exact failing logs, stack traces, and affected files.
     2. Formulates a targeted bug report for Gimli.
     3. Gimli applies fixes and adds missing tests in the worktree.
     4. Legolas re-tests. (Repeats seamlessly in the background up to 3 iterations).
   - **On Complete Pass (All test suites green, 0 Hugo warnings, 100% test coverage):**
     Legolas issues a QA sign-off certification.

---

### Phase 4: Independent Code Review & Retrospective Loop (🧝‍♂️ Elrond)

1. **Zero-Interruption Invocation & Context Provisioning:**
   - Gandalf pre-generates the branch git diff against master (`git diff master`) and commit summary.
   - Gandalf invokes Elrond with **read-only tools** (`enable_write_tools: false`), passing the branch diff, PR number/URL, and living spec directly in the prompt.
   - This ensures Elrond operates completely interruption-free without triggering interactive CLI permission prompts for `git log` or `git diff`.

2. **Independent Code Audit:**
   Elrond audits the changes using `view_file` to inspect templates, CSS, JS, and test scripts:
   - Evaluates code simplicity, CSS stacking context integrity, and vanilla JS efficiency.
   - Checks edge cases (e.g. mobile drawer interactions, resize behavior, accessibility hooks).
   - Verifies Rocket Loader safety and zero inline event handlers.

3. **Session Retrospective & Rule Codification:**
   - Evaluates friction, annoyances, and gotchas experienced during the session (e.g. tool scope limits, encoding quirks, framework traps).
   - Codifies lasting solutions permanently into `AGENTS.md` and `SKILL.md` so the team never encounters the same friction again.

4. **Actionable PR Review Comments:**
   - Elrond formats his structured review with a clear verdict (🟢 Approved or 🔴 Request Changes) and returns it in his final message to Gandalf.
   - Gandalf posts the review comment to the GitHub PR using `gh pr comment <pr-number> --body "<markdown>"`.
   - If improvements are flagged, Gimli iterates inside the worktree and Legolas re-verifies until Elrond signs off.

---

### Phase 5: Final Validation Gate (🧙‍♂️ Gandalf)

Gandalf reviews the complete git diff and verifies the specification:
```bash
cd .worktrees/<feature-name> && git diff master
```
- **Spec Accuracy Check:** Confirms `docs/specs/<feature-name>.md` is completely up to date, incorporating all design decisions, architectural refinements, and edge cases uncovered during development.
- **Spec Compliance Verification:** Confirms every signed-off acceptance criterion in `docs/specs/<feature-name>.md` is fulfilled and backed by automated regression tests in the test suite.
- **Integrity Check:** Verifies no accidental edits to author content or unwanted artifacts.

---

### Phase 6: Git Push, PR Creation, Dual-Port Preview & Author Hand-off

1. **Commit Atomically & Push Branch:**
   ```bash
   cd .worktrees/<feature-name>
   git add -A
   git commit -m "feat(<scope>): <concise description>"
   git push -u origin <feature-name>
   ```

2. **Create Pull Request & Link to Todoist:**
   Raise the PR using `gh pr create` and post the PR URL to the Todoist task:
   ```bash
   python scripts/site_sprint.py create-pr --task-id <task-id> --title "feat(<scope>): <title>" --body "<description>" --branch <feature-name>
   ```
   - **Clean & Meaningful PR Description:** PR descriptions must be concise and explain what we are trying to fix/build and how. Never include internal Todoist task IDs or localhost URLs in the PR body. Localhost preview URLs belong exclusively in the chat review briefing to the author.

3. **Automatic Dual-Port Server Management (Agent-Managed, Zero Author Effort):**
   The author must NEVER be expected to manually spin up or restart preview servers. The agent is strictly responsible for spinning up and maintaining both servers in the background:
   - **Master Baseline (:1313):** Check if port 1313 is active. If not, launch `hugo server --bind 0.0.0.0 --port 1313 -b http://localhost:1313/` in the background from the root repository.
   - **Feature Preview (:1314):** Launch `hugo server --bind 0.0.0.0 --port 1314 -b http://localhost:1314/` in the background from `.worktrees/<feature-name>`.
   - Verify both ports respond with HTTP 200 before notifying the author.
   - Keep both servers active so the author can immediately click and review the live URLs.

4. **Structured Review Briefing for Author:**
   Present the author with:
   - **Live Feature URL:** `http://localhost:1314/` (already running and live)
   - **Master Comparison URL:** `http://localhost:1313/` (already running and live)
   - **PR Link:** GitHub Pull Request URL.
   - **Verification Checklist:** Specific page links and interactions to check (e.g. "Visit `/tech/k8s/` and verify the backlinks card").

5. **Living Spec Iteration Loop (When author requests tweaks or changes):**
   - **Step 1 (Gandalf):** Whenever the author provides feedback, questions, or iterates on requirements, Gandalf **immediately updates `docs/specs/<feature-name>.md`** so the specification continuously reflects the exact evolved requirements and edge cases.
   - **Step 2 (Gimli):** Gimli implements the changes directly inside `.worktrees/<feature-name>` in strict accordance with the updated spec, updating or adding automated regression tests.
   - **Step 3 (Live Reload):** Hugo LiveReload on `:1314` updates the author's browser instantly.
   - **Step 4 (Legolas):** Legolas audits that all new or updated spec criteria have passing automated tests in the test suite inside the worktree.
   - **Step 5 (Push):** Updated commits are pushed to the PR branch.

6. **Sign-off, Merge & Cleanup:**
   Once the author explicitly reviews and gives sign-off, Gandalf automatically executes the merge and cleanup:
   ```bash
   # Merge PR via gh
   gh pr merge <feature-name> --merge --delete-branch

   # Sync root repository master
   git pull origin master

   # Safely remove the worktree
   git worktree remove .worktrees/<feature-name>

   # Mark Todoist task complete
   td task complete <task-id>
   ```
