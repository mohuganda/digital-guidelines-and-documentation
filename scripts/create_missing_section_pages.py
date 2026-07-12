from pathlib import Path
import re

def read_file(path):
    p = Path(path)
    if not p.exists():
        return ""
    text = p.read_text(encoding="utf-8")

    # Remove YAML front matter if present
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                lines = lines[i + 1:]
                break

    text = "\n".join(lines).strip()

    # Remove only the first markdown heading from each fragment.
    # The merged page will add the correct section/subsection heading.
    lines = text.splitlines()
    cleaned = []
    removed = False
    for line in lines:
        if not removed and re.match(r"^\s*#{1,5}\s+", line):
            removed = True
            continue
        cleaned.append(line)

    text = "\n".join(cleaned).strip()
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text

def write_merged(output, chapter_title, section_title, items):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)

    if output.exists():
        backup = output.with_suffix(output.suffix + ".bak-before-section-merge")
        backup.write_text(output.read_text(encoding="utf-8"), encoding="utf-8")

    parts = [
        f"# {chapter_title}",
        "",
        f"## {section_title}",
        "",
    ]

    missing = []

    for title, file_path, level in items:
        p = Path(file_path)
        if not p.exists():
            missing.append(file_path)
            continue

        parts.append(f"{'#' * level} {title}")
        parts.append("")

        body = read_file(p)
        if body:
            parts.append(body)
            parts.append("")

    output.write_text("\n".join(parts).strip() + "\n", encoding="utf-8")

    print(f"Created: {output}")
    if missing:
        print("  Missing fragments:")
        for m in missing:
            print(f"   - {m}")

jobs = [
    {
        "output": "docs/chapters_split/02/2-01-bacterial-infections.md",
        "chapter": "Chapter 2: Infectious Diseases",
        "section": "2.1 BACTERIAL INFECTIONS",
        "items": [
            ("2.1.1 Anthrax", "docs/chapters_split/02/02-00-overview.md", 3),
            ("2.1.2 Brucellosis", "docs/chapters_split/02/2-01-02-brucellosis.md", 3),
            ("2.1.3 Diphtheria", "docs/chapters_split/02/2-01-03-diphtheria.md", 3),
            ("2.1.4 Leprosy/Hansens disease", "docs/chapters_split/02/2-01-04-leprosy-hansens-disease.md", 3),
            ("2.1.5 Meningitis", "docs/chapters_split/02/2-01-05-meningitis.md", 3),
            ("2.1.5.1 Neonatal Meningitis", "docs/chapters_split/02/2-01-05-01-neonatal-meningitis.md", 4),
            ("2.1.5.2 Cryptococcal Meningitis", "docs/chapters_split/02/2-01-05-02-cryptococcal-meningitis.md", 4),
            ("2.1.5.3 TB Meningitis", "docs/chapters_split/02/2-01-05-03-tb-meningitis.md", 4),
            ("2.1.6 Plague", "docs/chapters_split/02/2-01-06-plague.md", 3),
            ("2.1.7 Septicaemia", "docs/chapters_split/02/2-01-07-septicaemia.md", 3),
            ("2.1.7.1 Neonatal Septicaemia", "docs/chapters_split/02/2-01-07-01-neonatal-septicaemia.md", 4),
            ("2.1.7.2 Septic Shock Management, In Adults", "docs/chapters_split/02/2-01-07-02-septic-shock-management-in-adults.md", 4),
            ("2.1.8 Tetanus", "docs/chapters_split/02/2-01-08-tetanus.md", 3),
            ("2.1.8.1 Neonatal Tetanus", "docs/chapters_split/02/2-01-08-01-neonatal-tetanus.md", 4),
            ("2.1.9 Typhoid Fever (Enteric Fever)", "docs/chapters_split/02/2-01-09-typhoid-fever-enteric-fever.md", 3),
            ("2.1.10 Typhus Fever", "docs/chapters_split/02/2-01-10-typhus-fever.md", 3),
        ],
    },
    {
        "output": "docs/chapters_split/04/4-01-cardiovascular-conditions.md",
        "chapter": "Chapter 4: Cardiovascular Diseases",
        "section": "4.1 CARDIOVASCULAR CONDITIONS",
        "items": [
            ("4.1.1 Hypertension", "docs/chapters_split/04/04-00-overview.md", 3),
            ("4.1.2 Infective Endocarditis", "docs/chapters_split/04/4-01-02-infective-endocarditis.md", 3),
            ("4.1.3 Heart Failure", "docs/chapters_split/04/4-01-03-heart-failure.md", 3),
            ("4.1.4 Pulmonary Oedema", "docs/chapters_split/04/4-01-04-pulmonary-oedema.md", 3),
            ("4.1.5 Atrial Fibrillation", "docs/chapters_split/04/4-01-05-atrial-fibrillation.md", 3),
            ("4.1.6 Hypertension", "docs/chapters_split/04/4-01-06-hypertension.md", 3),
            ("4.1.6.1 Hypertensive Emergencies and urgency", "docs/chapters_split/04/4-01-06-01-hypertensive-emergencies-and-urgency.md", 4),
            ("4.1.8 Pericarditis", "docs/chapters_split/04/4-01-08-pericarditis.md", 3),
            ("4.1.11 Stroke", "docs/chapters_split/04/4-01-11-stroke.md", 3),
        ],
    },
    {
        "output": "docs/chapters_split/05/5-01-non-infectious-respiratory-diseases.md",
        "chapter": "Chapter 5: Respiratory Diseases",
        "section": "5.1 NON-INFECTIOUS RESPIRATORY DISEASES",
        "items": [
            ("5.1.1 Asthma", "docs/chapters_split/05/05-00-overview.md", 3),
            ("5.1.1.2 Chronic Asthma", "docs/chapters_split/05/5-01-01-02-chronic-asthma.md", 4),
        ],
    },
    {
        "output": "docs/chapters_split/06/6-01-gastrointestinal-emergencies.md",
        "chapter": "Chapter 6: Gastrointestinal and Hepatic Diseases",
        "section": "6.1 GASTROINTESTINAL EMERGENCIES",
        "items": [
            ("6.1.1 Acute Abdomen", "docs/chapters_split/06/06-00-overview.md", 3),
            ("6.1.2 Acute Pancreatitis", "docs/chapters_split/06/6-01-02-acute-pancreatitis.md", 3),
            ("6.1.3 Upper Gastrointestinal Bleeding", "docs/chapters_split/06/6-01-03-upper-gastrointestinal-bleeding.md", 3),
            ("6.1.4 Peritonitis", "docs/chapters_split/06/6-01-04-peritonitis.md", 3),
            ("6.1.5 Diarrhoea", "docs/chapters_split/06/6-01-05-diarrhoea.md", 3),
        ],
    },
    {
        "output": "docs/chapters_split/07/7-01-renal-diseases.md",
        "chapter": "Chapter 7: Renal and Urinary Diseases",
        "section": "7.1 RENAL DISEASES",
        "items": [
            ("7.1 Renal Diseases", "docs/chapters_split/07/07-00-overview.md", 3),
            ("7.1.4 Glomerulonephritis", "docs/chapters_split/07/7-01-04-glomerulonephritis.md", 3),
        ],
    },
    {
        "output": "docs/chapters_split/08/8-01-endocrine-and-metabolic-conditions.md",
        "chapter": "Chapter 8: Endocrine and Metabolic Diseases",
        "section": "8.1 ENDOCRINE AND METABOLIC CONDITIONS",
        "items": [
            ("8.1 Endocrine and Metabolic Conditions", "docs/chapters_split/08/08-00-overview.md", 3),
            ("8.1.5 Goitre", "docs/chapters_split/08/8-01-05-goitre.md", 3),
            ("8.1.6 Hyperthyroidism", "docs/chapters_split/08/8-01-06-hyperthyroidism.md", 3),
        ],
    },
    {
        "output": "docs/chapters_split/10/10-01-infectious-musculoskeletal-conditions.md",
        "chapter": "Chapter 10: Musculoskeletal and Joint Diseases",
        "section": "10.1 INFECTIOUS MUSCULOSKELETAL CONDITIONS",
        "items": [
            ("10.1 Infectious Musculoskeletal Conditions", "docs/chapters_split/10/10-00-overview.md", 3),
            ("10.1.2 Osteomyelitis ICD10 CODE: M86", "docs/chapters_split/10/10-01-02-osteomyelitis-icd10-code-m86.md", 3),
            ("10.1.3 Pyomyositis", "docs/chapters_split/10/10-01-03-pyomyositis.md", 3),
            ("10.1.4 Tuberculosis of the Spine (Potts Disease) ICD10 CODE:", "docs/chapters_split/10/10-01-04-tuberculosis-of-the-spine-potts-disease-icd10-code.md", 3),
        ],
    },
    {
        "output": "docs/chapters_split/11/11-01-blood-diseases.md",
        "chapter": "Chapter 11: Blood Diseases and Blood Transfusion Guidelines",
        "section": "11.1 BLOOD DISEASES",
        "items": [
            ("11.1 Blood Diseases", "docs/chapters_split/11/11-00-overview.md", 3),
            ("11.1.1.1 Iron Deficiency Anaemia ICD10 CODE: D50", "docs/chapters_split/11/11-01-01-01-iron-deficiency-anaemia-icd10-code-d50.md", 4),
            ("11.1.1.2 Megaloblastic Anaemia ICD10 CODE: D51-52", "docs/chapters_split/11/11-01-01-02-megaloblastic-anaemia-icd10-code-d51-52.md", 4),
            ("11.1.1.3 Normocytic Anaemia", "docs/chapters_split/11/11-01-01-03-normocytic-anaemia.md", 4),
            ("11.1.2 Bleeding Disorders", "docs/chapters_split/11/11-01-02-bleeding-disorders.md", 3),
            ("11.1.3 Sickle Cell Disease", "docs/chapters_split/11/11-01-03-sickle-cell-disease.md", 3),
        ],
    },
    {
        "output": "docs/chapters_split/12/12-01-cancer-recognition-and-risk.md",
        "chapter": "Chapter 12: Oncology",
        "section": "12.1 CANCER RECOGNITION AND RISK",
        "items": [
            ("12.1 Cancer Recognition and Risk", "docs/chapters_split/12/12-00-overview.md", 3),
            ("12.1.1 Special Groups at Increased Risk of Cancer", "docs/chapters_split/12/12-01-01-special-groups-at-increased-risk-of-cancer.md", 3),
            ("12.1.2 Early Signs and Symptoms", "docs/chapters_split/12/12-01-02-early-signs-and-symptoms.md", 3),
            ("12.1.2.1 Urgent Signs and Symptoms", "docs/chapters_split/12/12-01-02-01-urgent-signs-and-symptoms.md", 4),
        ],
    },
    {
        "output": "docs/chapters_split/14/14-01-gynaecological-conditions.md",
        "chapter": "Chapter 14: Gynaecological Conditions",
        "section": "14.1 GYNAECOLOGICAL CONDITIONS",
        "items": [
            ("14.1 Gynaecological Conditions", "docs/chapters_split/14/14-00-overview.md", 3),
            ("14.1.2 Pelvic Inflammatory Disease (PID) ICD10 CODE: N70-N73", "docs/chapters_split/14/14-01-02-pelvic-inflammatory-disease-pid-icd10-code-n70-n73.md", 3),
            ("14.1.3 Abnormal Uterine Bleeding ICD10 CODE: N39.9", "docs/chapters_split/14/14-01-03-abnormal-uterine-bleeding-icd10-code-n39-9.md", 3),
            ("14.1.4 Menopause", "docs/chapters_split/14/14-01-04-menopause.md", 3),
        ],
    },
    {
        "output": "docs/chapters_split/15/15-01-family-planning-service-provision.md",
        "chapter": "Chapter 15: Family Planning (FP)",
        "section": "15.1 FAMILY PLANNING SERVICE PROVISION",
        "items": [
            ("15.1 Family Planning Service Provision", "docs/chapters_split/15/15-00-overview.md", 3),
            ("15.1.1 Provide Information about FP including Pre-ConceptionCare to Different Groups", "docs/chapters_split/15/15-01-01-provide-information-about-fp-including-pre-conceptioncare-to-different-groups.md", 3),
            ("15.1.2 Counsel High-Risk Clients", "docs/chapters_split/15/15-01-02-counsel-high-risk-clients.md", 3),
            ("15.1.3 Pre-Conception Care with Clients Who Desire to Conceive", "docs/chapters_split/15/15-01-03-pre-conception-care-with-clients-who-desire-to-conceive.md", 3),
            ("15.1.4 Discuss with PLW HIV Special Consideration for HIV", "docs/chapters_split/15/15-01-04-discuss-with-plw-hiv-special-consideration-for-hiv.md", 3),
            ("15.1.5 Educate and Counsel Clients to Make Informed Choice of", "docs/chapters_split/15/15-01-05-educate-and-counsel-clients-to-make-informed-choice-of.md", 3),
            ("15.1.6 Obtain and Record Client History", "docs/chapters_split/15/15-01-06-obtain-and-record-client-history.md", 3),
            ("15.1.7 Perform a Physical Assessment", "docs/chapters_split/15/15-01-07-perform-a-physical-assessment.md", 3),
            ("15.1.8 Perform a Pelvic Examination", "docs/chapters_split/15/15-01-08-perform-a-pelvic-examination.md", 3),
            ("15.1.9 Manage Client for Chosen FP Method", "docs/chapters_split/15/15-01-09-manage-client-for-chosen-fp-method.md", 3),
            ("15.1.10 Summary of Medical Eligibility for Contraceptives", "docs/chapters_split/15/15-01-10-summary-of-medical-eligibility-for-contraceptives.md", 3),
        ],
    },
    {
        "output": "docs/chapters_split/16/16-01-antenatal-care.md",
        "chapter": "Chapter 16: Obstetric Conditions",
        "section": "16.1 ANTENATAL CARE",
        "items": [
            ("16.1 Antenatal Care", "docs/chapters_split/16/16-00-overview.md", 3),
            ("16.1.1 Goal-Oriented Antenatal Care Protocol", "docs/chapters_split/16/16-01-01-goal-oriented-antenatal-care-protocol.md", 3),
            ("16.1.2 Management of Common Complaints during Pregnancy", "docs/chapters_split/16/16-01-02-management-of-common-complaints-during-pregnancy.md", 3),
            ("16.1.3 High Risk Pregnancy (HRP)", "docs/chapters_split/16/16-01-03-high-risk-pregnancy-hrp.md", 3),
        ],
    },
    {
        "output": "docs/chapters_split/16/16-02-management-of-selected-conditions-in-pregnancy.md",
        "chapter": "Chapter 16: Obstetric Conditions",
        "section": "16.2 MANAGEMENT OF SELECTED CONDITIONS IN PREGNANCY",
        "items": [
            ("16.2 Management of Selected Conditions in Pregnancy", "docs/chapters_split/16/16-02-management-of-selected-conditions-in.md", 3),
            ("16.2.1 Anaemia in Pregnancy", "docs/chapters_split/16/16-02-01-anaemia-in-pregnancy.md", 3),
            ("16.2.2 Pregnancy and HIV Infection", "docs/chapters_split/16/16-02-02-pregnancy-and-hiv-infection.md", 3),
            ("16.2.2.2 Counselling for HIV Positive Mothers", "docs/chapters_split/16/16-02-02-02-counselling-for-hiv-positive-mothers.md", 4),
            ("16.2.3 Chronic Hypertension in Pregnancy", "docs/chapters_split/16/16-02-03-chronic-hypertension-in-pregnancy.md", 3),
            ("16.2.4 Malaria in Pregnancy", "docs/chapters_split/16/16-02-04-malaria-in-pregnancy.md", 3),
            ("16.2.5 Diabetes in Pregnancy", "docs/chapters_split/16/16-02-05-diabetes-in-pregnancy.md", 3),
        ],
    },
    {
        "output": "docs/chapters_split/16/16-07-intrauterine-fetal-demise-iufd-or-fetal-death.md",
        "chapter": "Chapter 16: Obstetric Conditions",
        "section": "16.7 INTRAUTERINE FETAL DEMISE (IUFD) OR FETAL DEATH",
        "items": [
            ("16.7 Intrauterine Fetal Demise (IUFD) or Fetal Death", "docs/chapters_split/16/16-07-intrauterine-fetal-demise-iufd-or-fetal.md", 3),
        ],
    },
    {
        "output": "docs/chapters_split/17/17-01-newborn-and-young-infant-assessment.md",
        "chapter": "Chapter 17: Childhood Illness",
        "section": "17.1 NEWBORN AND YOUNG INFANT ASSESSMENT",
        "items": [
            ("17.1 Newborn and Young Infant Assessment", "docs/chapters_split/17/17-00-overview.md", 3),
            ("17.1.2 Assess for Special Treatment Needs, Local Infection, and", "docs/chapters_split/17/17-01-02-assess-for-special-treatment-needs-local-infection-and.md", 3),
        ],
    },
    {
        "output": "docs/chapters_split/18/18-01-immunization-and-vaccination.md",
        "chapter": "Chapter 18: Immunization",
        "section": "18.1 IMMUNIZATION AND VACCINATION",
        "items": [
            ("18.1 Immunization and Vaccination", "docs/chapters_split/18/18-00-overview.md", 3),
            ("18.1.2 Hepatitis B Vaccination", "docs/chapters_split/18/18-01-02-hepatitis-b-vaccination.md", 3),
            ("18.1.3 Yellow Fever Vaccination", "docs/chapters_split/18/18-01-03-yellow-fever-vaccination.md", 3),
            ("18.1.4 Tetanus Prevention", "docs/chapters_split/18/18-01-04-tetanus-prevention.md", 3),
        ],
    },
    {
        "output": "docs/chapters_split/18/18-02-special-immunization-considerations.md",
        "chapter": "Chapter 18: Immunization",
        "section": "18.2 SPECIAL IMMUNIZATION CONSIDERATIONS",
        "items": [
            ("18.2 Special Immunization Considerations", "docs/chapters_split/18/18-02-03-01-prophylaxis-against-neonatal-tetanus.md", 3),
            ("18.2.4 Vaccination against COVID-19", "docs/chapters_split/18/18-02-04-vaccination-against-covid-19.md", 3),
        ],
    },
    {
        "output": "docs/chapters_split/19/19-01-nutrition-in-special-conditions.md",
        "chapter": "Chapter 19: Nutrition",
        "section": "19.1 NUTRITION IN SPECIAL CONDITIONS",
        "items": [
            ("19.1 Nutrition in Special Conditions", "docs/chapters_split/19/19-00-overview.md", 3),
            ("19.1.2 Nutrition in HIV/AIDS", "docs/chapters_split/19/19-01-02-nutrition-in-hiv-aids.md", 3),
            ("19.1.3 Nutrition in Diabetes", "docs/chapters_split/19/19-01-03-nutrition-in-diabetes.md", 3),
        ],
    },
    {
        "output": "docs/chapters_split/19/19-02-malnutrition.md",
        "chapter": "Chapter 19: Nutrition",
        "section": "19.2 MALNUTRITION",
        "items": [
            ("19.2 MALNUTRITION ICD10 CODE: E40-43", "docs/chapters_split/19/19-02-malnutrition-icd10-code-e40-43.md", 3),
            ("19.2.1 Introduction on Malnutrition", "docs/chapters_split/19/19-02-01-introduction-on-malnutrition.md", 3),
            ("19.2.1.1 Classification of Malnutrition", "docs/chapters_split/19/19-02-01-01-classification-of-malnutrition.md", 4),
            ("19.2.1.2 Assessing Malnutrition in Children 6 months to 5 years", "docs/chapters_split/19/19-02-01-02-assessing-malnutrition-in-children-6-months-to-5-years.md", 4),
            ("19.2.2 Management of Acute Malnutrition in Children", "docs/chapters_split/19/19-02-02-management-of-acute-malnutrition-in-children.md", 3),
            ("19.2.2.1 Management of Moderate Acute Malnutrition", "docs/chapters_split/19/19-02-02-01-management-of-moderate-acute-malnutrition.md", 4),
            ("19.2.2.2 Management of Uncomplicated Severe Acute", "docs/chapters_split/19/19-02-02-02-management-of-uncomplicated-severe-acute.md", 4),
            ("19.2.2.3 Management of Complicated Severe Acute Malnutrition", "docs/chapters_split/19/19-02-02-03-management-of-complicated-severe-acute-malnutrition.md", 4),
            ("19.2.2.4 Treatment of Associated Conditions", "docs/chapters_split/19/19-02-02-04-treatment-of-associated-conditions.md", 4),
            ("19.2.2.5 Discharge from Nutritional Programme", "docs/chapters_split/19/19-02-02-05-discharge-from-nutritional-programme.md", 4),
            ("19.2.3 SAM in Infants Less than 6 Months", "docs/chapters_split/19/19-02-03-sam-in-infants-less-than-6-months.md", 3),
            ("19.2.4 Obesity and Overweight", "docs/chapters_split/19/19-02-04-obesity-and-overweight.md", 3),
        ],
    },
    {
        "output": "docs/chapters_split/20/20-01-common-eye-conditions.md",
        "chapter": "Chapter 20: Eye Conditions",
        "section": "20.1 COMMON EYE CONDITIONS",
        "items": [
            ("20.1 Common Eye Conditions", "docs/chapters_split/20/20-00-overview.md", 3),
            ("20.1.4 Trachoma", "docs/chapters_split/20/20-01-04-trachoma.md", 3),
            ("20.1.5 Keratitis", "docs/chapters_split/20/20-01-05-keratitis.md", 3),
            ("20.1.6 Uveitis", "docs/chapters_split/20/20-01-06-uveitis.md", 3),
            ("20.1.7 Orbital Cellulitis", "docs/chapters_split/20/20-01-07-orbital-cellulitis.md", 3),
            ("20.1.8 Postoperative Endophthalmitis", "docs/chapters_split/20/20-01-08-postoperative-endophthalmitis.md", 3),
            ("20.1.9 Xerophthalmia", "docs/chapters_split/20/20-01-09-xerophthalmia.md", 3),
        ],
    },
    {
        "output": "docs/chapters_split/21/21-01-ear-conditions.md",
        "chapter": "Chapter 21: Ear, Nose and Throat Conditions",
        "section": "21.1 EAR CONDITIONS",
        "items": [
            ("21.1 Ear Conditions", "docs/chapters_split/21/21-00-overview.md", 3),
            ("21.1.2 Wax in the Ear", "docs/chapters_split/21/21-01-02-wax-in-the-ear.md", 3),
            ("21.1.3 Otitis External", "docs/chapters_split/21/21-01-03-otitis-external.md", 3),
            ("21.1.4 Otitis Media (Suppurative)", "docs/chapters_split/21/21-01-04-otitis-media-suppurative.md", 3),
            ("21.1.6 Mastoiditis", "docs/chapters_split/21/21-01-06-mastoiditis.md", 3),
        ],
    },
    {
        "output": "docs/chapters_split/22/22-01-bacterial-skin-infections.md",
        "chapter": "Chapter 22: Skin Diseases",
        "section": "22.1 BACTERIAL SKIN INFECTIONS",
        "items": [
            ("22.1 Bacterial Skin Infections", "docs/chapters_split/22/22-00-overview.md", 3),
            ("22.1.2 Boils (Furuncle)/Carbuncle", "docs/chapters_split/22/22-01-02-boils-furuncle-carbuncle.md", 3),
            ("22.1.3 Cellulitis and Erysipelas", "docs/chapters_split/22/22-01-03-cellulitis-and-erysipelas.md", 3),
        ],
    },
    {
        "output": "docs/chapters_split/23/23-01-oral-and-dental-assessment.md",
        "chapter": "Chapter 23: Oral and Dental Conditions",
        "section": "23.1 ORAL AND DENTAL ASSESSMENT",
        "items": [
            ("23.1 Oral and Dental Assessment", "docs/chapters_split/23/23-00-overview.md", 3),
        ],
    },
    {
        "output": "docs/chapters_split/24/24-01-surgery.md",
        "chapter": "Chapter 24: Surgery, Radiology and Anaesthesia",
        "section": "24.1 SURGERY",
        "items": [
            ("24.1 Surgery", "docs/chapters_split/24/24-00-overview.md", 3),
            ("24.1.2 Internal Haemorrhage", "docs/chapters_split/24/24-01-02-internal-haemorrhage.md", 3),
            ("24.1.3 Management of Medical Conditions in Surgical Patient", "docs/chapters_split/24/24-01-03-management-of-medical-conditions-in-surgical-patient.md", 3),
            ("24.1.4 Newborn with Surgical Emergencies", "docs/chapters_split/24/24-01-04-newborn-with-surgical-emergencies.md", 3),
            ("24.1.5 Surgical Antibiotic Prophylaxis", "docs/chapters_split/24/24-01-05-surgical-antibiotic-prophylaxis.md", 3),
            ("24.1.1.1 Techniques for Regional Anaesthesia", "docs/chapters_split/24/24-01-01-01-techniques-for-regional-anaesthesia.md", 4),
        ],
    },
]

for job in jobs:
    write_merged(job["output"], job["chapter"], job["section"], job["items"])

print("Done creating missing section-level pages.")
