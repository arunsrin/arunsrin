# Feature Specification: Hugo Dev Container & GitHub Codespaces Environment

## 1. Overview & Context

Previously, this repository was powered by MkDocs (a Python-based static site generator). During that period, a default Microsoft Python 3 dev container configuration was generated in `.devcontainer/devcontainer.json`.

Following the migration to **Hugo**, spinning up a GitHub Codespace defaulted to a Python 3 environment because Codespaces reads `.devcontainer/devcontainer.json` by default. The file retained:
- `"name": "Python 3"`
- `"image": "mcr.microsoft.com/devcontainers/python:0-3.11"`
- An unfulfilled `postCreateCommand: "hugo version"` that failed due to Hugo not being installed in the Python container.

This specification modernizes the Dev Container configuration so that GitHub Codespaces launches directly into a tailored Hugo Extended development environment with all required test runtimes (Python 3, Node.js, `jq`, GitHub CLI) and editor tooling.

---

## 2. Technical Architecture & Implementation Details

### 2.1 Configuration File (`.devcontainer/devcontainer.json`)

The dev container configuration uses the official Microsoft base image paired with official Dev Container Features:

1. **Base Image:**
   `mcr.microsoft.com/devcontainers/base:ubuntu`
   Provides a clean, lightweight Ubuntu environment with standard tooling (`curl`, `git`, `zsh`, `bash`, `sudo`) and non-root `vscode` user.

2. **Features:**
   - `ghcr.io/devcontainers/features/hugo:1`:
     - `version`: `"latest"`
     - `extended`: `true` (installs Hugo Extended edition for Sass/SCSS and full asset pipeline compatibility)
   - `ghcr.io/devcontainers/features/python:1`:
     - `version`: `"3.11"`
     - `installTools`: `false` (lean installation for running repository test suites and linting scripts)
   - `ghcr.io/devcontainers/features/node:1`:
     - `version`: `"lts"` (for executing JavaScript test suites `test_js.js` and `test_search.js`)
   - `ghcr.io/devcontainers/features/github-cli:1`:
     - Pre-installs `gh` CLI for seamless pull request and issue workflows inside Codespaces.

3. **Port Forwarding:**
   - Port `1313`: Hugo development server (`hugo server`), labeled "Hugo Server" with `onAutoForward: "notify"`.
   - Port `1314`: Feature worktree preview server (per `AGENTS.md` Rule 8 dual-port preview architecture), labeled "Worktree Preview" with `onAutoForward: "notify"`.

4. **Lifecycle Hooks (`postCreateCommand`):**
   `"sudo apt-get update && sudo apt-get install -y jq && chmod +x scripts/*.sh && hugo version"`
   - Installs `jq` for JSON index validation in `scripts/test.sh`.
   - Ensures shell scripts in `scripts/` have executable permissions.
   - Logs `hugo version` to confirm Hugo Extended installation.

5. **VS Code Extensions & Settings:**
   - **AI Pair Programming:** `github.copilot`, `github.copilot-chat`
   - **Vim Emulation:** `vscodevim.vim` (with `vim.useSystemClipboard: true`, `vim.hlsearch: true`)
   - **Hugo Intelligence:** `budparr.language-hugo-html` (Hugo Go HTML templates), `hugo-intel.hugo-vscode` (autocomplete & front matter parameters)
   - **Markdown Authoring:** `yzhang.markdown-all-in-one` (keyboard shortcuts, table formatting, list auto-formatting), `davidanson.vscode-markdownlint` (linter), `bierner.markdown-emoji` (emoji support)
   - HTML default formatter configuration.

---

## 3. Automated Testing & Verification

A dedicated regression test suite is added at `scripts/test_devcontainer.py`:
1. Validates existence and strict JSON parseability of `.devcontainer/devcontainer.json`.
2. Validates container name reflects Hugo and is not the legacy "Python 3".
3. Validates base image is `mcr.microsoft.com/devcontainers/base:ubuntu`.
4. Validates `ghcr.io/devcontainers/features/hugo:1` feature is configured with `extended: true`.
5. Validates companion test runtimes (Python, Node.js, `gh`, `jq`) are properly configured.
6. Validates port forwarding covers both 1313 (Hugo) and 1314 (worktree preview).
7. Validates VS Code extensions include Hugo template intelligence.
8. Integrated as Step 20 into `./scripts/test.ps1`, `./scripts/test.sh`, and dynamically discovered in `.github/workflows/ci.yml`.
