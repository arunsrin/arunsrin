#!/usr/bin/env bash
# Cross-Platform Cleanup Script for arunsrin's notes (WSL / Linux / macOS)
# Usage: ./scripts/cleanup.sh [feature-name] [--task-id <id>] [--no-merge] [--merge-method <squash|merge|rebase>]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

"$PYTHON_CMD" "$SCRIPT_DIR/site_sprint.py" cleanup "$@"
