#!/usr/bin/env python3
"""
Automated Regression Test Suite for Sprint Cleanup Tooling

Validates:
1. Existence and syntax of scripts/cleanup.ps1 and scripts/cleanup.sh.
2. CLI parser options for 'site_sprint.py cleanup' (--task-id, --no-merge, --merge-method).
3. Graceful execution of server termination function (kill_preview_servers) on idle ports.
4. Worktree discovery and auto-detection functions.
"""

import sys
import os
import subprocess
import shutil

# Windows Python UTF-8 Stdout Reconfiguration (Rule 12)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

def test_cleanup_tooling():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    scripts_dir = os.path.join(root_dir, "scripts")
    site_sprint_path = os.path.join(scripts_dir, "site_sprint.py")
    cleanup_ps1_path = os.path.join(scripts_dir, "cleanup.ps1")
    cleanup_sh_path = os.path.join(scripts_dir, "cleanup.sh")

    print("--- Sprint Cleanup Tooling Test Suite ---")

    # 1. Validate script files existence
    print("\n1. Auditing cleanup script wrappers existence:")
    assert os.path.exists(cleanup_ps1_path), f"Missing {cleanup_ps1_path}"
    assert os.path.exists(cleanup_sh_path), f"Missing {cleanup_sh_path}"
    assert os.path.exists(site_sprint_path), f"Missing {site_sprint_path}"
    print("  ✓ scripts/cleanup.ps1, scripts/cleanup.sh, and scripts/site_sprint.py verified.")

    # 2. Validate wrapper script contents & parameters
    print("\n2. Auditing wrapper scripts content & encoding safety:")
    with open(cleanup_ps1_path, "r", encoding="utf-8") as f:
        ps1_content = f.read()
    assert "[Parameter(Position=0)]" in ps1_content, "Missing Feature parameter in cleanup.ps1"
    assert "site_sprint.py" in ps1_content, "cleanup.ps1 must forward to site_sprint.py"
    assert "cleanup" in ps1_content, "cleanup.ps1 must pass cleanup command"
    assert "NoMerge" in ps1_content, "Missing NoMerge switch in cleanup.ps1"
    assert "MergeMethod" in ps1_content, "Missing MergeMethod parameter in cleanup.ps1"

    with open(cleanup_sh_path, "r", encoding="utf-8") as f:
        sh_content = f.read()
    assert "#!/usr/bin/env bash" in sh_content, "Missing bash shebang in cleanup.sh"
    assert "site_sprint.py" in sh_content, "cleanup.sh must forward to site_sprint.py"
    assert 'cleanup "$@"' in sh_content, "cleanup.sh must pass cleanup command and arguments"
    print("  ✓ Parameter forwarding and syntax validated across cleanup.ps1 and cleanup.sh.")

    # 3. Validate CLI Help & Subcommand Options
    print("\n3. Validating 'site_sprint.py cleanup --help' CLI output and argument validation:")
    python_bin = sys.executable
    proc = subprocess.run([python_bin, site_sprint_path, "cleanup", "--help"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
    assert proc.returncode == 0, f"cleanup --help failed: {proc.stderr}"
    help_text = proc.stdout
    assert "--task-id" in help_text, "Missing --task-id in cleanup help"
    assert "--no-merge" in help_text, "Missing --no-merge in cleanup help"
    assert "--merge-method" in help_text, "Missing --merge-method in cleanup help"
    assert "squash" in help_text, "Missing squash merge choice in cleanup help"
    print("  ✓ CLI parser successfully exposes all cleanup arguments.")

    # Gate 9: Negative test - invalid merge method must be rejected
    neg_proc = subprocess.run([python_bin, site_sprint_path, "cleanup", "--merge-method", "invalid-method"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
    assert neg_proc.returncode != 0, "CLI must reject invalid --merge-method"
    print("  ✓ Negative test: invalid arguments cleanly rejected.")

    # 4. Validate Server Process Termination Function
    print("\n4. Validating kill_preview_servers graceful execution on idle ports:")
    # Import site_sprint module directly
    sys.path.insert(0, scripts_dir)
    import site_sprint
    # Call kill_preview_servers with dummy high ports to verify no crash
    site_sprint.kill_preview_servers([59998, 59999])
    print("  ✓ kill_preview_servers executed gracefully without exceptions.")

    # 5. Validate Worktree Discovery & Repo Root Resolution Functions
    print("\n5. Validating find_feature_worktrees and get_repo_root functionality:")
    worktrees = site_sprint.find_feature_worktrees()
    assert isinstance(worktrees, list), "find_feature_worktrees must return a list"
    print(f"  ✓ find_feature_worktrees returned {len(worktrees)} active worktrees.")

    repo_root = site_sprint.get_repo_root()
    assert os.path.exists(repo_root), f"Repo root '{repo_root}' does not exist"
    assert not repo_root.endswith(".worktrees"), "Repo root must not resolve to .worktrees"
    assert os.path.exists(os.path.join(repo_root, "home")), "Repo root must contain 'home' directory"
    print(f"  ✓ get_repo_root correctly resolved main repository root: {repo_root}")

    print("\n=== All Cleanup Tooling tests passed successfully! ===")

if __name__ == "__main__":
    test_cleanup_tooling()
