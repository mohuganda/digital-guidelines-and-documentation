from __future__ import annotations

import re
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

SOURCE_DIR = Path("odl_output/cleaned_split/split_chapters")
OUTPUT_DIR = Path("odl_output/review_fixed_split/split_chapters")
REPORT_FILE = Path("odl_output/review_fixed_split/review_fix_report.txt")

# Rows longer than this inside tables will be flagged for review
LONG_TABLE_ROW_THRESHOLD = 220


# ============================================================
# Helpers
# ============================================================

def write_report(lines: list[str]) -> None:
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def is_table_row(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|")


def is_table_separator(line: str) -> bool:
    stripped = line.strip()
    return bool(re.fullmatch(r"\|[\-\:\|\s]+\|", stripped))


# ============================================================
# Conservative cleanup functions
# ============================================================

def fix_weird_bullets(text: str) -> tuple[str, int]:
    """
    Replace common extracted bullet artifacts with normal markdown bullets.
    """
    count = 0

    patterns = [
        r"(?m)^\s*~\s+",
        r"(?m)^\s*\s*",
        r"(?m)^\s*\s*",
        r"(?m)^\s*\s*",
        r"(?m)^\s*\s*",
        r"(?m)^\s*◦\s*",
    ]

    for pattern in patterns:
        text, n = re.subn(pattern, "- ", text)
        count += n

    return text, count


def fix_nested_dash_bullets(text: str) -> tuple[str, int]:
    """
    Turn '- - item' into properly indented nested bullets.
    """
    text, count = re.subn(r"(?m)^- -\s+", "  - ", text)
    return text, count


def fix_inline_artifact_bullets(text: str) -> tuple[str, int]:
    """
    Replace inline odd bullet markers that appear inside sentences/table cells.
    Keeps this conservative.
    """
    count = 0

    replacements = [
        (r"\s+\s+", "<br>- "),
        (r"\s+\s+", "<br>- "),
        (r"\s+\s+", "<br>- "),
        (r"\s+\s+", "<br>- "),
    ]

    for pattern, repl in replacements:
        text, n = re.subn(pattern, repl, text)
        count += n

    return text, count


def fix_hyphenated_linebreaks(text: str) -> tuple[str, int]:
    """
    Join obvious PDF line-break hyphenations:
      hyperventila-
      tion
    -> hyperventilation

    Only does this when a line ends with a word fragment + hyphen
    and the next line starts with a lowercase continuation.
    """
    pattern = re.compile(r"([A-Za-z]{3,})-\n([a-z]{2,})")
    text, count = pattern.subn(r"\1\2", text)
    return text, count


def fix_split_units(text: str) -> tuple[str, int]:
    """
    Fix obvious unit breaks like:
      mg/kg/
      hour
    -> mg/kg/hour
    """
    patterns = [
        (r"mg/kg/\n\s*hour", "mg/kg/hour"),
        (r"ml/\n\s*hour", "ml/hour"),
        (r"L/\n\s*min", "L/min"),
        (r"l/\n\s*min", "l/min"),
        (r"SpO2\s*<\s*90%\n", "SpO2 <90% "),
    ]

    count = 0
    for pattern, repl in patterns:
        text, n = re.subn(pattern, repl, text, flags=re.IGNORECASE)
        count += n

    return text, count


def fix_management_glue(text: str) -> tuple[str, int]:
    """
    Separate headings accidentally glued to previous sentence endings.
    Example:
      ... disturbances (acidosis) Management
    """
    patterns = [
        (r"(\)\s+)Management\b", r"\1\n\n### Management"),
        (r"(\)\s+)Clinical features\b", r"\1\n\n### Clinical features"),
        (r"(\)\s+)Differential diagnosis\b", r"\1\n\n### Differential diagnosis"),
        (r"(\)\s+)Investigations\b", r"\1\n\n### Investigations"),
        (r"(\)\s+)Prevention\b", r"\1\n\n### Prevention"),
    ]

    count = 0
    for pattern, repl in patterns:
        text, n = re.subn(pattern, repl, text)
        count += n

    return text, count


def normalize_blank_lines(text: str) -> tuple[str, int]:
    text2 = re.sub(r"\n{4,}", "\n\n\n", text)
    return text2, 0 if text2 == text else 1


# ============================================================
# Review flagging
# ============================================================

def flag_long_table_rows(text: str) -> list[str]:
    findings: list[str] = []
    for i, line in enumerate(text.splitlines(), start=1):
        if is_table_row(line) and not is_table_separator(line):
            if len(line) > LONG_TABLE_ROW_THRESHOLD:
                findings.append(f"Line {i}: long table row ({len(line)} chars)")
    return findings


def flag_headerless_tables(text: str) -> list[str]:
    """
    Flag tables that start with content row before separator, where the first row
    looks like content rather than a real header.
    """
    findings: list[str] = []
    lines = text.splitlines()

    i = 0
    while i < len(lines) - 1:
        if is_table_row(lines[i]) and is_table_separator(lines[i + 1]):
            header = lines[i].strip()

            suspicious = False
            if re.search(r"<br>|- ", header):
                suspicious = True
            if len(header) > 120:
                suspicious = True
            if "TREATMENT" not in header and "LOC" not in header and "TYPE" not in header and "FEATURES" not in header:
                if re.search(r"\bmg\b|\bml\b|\bpoisoning\b|\bpatient\b", header, re.IGNORECASE):
                    suspicious = True

            if suspicious:
                findings.append(f"Line {i+1}: possible content row used as header")
            i += 2
        else:
            i += 1

    return findings


def flag_suspicious_words(text: str) -> list[str]:
    """
    Flag common OCR/extraction word issues but do not auto-fix aggressively.
    """
    patterns = [
        r"\btoxicn\b",
        r"\bismall\b",
        r"\boccursb\b",
        r"\bo\s?ccupational\b",
        r"\bunconciousness\b",
        r"\bMantain\b",
    ]
    findings: list[str] = []
    lines = text.splitlines()

    for i, line in enumerate(lines, start=1):
        for pattern in patterns:
            if re.search(pattern, line, flags=re.IGNORECASE):
                findings.append(f"Line {i}: suspicious wording -> {line.strip()}")
                break

    return findings


# ============================================================
# File processing
# ============================================================

def process_file(src: Path, dst: Path) -> tuple[dict[str, int], list[str]]:
    text = src.read_text(encoding="utf-8")

    stats: dict[str, int] = {}

    text, stats["weird_bullets_fixed"] = fix_weird_bullets(text)
    text, stats["nested_dash_bullets_fixed"] = fix_nested_dash_bullets(text)
    text, stats["inline_artifact_bullets_fixed"] = fix_inline_artifact_bullets(text)
    text, stats["hyphenated_linebreaks_fixed"] = fix_hyphenated_linebreaks(text)
    text, stats["split_units_fixed"] = fix_split_units(text)
    text, stats["management_glue_fixed"] = fix_management_glue(text)
    text, stats["blanklines_normalized"] = normalize_blank_lines(text)

    findings: list[str] = []
    findings.extend(flag_long_table_rows(text))
    findings.extend(flag_headerless_tables(text))
    findings.extend(flag_suspicious_words(text))

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text.strip() + "\n", encoding="utf-8")

    return stats, findings


# ============================================================
# Main
# ============================================================

def main() -> None:
    if not SOURCE_DIR.exists():
        raise FileNotFoundError(f"Source directory not found: {SOURCE_DIR}")

    report_lines: list[str] = []
    report_lines.append("Review Fix Report")
    report_lines.append("=" * 40)
    report_lines.append(f"Source: {SOURCE_DIR}")
    report_lines.append(f"Output: {OUTPUT_DIR}")
    report_lines.append("")

    total_files = 0
    total_findings = 0

    for src in sorted(SOURCE_DIR.rglob("*.md")):
        rel = src.relative_to(SOURCE_DIR)
        dst = OUTPUT_DIR / rel

        stats, findings = process_file(src, dst)
        total_files += 1
        total_findings += len(findings)

        stat_summary = ", ".join(f"{k}={v}" for k, v in stats.items() if v)
        if not stat_summary:
            stat_summary = "no automatic changes"

        report_lines.append(str(rel))
        report_lines.append(f"  changes: {stat_summary}")

        if findings:
            report_lines.append("  review flags:")
            for item in findings:
                report_lines.append(f"    - {item}")
        else:
            report_lines.append("  review flags: none")

        report_lines.append("")

    report_lines.append(f"Total files processed: {total_files}")
    report_lines.append(f"Total review flags: {total_findings}")

    write_report(report_lines)

    print("Done.")
    print(f"Output written to: {OUTPUT_DIR}")
    print(f"Report written to: {REPORT_FILE}")


if __name__ == "__main__":
    main()
