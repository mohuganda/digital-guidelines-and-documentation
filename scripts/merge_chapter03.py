from pathlib import Path

chapter_dir = Path("docs/chapters_split/03")
output_file = chapter_dir / "index.md"

# Files to merge in order.
# We exclude index.md because it is the output file.
# We also exclude index_landing_backup.md if already created.
files = sorted(
    [
        p for p in chapter_dir.glob("*.md")
        if p.name not in {"index.md", "index_landing_backup.md"}
    ],
    key=lambda p: p.name
)

merged = []

merged.append("# Chapter 3: HIV/AIDS and Sexually Transmitted Infections\n\n")

for file_path in files:
    text = file_path.read_text(encoding="utf-8")

    # Remove repeated chapter H1 from each split file
    text = text.replace("# Chapter 3: HIV/AIDS and Sexually Transmitted Infections", "").strip()

    # Add source marker as an HTML comment for traceability but not visible on page
    merged.append(f"\n\n<!-- Source: {file_path.name} -->\n\n")
    merged.append(text)
    merged.append("\n")

output_file.write_text("\n".join(merged).strip() + "\n", encoding="utf-8")

print(f"Merged {len(files)} files into {output_file}")
for p in files:
    print(f" - {p.name}")
