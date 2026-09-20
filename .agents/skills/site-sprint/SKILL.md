---
name: site-sprint
description: "Autonomous multi-agent sprint cycle for arunsrin's notes: Gandalf (PM - interviews author & refines Todoist requirements) -> Gimli (Dev - crafts code in worktree) -> Legolas (QA - runs strict test suite with feedback loop) -> Gandalf (validates sign-off) -> Git push and Pull Request for human review. Trigger via `/site-sprint` or when asked to run a multi-agent sprint."
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
  │ 🧙‍♂️ Phase 4: Gandalf (Final Validation)       │
  │ Confirms diff matches signed-off criteria.   │
  └──────────────────────┬───────────────────────┘
                         │
                         ▼
  ┌──────────────────────────────────────────────┐
  │ 🚀 Phase 5: Push & Pull Request              │
  │ Pushes branch and raises PR for author to     │
  │ preview locally, merge, and close.           │
  └──────────────────────────────────────────────┘
```

---

## The Fellowship (Agent Personas)

1. 🧙‍♂️ **Gandalf (The Strategist / Product Manager):**
   - **Motto:** *"All we have to decide is what to do with the time that is given us."*
    - **Role:** Queries Todoist, analyzes architecture, interviews the human author with clarifying questions and implementation choices, and writes the feature specification in `docs/specs/<feature-name>.md`.
2. ⚒️ **Gimli (The Code Smith / Developer):**
   - **Motto:** *"Faithless is he that says farewell when the road darkens."*
   - **Role:** Works in the background inside an isolated worktree (`.worktrees/<name>`). Implements HTML, CSS, JS, and Hugo templates strictly adhering to `AGENTS.md` (Sacred Prose, zero bloat, vanilla JS, Cloudflare safety).
3. 🏹 **Legolas (The Sharp-Eyed Scout / QA Tester):**
   - **Motto:** *"A red sun rises. Blood has been spilled this night... or a link was broken."*
   - **Role:** Ruthlessly tests the worktree with `./scripts/test.sh` (strict Hugo build, valid JSON indexes, 19k+ link audit, Rocket Loader safety, JS tests). Sends precise reproduction steps and error logs back to Gimli until zero defects remain.

---

## Sprint Execution Procedure

### Phase 1: Interactive Scoping & Human Sign-off (🧙‍♂️ Gandalf)

1. **Backlog Inspection:**
   Inspect Todoist for groomed tasks ready for execution:
   ```bash
   ./scripts/site_sprint.py pick-next
   # or: td task list --project "Site updates 🌐" --filter "@llm-task & @next" --json
   ```
   - **Groomed Tasks (`llm-task` + `next`):** Pick the highest-priority task that has been reviewed and groomed by the author (tagged with both `llm-task` and `next`).
   - **If no groomed tasks are found:** Check `./scripts/site_sprint.py status`. Inform the author of any pending ungroomed AI tasks (`llm-task` only) awaiting their review and `next` tag, or audit digital garden notes/templates to propose new candidate tasks.
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
   - Core Guardrails from [AGENTS.md](file:///home/arunsrin/code/arunsrin.mkdocs/AGENTS.md) (Sacred Prose, zero bloat, light blue visual theme, Rocket Loader safety).

---

### Phase 2: Background Code Crafting (⚒️ Gimli)

1. **Isolated Worktree Creation:**
   Ensure the main repository tree permanently stays on `master`:
   ```bash
   git worktree add -b <feature-name> .worktrees/<feature-name> master
   ```

2. **Implementation:**
   Gimli implements all requirements specified in `docs/specs/<feature-name>.md` within `.worktrees/<feature-name>`:
   - Clean, lightweight vanilla JS (no frameworks).
   - Responsive styling adhering to the light blue gradient theme.
   - No modification to existing author prose in markdown files.
   - Tags properly closed and balanced.

3. **Mandatory Companion Automated Test Authoring:**
   Whenever new code, templates, shortcodes, partials, CSS components, or JavaScript behaviors are introduced, Gimli MUST author corresponding automated regression tests and wire them into `./scripts/test.sh` (e.g. dedicated test scripts under `scripts/test_*.py` or `scripts/test_*.js`).
   *Test Authoring Criteria:*
   - **New Templates / Partials:** Assert presence of generated DOM elements, correct CSS class hooks, and zero template execution errors across pages.
   - **Content & Taxonomy Logic:** Assert coverage integrity across notes, relationship accuracy, and include negative tests preventing spurious matches or topic leaks.
   - **Client-Side Scripts:** Assert event listener correctness, Rocket Loader compatibility (zero inline handlers), and state persistence.
   - **Zero Untested Features:** A feature is NEVER considered complete without accompanying automated test coverage.

---

### Phase 3: Background QA Verification Loop (🏹 Legolas)

1. **Automated Test Run & Test Coverage Audit:**
   Legolas audits that automated regression tests exist for all newly introduced code in the diff, and executes the strict test suite inside the worktree:
   ```bash
   ./scripts/site_sprint.py run-tests .worktrees/<feature-name>
   # or: cd .worktrees/<feature-name> && ./scripts/test.sh
   ```
   If new code lacks companion automated tests in `./scripts/test.sh`, Legolas rejects the build and instructs Gimli to author tests before certifying approval.

2. **Automated Feedback Loop:**
   - **On Any Failure (Exit code != 0 or missing test coverage):**
     1. Legolas captures exact failing logs, stack traces, and affected files.
     2. Formulates a targeted bug report for Gimli.
     3. Gimli applies fixes and adds missing tests in the worktree.
     4. Legolas re-tests. (Repeats seamlessly in the background up to 3 iterations).
   - **On Complete Pass (All test suites green, 0 Hugo warnings, 100% test coverage):**
     Legolas issues a QA sign-off certification.

---

### Phase 4: Final Validation Gate (🧙‍♂️ Gandalf)

Gandalf reviews the complete git diff:
```bash
cd .worktrees/<feature-name> && git diff master
```
- Confirms every signed-off acceptance criterion in `docs/specs/<feature-name>.md` is fulfilled.
- Verifies no accidental edits to author content or unwanted artifacts.

---

### Phase 5: Git Push, PR Creation, Dual-Port Preview & Author Hand-off

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
   ./scripts/site_sprint.py create-pr --task-id <task-id> --title "feat(<scope>): <title>" --body "<description>" --branch <feature-name>
   ```

3. **The Dual-Port Preview Strategy:**
   Never interrupt `master` running on port 1313. The author tests the candidate feature on port 1314:
   - **Master Baseline:** `http://localhost:1313/` (main tree on `master`)
   - **Feature Preview:** `http://localhost:1314/` (worktree with LiveReload)

   Launch preview with a single command:
   ```bash
   ./scripts/site_sprint.py preview
   # or: cd .worktrees/<feature-name> && hugo server --port 1314
   ```

4. **Structured Review Briefing for Author:**
   Present the author with:
   - **PR Link:** GitHub Pull Request URL.
   - **Preview URL:** `http://localhost:1314/`
   - **Verification Checklist:** Direct page links and interactions to check (e.g. "Visit `/tech/docker/` and check the backlinks section").
   - **Comparison:** Mention opening `:1313` and `:1314` side-by-side.

5. **Interactive Iteration Loop (If author requests tweaks):**
   - Author requests changes (e.g., "Adjust card padding" or "Change icon").
   - Gimli edits directly inside `.worktrees/<feature-name>`.
   - Hugo LiveReload on `:1314` updates the author's browser instantly.
   - Legolas re-verifies with `./scripts/test.sh` inside the worktree.
   - Updated commits are pushed to the PR branch.

6. **Sign-off, Merge & Cleanup:**
   Once the author explicitly approves:
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

