#!/usr/bin/env python3
"""
Automated CI Parity Test Suite
Validates that every test script in scripts/ (test_*.py and test_*.js) is
guaranteed to be executed in GitHub Actions (.github/workflows/ci.yml),
either via dynamic wildcard discovery or explicit invocation.
"""

import os
import re
import sys
import glob

# Ensure UTF-8 output across Windows and Linux terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

def run_tests():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ci_yaml_path = os.path.join(root_dir, ".github", "workflows", "ci.yml")
    scripts_dir = os.path.join(root_dir, "scripts")

    print("--- CI Parity & Automated Test Discovery Test Suite ---")

    if not os.path.exists(ci_yaml_path):
        print(f"Error: {ci_yaml_path} does not exist.")
        sys.exit(1)

    with open(ci_yaml_path, "r", encoding="utf-8") as fp:
        ci_content = fp.read()

    # Discover all test scripts in scripts/
    py_tests = [os.path.basename(p) for p in glob.glob(os.path.join(scripts_dir, "test_*.py"))]
    js_tests = [os.path.basename(p) for p in glob.glob(os.path.join(scripts_dir, "test_*.js"))]
    all_tests = sorted(py_tests + js_tests)

    print(f"1. Discovered {len(all_tests)} test suites in scripts/:")
    for t in all_tests:
        print(f"   - {t}")

    # Check execution mechanisms in ci.yml
    has_py_wildcard = bool(re.search(r'scripts/test_\*\.py', ci_content) or re.search(r'test\.sh', ci_content))
    has_js_wildcard = bool(re.search(r'scripts/test_\*\.js', ci_content) or re.search(r'test\.sh', ci_content))

    print("\n2. Verifying execution coverage in .github/workflows/ci.yml:")
    missing_tests = []
    for test_file in all_tests:
        if test_file.endswith(".py") and has_py_wildcard:
            print(f"  ✓ {test_file} covered by dynamic wildcard in CI")
            continue
        if test_file.endswith(".js") and has_js_wildcard:
            print(f"  ✓ {test_file} covered by dynamic wildcard in CI")
            continue

        # Check explicit invocation
        if test_file in ci_content:
            print(f"  ✓ {test_file} explicitly invoked in CI")
        else:
            print(f"  ✗ {test_file} MISSING from .github/workflows/ci.yml!")
            missing_tests.append(test_file)

    if missing_tests:
        print(f"\n[FAIL] {len(missing_tests)} test suite(s) are missing from CI: {missing_tests}")
        print("Please wire them into .github/workflows/ci.yml or enable dynamic test discovery.")
        sys.exit(1)

    print("\n✓ CI PARITY VERIFIED: All test suites are guaranteed to run in GitHub Actions CI!")

if __name__ == "__main__":
    run_tests()
