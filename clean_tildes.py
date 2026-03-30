from __future__ import annotations

import os
import re

BASE_DIR = "docs/chapters_split"


def clean_file(path: str) -> bool:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # 1. Convert tilde separators / pseudo-bullets into markdown bullets
    # Example:
    #   "Causes ~ Fever ~ Cough"
    # becomes lines starting with "- "
    content = re.sub(r"\s*~\s*", "\n- ", content)

    # 2. Remove accidental extra blank lines before bullets
    content = re.sub(r"\n\s*\n\s*-", "\n- ", content)

    # 3. Ensure there is a blank line before bullet lists
    # This helps MkDocs render them as real lists instead of inline text
    content = re.sub(r"([^\n])\n(- )", r"\1\n\n\2", content)

    # 4. Clean repeated spaces
    content = re.sub(r"[ ]{2,}", " ", content)

    # 5. Remove empty bullet lines if any were created
    content = re.sub(r"\n- \n", "\n", content)

    # 6. Clean bullets that accidentally became attached to headings
    # Example: "### Causes\n- item" is okay
    # But this avoids weird leading spaces around bullets
    content = re.sub(r"\n[ \t]+- ", "\n- ", content)

    # 7. Normalize excessive blank lines to max two
    content = re.sub(r"\n{3,}", "\n\n", content)

    if content != original:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return True

    return False


def main() -> None:
    updated = 0

    for root, _, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith(".md"):
                path = os.path.join(root, file)
                if clean_file(path):
                    updated += 1

    print(f"✔ Cleaned files: {updated}")


if __name__ == "__main__":
    main()
