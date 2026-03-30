from __future__ import annotations

import re
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

SOURCE_MD = Path("odl_output/UCG2023.md")
OUTPUT_BASE = Path("odl_output/staged_split")

EXTRACTED_DIR = OUTPUT_BASE / "extracted_chapters"
SPLIT_DIR = OUTPUT_BASE / "split_chapters"
REPORT_FILE = OUTPUT_BASE / "split_report.txt"


# ============================================================
# Helpers
# ============================================================

def slugify(text: str, max_words: int = 10, max_len: int = 80) -> str:
    """
    Convert a heading/title into a short filesystem-friendly slug.
    """
    text = text.lower()
    text = re.sub(r"icd10\s*code:?\s*", "", text, flags=re.IGNORECASE)
    text = re.split(
        r"\b(cause|causes|clinical features|management|investigations|differential diagnosis|prevention|note)\b",
        text,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")

    words = [w for w in text.split("-") if w]
    text = "-".join(words[:max_words])

    if len(text) > max_len:
        text = text[:max_len].rstrip("-")

    return text or "untitled"


def clean_title(raw: str) -> str:
    raw = re.sub(r"^[#\-\s]+", "", raw).strip()
    raw = re.sub(r"\s+", " ", raw)
    return raw


def clean_filename_title(raw: str) -> str:
    """
    Safer filename title cleanup for chapter files.
    """
    raw = clean_title(raw)
    raw = re.split(
        r"\b(icd10|cause|causes|clinical features|management|investigations|prevention|note)\b",
        raw,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0].strip()
    return raw


# ============================================================
# ODL chapter detection
# ============================================================

def find_odl_chapter_matches(text: str) -> list[re.Match[str]]:
    """
    Detect ODL chapter starts.

    Observed ODL patterns include:
      # Infectious Diseases2
      # Infectious Diseases 2
      # 2 Infectious Diseases
      # 2. Infectious Diseases
    """
    patterns = [
        r"(?m)^\s*#\s+(.+?)(\d{1,2})\s*$",            # Infectious Diseases2
        r"(?m)^\s*#\s+(.+?)\s+(\d{1,2})\s*$",        # Infectious Diseases 2
        r"(?m)^\s*#\s+(\d{1,2})[.\s]+(.+?)\s*$",     # 2 Infectious Diseases / 2. Infectious Diseases
    ]

    matches: list[re.Match[str]] = []
    seen_starts = set()

    for pattern in patterns:
        for m in re.finditer(pattern, text, flags=re.MULTILINE):
            if m.start() not in seen_starts:
                matches.append(m)
                seen_starts.add(m.start())

    matches.sort(key=lambda m: m.start())
    return matches


def parse_chapter_match(m: re.Match[str]) -> tuple[str, str]:
    """
    Return chapter number and chapter title from a detected ODL heading.
    """
    g1 = m.group(1).strip()
    g2 = m.group(2).strip()

    if g1.isdigit():
        chapter_number = g1
        chapter_title = g2
    elif g2.isdigit():
        chapter_number = g2
        chapter_title = g1
    else:
        raise ValueError(f"Could not parse chapter heading groups: {g1!r}, {g2!r}")

    return chapter_number, clean_title(chapter_title)


# ============================================================
# Chapter extraction
# ============================================================

def extract_chapters(text: str) -> list[tuple[str, str, str]]:
    """
    Extract top-level chapters from the full ODL markdown.

    Returns tuples of:
      (chapter_number, chapter_title, chapter_content)
    """
    matches = find_odl_chapter_matches(text)
    if not matches:
        raise ValueError("No chapter headings found in ODL markdown.")

    chapters: list[tuple[str, str, str]] = []

    for idx, match in enumerate(matches):
        chapter_number, chapter_title = parse_chapter_match(match)
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        chapter_content = text[start:end].strip()

        chapters.append((chapter_number, chapter_title, chapter_content))

    return chapters


def save_extracted_chapter(chapter_number: str, chapter_title: str, content: str) -> Path:
    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{chapter_number}-{slugify(clean_filename_title(chapter_title))}.md"
    out_path = EXTRACTED_DIR / filename
    out_path.write_text(content.strip() + "\n", encoding="utf-8")
    return out_path


# ============================================================
# Subchapter splitting
# ============================================================

def split_chapter_text(chapter_text: str, chapter_prefix: str) -> list[tuple[str, str]]:
    """
    Split a chapter into numbered subchapters.

    Handles messy ODL patterns like:
      2.1.1 Anthrax ICD10 CODE...
      ######## 1.3.5 Paracetamol Poisoning...
      - 1.3.11 Methyl Alcohol Poisoning...

    Returns empty list if no real numbered descendants are found.
    """
    pattern = re.compile(
        rf"(?m)^[#\-\s]*({re.escape(chapter_prefix)}\.\d+(?:\.\d+)*)\s+([^\n]+)$"
    )

    matches = list(pattern.finditer(chapter_text))
    if not matches:
        return []

    sections: list[tuple[str, str]] = []

    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(chapter_text)

        section_number = match.group(1).strip()
        section_title = clean_title(match.group(2))
        content = chapter_text[start:end].strip()

        if not content:
            continue

        filename = f"{section_number}-{slugify(section_title)}.md"
        sections.append((filename, content))

    return sections


def save_split_sections(chapter_number: str, sections: list[tuple[str, str]]) -> list[Path]:
    target_dir = SPLIT_DIR / chapter_number
    target_dir.mkdir(parents=True, exist_ok=True)

    saved_paths: list[Path] = []
    for filename, content in sections:
        out_path = target_dir / filename
        out_path.write_text(content.strip() + "\n", encoding="utf-8")
        saved_paths.append(out_path)

    return saved_paths


def save_whole_chapter(chapter_number: str, chapter_title: str, content: str) -> Path:
    target_dir = SPLIT_DIR / chapter_number
    target_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{chapter_number}-{slugify(clean_filename_title(chapter_title))}.md"
    out_path = target_dir / filename
    out_path.write_text(content.strip() + "\n", encoding="utf-8")
    return out_path


# ============================================================
# Reporting
# ============================================================

def write_report(lines: list[str]) -> None:
    OUTPUT_BASE.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ============================================================
# Main
# ============================================================

def main() -> None:
    if not SOURCE_MD.exists():
        raise FileNotFoundError(f"Source file not found: {SOURCE_MD}")

    text = SOURCE_MD.read_text(encoding="utf-8")

    OUTPUT_BASE.mkdir(parents=True, exist_ok=True)
    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
    SPLIT_DIR.mkdir(parents=True, exist_ok=True)

    report_lines: list[str] = []
    report_lines.append("ODL Extraction and Split Report")
    report_lines.append("=" * 40)

    chapters = extract_chapters(text)
    report_lines.append(f"Top-level chapters found: {len(chapters)}")
    report_lines.append("")

    for chapter_number, chapter_title, chapter_content in chapters:
        extracted_path = save_extracted_chapter(chapter_number, chapter_title, chapter_content)

        split_sections = split_chapter_text(chapter_content, chapter_number)

        report_lines.append(f"Chapter {chapter_number}: {chapter_title}")
        report_lines.append(f"  Extracted file: {extracted_path.name}")

        if split_sections:
            saved = save_split_sections(chapter_number, split_sections)
            report_lines.append(f"  Split subchapters: {len(saved)}")
            for p in saved:
                report_lines.append(f"    - {p.name}")
        else:
            whole_path = save_whole_chapter(chapter_number, chapter_title, chapter_content)
            report_lines.append("  Split subchapters: 0")
            report_lines.append(f"  Saved whole chapter: {whole_path.name}")

        report_lines.append("")

    write_report(report_lines)

    print("Done.")
    print(f"Extracted chapters folder: {EXTRACTED_DIR}")
    print(f"Split chapters folder: {SPLIT_DIR}")
    print(f"Report: {REPORT_FILE}")


if __name__ == "__main__":
    main()
