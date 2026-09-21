#!/usr/bin/env python3
"""
fill_paragraph.py - Emacs/Vim-style paragraph wrapper and linter for Markdown prose.

Formats markdown paragraphs to a crisp column limit (default: 70 characters),
matching Emacs fill-paragraph (Alt+q) and Vim (gq).

Preserves:
- YAML Frontmatter (--- ... ---)
- Fenced code blocks (``` ... ``` or ~~~ ... ~~~)
- Markdown tables (| ... |)
- Headings (# ...)
- Horizontal rules (---, ***, ___)
- Raw HTML container blocks (<div>, <details>, etc.)
- Hugo shortcodes ({{< ... >}}, {{% ... %}})
- Reference link definitions ([label]: url ...)
- Standalone link lines and image links (e.g. [Button](url) or ![alt](img))
- Card header items with bold titles (- :icon: __Title__)
- Atomic inline tokens: HTML tags, Goldmark attribute lists ({ .class }),
  inline code (`...`), and link URLs ((https://...))
- List item hanging indentation (- , * , + , 1. ) and blockquotes (> )
"""

import argparse
import glob
import os
import re
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def protect_spaces(text: str) -> str:
    """Protect spaces inside atomic markdown/Hugo constructs using non-breaking space."""
    # 1. Backtick inline code: `...`
    def repl_code(m):
        return m.group(0).replace(" ", "\u00A0")

    text = re.sub(r"`[^`\n]+`", repl_code, text)

    # 2. HTML tags: <...>
    def repl_html(m):
        return m.group(0).replace(" ", "\u00A0")

    text = re.sub(r"<[^>\n]+>", repl_html, text)

    # 3. Attribute lists: {...}
    def repl_attrs(m):
        return m.group(0).replace(" ", "\u00A0")

    text = re.sub(r"\{[^{}\n]+\}", repl_attrs, text)

    # 4. Link destinations: (...)
    def repl_link(m):
        return m.group(0).replace(" ", "\u00A0")

    text = re.sub(r'\([^\)\n\s]+(?:\s+"[^"\n]*")?\)', repl_link, text)

    return text


def unprotect_spaces(text: str) -> str:
    """Restore protected non-breaking spaces back to regular spaces."""
    return text.replace("\u00A0", " ")


def wrap_words(words: list[str], width: int, initial_indent: str, subsequent_indent: str) -> str:
    """Wraps a list of words into lines with initial and subsequent indentation."""
    if not words:
        return initial_indent.rstrip()

    # Pre-process words: attach standalone dash/punctuation ('-', '--', '—') to previous word
    # to avoid starting a wrapped line with a dash (which looks like an accidental sub-bullet)
    merged_words = []
    for w in words:
        if merged_words and w in ("-", "--", "—"):
            merged_words[-1] = merged_words[-1] + " " + w
        else:
            merged_words.append(w)

    lines = []
    current_line = initial_indent
    prefix = initial_indent

    for word in merged_words:
        if current_line == prefix:
            current_line += word
        elif len(current_line) + 1 + len(word) <= width:
            current_line += " " + word
        else:
            lines.append(current_line)
            current_line = subsequent_indent + word
            prefix = subsequent_indent

    if current_line:
        lines.append(current_line)

    return "\n".join(lines)


def is_table_row(line: str) -> bool:
    """Check if a line is part of a markdown table."""
    s = line.strip()
    return s.startswith("|") or (s.count("|") >= 2 and not s.startswith("```"))


def is_hr(line: str) -> bool:
    """Check if a line is a horizontal rule (---, ***, ___)."""
    s = line.strip()
    return re.match(r"^(?:-{3,}|\*{3,}|_{3,})$", s) is not None


def is_heading(line: str) -> bool:
    """Check if a line is a markdown heading."""
    return re.match(r"^\s*#{1,6}\s+", line) is not None


def is_html_block(line: str) -> bool:
    """Check if a line is a raw HTML container or tag."""
    s = line.strip()
    return bool(re.match(r"^</?[a-zA-Z0-9]+(?:\s+[^>]*)?>?$", s) or s.startswith("<!--"))


def is_shortcode(line: str) -> bool:
    """Check if a line is a Hugo shortcode."""
    s = line.strip()
    return s.startswith("{{<") or s.startswith("{{%") or s.startswith("{{-") or s.startswith("{{")


def is_ref_link(line: str) -> bool:
    """Check if a line is a reference link definition e.g. [1]: http..."""
    return bool(re.match(r"^\s*\[[^\]]+\]:\s+\S+", line))


def is_standalone_link_or_image(line: str) -> bool:
    """Check if a line consists solely of a markdown link or image (e.g. card action button)."""
    s = line.strip()
    return bool(re.match(r"^!?\[[^\]]+\]\([^\)]+\)$", s))


def is_card_header(line: str) -> bool:
    """Check if a line is a card or directory item header (e.g. - :icon: __Title__)."""
    return bool(re.match(r"^\s*[-*+]\s+.*__[^_\n]+__\s*$", line))


def is_list_bullet(line: str) -> bool:
    """Check if a line starts with a list bullet."""
    return bool(re.match(r"^\s*([-*+]|\d+\.)\s+", line))


def is_blockquote(line: str) -> bool:
    """Check if a line starts with blockquote symbol."""
    return bool(re.match(r"^\s*>+", line))


def format_markdown(content: str, width: int = 70) -> str:
    """
    Format prose paragraphs in markdown content to `width` characters per line.
    Returns the formatted markdown string.
    """
    if not content:
        return content

    content_stripped = content.rstrip("\r\n")
    trailing_newlines = content[len(content_stripped) :]
    if not trailing_newlines and content.endswith("\n"):
        trailing_newlines = "\n"

    raw_lines = content_stripped.split("\n")
    output_lines = []
    i = 0
    n = len(raw_lines)

    # 1. Preserve YAML frontmatter verbatim
    if n > 0 and raw_lines[0].strip() == "---":
        output_lines.append(raw_lines[0])
        i = 1
        while i < n:
            output_lines.append(raw_lines[i])
            if raw_lines[i].strip() == "---":
                i += 1
                break
            i += 1

    in_fenced_code = False
    fence_marker = ""

    while i < n:
        line = raw_lines[i]
        sline = line.strip()

        # 2. Preserve fenced code blocks verbatim
        if not in_fenced_code:
            m = re.match(r"^(\s*)(`{3,}|~{3,})", line)
            if m:
                in_fenced_code = True
                fence_marker = m.group(2)
                output_lines.append(line)
                i += 1
                continue
        else:
            output_lines.append(line)
            m = re.match(r"^\s*(`{3,}|~{3,})", line)
            if m and m.group(1).startswith(fence_marker[:3]) and len(m.group(1)) >= len(fence_marker):
                in_fenced_code = False
            i += 1
            continue

        # 3. Preserve blank lines
        if not sline:
            output_lines.append("")
            i += 1
            continue

        # 4. Preserve non-prose lines (headings, tables, hrs, shortcodes, html blocks, ref links, standalone links, card headers)
        if (
            is_heading(line)
            or is_table_row(line)
            or is_hr(line)
            or is_shortcode(line)
            or is_html_block(line)
            or is_ref_link(line)
            or is_standalone_link_or_image(line)
            or is_card_header(line)
        ):
            output_lines.append(line)
            i += 1
            continue

        # 5. Handle blockquotes
        m_quote = re.match(r"^(\s*>+\s*)", line)
        if m_quote:
            quote_prefix = m_quote.group(1)
            quote_lines = [line[len(quote_prefix) :]]
            i += 1
            while i < n:
                next_line = raw_lines[i]
                if not next_line.strip():
                    break
                m_next = re.match(r"^(\s*>+\s*)", next_line)
                if m_next and m_next.group(1).strip() == quote_prefix.strip():
                    quote_lines.append(next_line[len(m_next.group(1)) :])
                    i += 1
                elif (
                    not is_list_bullet(next_line)
                    and not is_heading(next_line)
                    and not is_table_row(next_line)
                    and not is_hr(next_line)
                    and not is_shortcode(next_line)
                    and not is_html_block(next_line)
                    and not is_standalone_link_or_image(next_line)
                    and not is_card_header(next_line)
                ):
                    quote_lines.append(next_line.strip())
                    i += 1
                else:
                    break

            full_text = " ".join(ql.strip() for ql in quote_lines)
            protected = protect_spaces(full_text)
            wrapped = wrap_words(
                protected.split(),
                width,
                initial_indent=quote_prefix,
                subsequent_indent=quote_prefix,
            )
            output_lines.extend(unprotect_spaces(wrapped).splitlines())
            continue

        # 6. Handle list items
        m_list = re.match(r"^(\s*)([-*+]|\d+\.)(\s+\[[ xX]\])?(\s+)", line)
        if m_list:
            indent = m_list.group(1)
            bullet = m_list.group(2)
            checkbox = m_list.group(3) or ""
            spacing = m_list.group(4)
            initial_prefix = indent + bullet + checkbox + spacing
            subsequent_prefix = " " * len(initial_prefix)

            item_text = line[len(initial_prefix) :]
            item_lines = [item_text]
            i += 1

            while i < n:
                next_line = raw_lines[i]
                if not next_line.strip():
                    break
                if (
                    is_list_bullet(next_line)
                    or is_heading(next_line)
                    or is_table_row(next_line)
                    or is_hr(next_line)
                    or is_shortcode(next_line)
                    or is_html_block(next_line)
                    or is_blockquote(next_line)
                    or is_standalone_link_or_image(next_line)
                    or is_card_header(next_line)
                ):
                    break
                item_lines.append(next_line.strip())
                i += 1

            full_text = " ".join(item_lines).strip()
            protected = protect_spaces(full_text)
            wrapped = wrap_words(
                protected.split(),
                width,
                initial_indent=initial_prefix,
                subsequent_indent=subsequent_prefix,
            )
            output_lines.extend(unprotect_spaces(wrapped).splitlines())
            continue

        # 7. Handle regular prose paragraphs
        m_indent = re.match(r"^(\s*)", line)
        indent_prefix = m_indent.group(1) if m_indent else ""

        para_lines = [line[len(indent_prefix) :].strip()]
        i += 1
        while i < n:
            next_line = raw_lines[i]
            if not next_line.strip():
                break
            if (
                is_heading(next_line)
                or is_table_row(next_line)
                or is_hr(next_line)
                or is_shortcode(next_line)
                or is_html_block(next_line)
                or is_ref_link(next_line)
                or is_list_bullet(next_line)
                or is_blockquote(next_line)
                or is_standalone_link_or_image(next_line)
                or is_card_header(next_line)
            ):
                break
            para_lines.append(next_line.strip())
            i += 1

        full_text = " ".join(para_lines).strip()
        protected = protect_spaces(full_text)
        wrapped = wrap_words(
            protected.split(),
            width,
            initial_indent=indent_prefix,
            subsequent_indent=indent_prefix,
        )
        output_lines.extend(unprotect_spaces(wrapped).splitlines())

    result = "\n".join(output_lines) + trailing_newlines
    return result


def discover_files(paths: list[str]) -> list[Path]:
    """Discover markdown files from provided paths or default content directory."""
    if not paths:
        base_dir = Path("home")
        if not base_dir.exists() and Path("../home").exists():
            base_dir = Path("../home")
        return sorted(base_dir.rglob("*.md"))

    discovered = []
    for p_str in paths:
        p = Path(p_str)
        if p.is_file() and p.suffix.lower() == ".md":
            discovered.append(p)
        elif p.is_dir():
            discovered.extend(sorted(p.rglob("*.md")))
        else:
            for match in glob.glob(p_str, recursive=True):
                mp = Path(match)
                if mp.is_file() and mp.suffix.lower() == ".md":
                    discovered.append(mp)
    return sorted(list(set(discovered)))


def main():
    parser = argparse.ArgumentParser(
        description="Emacs/Vim-style paragraph wrapper and linter for Markdown prose."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Files or directories to process (default: home/**/*.md)",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=70,
        help="Target column width limit (default: 70)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check only; exit with code 1 if any files need formatting",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Reformat files in-place (default behavior)",
    )

    args = parser.parse_args()
    check_mode = args.check

    files = discover_files(args.paths)
    if not files:
        print("No markdown files found to process.")
        sys.exit(0)

    needs_formatting = []

    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fp:
                content = fp.read()
            formatted = format_markdown(content, width=args.width)
            if formatted != content:
                needs_formatting.append(f)
                if not check_mode:
                    with open(f, "w", encoding="utf-8") as fp:
                        fp.write(formatted)
        except Exception as e:
            print(f"Error processing {f}: {e}", file=sys.stderr)
            sys.exit(2)

    if check_mode:
        if needs_formatting:
            print(f"Found {len(needs_formatting)} file(s) that need paragraph filling:")
            for f in needs_formatting:
                print(f"  - {f}")
            print(f"\nRun 'python scripts/fill_paragraph.py --fix' to reformat.")
            sys.exit(1)
        else:
            print(f"All {len(files)} markdown file(s) are properly paragraph-filled.")
            sys.exit(0)
    else:
        if needs_formatting:
            print(f"Successfully formatted {len(needs_formatting)} / {len(files)} markdown file(s).")
        else:
            print(f"All {len(files)} markdown file(s) already conform to {args.width}-column limit.")
        sys.exit(0)


if __name__ == "__main__":
    main()
