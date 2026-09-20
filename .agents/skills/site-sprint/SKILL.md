---
name: site-sprint
description: "Autonomous multi-agent sprint cycle for arunsrin's notes: Product Manager (refines/creates Todoist requirements) -> Developer (implements in an isolated worktree) -> QA Tester (executes strict test suites with automated feedback loop) -> PM (validates acceptance criteria) -> Git push and Pull Request for human review. Trigger via `/site-sprint` or when asked to run a multi-agent sprint."
---

# Multi-Agent Development Sprint (`/site-sprint`)

This skill orchestrates a complete autonomous multi-agent feature sprint for **arunsrin's notes** ([https://www.arunsr.in](https://www.arunsr.in)).

```
  ┌────────────────────────┐
  │ 1. Product Manager     │  Queries Todoist ('Site updates 🌐'), selects highest
  │    (PM) Agent          │  priority task, refines requirements into SPEC.md.
  └───────────┬────────────┘
              │
              ▼
  ┌────────────────────────┐
  │ 2. Developer Agent     │  Creates isolated git worktree (.worktrees/<name>)
  │                        │  and implements feature adhering to AGENTS.md rules.
  └───────────┬────────────┘
              │
              ▼
  ┌────────────────────────┐
  │ 3. QA / Test Agent     │  Executes ./scripts/test.sh inside worktree.
  │                        │  Loops back to Developer on failure with error logs.
  └───────────┬────────────┘
              │ (All tests pass)
              ▼
  ┌────────────────────────┐
  │ 4. PM Validation       │  Validates git diff against SPEC.md acceptance criteria.
  └───────────┬────────────┘
              │
              ▼
  ┌────────────────────────┐
  │ 5. Push & Pull Request │  Pushes branch, creates PR, and notifies human author
  │    (Human Review)      │  for final local preview, merge, and closing the task.
  └────────────────────────┘
```

---

## Sprint Execution Procedure

When `/site-sprint` is invoked, the orchestrating agent executes the following 5 phases:

### Phase 1: Product Manager Agent (`pm-agent`)

1. **Backlog Inspection:**
   Run `./scripts/site_sprint.py pick-next` (or query Todoist directly: `td task list --project "Site updates 🌐" --labels "llm-task" --json`).
   - If tasks are present: pick the highest-priority pending task.
   - If no tasks are present or user asked for ideas: audit current digital garden notes/templates, formulate a high-value requirement, add the task to Todoist (`td task add ...`), and proceed.

2. **Requirements Refinement (`SPEC.md`):**
   Produce a crisp, unambiguous specification saved at `<worktree>/SPEC.md` covering:
   - **Task Context & User Story:** Summary and goal.
   - **Acceptance Criteria:** Numbered, testable criteria.
   - **Architectural Guardrails (from [AGENTS.md](file:///home/arunsrin/code/arunsrin.mkdocs/AGENTS.md)):**
     - *Sacred Prose Principle:* Writing/text in notes and reviews must NEVER be rewritten.
     - *Zero Bloat:* Vanilla deferred JS and lightweight CSS only (no heavy frameworks).
     - *Light Blue Identity:* Turquoise-to-sky-blue header gradient (`#40E0D0` to `#2fa4e7`).
     - *Cloudflare Safety:* No inline event handlers; cache-busting on static assets.
     - *Hugo CI Parity:* Zero warnings with `--panicOnWarning`.

---

### Phase 2: Developer Agent (`dev-agent`)

1. **Isolated Worktree Setup:**
   Ensure the main working tree remains permanently on `master`. Create a dedicated worktree:
   ```bash
   git worktree add -b <feature-name> .worktrees/<feature-name> master
   ```

2. **Implementation:**
   Implement code and template changes inside `.worktrees/<feature-name>`:
   - Create or edit files in `layouts/`, `home/css/`, `home/static/`, or `scripts/`.
   - Respect HTML container balance (e.g. `<div class="grid cards" markdown>`).
   - Ensure all DOM queries wait for `DOMContentLoaded`.

---

### Phase 3: QA / Test Agent (`qa-agent`) & Feedback Loop

1. **Test Execution:**
   Run the test runner inside the worktree:
   ```bash
   ./scripts/site_sprint.py run-tests .worktrees/<feature-name>
   # or directly:
   cd .worktrees/<feature-name> && ./scripts/test.sh
   ```

2. **Automated Feedback Loop:**
   - **If any test fails (Hugo build error, invalid JSON, broken internal link, Rocket Loader violation):**
     1. Capture failure stdout and stderr.
     2. Send exact logs and root cause diagnosis back to the Developer Agent.
     3. Developer Agent fixes the issue in `.worktrees/<feature-name>`.
     4. QA Agent re-tests. (Repeat until 100% passing or maximum 3 iterations).
   - **If all 9 tests pass:**
     Issue QA sign-off log.

---

### Phase 4: PM Validation & Quality Gate

The Product Manager agent inspects the final git diff:
```bash
cd .worktrees/<feature-name> && git diff master
```
- Validate every acceptance criterion from `SPEC.md` is met.
- Ensure no accidental changes were made to markdown author notes.
- Verify no extraneous files or secrets are staged.

---

### Phase 5: Push & PR Creation for Human Sign-off

1. **Commit & Push:**
   Commit inside the worktree using conventional commit messages:
   ```bash
   cd .worktrees/<feature-name>
   git add -A
   git commit -m "feat(<scope>): <concise description>"
   git push -u origin <feature-name>
   ```

2. **Raise Pull Request:**
   Create the GitHub PR using `gh pr create` (or output the branch comparison URL `https://github.com/arunsrin/arunsrin/pull/new/<feature-name>`):
   ```markdown
   ### Summary of Changes
   - Implemented <feature> per Todoist task <id>

   ### Acceptance Criteria Checklist
   - [x] Criteria 1
   - [x] Criteria 2

   ### Verification
   - Strict Hugo build: 0 warnings
   - Internal links: 100% valid
   - Safety tests: 9/9 passing
   ```

3. **Human Handoff:**
   Present the PR link and testing summary to the human author. The author reviews on preview server, merges, and closes the task.
