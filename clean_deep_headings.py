from pathlib import Path
import re

ROOT = Path("docs/chapters_split")

# Convert markdown headings with 4 or more # into bold labels.
# Example:
# #### Prevention  -> **Prevention**
# ######## Cause   -> **Cause**
#
# H1, H2, and H3 are left untouched.

heading_re = re.compile(r"^(#{4,})\s*(.+?)\s*$")

changed_files = []

for path in ROOT.rglob("*.md"):
    original = path.read_text(encoding="utf-8")
    lines = original.splitlines()
    new_lines = []

    for line in lines:
        match = heading_re.match(line)

        if match:
            text = match.group(2).strip()

            # Avoid wrapping already-bold text again
            if text.startswith("**") and text.endswith("**"):
                new_lines.append(text)
            else:
                new_lines.append(f"**{text}**")
        else:
            new_lines.append(line)

    updated = "\n".join(new_lines)

    if original.endswith("\n"):
        updated += "\n"

    if updated != original:
        path.write_text(updated, encoding="utf-8")
        changed_files.append(str(path))

print(f"Updated {len(changed_files)} files.")
for file_path in changed_files:
    print(file_path)
