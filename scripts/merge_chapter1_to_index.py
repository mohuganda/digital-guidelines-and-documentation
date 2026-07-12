from pathlib import Path
import re

chapter_dir = Path("docs/chapters_split/01")
output = chapter_dir / "index.md"

sources = [
    chapter_dir / "index.md.bak-before-full-chapter-merge",
    chapter_dir / "1-01-common-emergencies.md",
    chapter_dir / "1-02-trauma-and-injuries.md",
    chapter_dir / "1-03-poisoning.md",
    chapter_dir / "1-04-hypoxaemia-management-and-oxygen-therapy-guidelines.md",
]

def strip_front_matter(text: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return "\n".join(lines[i + 1:]).strip()
    return text.strip()

def remove_duplicate_chapter_title(text: str) -> str:
    lines = text.splitlines()
    cleaned = []
    removed = False

    for line in lines:
        # Remove repeated chapter title headings from source fragments.
        if not removed and re.match(r"^\s*#\s+Chapter 1:\s+Emergencies and Trauma\s*$", line.strip(), re.I):
            removed = True
            continue
        cleaned.append(line)

    return "\n".join(cleaned).strip()

def normalize_heading_levels(text: str, is_landing: bool = False) -> str:
    lines = text.splitlines()
    out = []

    for line in lines:
        s = line.strip()

        # Remove repeated digital navigation note from section pages if present.
        # We only want the note from the chapter landing, not repeated throughout the full chapter page.
        if s.startswith('!!! note "Digital navigation note"') and not is_landing:
            out.append("<!-- removed repeated digital navigation note -->")
            continue

        # If section files start with # Chapter 1 and ## 1.x, keep only useful section/topic headings.
        # Convert any accidental H1 in section fragments into H2.
        if re.match(r"^#\s+1\.\d+\s+", s):
            out.append("## " + s[2:].strip())
            continue

        # Convert any accidental H2 for clinical topics into H3 only when it starts 1.x.x
        if re.match(r"^##\s+1\.\d+\.\d+\s+", s):
            out.append("### " + s[3:].strip())
            continue

        # Convert any accidental H3 for deeper clinical topics into H4 only when it starts 1.x.x.x
        if re.match(r"^###\s+1\.\d+\.\d+\.\d+\s+", s):
            out.append("#### " + s[4:].strip())
            continue

        out.append(line)

    return "\n".join(out).strip()

def demote_common_noise_headings(text: str) -> str:
    """
    Demote common clinical labels from headings to bold text.
    This helps prevent the right TOC from being overloaded.
    We can expand this list later after reviewing the chapter.
    """
    labels = {
        "Cause",
        "Causes",
        "Clinical features",
        "Investigations",
        "Investigation",
        "Differential diagnosis",
        "Management",
        "Treatment",
        "Prevention",
        "General management",
        "Supportive Treatment in Poisoning",
        "Criteria for referral for antivenom",
        "Antivenom",
        "Venom in eyes",
    }

    out = []
    for line in text.splitlines():
        s = line.strip()
        m = re.match(r"^(#{2,6})\s+(.+?)\s*$", s)
        if m:
            title = m.group(2).strip()
            if title in labels:
                out.append(f"**{title}**")
                continue
        out.append(line)

    return "\n".join(out).strip()

parts = []

landing = strip_front_matter(sources[0].read_text(encoding="utf-8"))
landing = remove_duplicate_chapter_title(landing)
landing = normalize_heading_levels(landing, is_landing=True)

parts.append(landing)

for src in sources[1:]:
    if not src.exists():
        print(f"Missing source: {src}")
        continue

    text = strip_front_matter(src.read_text(encoding="utf-8"))
    text = remove_duplicate_chapter_title(text)
    text = normalize_heading_levels(text, is_landing=False)
    text = demote_common_noise_headings(text)

    parts.append(text)

merged = "\n\n---\n\n".join(p.strip() for p in parts if p.strip())
merged = re.sub(r"\n{4,}", "\n\n\n", merged)

output.write_text(merged.strip() + "\n", encoding="utf-8")

print(f"Merged Chapter 1 into: {output}")
print("Backup used: docs/chapters_split/01/index.md.bak-before-full-chapter-merge")
