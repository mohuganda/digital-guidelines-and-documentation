from __future__ import annotations

import os
import re
from pathlib import Path

OLD_DIR = Path("docs/chapters_split")
NEW_DIR = Path("odl_output/cleaned_split/split_chapters")


def extract_section_key(filename: str) -> str | None:
    """
    Extract the logical section number from either naming style.

    Examples:
      1-03-04-acetylsalicylic-acid-aspirin-poisoning.md -> 1.3.4
      1.3.4-acetylsalicylic-acid-aspirin-poisoning-t39-0.md -> 1.3.4
      1-03-12-02-chronic-alcohol-poisoning.md -> 1.3.12.2
      16-04-08-01-care-of-mother-immediately-after-delivery.md -> 16.4.8.1
    """
    stem = Path(filename).stem

    # Style 1: dotted numbering already present
    m = re.match(r"^(\d+(?:\.\d+)+)\b", stem)
    if m:
        return m.group(1)

    # Style 2: dash-separated numbering at beginning
    m = re.match(r"^(\d+(?:-\d+)+)\b", stem)
    if m:
        raw = m.group(1)
        parts = raw.split("-")
        # Normalize zero-padded segments, e.g. 03 -> 3
        parts = [str(int(p)) for p in parts]
        return ".".join(parts)

    return None


def get_old_header_and_rest(content: str) -> tuple[str, str]:
    """
    Keep the top header block from the old file.
    Usually:
      # Chapter ...
      ## / ### section title
      ICD10 CODE...
    Then replace the remainder with cleaned ODL body.
    """
    lines = content.splitlines()

    header_end = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("ICD10"):
            header_end = i + 1
            break

    # fallback if ICD10 line does not exist
    if header_end == 0:
        seen_heading_count = 0
        for i, line in enumerate(lines):
            if line.strip().startswith("#"):
                seen_heading_count += 1
            if seen_heading_count >= 2 and not line.strip():
                header_end = i
                break

    if header_end == 0:
        # last fallback: keep first 2 non-empty heading-ish lines
        header_end = min(len(lines), 4)

    header = "\n".join(lines[:header_end]).strip()
    rest = "\n".join(lines[header_end:]).strip()
    return header, rest


def strip_new_file_header(content: str) -> str:
    """
    Remove the top heading block from the cleaned ODL file,
    so only the body is injected into the old split file.
    """
    lines = content.splitlines()

    body_start = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("ICD10"):
            body_start = i + 1
            break

    if body_start == 0:
        # if no ICD10 line, skip initial title block until first real paragraph
        for i, line in enumerate(lines):
            if i > 0 and line.strip() and not line.strip().startswith("#"):
                body_start = i
                break

    return "\n".join(lines[body_start:]).strip()


def build_new_index() -> dict[str, Path]:
    """
    Build a lookup of cleaned ODL files by logical section number.
    """
    index: dict[str, Path] = {}

    for path in NEW_DIR.rglob("*.md"):
        key = extract_section_key(path.name)
        if key:
            index[key] = path

    return index


def merge_file(old_path: Path, new_path: Path) -> None:
    old_content = old_path.read_text(encoding="utf-8")
    new_content = new_path.read_text(encoding="utf-8")

    old_header, _ = get_old_header_and_rest(old_content)
    new_body = strip_new_file_header(new_content)

    merged = old_header + "\n\n" + new_body.strip() + "\n"
    old_path.write_text(merged, encoding="utf-8")


def main() -> None:
    new_index = build_new_index()

    merged_count = 0
    missing_count = 0

    for old_path in sorted(OLD_DIR.rglob("*.md")):
        key = extract_section_key(old_path.name)

        # Skip index / overview-like files without a real numbered section
        if not key:
            print(f"⚠ Skipped (no section key): {old_path.name}")
            continue

        new_path = new_index.get(key)

        if new_path:
            merge_file(old_path, new_path)
            print(f"✔ Merged: {old_path.name}  <-  {new_path.name}")
            merged_count += 1
        else:
            print(f"⚠ Missing section match for: {old_path.name}  [key={key}]")
            missing_count += 1

    print()
    print(f"Done. Merged: {merged_count}, Missing: {missing_count}")


if __name__ == "__main__":
    main()
