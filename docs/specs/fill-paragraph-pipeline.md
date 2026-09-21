# Feature Specification: Fill-Paragraph Linter and Auto-Commit Pipeline

## 1. Overview & Context

The author writes markdown notes across multiple environments, historically using Emacs (`Alt+q` / `fill-paragraph`) and Vim (visual mode `q` / `gq`), which format prose paragraphs to a crisp ~70-character column limit. However, occasional edits via Typora or GitHub's web-based editor introduce long spilling lines (>80–150 characters) that break the consistent line-wrapped aesthetic of the repository's source files.

This feature introduces an automated **fill-paragraph linter and formatter** that:
1. Formats markdown prose to a 70-character column limit (matching Emacs default `fill-column` and existing note distribution).
2. Preserves all markdown structures and Hugo-specific features: YAML frontmatter, fenced and indented code blocks, markdown tables, headings, raw HTML blocks, Hugo shortcodes, inline code, URLs/hyperlinks, and Goldmark attribute annotations (e.g. `:material-penguin:{ .anim-heart }`).
3. Handles list items (`- `, `* `, `+ `, `1. `) and blockquotes (`> `) with proper hanging indentation.
4. Integrates seamlessly into GitHub Actions CI (`.github/workflows/ci.yml`) on `pull_request` events to automatically format and commit back spilling lines to the PR branch (`style(prose): fill paragraphs to 70 columns [skip ci]`).
5. Performs an initial one-time fix across all existing markdown files in `home/`.
6. Provides a companion automated test suite (`scripts/test_fill_paragraph.py`) validating all formatting and edge cases locally and in CI.

---

## 2. Architecture & Design

### 2.1 Formatting Engine (`scripts/fill_paragraph.py`)
A dedicated, zero-dependency Python script designed specifically for Hugo/Goldmark markdown:
- **CLI Options:**
  - `python scripts/fill_paragraph.py --check`: Inspects files and exits with code 1 if any paragraphs exceed the column limit or need formatting.
  - `python scripts/fill_paragraph.py --fix`: Reformats files in-place.
  - Optional path arguments: Target specific files or directories (defaults to `home/**/*.md`).
  - `--width 70`: Configurable column limit, defaulting to 70.
- **Parsing & Preservation Rules:**
  - **YAML Frontmatter:** Content between opening `---` and closing `---` at the top of the file is left 100% untouched.
  - **Code Blocks:** Fenced code blocks (` ``` ` or `~~~`) and indented code blocks are left 100% untouched.
  - **Tables:** Any markdown table rows (lines containing `|`) are left 100% untouched.
  - **Headings:** ATX headings (`#`, `##`, `###`, etc.) are left untouched.
  - **Hugo Shortcodes & HTML Blocks:** Blocks starting with `{{<`, `{{%`, or raw HTML tags (`<div>`, `<details>`, `<iframe`, etc.) are preserved.
  - **Atomic Inline Tokens:** URLs (`https://...`), full markdown links (`[text](url)`), images (`![alt](url)`), and Goldmark inline attributes (`:icon:{ .class }`) are treated as indivisible units to ensure braces or URLs are never split across lines.
  - **List Items:** Unordered lists (`- `, `* `, `+ `) and ordered lists (`1. `, `2. `) wrap continuation lines with hanging indentation matching the content offset.
  - **Blockquotes:** Lines starting with `>` wrap subsequent lines with the matching `> ` quote prefix.
  - **Hard Line Breaks:** Lines ending with two or more spaces or `\` are preserved as hard breaks.

### 2.2 CI Workflow Integration (`.github/workflows/ci.yml`)
- Configures `permissions: contents: write` to allow the GitHub Actions bot to push back to PR branches.
- For `pull_request` events:
  - Checks out the PR branch with `ref: ${{ github.head_ref }}`.
  - Runs `python3 scripts/fill_paragraph.py --fix`.
  - Checks `git status --porcelain home`. If changes exist:
    - Commits changes as `github-actions[bot]`: `style(prose): fill paragraphs to 70 columns [skip ci]`.
    - Pushes the commit back to the PR branch.
  - Continues to Hugo build and test suites to verify that the site builds cleanly on the formatted files.

### 2.3 One-Time Batch Reformatting
- Runs `python scripts/fill_paragraph.py --fix` across all markdown files in `home/`.
- Verifies that `hugo --gc --minify --panicOnWarning` compiles with zero warnings or errors.
- Verifies that all 15 existing test suites and link checkers pass with 100% success.

---

## 3. Constraints & Guardrails

1. **Sacred Prose Principle:**
   The formatter reflows line breaks only. It does NOT alter words, grammar, phrasing, tone, punctuation, or content.
2. **Zero Bloat & Zero External Dependencies:**
   Implemented in standard Python (standard library `re`, `sys`, `pathlib`, `argparse`). No npm packages or third-party dependencies required.
3. **Encoding & Cross-Platform Support:**
   Strict UTF-8 read and write everywhere, with Windows stdout reconfigured (`hasattr(sys.stdout, "reconfigure")`).
4. **CI Parity & Automated Discovery:**
   `scripts/test_fill_paragraph.py` is created and integrated into `./scripts/test.ps1`, `./scripts/test.sh`, and covered dynamically by `scripts/test_ci_parity.py`.
5. **Git Worktree Isolation:**
   All changes and the specification itself live strictly within `.worktrees/fill-paragraph-linter`. Zero direct commits or pushes to `master`.

---

## 4. Acceptance Criteria

1. **Precision Formatting Engine (`scripts/fill_paragraph.py`):**
   - Correctly wraps paragraphs to 70 characters.
   - Accurately preserves frontmatter, fenced code blocks, tables, headings, HTML blocks, shortcodes, URLs, and Goldmark attributes.
   - Accurately handles list items and blockquotes with hanging indents.
   - Provides both `--check` and `--fix` modes.
2. **Automated Regression Test Suite (`scripts/test_fill_paragraph.py`):**
   - Tests frontmatter preservation, code block preservation, table preservation, list wrapping, blockquote wrapping, URL/attribute preservation, and idempotency (running twice produces identical output).
   - Passes with exit code 0.
3. **CI Pipeline Integration (`.github/workflows/ci.yml`):**
   - Configures `contents: write` permission.
   - Adds PR-triggered auto-formatting step that commits and pushes changes back to the PR branch when `home/` contains unformatted lines.
4. **Local Test Suites & CI Parity:**
   - `./scripts/test.ps1` and `./scripts/test.sh` include the new test and pass cleanly.
   - `scripts/test_ci_parity.py` verifies all test suites in `scripts/` are executed in CI.
5. **Full Site Build Integrity:**
   - Hugo builds cleanly (`hugo --gc --minify --panicOnWarning`) with zero warnings.
   - All internal links, backlinks, search index, and page structures remain 100% intact after the one-time batch reformatting.
