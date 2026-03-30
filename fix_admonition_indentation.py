from __future__ import annotations

import re
from pathlib import Path

ROOT = Path("docs/chapters_split")
SUFFIX = ".md"

ADMONITION_START_RE = re.compile(r"^([ \t]*)(\?{3}\+?|!{3}\+?)\s+.*$")
BULLET_RE = re.compile(r"^([ \t]*)([-*+]\s+.*)$")


def fix_admonition_indentation(text: str) -> tuple[str, int]:
    """
    Ensure list items directly under MkDocs admonitions are indented.

    Example:
        ??? note "Title"
        - item 1
        - item 2

    becomes:
        ??? note "Title"
            - item 1
            - item 2
    """
    lines = text.splitlines()
    out: list[str] = []
    fixes = 0
    i = 0

    while i < len(lines):
        line = lines[i]
        out.append(line)

        m = ADMONITION_START_RE.match(line)
        if not m:
            i += 1
            continue

        base_indent = m.group(1)
        content_indent = base_indent + "    "

        i += 1

        while i < len(lines):
            current = lines[i]

            if current.strip() == "":
                out.append(current)
                i += 1
                continue

            # stop if we hit a non-indented normal block
            current_indent_len = len(current) - len(current.lstrip(" \t"))
            base_indent_len = len(base_indent)

            bullet_match = BULLET_RE.match(current)

            if bullet_match:
                bullet_indent_len = len(bullet_match.group(1))
                if bullet_indent_len <= base_indent_len:
                    out.append(content_indent + bullet_match.group(2))
                    fixes += 1
                    i += 1
                    continue
                else:
                    out.append(current)
                    i += 1
                    continue

            # already properly indented admonition content
            if current_indent_len > base_indent_len:
                out.append(current)
                i += 1
                continue

            # otherwise we've reached content outside the admonition
            break

    new_text = "\n".join(out)
    if text.endswith("\n"):
        new_text += "\n"

    return new_text, fixes


def process_file(path: Path) -> int:
    original = path.read_text(encoding="utf-8")
    fixed, changes = fix_admonition_indentation(original)

    if changes > 0 and fixed != original:
        path.write_text(fixed, encoding="utf-8")

    return changes


def main() -> None:
    if not ROOT.exists():
        raise FileNotFoundError(f"Folder not found: {ROOT}")

    files_changed = 0
    total_fixes = 0

    for path in sorted(ROOT.rglob(f"*{SUFFIX}")):
        changes = process_file(path)
        if changes > 0:
            files_changed += 1
            total_fixes += changes
            print(f"✔ Fixed {changes:>2} bullet line(s): {path}")

    print("\nDone.")
    print(f"Files changed: {files_changed}")
    print(f"Indented bullet lines: {total_fixes}")


if __name__ == "__main__":
    main()
