# Specification: Automated Cross-Platform Sprint Cleanup Tooling

## 1. Context & User Story
After completing a feature sprint and securing the author's sign-off, cleaning up feature branches currently requires executing a series of manual steps:
1. Squash-merging the PR on GitHub (`gh pr merge --squash --delete-branch`).
2. Terminating background Hugo servers on ports 1313 and 1314.
3. Removing the isolated worktree (`git worktree remove .worktrees/<feature-name>`).
4. Deleting the local branch (`git branch -D <feature-name>`).
5. Switching to `master` in the root repository and pulling the latest remote commits (`git pull origin master`).
6. Marking the Todoist task complete (`td task complete <task-id>`).

Performing these steps manually is slow, error-prone, and can result in locked files on Windows NTFS or orphan processes.

As a digital garden author and agentic pair programmer, I want automated, cross-platform cleanup scripts (`scripts/cleanup.ps1` for PowerShell and `scripts/cleanup.sh` for WSL/Linux, backed by `python scripts/site_sprint.py cleanup`) so that:
- A single command executes the entire teardown, merge, sync, and Todoist completion flow in seconds.
- Background preview processes on ports 1313 and 1314 are reliably terminated without leaving locked build files.
- The root repository is left cleanly on `master` with the latest changes pulled.
- The command works identically in native Windows PowerShell and WSL/Linux.

---

## 2. Core Guardrails (AGENTS.md Compliance)
- **Master Branch Inviolability (Rule 8)**: Tooling development occurs strictly within `.worktrees/automated-sprint-cleanup`.
- **Cross-Platform Parity**: The cleanup command must run natively in Windows PowerShell (`scripts/cleanup.ps1`) and WSL/Linux (`scripts/cleanup.sh`).
- **Idempotency & Fault Tolerance**: If a PR is already merged, a server is not running, or a branch is already deleted, the cleanup script must report the state and continue gracefully without crashing.
- **Automated Regression Testing & CI Parity (Rules 10 & 11)**: Dedicated automated test suite in `scripts/test_cleanup_tooling.py` integrated into `test.ps1`, `test.sh`, and GitHub Actions CI.
- **Windows UTF-8 Stdout Reconfiguration (Rule 12)**: All companion Python test scripts must include standard UTF-8 stdout reconfiguration.

---

## 3. Numbered Acceptance Criteria

1. **CLI Subcommand in `site_sprint.py`**:
   - `python scripts/site_sprint.py cleanup [feature-name]` supports optional feature name (auto-detecting if only one worktree is active), `--task-id`, `--no-merge`, and `--merge-method` (`squash`, `merge`, `rebase`).
2. **Server Process Termination**:
   - Safely identifies and terminates any processes listening on ports 1313 and 1314 or running Hugo server instances across Windows and Linux.
3. **Automated PR Merge**:
   - Merges the feature PR using `gh pr merge <branch> --squash --delete-branch` (unless `--no-merge` is specified).
   - If the PR is already in `MERGED` state, logs the status and proceeds smoothly.
4. **Worktree & Branch Teardown**:
   - Removes `.worktrees/<feature-name>` using `git worktree remove --force`.
   - Prunes worktree records using `git worktree prune`.
   - Deletes local branch `git branch -D <feature-name>`.
5. **Root Repository Master Sync**:
   - Ensures root repository is on `master` (`git checkout master`).
   - Pulls latest merged commits (`git pull origin master`).
6. **Todoist Completion**:
   - If a `--task-id` is provided or discoverable in Todoist, completes the task using `td task complete <task-id>`.
7. **Native Shell Wrappers**:
   - `scripts/cleanup.ps1` provides seamless execution in PowerShell.
   - `scripts/cleanup.sh` provides seamless execution in WSL / Linux.
8. **Automated Regression Testing**:
   - `scripts/test_cleanup_tooling.py` validates CLI parser options, server termination routines, and shell script wrappers.
   - All tests pass in `./scripts/test.ps1` and `./scripts/test.sh`.
