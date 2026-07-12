from pathlib import Path
import re

ROOT = Path("docs/chapters_split/01")

sections = {
    "1-01-common-emergencies.md": {
        "title": "1.1 COMMON EMERGENCIES",
        "files": [
            ("1.1.1 Anaphylactic Shock", "1-01-01-anaphylactic-shock.md", 3),
            ("1.1.2 Hypovolaemic Shock", "1-01-02-hypovolaemic-shock.md", 3),
            ("1.1.2.1 Hypovolaemic Shock in Children", "1-01-02-01-hypovolaemic-shock-in-children.md", 4),
            ("1.1.3 Dehydration", "1-01-03-dehydration.md", 3),
            ("1.1.3.1 Dehydration in Children under 5 years", "1-01-03-01-dehydration-in-children-under-5-years.md", 4),
            ("1.1.3.2 Dehydration in Older Children and Adults", "1-01-03-02-dehydration-in-older-children-and-adults.md", 4),
            ("1.1.4 Fluids and Electrolytes Imbalances", "1-01-04-fluids-and-electrolytes-imbalances.md", 3),
            ("1.1.4.1 IV Fluid management in children", "1-01-04-01-iv-fluid-management-in-children.md", 4),
            ("1.1.5 Febrile Convulsions", "1-01-05-febrile-convulsions.md", 3),
            ("1.1.6 Hypoglycaemia", "1-01-06-hypoglycaemia.md", 3),
        ],
    },
    "1-02-trauma-and-injuries.md": {
        "title": "1.2 TRAUMA AND INJURIES",
        "files": [
            ("1.2.1 Bites and Stings", "1-02-01-bites-and-stings.md", 3),
            ("1.2.1.1 Snakebites", "1-02-01-01-snakebites.md", 4),
            ("1.2.1.2 Insect Bites & Stings", "1-02-01-02-insect-bites-stings.md", 4),
            ("1.2.1.3 Animal and Human Bites", "1-02-01-03-animal-and-human-bites.md", 4),
            ("1.2.1.4 Rabies Post Exposure Prophylaxis", "1-02-01-04-rabies-post-exposure-prophylaxis.md", 4),
            ("1.2.1.5 Rabies Vaccine Schedules", "1-02-01-05-rabies-vaccine-schedules.md", 4),
            ("1.2.2 Fractures", "1-02-02-fractures.md", 3),
            ("1.2.3 Burns", "1-02-03-burns.md", 3),
            ("1.2.4 Wounds", "1-02-04-wounds.md", 3),
            ("1.2.5 Head Injuries", "1-02-05-head-injuries.md", 3),
            ("1.2.5.1 Traumatic Spinal Injury", "1-02-05-01-traumatic-spinal-injury.md", 4),
            ("1.2.6 Sexual Assault/Rape", "1-02-06-sexual-assault-rape.md", 3),
        ],
    },
    "1-03-poisoning.md": {
        "title": "1.3 POISONING",
        "files": [
            ("1.3.1 General Management of Poisoning ICD10 CODE: T36-T50", "1-03-01-general-management-of-poisoning-icd10-code-t36-t50.md", 3),
            ("1.3.1.2 Removal and Elimination of Ingested Poison", "1-03-01-02-removal-and-elimination-of-ingested-poison.md", 4),
            ("1.3.2 Acute Organophosphate Poisoning", "1-03-02-acute-organophosphate-poisoning.md", 3),
            ("1.3.3 Paraffin and Other Petroleum Products Poisoning ICD10", "1-03-03-paraffin-and-other-petroleum-products-poisoning-icd10.md", 3),
            ("1.3.4 Acetylsalicylic Acid (Aspirin) Poisoning", "1-03-04-acetylsalicylic-acid-aspirin-poisoning.md", 3),
            ("1.3.5 Paracetamol Poisoning", "1-03-05-paracetamol-poisoning.md", 3),
            ("1.3.6 Iron Poisoning", "1-03-06-iron-poisoning.md", 3),
            ("1.3.7 Carbon Monoxide Poisoning", "1-03-07-carbon-monoxide-poisoning.md", 3),
            ("1.3.8 Barbiturate Poisoning", "1-03-08-barbiturate-poisoning.md", 3),
            ("1.3.9 Opioid Poisoning ICD10 CODE: T40", "1-03-09-opioid-poisoning-icd10-code-t40.md", 3),
            ("1.3.10 Warfarin Poisoning", "1-03-10-warfarin-poisoning.md", 3),
            ("1.3.11 Methyl Alcohol (Methanol) Poisoning", "1-03-11-methyl-alcohol-methanol-poisoning.md", 3),
            ("1.3.12 Alcohol (Ethanol) Poisoning", "1-03-12-alcohol-ethanol-poisoning.md", 3),
            ("1.3.12.1 Acute Alcohol Poisoning", "1-03-12-01-acute-alcohol-poisoning.md", 4),
            ("1.3.12.2 Chronic Alcohol Poisoning", "1-03-12-02-chronic-alcohol-poisoning.md", 4),
            ("1.3.13 Food Poisoning", "1-03-13-food-poisoning.md", 3),
        ],
    },
    "1-04-hypoxaemia-management-and-oxygen-therapy-guidelines.md": {
        "title": "1.4 HYPOXAEMIA MANAGEMENT AND OXYGEN THERAPY GUIDELINES",
        "files": [
            ("1.4 HYPOXAEMIA MANAGEMENT AND OXYGEN THERAPY GUIDELINES", "1-04-hypoxeamia-management-and-oxygen-therapy-guidelines.md", 2),
        ],
    },
}

def clean_fragment(text: str) -> str:
    """
    Remove top-level page titles from fragment files so that the merged page controls heading levels.
    Keeps body content, tables, admonitions, and images.
    """
    lines = text.splitlines()

    # Remove YAML front matter if present.
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                lines = lines[i + 1:]
                break

    cleaned = []
    skipped_first_heading = False

    for line in lines:
        stripped = line.strip()

        # Drop first heading from each source file, because we add the correct heading during merge.
        if not skipped_first_heading and re.match(r"^#{1,4}\s+", stripped):
            skipped_first_heading = True
            continue

        cleaned.append(line)

    text = "\n".join(cleaned).strip()

    # Light cleanup: reduce excessive blank lines.
    text = re.sub(r"\n{4,}", "\n\n\n", text)

    return text

def write_section(output_name: str, section):
    output_path = ROOT / output_name
    backup_path = ROOT / f"{output_name}.bak-before-section-merge"

    if output_path.exists():
        backup_path.write_text(output_path.read_text(encoding="utf-8"), encoding="utf-8")

    parts = [
        "# Chapter 1: Emergencies and Trauma",
        "",
        f"## {section['title']}",
        "",
    ]

    missing = []

    for title, filename, level in section["files"]:
        source_path = ROOT / filename

        if not source_path.exists():
            missing.append(filename)
            continue

        heading_marks = "#" * level
        fragment = clean_fragment(source_path.read_text(encoding="utf-8"))

        parts.append(f"{heading_marks} {title}")
        parts.append("")

        if fragment:
            parts.append(fragment)
            parts.append("")

    output_path.write_text("\n".join(parts).strip() + "\n", encoding="utf-8")

    print(f"Created/updated: {output_path}")
    if missing:
        print("  Missing source files:")
        for m in missing:
            print(f"   - {m}")

for output_name, section in sections.items():
    write_section(output_name, section)

print("Done merging Chapter 1 section pages.")
