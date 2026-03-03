#!/usr/bin/env python3
import re
from pathlib import Path

TARGET = Path("docs/chapters_split/00")

roman_line = re.compile(r"^\s*[IVXLCDM]{1,10}\s*$")
arabic_line = re.compile(r"^\s*\d{1,4}\s*$")

def cleanup_text(text: str) -> str:
    out_lines = []
    for line in text.splitlines():
        if roman_line.match(line):
            continue
        if arabic_line.match(line):
            continue
        out_lines.append(line)

    cleaned = "\n".join(out_lines)

    # collapse 3+ newlines into 2
    cleaned = re.sub(r"\n\s*\n\s*\n+", "\n\n", cleaned)

    # remove trailing spaces
    cleaned = re.sub(r"[ \t]+$", "", cleaned, flags=re.MULTILINE)

    # ensure ends with newline
    if not cleaned.endswith("\n"):
        cleaned += "\n"
    return cleaned

def main():
    if not TARGET.exists():
        raise SystemExit(f"Folder not found: {TARGET}")

    files = sorted(TARGET.glob("*.md"))
    if not files:
        raise SystemExit(f"No markdown files found in: {TARGET}")

    for f in files:
        original = f.read_text(encoding="utf-8", errors="ignore")
        cleaned = cleanup_text(original)
        if cleaned != original:
            f.write_text(cleaned, encoding="utf-8")
            print(f"Cleaned: {f}")
        else:
            print(f"No change: {f}")

if __name__ == "__main__":
    main()