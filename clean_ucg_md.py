from pathlib import Path
import re

CHAPTER_DIR = Path("docs/chapters")

# Lines that are only ~ or ~~ or ~~~ etc (allow spaces)
tilde_only = re.compile(r"^\s*~+\s*$")

# Also remove the stray "Uganda Clinical Guidelines 2023" footer/header line if it appears alone
ucg_footer = re.compile(r"^\s*Uganda Clinical Guidelines 2023\s*$")

def clean_file(p: Path) -> int:
    lines = p.read_text(errors="ignore").splitlines()
    out = []
    removed = 0

    for line in lines:
        if tilde_only.match(line):
            removed += 1
            continue
        if ucg_footer.match(line):
            removed += 1
            continue
        out.append(line)

    # collapse excessive blank lines (3+ -> 2)
    text = "\n".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
    p.write_text(text)
    return removed

total_removed = 0
count_files = 0

for p in sorted(CHAPTER_DIR.glob("*.md")):
    total_removed += clean_file(p)
    count_files += 1

print(f"Cleaned {count_files} chapter files. Removed {total_removed} junk lines.")
