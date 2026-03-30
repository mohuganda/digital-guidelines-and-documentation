from __future__ import annotations

import re
from pathlib import Path

ROOT = Path("docs/chapters_split")
SUFFIX = ".md"


ADMONITION_START_RE = re.compile(
    r"""^
    (?P<indent>[ \t]*)
    (?P<marker>\?{3}\+?|!{3}\+?)
    [ \t]+
    .*
    $""",
    re.VERBOSE,
)


def fix_admonition_blank_lines(text: str) -> tuple[str, int]:
    """
    Remove blank lines immediately after MkDocs admonition starters.

    Example fixed:
        ??? note "Title"

            - item

    becomes:
        ??? note "Title"
            - item
    """
    lines = text.splitlines()
    out: list[str] = []
    changes = 0
    i = 0

    while i < len(lines):
        line = lines[i]
        out.append(line)

        match = ADMONITION_START_RE.match(line)
        if match and i + 2 < len(lines):
            next_line = lines[i + 1]
            after_next = lines[i + 2]

            same_or_deeper_indent = len(after_next) - len(after_next.lstrip(" \t")) > len(
                match.group("indent")
            )

            if next_line.strip() == "" and after_next.strip() != "" and same_or_deeper_indent:
                changes += 1
                i += 2
                out.append(after_next)
                i += 1
                continue

        i += 1

    new_text = "\n".join(out)
    if text.endswith("\n"):
        new_text += "\n"

    return new_text, changes


def process_file(path: Path) -> int:
    original = path.read_text(encoding="utf-8")
    fixed, changes = fix_admonition_blank_lines(original)

    if changes > 0 and fixed != original:
        path.write_text(fixed, encoding="utf-8")

    return changes


def main() -> None:
    if not ROOT.exists():
        raise FileNotFoundError(f"Folder not found: {ROOT}")

    total_files_changed = 0
    total_admonitions_fixed = 0

    for path in sorted(ROOT.rglob(f"*{SUFFIX}")):
        changes = process_file(path)
        if changes > 0:
            total_files_changed += 1
            total_admonitions_fixed += changes
            print(f"✔ Fixed {changes:>2} admonition block(s): {path}")

    print("\nDone.")
    print(f"Files changed: {total_files_changed}")
    print(f"Admonition blank lines removed: {total_admonitions_fixed}")


if __name__ == "__main__":
    main()
