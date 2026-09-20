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
   - **Role:** Queries Todoist, analyzes architecture, interviews the human author with clarifying questions and implementation choices, and writes the authoritative `SPEC.md`.
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
   Inspect Todoist:
   ```bash
   ./scripts/site_sprint.py pick-next
   # or: td task list --project "Site updates 🌐" --labels "llm-task" --json
   ```
   - If tasks are present: pick the highest-priority pending task.
   - If no tasks are present or user asked for ideas: audit digital garden notes/templates, formulate a high-value requirement, add the task to Todoist (`td task add ...`), and proceed.

2. **Codebase & Architectural Analysis:**
   Inspect related files, templates, styles, and data structures. Identify potential tradeoffs, UX choices, or edge cases.

3. **Interactive Human Interview & Sign-off Gate:**
   - Present the proposed feature, approach, and options to the author.
   - Ask clarifying implementation questions (e.g. design preferences, content sources, scope limits).
   - **CRITICAL GATE:** Do NOT dispatch background agents until the human author answers and explicitly confirms/signs off (e.g. "Proceed", "Looks good", or specific direction).

4. **Generate Approved `SPEC.md`:**
   Once sign-off is received, write `<worktree>/SPEC.md` containing:
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
   Gimli implements all requirements specified in `SPEC.md` within `.worktrees/<feature-name>`:
   - Clean, lightweight vanilla JS (no frameworks).
   - Responsive styling adhering to the light blue gradient theme.
   - No modification to existing author prose in markdown files.
   - Tags properly closed and balanced.

---

### Phase 3: Background QA Verification Loop (🏹 Legolas)

1. **Automated Test Run:**
   Legolas executes the strict test suite inside the worktree:
   ```bash
   ./scripts/site_sprint.py run-tests .worktrees/<feature-name>
   # or: cd .worktrees/<feature-name> && ./scripts/test.sh
   ```

2. **Automated Feedback Loop:**
   - **On Any Failure (Exit code != 0):**
     1. Legolas captures exact failing logs, stack traces, and affected files.
     2. Formulates a targeted bug report for Gimli.
     3. Gimli applies fixes in the worktree.
     4. Legolas re-tests. (Repeats seamlessly in the background up to 3 iterations).
   - **On Complete Pass (All 9 suites green, 0 Hugo warnings):**
     Legolas issues a QA sign-off certification.

---

### Phase 4: Final Validation Gate (🧙‍♂️ Gandalf)

Gandalf reviews the complete git diff:
```bash
cd .worktrees/<feature-name> && git diff master
```
- Confirms every signed-off acceptance criterion in `SPEC.md` is fulfilled.
- Verifies no accidental edits to author content or unwanted artifacts.

---

### Phase 5: Git Push, PR Creation & Todoist Linking

1. **Commit Atomically:**
   ```bash
   cd .worktrees/<feature-name>
   git add -A
   git commit -m "feat(<scope>): <concise description>"
   git push -u origin <feature-name>
   ```

2. **Create Pull Request & Link to Todoist:**
   Raise the PR using `gh pr create` and automatically post the resulting PR URL as a comment to the Todoist task:
   ```bash
   # Using the helper script:
   ./scripts/site_sprint.py create-pr --task-id <task-id> --title "feat(<scope>): <title>" --body "<description>" --branch <feature-name>

   # Or manually:
   PR_URL=$(gh pr create --title "feat(<scope>): <title>" --body "<description>")
   td comment add <task-id> --content "PR raised: $PR_URL"
   ```

3. **Hand-off to Human Author:**
   Notify the author: *"The Fellowship has completed the quest! PR is created at <PR_URL> and linked to Todoist task <id> for your local preview, final merge, and closing the task."*

