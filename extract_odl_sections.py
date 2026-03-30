from __future__ import annotations

import re
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

SOURCE_MD = Path("odl_output/UCG2023.md")
OUTPUT_DIR = Path("odl_output/extracted_sections")


# ============================================================
# Helpers
# ============================================================

def find_match(text: str, patterns: list[str], label: str) -> re.Match[str]:
    """
    Try several regex patterns and return the first successful match.
    This is useful because ODL headings are not always perfectly uniform.
    """
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        if match:
            print(f"Matched {label} with pattern: {pattern}")
            return match

    raise ValueError(
        f"Could not find {label} using any of these patterns:\n" +
        "\n".join(patterns)
    )


def save_output(filename: str, content: str) -> None:
    """
    Save extracted chapter text to the target output directory.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / filename
    out_path.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"Saved: {out_path}")


# ============================================================
# Main extraction logic
# ============================================================

def main() -> None:
    if not SOURCE_MD.exists():
        raise FileNotFoundError(f"Source file not found: {SOURCE_MD}")

    text = SOURCE_MD.read_text(encoding="utf-8")

    # --------------------------------------------------------
    # Start of chapter 1.3
    # We match the exact poisoning heading from the ODL output.
    # --------------------------------------------------------
    ch13_start = find_match(
        text,
        [
            r"(?m)^\s*1\.3\s+POISONING\b",
            r"(?m)^\s*#{0,6}\s*1\.3\s+POISONING\b",
        ],
        "start of chapter 1.3",
    )

    # --------------------------------------------------------
    # Start of chapter 1.4
    # ODL may preserve this as a plain line or as a markdown heading.
    # --------------------------------------------------------
    ch14_start = find_match(
        text,
        [
            r"(?m)^\s*#{0,6}\s*1\.4\s+HYPOXEAMIA\s+MANAGEMENT\s+AND\s+OXYGEN\s+THERAPY\s+GUIDELINES\b",
            r"(?m)^\s*1\.4\s+HYPOXEAMIA\s+MANAGEMENT\s+AND\s+OXYGEN\s+THERAPY\s+GUIDELINES\b",
            r"(?m)^\s*#{0,6}\s*1\.4\b.*HYPOXEAMIA.*OXYGEN.*THERAPY\b",
        ],
        "start of chapter 1.4",
    )

    # --------------------------------------------------------
    # Start of chapter 2
    # ODL chapter starts appear to use a single #, for example:
    #   # Infectious Diseases2
    # We therefore stop chapter 1.4 at the first matching chapter 2 heading.
    # --------------------------------------------------------
    ch2_start = find_match(
        text,
        [
            r"(?m)^\s*#\s*Infectious\s+Diseases2\b",
            r"(?m)^\s*#\s*Infectious\s+Diseases\s*2\b",
            r"(?m)^\s*#\s*Infectious\s+Diseases\b",
        ],
        "start of chapter 2",
    )

    # --------------------------------------------------------
    # Extract content ranges
    # --------------------------------------------------------
    chapter_13 = text[ch13_start.start():ch14_start.start()]
    chapter_14 = text[ch14_start.start():ch2_start.start()]

    # --------------------------------------------------------
    # Save extracted chapters
    # --------------------------------------------------------
    save_output("1.3-poisoning.md", chapter_13)
    save_output("1.4-hypoxeamia-management-and-oxygen-therapy-guidelines.md", chapter_14)

    print("\nExtraction complete.")
    print("Output files:")
    print(" - 1.3-poisoning.md")
    print(" - 1.4-hypoxeamia-management-and-oxygen-therapy-guidelines.md")


if __name__ == "__main__":
    main()
