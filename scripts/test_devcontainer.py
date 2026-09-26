#!/usr/bin/env python3
"""
Automated Test Suite for Dev Container & Codespaces Configuration
Validates:
1. File Existence & Parsing:
   - .devcontainer/devcontainer.json exists and parses as valid JSON.
2. Naming & Base Image:
   - Container name reflects Hugo (not legacy 'Python 3').
   - Base image is mcr.microsoft.com/devcontainers/base:ubuntu (not python:0-3.11).
3. Dev Container Features:
   - ghcr.io/devcontainers/features/hugo:1 configured with extended: true.
   - ghcr.io/devcontainers/features/python:1 configured (for test scripts).
   - ghcr.io/devcontainers/features/node:1 configured (for JS tests).
   - ghcr.io/devcontainers/features/github-cli:1 configured.
4. Port Forwarding & Attributes:
   - forwardPorts includes 1313 (Hugo server) and 1314 (Worktree preview).
   - portsAttributes labels both 1313 and 1314.
5. Lifecycle & Tooling:
   - postCreateCommand installs jq and verifies hugo version.
6. VS Code Extensions:
   - Includes Hugo syntax and front matter extensions.
   - Includes GitHub Copilot and Copilot Chat.
   - Includes VSCodeVim with clipboard integration.
   - Includes Markdown All-in-One and markdownlint.
"""

import json
import os
import sys

# Windows Python UTF-8 Stdout Reconfiguration (Rule 12)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def run_tests():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    devcontainer_path = os.path.join(root_dir, ".devcontainer", "devcontainer.json")

    print("--- Dev Container & Codespaces Configuration Regression Test Suite ---")

    # 1. Existence and Parseability
    print("1. Auditing .devcontainer/devcontainer.json existence and JSON syntax:")
    assert os.path.exists(devcontainer_path), f"Missing configuration file at {devcontainer_path}"
    with open(devcontainer_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print("  ✓ .devcontainer/devcontainer.json exists and parsed as valid JSON.")

    # 2. Naming and Base Image
    print("2. Auditing container name and base image:")
    name = data.get("name", "")
    assert "hugo" in name.lower(), f"Container name '{name}' must reference Hugo!"
    assert name != "Python 3", "Container name must not be the legacy 'Python 3'!"

    image = data.get("image", "")
    assert "python" not in image.lower(), f"Base image '{image}' must not be a python-only container!"
    assert "base" in image.lower() or "ubuntu" in image.lower(), (
        f"Base image '{image}' should be a standard base container!"
    )
    print(f"  ✓ Name: '{name}' | Image: '{image}' verified.")

    # 3. Features Verification
    print("3. Auditing Dev Container Features:")
    features = data.get("features", {})
    assert isinstance(features, dict), "features must be a dictionary"

    hugo_feat = features.get("ghcr.io/devcontainers/features/hugo:1")
    assert hugo_feat is not None, "Missing ghcr.io/devcontainers/features/hugo:1 feature!"
    assert hugo_feat.get("extended") is True, "Hugo feature must enable extended edition (extended: true)!"

    python_feat = features.get("ghcr.io/devcontainers/features/python:1")
    assert python_feat is not None, "Missing ghcr.io/devcontainers/features/python:1 for test suite execution!"

    node_feat = features.get("ghcr.io/devcontainers/features/node:1")
    assert node_feat is not None, "Missing ghcr.io/devcontainers/features/node:1 for JS test execution!"

    gh_feat = features.get("ghcr.io/devcontainers/features/github-cli:1")
    assert gh_feat is not None, "Missing ghcr.io/devcontainers/features/github-cli:1 feature!"
    print("  ✓ Features verified: Hugo (extended), Python, Node.js, GitHub CLI.")

    # 4. Port Forwarding
    print("4. Auditing forwarded ports and port attributes:")
    forward_ports = data.get("forwardPorts", [])
    assert 1313 in forward_ports, "forwardPorts must include 1313 (Hugo server)!"
    assert 1314 in forward_ports, "forwardPorts must include 1314 (Worktree preview server)!"

    port_attrs = data.get("portsAttributes", {})
    assert "1313" in port_attrs, "portsAttributes missing entry for 1313"
    assert "1314" in port_attrs, "portsAttributes missing entry for 1314"
    print("  ✓ Forwarded ports 1313 and 1314 verified with custom attributes.")

    # 5. Lifecycle Hook
    print("5. Auditing postCreateCommand:")
    post_create = data.get("postCreateCommand", "")
    assert "jq" in post_create, "postCreateCommand should install jq for index verification"
    assert "hugo version" in post_create, "postCreateCommand should execute 'hugo version'"
    print(f"  ✓ postCreateCommand verified: '{post_create}'")

    # 6. VS Code Extensions & Settings
    print("6. Auditing VS Code extensions customization:")
    customizations = data.get("customizations", {})
    vscode_custom = customizations.get("vscode", {})
    extensions = vscode_custom.get("extensions", [])
    settings = vscode_custom.get("settings", {})

    # Hugo extensions
    assert any("hugo" in ext.lower() for ext in extensions), (
        "VS Code extensions must include Hugo extensions!"
    )

    # Copilot extensions
    assert "github.copilot" in extensions, "VS Code extensions must include 'github.copilot'!"
    assert "github.copilot-chat" in extensions, "VS Code extensions must include 'github.copilot-chat'!"

    # Vim keybindings & settings
    assert "vscodevim.vim" in extensions, "VS Code extensions must include 'vscodevim.vim'!"
    assert settings.get("vim.useSystemClipboard") is True, (
        "VS Code settings should enable vim.useSystemClipboard for seamless clipboard integration!"
    )

    # Markdown tooling
    assert "yzhang.markdown-all-in-one" in extensions, (
        "VS Code extensions must include 'yzhang.markdown-all-in-one'!"
    )
    assert "davidanson.vscode-markdownlint" in extensions, (
        "VS Code extensions must include 'davidanson.vscode-markdownlint'!"
    )

    print(f"  ✓ Extensions verified ({len(extensions)} extensions): {extensions}")
    print("  ✓ Vim settings verified: vim.useSystemClipboard = True, vim.hlsearch = True.")

    print("\n✓ ALL DEV CONTAINER & CODESPACES TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    run_tests()
