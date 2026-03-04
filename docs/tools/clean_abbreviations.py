#!/usr/bin/env python3
import re
import argparse
from pathlib import Path

HEADER_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")

def find_section(md: str, title: str):
    """
    Returns (start_idx, end_idx, heading_level) for a section whose heading text matches title.
    Section end is the next heading of same or higher level, or EOF.
    """
    lines = md.splitlines(True)
    start = None
    level = None

    for i, line in enumerate(lines):
        m = HEADER_RE.match(line)
        if not m:
            continue
        lvl = len(m.group(1))
        txt = m.group(2).strip().lower()

        if txt == title.lower():
            start = i
            level = lvl
            break

    if start is None:
        return None

    end = len(lines)
    for j in range(start + 1, len(lines)):
        m = HEADER_RE.match(lines[j])
        if not m:
            continue
        lvl = len(m.group(1))
        if lvl <= level:
            end = j
            break

    return start, end, level

def normalize_abbrev_lines(block: str):
    """
    Convert messy abbrev block into list of (abbr, meaning).
    Heuristics:
    - Join wrapped lines where meaning continues.
    - Accept separators: '-', '–', ':', multiple spaces.
    - Ignore empty lines and obvious non-entries.
    """
    raw_lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
    # Merge lines that are clearly continuations (no abbreviation pattern at start)
    merged = []
    for ln in raw_lines:
        # looks like a new abbrev line if it starts with ALLCAPS/NUM or acronym-ish token
        if re.match(r"^[A-Z0-9][A-Z0-9/\-\(\)]{1,15}\b", ln) and (
            " - " in ln or " – " in ln or ":" in ln or re.search(r"\s{2,}", ln)
        ):
            merged.append(ln)
        else:
            if merged:
                merged[-1] = merged[-1].rstrip() + " " + ln
            else:
                merged.append(ln)

    pairs = []
    for ln in merged:
        # unify separators
        ln = ln.replace("–", "-")
        # Try patterns: ABBR - Meaning, ABBR: Meaning, ABBR  Meaning (2+ spaces)
        m = re.match(r"^([A-Z0-9][A-Z0-9/\-\(\)]{1,20})\s*-\s*(.+)$", ln)
        if not m:
            m = re.match(r"^([A-Z0-9][A-Z0-9/\-\(\)]{1,20})\s*:\s*(.+)$", ln)
        if not m:
            m = re.match(r"^([A-Z0-9][A-Z0-9/\-\(\)]{1,20})\s{2,}(.+)$", ln)

        if not m:
            # skip lines that don't match an abbrev/meaning layout
            continue

        abbr = m.group(1).strip()
        meaning = re.sub(r"\s+", " ", m.group(2).strip())
        pairs.append((abbr, meaning))

    # de-dup by abbreviation, keep the longest meaning (usually the most complete)
    dedup = {}
    for abbr, meaning in pairs:
        if abbr not in dedup or len(meaning) > len(dedup[abbr]):
            dedup[abbr] = meaning

    # sort A–Z
    cleaned = sorted(dedup.items(), key=lambda x: x[0])
    return cleaned

def as_markdown_table(items):
    out = []
    out.append("| Abbreviation | Meaning |")
    out.append("|---|---|")
    for abbr, meaning in items:
        meaning = meaning.replace("|", "\\|")
        out.append(f"| **{abbr}** | {meaning} |")
    return "\n".join(out) + "\n"

def main():
    ap = argparse.ArgumentParser(description="Clean an 'Abbreviations' section in a Markdown file into a sorted table.")
    ap.add_argument("--file", required=True, help="Path to the markdown file containing the Abbreviations section.")
    ap.add_argument("--title", default="Abbreviations", help="Heading title to clean (default: Abbreviations).")
    ap.add_argument("--backup", action="store_true", help="Create a .bak copy before modifying.")
    args = ap.parse_args()

    path = Path(args.file)
    md = path.read_text(encoding="utf-8")

    found = find_section(md, args.title)
    if not found:
        raise SystemExit(f"Section heading '{args.title}' not found in {path}")

    start, end, lvl = found
    lines = md.splitlines(True)

    # section body is everything after heading line until end marker
    heading_line = lines[start]
    body = "".join(lines[start + 1:end])

    cleaned_items = normalize_abbrev_lines(body)
    table = "\n" + as_markdown_table(cleaned_items) + "\n"

    new_lines = []
    new_lines.extend(lines[: start + 1])
    new_lines.append(table)
    new_lines.extend(lines[end:])

    new_md = "".join(new_lines)

    if args.backup:
        path.with_suffix(path.suffix + ".bak").write_text(md, encoding="utf-8")

    path.write_text(new_md, encoding="utf-8")
    print(f"Cleaned {len(cleaned_items)} abbreviations in: {path}")

if __name__ == "__main__":
    main()