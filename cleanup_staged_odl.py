from __future__ import annotations

import re
import shutil
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

SOURCE_BASE = Path("odl_output/staged_split")
SOURCE_SPLIT_DIR = SOURCE_BASE / "split_chapters"

OUTPUT_BASE = Path("odl_output/cleaned_split")
OUTPUT_SPLIT_DIR = OUTPUT_BASE / "split_chapters"
REPORT_FILE = OUTPUT_BASE / "cleanup_report.txt"


# ============================================================
# Helpers
# ============================================================

def slugify(text: str, max_words: int = 10, max_len: int = 80) -> str:
    """
    Make a safe short slug for filenames.
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


def write_report(lines: list[str]) -> None:
    OUTPUT_BASE.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ============================================================
# Filename cleanup
# ============================================================

def clean_filename(path: Path) -> str:
    """
    Keep numbering, but shorten polluted title tails safely.
    Example:
      1.3.2-acute-organophosphate-poisoning-t60-0-organophosphates-are-ingredients-of-some.md
    becomes:
      1.3.2-acute-organophosphate-poisoning-t60-0.md
    """
    stem = path.stem
    suffix = path.suffix

    m = re.match(r"^(\d+(?:\.\d+)*)-(.+)$", stem)
    if not m:
        return path.name

    number = m.group(1)
    title = m.group(2)

    title = re.split(
        r"\b(cause|causes|clinical-features|management|investigations|differential-diagnosis|prevention|note)\b",
        title,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]

    title = slugify(title)

    return f"{number}-{title}{suffix}"


# ============================================================
# Content cleanup
# ============================================================

def remove_banner_noise(text: str) -> tuple[str, int]:
    """
    Remove repeated page banner lines introduced by ODL.
    Conservative: only removes known noisy lines.
    """
    patterns = [
        r"(?mi)^\s*uganda clinical guidelines 2023chapter\s+\d+[:\s].*$",
        r"(?mi)^\s*-\s*uganda clinical guidelines 2023chapter\s+\d+[:\s].*$",
        r"(?mi)^\s*#+\s*uganda clinical guidelines 2023chapter\s+\d+[:\s].*$",
        r"(?mi)^\s*uganda clinical guidelines 2023\s*$",
        r"(?mi)^\s*chapter\s+\d+[:\s].*uganda clinical guidelines.*$",
    ]

    total_removed = 0
    for pattern in patterns:
        text, count = re.subn(pattern, "", text)
        total_removed += count

    return text, total_removed


def clean_heading_spacing(text: str) -> tuple[str, int]:
    """
    Fix obvious broken spacing inside headings only.
    Conservative and line-based.
    """
    count = 0
    lines = text.splitlines()
    cleaned: list[str] = []

    heading_pattern = re.compile(r"^\s*(#+|\d+(?:\.\d+)*\s+)")

    for line in lines:
        original = line

        if heading_pattern.match(line):
            # Fix broken internal spacing like "T rauma"
            line = re.sub(r"\b([A-Z])\s+([a-z]{2,})\b", r"\1\2", line)

            # Fix "H YPOXEAMIA" style rare splits if present
            line = re.sub(r"\b([A-Z])\s+([A-Z][a-z]+)\b", r"\1\2", line)

            # Collapse excess spaces
            line = re.sub(r"[ \t]{2,}", " ", line).rstrip()

        if line != original:
            count += 1

        cleaned.append(line)

    return "\n".join(cleaned), count


def remove_empty_hash_lines(text: str) -> tuple[str, int]:
    """
    Remove useless standalone heading markers like:
      #
      ####
    """
    text, count = re.subn(r"(?m)^\s*#{1,6}\s*$\n?", "", text)
    return text, count


def normalize_blank_lines(text: str) -> tuple[str, int]:
    """
    Keep spacing readable without compressing too hard.
    """
    original = text
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    count = 0 if text == original else 1
    return text, count


def clean_file_content(text: str) -> tuple[str, dict[str, int]]:
    """
    Run conservative cleanup steps.
    """
    stats: dict[str, int] = {}

    text, stats["banner_noise_removed"] = remove_banner_noise(text)
    text, stats["heading_spacing_fixed"] = clean_heading_spacing(text)
    text, stats["empty_hash_lines_removed"] = remove_empty_hash_lines(text)
    text, stats["blankline_normalized"] = normalize_blank_lines(text)

    # Final trim only, no paragraph surgery
    text = text.strip() + "\n"
    return text, stats


# ============================================================
# Main
# ============================================================

def main() -> None:
    if not SOURCE_SPLIT_DIR.exists():
        raise FileNotFoundError(f"Missing source split folder: {SOURCE_SPLIT_DIR}")

    if OUTPUT_BASE.exists():
        shutil.rmtree(OUTPUT_BASE)

    OUTPUT_SPLIT_DIR.mkdir(parents=True, exist_ok=True)

    report: list[str] = []
    report.append("Cleanup Report")
    report.append("=" * 40)
    report.append(f"Source: {SOURCE_SPLIT_DIR}")
    report.append(f"Output: {OUTPUT_SPLIT_DIR}")
    report.append("")

    total_files = 0
    renamed_files = 0

    for chapter_dir in sorted(SOURCE_SPLIT_DIR.iterdir()):
        if not chapter_dir.is_dir():
            continue

        out_chapter_dir = OUTPUT_SPLIT_DIR / chapter_dir.name
        out_chapter_dir.mkdir(parents=True, exist_ok=True)

        report.append(f"Chapter folder: {chapter_dir.name}")

        for md_file in sorted(chapter_dir.glob("*.md")):
            total_files += 1

            new_name = clean_filename(md_file)
            if new_name != md_file.name:
                renamed_files += 1

            out_path = out_chapter_dir / new_name

            text = md_file.read_text(encoding="utf-8")
            cleaned_text, stats = clean_file_content(text)
            out_path.write_text(cleaned_text, encoding="utf-8")

            stat_parts = ", ".join(f"{k}={v}" for k, v in stats.items() if v)
            if not stat_parts:
                stat_parts = "no visible cleanup needed"

            report.append(f"  {md_file.name} -> {new_name}")
            report.append(f"    {stat_parts}")

        report.append("")

    report.append(f"Total files processed: {total_files}")
    report.append(f"Files renamed: {renamed_files}")

    write_report(report)

    print("Done.")
    print(f"Cleaned split folder: {OUTPUT_SPLIT_DIR}")
    print(f"Cleanup report: {REPORT_FILE}")


if __name__ == "__main__":
    main()
