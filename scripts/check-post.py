#!/usr/bin/env python3
"""Lint a blog post before publishing.

    scripts/check-post.py _drafts/my-post.md [more files ...]

Checks front matter, file naming, image paths and alt text, and the two LaTeX
pitfalls of kramdown on GitHub Pages:
  * inline $...$ containing a backslash before punctuation (kramdown strips it);
  * display $$ blocks without a blank line before them (they render inline).
Exits with status 1 if any error is found.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KRAMDOWN_ESCAPES = set("\\.*_+-`()[]{}#!:|\"'$=<>")
POST_NAME = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9]+(-[a-z0-9]+)*\.md$")
DRAFT_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*\.md$")


def split_front_matter(text):
    if not text.startswith("---\n"):
        return None, text, 0
    end = text.find("\n---\n", 4)
    if end < 0:
        return None, text, 0
    fm = text[4:end]
    return fm, text[end + 5:], fm.count("\n") + 3


def mask_code(body):
    """Blank out fenced code blocks and inline code, keeping line numbers."""
    out, fence = [], None
    for line in body.split("\n"):
        stripped = line.lstrip()
        if fence:
            out.append("")
            if stripped.startswith(fence):
                fence = None
            continue
        m = re.match(r"(`{3,}|~{3,})", stripped)
        if m:
            fence = m.group(1)
            out.append("")
            continue
        out.append(re.sub(r"`[^`\n]*`", lambda s: " " * len(s.group(0)), line))
    return out


def check(path):
    errors, warnings = [], []
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    fm, body, offset = split_front_matter(text)

    in_posts = p.parent.name == "_posts"
    if in_posts and not POST_NAME.match(p.name):
        errors.append("file name must be YYYY-MM-DD-slug.md (lower-case slug, hyphens)")
    if p.parent.name == "_drafts" and not DRAFT_NAME.match(p.name):
        errors.append("draft name must be slug.md (lower-case slug, hyphens)")

    if fm is None:
        errors.append("missing front matter block (--- ... ---) at the top")
        fm = ""
    for key in ("title", "description"):
        m = re.search(rf"^{key}:\s*(.*)$", fm, re.M)
        if not m or m.group(1).strip() in ("", '""', "''"):
            errors.append(f"front matter: '{key}' is missing or empty")
    if "One-sentence summary shown in post lists" in fm:
        errors.append("front matter: 'description' is still the template placeholder")
    if re.search(r"^description:.*\$", fm, re.M):
        warnings.append("front matter: avoid math in 'description' (it is shown as plain text)")

    lines = mask_code(body)

    # Display math: a $$ block needs blank lines around it, otherwise it renders inline.
    in_display = False
    for i, line in enumerate(lines):
        s = line.strip()
        if not in_display:
            opens_block = s == "$$"
            one_line_block = len(s) > 4 and s.startswith("$$") and s.endswith("$$") and s.count("$$") == 2
            if not (opens_block or one_line_block):
                continue
            prev = lines[i - 1].strip() if i > 0 else ""
            if prev:
                errors.append(f"line {i + 1 + offset}: display math needs a blank line before $$, otherwise it renders inline")
            if opens_block:
                in_display = True
                continue
        elif not s.endswith("$$"):
            continue
        in_display = False
        nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
        if nxt:
            warnings.append(f"line {i + 1 + offset}: add a blank line after the display math block")

    # Inline $...$ (outside $$...$$) that contains backslash + escapable punctuation.
    for i, line in enumerate(lines):
        no_double = re.sub(r"\$\$.*?\$\$", lambda s: " " * len(s.group(0)), line)
        if no_double.strip().startswith("$$"):
            continue
        for m in re.finditer(r"(?<![\\$])\$([^$\n]+?)\$(?!\$)", no_double):
            expr = m.group(1)
            bad = sorted({expr[j + 1] for j in range(len(expr) - 1)
                          if expr[j] == "\\" and expr[j + 1] in KRAMDOWN_ESCAPES})
            if bad:
                chars = " ".join("\\" + c for c in bad)
                errors.append(f"line {i + 1 + offset}: inline ${expr}$ contains {chars}; "
                              f"write it as $${expr}$$ so the backslashes survive")

    # Images: Markdown and the figure include.
    raw_lines = body.split("\n")
    for i, line in enumerate(lines):
        for alt, src in re.findall(r"!\[([^\]]*)\]\(([^)\s]+)", line):
            if not alt.strip():
                warnings.append(f"line {i + 1 + offset}: image {src} has no alt text")
            check_src(src, i + 1 + offset, errors)
    joined = "\n".join(raw_lines)
    for m in re.finditer(r"\{%\s*include\s+figure\.html(.*?)%\}", joined, re.S):
        line_no = joined[:m.start()].count("\n") + 1 + offset
        args = m.group(1)
        src = re.search(r'src="([^"]+)"', args)
        if not src:
            errors.append(f"line {line_no}: figure include without src")
        else:
            check_src(src.group(1), line_no, errors)
        if not re.search(r'alt="[^"]+"', args) and not re.search(r'caption="[^"]+"', args):
            warnings.append(f"line {line_no}: figure has neither alt nor caption")

    if re.search(r"^# ", "\n".join(lines), re.M):
        warnings.append("body uses a level-1 heading; start sections at ##")

    return errors, warnings


def check_src(src, line_no, errors):
    if re.match(r"^(https?:)?//", src):
        return
    if not src.startswith("/"):
        errors.append(f"line {line_no}: image path {src} must start with /assets/")
        return
    if not (ROOT / src.lstrip("/")).exists():
        errors.append(f"line {line_no}: image {src} not found in the repository")


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip())
        return 2
    status = 0
    for path in argv[1:]:
        errors, warnings = check(path)
        for w in warnings:
            print(f"{path}: warning: {w}")
        for e in errors:
            print(f"{path}: error: {e}")
        if errors:
            status = 1
        elif not warnings:
            print(f"{path}: ok")
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv))
