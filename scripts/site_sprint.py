#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
from typing import Any, Dict, List, Optional

PROJECT_NAME = "Site updates 🌐"
PROJECT_ID = "6hWVfCmh7qC5P3HW"
REQUIRED_LABEL = "llm-task"


def run_cmd(cmd: List[str], cwd: Optional[str] = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
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


def filter_llm_tasks(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter tasks tagged with llm-task and sort by priority descending."""
    llm_tasks = [
        t for t in tasks
        if REQUIRED_LABEL in t.get("labels", []) and not t.get("checked", False)
    ]
    # Priority 4 is highest in Todoist API, 1 is lowest
    llm_tasks.sort(key=lambda t: t.get("priority", 1), reverse=True)
    return llm_tasks


def cmd_status():
    """Print current sprint status (backlog tasks and active worktrees)."""
    print(f"=== Todoist Backlog Status ({PROJECT_NAME}) ===")
    all_tasks = get_pending_tasks()
    llm_tasks = filter_llm_tasks(all_tasks)

    print(f"Total open tasks: {len(all_tasks)}")
    print(f"Actionable AI tasks ('{REQUIRED_LABEL}'): {len(llm_tasks)}")
    print("-" * 60)
    for i, t in enumerate(llm_tasks, 1):
        tid = t.get("id")
        prio = f"P{5 - t.get('priority', 1)}" # convert API 4->P1, 1->P4
        content = t.get("content")
        desc = t.get("description", "").strip()
        desc_preview = f" - {desc[:60]}..." if desc else ""
        print(f"{i}. [{prio}] ({tid}) {content}{desc_preview}")

    print("\n=== Active Git Worktrees ===")
    proc = run_cmd(["git", "worktree", "list"])
    if proc.returncode == 0:
        print(proc.stdout.strip())
    else:
        print("Failed to list worktrees", file=sys.stderr)


def cmd_pick_next():
    """Output the next highest priority task as structured JSON for the PM agent."""
    all_tasks = get_pending_tasks()
    llm_tasks = filter_llm_tasks(all_tasks)
    if not llm_tasks:
        print(json.dumps({"task": None, "message": f"No pending tasks tagged '{REQUIRED_LABEL}'"}))
        return
    next_task = llm_tasks[0]
    print(json.dumps({"task": next_task}, indent=2))


def cmd_run_tests(worktree_path: str):
    """Execute ./scripts/test.sh inside the specified worktree."""
    if not os.path.exists(worktree_path):
        print(f"Worktree path '{worktree_path}' does not exist", file=sys.stderr)
        sys.exit(1)

    test_script = os.path.join(worktree_path, "scripts", "test.sh")
    if not os.path.exists(test_script):
        print(f"Test script not found at '{test_script}'", file=sys.stderr)
        sys.exit(1)

    print(f"Running test suite in {worktree_path}...")
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


def main():
    parser = argparse.ArgumentParser(description="Multi-Agent Sprint & Backlog Tooling")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("status", help="Show current backlog and active worktrees")
    subparsers.add_parser("pick-next", help="Select highest-priority llm-task from Todoist")
    
    test_parser = subparsers.add_parser("run-tests", help="Run test suite in a worktree")
    test_parser.add_argument("worktree", help="Path to the worktree directory")

    args = parser.parse_args()

    if args.command == "status":
        cmd_status()
    elif args.command == "pick-next":
        cmd_pick_next()
    elif args.command == "run-tests":
        cmd_run_tests(args.worktree)


if __name__ == "__main__":
    main()
