#!/usr/bin/env python3
import argparse
import json
import os
import shutil
import subprocess
import sys
from typing import Any, Dict, List, Optional

# Ensure UTF-8 output across Windows and Linux terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PROJECT_NAME = "Site updates 🌐"
PROJECT_ID = "6hWVfCmh7qC5P3HW"
REQUIRED_LABELS = ["llm-task", "next"]


def run_cmd(cmd: List[str], cwd: Optional[str] = None) -> subprocess.CompletedProcess:
    resolved_cmd = list(cmd)
    if resolved_cmd:
        exe = shutil.which(resolved_cmd[0])
        if exe:
            resolved_cmd[0] = exe
    return subprocess.run(
        resolved_cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def get_pending_tasks() -> List[Dict[str, Any]]:
    """Fetch pending tasks from Todoist project 'Site updates 🌐'."""
    cmd = ["td", "task", "list", "--project", PROJECT_ID, "--json"]
    proc = run_cmd(cmd)
    if proc.returncode != 0:
        # Fallback to project name
        proc = run_cmd(["td", "task", "list", "--project", PROJECT_NAME, "--json"])
        if proc.returncode != 0:
            print(f"Error querying Todoist: {proc.stderr.strip()}", file=sys.stderr)
            return []
    try:
        data = json.loads(proc.stdout)
        results = data.get("results", [])
        return results
    except Exception as e:
        print(f"Failed to parse Todoist JSON: {e}", file=sys.stderr)
        return []


def filter_llm_tasks(tasks: List[Dict[str, Any]], require_next: bool = True) -> List[Dict[str, Any]]:
    """Filter tasks tagged with required labels and sort by priority descending."""
    targets = REQUIRED_LABELS if require_next else ["llm-task"]
    matched = [
        t for t in tasks
        if all(lbl in t.get("labels", []) for lbl in targets) and not t.get("checked", False)
    ]
    # Priority 4 is highest in Todoist API, 1 is lowest
    matched.sort(key=lambda t: t.get("priority", 1), reverse=True)
    return matched


def cmd_status():
    """Print current sprint status (backlog tasks and active worktrees)."""
    print(f"=== Todoist Backlog Status ({PROJECT_NAME}) ===")
    all_tasks = get_pending_tasks()
    groomed_tasks = filter_llm_tasks(all_tasks, require_next=True)
    ungroomed_tasks = [
        t for t in all_tasks
        if "llm-task" in t.get("labels", []) and "next" not in t.get("labels", []) and not t.get("checked", False)
    ]
    ungroomed_tasks.sort(key=lambda t: t.get("priority", 1), reverse=True)

    print(f"Total open tasks in project: {len(all_tasks)}")
    print(f"Groomed & ready for execution ('llm-task' + 'next'): {len(groomed_tasks)}")
    print("-" * 60)
    if groomed_tasks:
        for i, t in enumerate(groomed_tasks, 1):
            tid = t.get("id")
            prio = f"P{5 - t.get('priority', 1)}"  # convert API 4->P1, 1->P4
            content = t.get("content")
            desc = t.get("description", "").strip()
            desc_preview = f" - {desc[:60]}..." if desc else ""
            print(f"{i}. [{prio}] ({tid}) {content}{desc_preview}")
    else:
        print("No groomed tasks marked with 'next'.")

    if ungroomed_tasks:
        print(f"\nUngroomed AI backlog ('llm-task' awaiting 'next' tag): {len(ungroomed_tasks)}")
        for i, t in enumerate(ungroomed_tasks, 1):
            tid = t.get("id")
            prio = f"P{5 - t.get('priority', 1)}"
            content = t.get("content")
            print(f"  - [{prio}] ({tid}) {content}")

    print("\n=== Active Git Worktrees ===")
    proc = run_cmd(["git", "worktree", "list"])
    if proc.returncode == 0:
        print(proc.stdout.strip())
    else:
        print("Failed to list worktrees", file=sys.stderr)


def cmd_pick_next():
    """Output the next highest priority task matching both 'llm-task' and 'next' as JSON for the PM agent."""
    all_tasks = get_pending_tasks()
    ready_tasks = filter_llm_tasks(all_tasks, require_next=True)
    if not ready_tasks:
        print(json.dumps({
            "task": None,
            "message": "No pending tasks tagged with both 'llm-task' and 'next'. Please review the backlog in Todoist and add the 'next' label to tasks ready for execution."
        }, indent=2))
        return
    next_task = ready_tasks[0]
    print(json.dumps({"task": next_task}, indent=2))


def cmd_run_tests(worktree_path: str):
    """Execute test suite inside the specified worktree."""
    if not os.path.exists(worktree_path):
        print(f"Worktree path '{worktree_path}' does not exist", file=sys.stderr)
        sys.exit(1)

    print(f"Running test suite in {worktree_path}...")
    if sys.platform == "win32":
        ps_script = os.path.abspath(os.path.join(worktree_path, "scripts", "test.ps1"))
        if os.path.exists(ps_script):
            proc = run_cmd(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ps_script], cwd=worktree_path)
        else:
            sh_script = os.path.abspath(os.path.join(worktree_path, "scripts", "test.sh"))
            if not os.path.exists(sh_script):
                print(f"Test script not found at '{ps_script}' or '{sh_script}'", file=sys.stderr)
                sys.exit(1)
            proc = run_cmd(["bash", sh_script], cwd=worktree_path)
    else:
        test_script = os.path.abspath(os.path.join(worktree_path, "scripts", "test.sh"))
        if not os.path.exists(test_script):
            print(f"Test script not found at '{test_script}'", file=sys.stderr)
            sys.exit(1)
        proc = run_cmd([test_script], cwd=worktree_path)

    output = {
        "passed": proc.returncode == 0,
        "exit_code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }
    print(json.dumps(output, indent=2))
    if proc.returncode != 0:
        sys.exit(proc.returncode)


def cmd_create_pr(task_id: str, title: str, body: str, branch: Optional[str] = None, base: str = "master"):
    """Raise PR via gh and post the URL as a comment to the Todoist task."""
    cmd = ["gh", "pr", "create", "--base", base, "--title", title, "--body", body]
    if branch:
        cmd.extend(["--head", branch])
    
    print(f"Creating GitHub Pull Request...")
    proc = run_cmd(cmd)
    if proc.returncode != 0:
        print(f"Failed to create PR: {proc.stderr.strip()}", file=sys.stderr)
        sys.exit(proc.returncode)

    pr_url = proc.stdout.strip()
    print(f"✓ PR created: {pr_url}")

    if task_id:
        print(f"Posting PR URL to Todoist task {task_id}...")
        comment_proc = run_cmd(["td", "comment", "add", task_id, "--content", f"PR raised: {pr_url}"])
        if comment_proc.returncode == 0:
            print(f"✓ Comment posted to Todoist task {task_id}")
        else:
            print(f"Warning: Failed to post comment to Todoist: {comment_proc.stderr.strip()}", file=sys.stderr)

    return pr_url


def find_feature_worktrees() -> List[str]:
    """Return list of active feature worktree paths under .worktrees/."""
    proc = run_cmd(["git", "worktree", "list", "--porcelain"])
    if proc.returncode != 0:
        return []
    worktrees = []
    for line in proc.stdout.splitlines():
        if line.startswith("worktree "):
            path = line.split(" ", 1)[1]
            if ".worktrees" in path:
                worktrees.append(path)
    return worktrees


def cmd_preview(target: Optional[str] = None, port: int = 1314):
    """Launch hugo server for a worktree on dedicated preview port (default: 1314)."""
    worktree_path = None
    if target:
        if os.path.exists(target):
            worktree_path = os.path.abspath(target)
        elif os.path.exists(os.path.join(".worktrees", target)):
            worktree_path = os.path.abspath(os.path.join(".worktrees", target))
        else:
            print(f"Error: Worktree not found for '{target}'.", file=sys.stderr)
            sys.exit(1)
    else:
        active = find_feature_worktrees()
        if not active:
            print("Error: No active feature worktrees found under .worktrees/.", file=sys.stderr)
            print("To start a sprint: /site-sprint or git worktree add -b <name> .worktrees/<name> master", file=sys.stderr)
            sys.exit(1)
        elif len(active) == 1:
            worktree_path = active[0]
        else:
            print("Multiple active worktrees detected:")
            for i, p in enumerate(active, 1):
                print(f"  {i}. {os.path.basename(p)} ({p})")
            print(f"\nDefaulting to: {os.path.basename(active[0])}")
            worktree_path = active[0]

    feature_name = os.path.basename(worktree_path)
    print("=" * 64)
    print("🚀 Hugo Feature Preview Server (Dual-Port Strategy)")
    print(f"Feature:         {feature_name}")
    print(f"Directory:       {worktree_path}")
    print(f"Preview URL:     http://localhost:{port}/")
    print(f"Master Baseline: http://localhost:1313/ (production reference)")
    print("LiveReload:      Active (edits in worktree refresh automatically)")
    print("=" * 64)
    print("Press Ctrl+C to stop the preview server.\n")

    hugo_bin = shutil.which("hugo") or "hugo"
    cmd = [
        hugo_bin, "server",
        "--bind", "0.0.0.0",
        "--port", str(port),
        "-b", f"http://localhost:{port}/"
    ]
    try:
        subprocess.run(cmd, cwd=worktree_path)
    except KeyboardInterrupt:
        print("\n✓ Preview server stopped.")


def main():
    parser = argparse.ArgumentParser(description="Multi-Agent Sprint & Backlog Tooling")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("status", help="Show current backlog and active worktrees")
    subparsers.add_parser("pick-next", help="Select highest-priority llm-task from Todoist")
    
    test_parser = subparsers.add_parser("run-tests", help="Run test suite in a worktree")
    test_parser.add_argument("worktree", help="Path to the worktree directory")

    preview_parser = subparsers.add_parser("preview", help="Start Hugo preview server on port 1314")
    preview_parser.add_argument("feature", nargs="?", default=None, help="Feature name or worktree path (default: auto-detect)")
    preview_parser.add_argument("--port", type=int, default=1314, help="Port to bind (default: 1314)")

    pr_parser = subparsers.add_parser("create-pr", help="Create PR via gh and comment URL on Todoist task")
    pr_parser.add_argument("--task-id", required=True, help="Todoist task ID")
    pr_parser.add_argument("--title", required=True, help="PR Title")
    pr_parser.add_argument("--body", required=True, help="PR Description")
    pr_parser.add_argument("--branch", default=None, help="Branch name (default: current)")
    pr_parser.add_argument("--base", default="master", help="Base branch (default: master)")

    args = parser.parse_args()

    if args.command == "status":
        cmd_status()
    elif args.command == "pick-next":
        cmd_pick_next()
    elif args.command == "run-tests":
        cmd_run_tests(args.worktree)
    elif args.command == "preview":
        cmd_preview(args.feature, args.port)
    elif args.command == "create-pr":
        cmd_create_pr(args.task_id, args.title, args.body, args.branch, args.base)


if __name__ == "__main__":
    main()
