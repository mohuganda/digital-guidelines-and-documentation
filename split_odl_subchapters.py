from __future__ import annotations

import re
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

SOURCE_DIR = Path("odl_output/extracted_sections")
OUTPUT_DIR = Path("odl_output/split_subchapters")


# ============================================================
# Helpers
# ============================================================

def slugify(text: str, max_words: int = 10, max_len: int = 80) -> str:
    """
    Convert a section title into a short filesystem-friendly slug.
    Prevents extremely long filenames from messy ODL headings.
    """
    text = text.lower()

    # Remove ICD noise
    text = re.sub(r"icd10\s*code:?\s*", "", text, flags=re.IGNORECASE)

    # Stop at spillover keywords (ODL often merges paragraphs)
    text = re.split(
        r"\b(cause|causes|clinical features|management|investigations|differential diagnosis|prevention|note)\b",
        text,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]

    # Clean characters
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")

    # Limit words
    words = [w for w in text.split("-") if w]
    text = "-".join(words[:max_words])

    # Limit total length
    if len(text) > max_len:
        text = text[:max_len].rstrip("-")

    return text or "untitled"


def clean_title(raw: str) -> str:
    """
    Clean title text captured from ODL headings.
    """
    raw = re.sub(r"^[#\-\s]+", "", raw).strip()
    raw = re.sub(r"\s+", " ", raw)
    return raw


def split_chapter_text(chapter_text: str, chapter_prefix: str) -> list[tuple[str, str]]:
    """
    Split a chapter into subchapters using robust heading detection.

    Handles messy ODL formats like:
      1.3.2 Acute Organophosphate Poisoning ICD10 CODE: T60.0
      ######## 1.3.5 Paracetamol Poisoning ICD10 CODE: T39.1
      - 1.3.11 Methyl Alcohol Poisoning

    Important:
    - Captures ONLY one line for title (prevents paragraph overflow)
    - Returns empty list if no valid subchapters (e.g. 1.4)
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


def save_sections(sections: list[tuple[str, str]], subdir: str) -> None:
    """
    Save split subchapter files.
    """
    target_dir = OUTPUT_DIR / subdir
    target_dir.mkdir(parents=True, exist_ok=True)

    for filename, content in sections:
        out_path = target_dir / filename
        out_path.write_text(content.strip() + "\n", encoding="utf-8")
        print(f"Saved: {out_path}")


def save_whole_chapter(subdir: str, filename: str, content: str) -> None:
    """
    Save chapter as-is (used for 1.4 and similar cases).
    """
    target_dir = OUTPUT_DIR / subdir
    target_dir.mkdir(parents=True, exist_ok=True)

    out_path = target_dir / filename
    out_path.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"Saved whole chapter: {out_path}")


# ============================================================
# Main logic
# ============================================================

def main() -> None:
    poisoning_file = SOURCE_DIR / "1.3-poisoning.md"
    hypox_file = SOURCE_DIR / "1.4-hypoxeamia-management-and-oxygen-therapy-guidelines.md"

    if not poisoning_file.exists():
        raise FileNotFoundError(f"Missing file: {poisoning_file}")

    if not hypox_file.exists():
        raise FileNotFoundError(f"Missing file: {hypox_file}")

    poisoning_text = poisoning_file.read_text(encoding="utf-8")
    hypox_text = hypox_file.read_text(encoding="utf-8")

    # Split 1.3
    poisoning_sections = split_chapter_text(poisoning_text, "1.3")

    # Split 1.4 (may return empty)
    hypox_sections = split_chapter_text(hypox_text, "1.4")

    if poisoning_sections:
        save_sections(poisoning_sections, "1.3")
    else:
        save_whole_chapter("1.3", "1.3-poisoning.md", poisoning_text)

    if hypox_sections:
        save_sections(hypox_sections, "1.4")
    else:
        save_whole_chapter(
            "1.4",
            "1.4-hypoxeamia-management-and-oxygen-therapy-guidelines.md",
            hypox_text,
        )

    print("\nDone.")
    print(f"1.3 subchapters: {len(poisoning_sections)}")
    print(f"1.4 subchapters: {len(hypox_sections)}")


if __name__ == "__main__":
    main()
