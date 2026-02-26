import re
import unicodedata
from pathlib import Path

# ----------------------------
# Settings
# ----------------------------
BASE_DIR = Path("docs/chapters")          # where your 00-front-matter.md and 01-.. 24-.. live
OUT_DIR  = Path("docs/chapters_split")    # new output location (safer than overwriting)
OUT_DIR.mkdir(parents=True, exist_ok=True)

# If True: drop lines that are only "~" or only "x" etc.
CLEAN_ARTIFACT_LINES = True

# Recognize subchapter patterns like:
# 1.1   1.1.1   18.2.4   10.3.12
SUB_RE = re.compile(r"^\s*((?:\d{1,2}\.)+\d{1,2})\s+(.+?)\s*$")

CHAPTER_TITLE_RE = re.compile(r"(?im)^\s*#\s*Chapter\s+(\d{1,2})\s*:\s*(.+?)\s*$")

def slugify(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:80] if s else "section"

def clean_lines(text: str) -> str:
    if not CLEAN_ARTIFACT_LINES:
        return text
    out = []
    for line in text.splitlines():
        stripped = line.strip()
        # drop single-character noise lines (very common from pdf2text tables/layout)
        if stripped in {"~", "x", "X", "•"}:
            continue
        # drop lines that are ONLY repeated tildes/x (like "~~~~" or "xxx")
        if re.fullmatch(r"[~]+", stripped):
            continue
        if re.fullmatch(r"[xX]+", stripped):
            continue
        out.append(line)
    # reduce excessive blank lines
    cleaned = "\n".join(out)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip() + "\n"

def write_md(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(clean_lines(content), encoding="utf-8")

def parse_chapter_num_and_title(chapter_text: str):
    m = CHAPTER_TITLE_RE.search(chapter_text)
    if not m:
        return None, None
    return int(m.group(1)), m.group(2).strip()

def split_into_sections(chap_no: int, chap_title: str, chap_text: str):
    """
    Returns a list of sections:
    [
      {"id":"18", "title":"Overview", "md":"..."},
      {"id":"18.2", "title":"Something", "md":"..."},
      {"id":"18.2.4", "title":"Something", "md":"..."},
      ...
    ]
    We split on lines like "18.2.4 Vaccination against COVID-19"
    """
    lines = chap_text.splitlines()

    # find all subheading lines
    hits = []
    for i, line in enumerate(lines):
        m = SUB_RE.match(line)
        if not m:
            continue
        sec_id = m.group(1)     # e.g., 18.2.4
        title  = m.group(2)     # remainder
        title = title.encode("ascii", "ignore").decode("ascii")
        # only accept if it belongs to this chapter (starts with f"{chap_no}.")
        if not sec_id.startswith(f"{chap_no}."):
            continue
        hits.append((i, sec_id, title))

    sections = []

    # Always create an "Overview" section: from start to first hit (or whole file)
    if hits:
        overview_block = "\n".join(lines[:hits[0][0]]).strip()
    else:
        overview_block = "\n".join(lines).strip()

    # Ensure Overview has a proper heading
    overview_md = f"# Chapter {chap_no}: {chap_title}\n\n"
    if overview_block:
        # remove duplicate top H1 if present
        overview_block = re.sub(r"(?im)^\s*#\s*Chapter\s+\d{1,2}\s*:\s*.+?\s*$", "", overview_block).strip()
        overview_md += overview_block + "\n"
    sections.append({"id": f"{chap_no}", "title": "Overview", "md": overview_md})

    # Now split each found section
    for idx, (line_idx, sec_id, sec_title) in enumerate(hits):
        start = line_idx
        end = hits[idx + 1][0] if idx < len(hits) - 1 else len(lines)
        block = "\n".join(lines[start:end]).strip()

        # Replace the raw "18.2.4 Title" line with a Markdown heading
        block_lines = block.splitlines()
        if block_lines:
            first = block_lines[0]
            m = SUB_RE.match(first)
            if m:
                new_h = f"## {sec_id} {sec_title}"
                block_lines[0] = new_h
                block = "\n".join(block_lines)

        # Prepend chapter title context lightly (optional)
        md = f"# Chapter {chap_no}: {chap_title}\n\n{block}\n"
        sections.append({"id": sec_id, "title": sec_title, "md": md})

    return sections

def section_filename(chap_no: int, sec_id: str, title: str):
    """
    Create stable filenames like:
    docs/chapters_split/chapters_split/18/18-02-04-vaccination-against-covid-19.md
    """
    if sec_id == f"{chap_no}":
        return Path(f"{chap_no:02d}") / f"{chap_no:02d}-00-overview.md"
    parts = sec_id.split(".")  # ["18","2","4"]
    # Pad each part except chapter to 2 digits
    padded = [parts[0]] + [p.zfill(2) for p in parts[1:]]
    # build like 18-02-04
    stem = "-".join(padded)
    return Path(f"{chap_no:02d}") / f"{stem}-{slugify(title)}.md"

def main():
    # Read current chapter files (00-front-matter + 01..24)
    chapter_files = sorted(BASE_DIR.glob("*.md"))

    # Identify front matter (00-...)
    front_file = next((p for p in chapter_files if p.name.startswith("00-")), None)

    # Load chapters 1..24 files
    numbered = [p for p in chapter_files if re.match(r"^\d{2}-", p.name)]
    numbered = sorted(numbered)

    # Build nav structure
    nav = []
    # Home -> front matter if exists
    if front_file and front_file.exists():
        # Copy front matter as-is into OUT_DIR root
        fm_out = OUT_DIR / "00-front-matter.md"
        write_md(fm_out, front_file.read_text(errors="ignore"))
        nav.append("  - Home: chapters_split/00-front-matter.md")
    else:
        nav.append(f"  - Home: {numbered[0].as_posix().replace('docs/chapters/','') if numbered else 'index.md'}")

    nav.append("  - UCG 2023:")

    # Add front matter into UCG 2023 menu
    if front_file and front_file.exists():
        nav.append("      - Front matter: chapters_split/00-front-matter.md")

    # Process each chapter file
    for chap_path in numbered:
        chap_text = chap_path.read_text(errors="ignore")
        chap_no, chap_title = parse_chapter_num_and_title(chap_text)

        # If the file doesn't have "# Chapter N: Title" we fallback from filename
        if chap_no is None:
            m = re.match(r"^(\d{2})-(.+)\.md$", chap_path.name)
            chap_no = int(m.group(1)) if m else 0
            chap_title = (m.group(2).replace("-", " ").title() if m else chap_path.stem)

        sections = split_into_sections(chap_no, chap_title, chap_text)

        # Write sections + build nav for this chapter
        chap_group_label = f"Chapter {chap_no}: {chap_title}"
        safe_chap = chap_group_label.replace('"', "'")
        nav.append(f'      - "{safe_chap}":')

        # For each section create file and nav line
        for sec in sections:
            out_rel = section_filename(chap_no, sec["id"], sec["title"])
            out_path = OUT_DIR / out_rel
            write_md(out_path, sec["md"])

            # Nav label
            if sec["id"] == f"{chap_no}":
                label = "Overview"
            else:
                # show like "18.2.4 Vaccination against COVID-19"
                label = f'{sec["id"]} {sec["title"]}'
            safe_label = label.replace('"', "'")
            nav.append(f'          - "{safe_label}": chapters_split/{out_rel.as_posix()}')

    # Rewrite mkdocs.yml cleanly (site config + nav)
    mkdocs_content = f"""site_name: Uganda Clinical Guidelines 2023
site_description: Ministry of Health - Uganda Clinical Guidelines 2023 (Web version)

theme:
  name: material
  features:
    - navigation.sections
    - navigation.expand
    - navigation.top
    - navigation.footer
    - toc.follow
    - search.suggest
    - search.highlight

markdown_extensions:
  - attr_list
  - toc:
      permalink: true

nav:
{chr(10).join(nav)}
"""
    Path("mkdocs.yml").write_text(mkdocs_content, encoding="utf-8")

    print(f"Done. Wrote split content to: {OUT_DIR}")
    print("Updated mkdocs.yml navigation to use the split files.")
    print("Next: run `mkdocs serve` and browse.")

if __name__ == "__main__":
    main()