# Digital Guidelines Prototype – Uganda Clinical Guidelines (UCG) 2023

This repository contains a working prototype that converts the **Uganda Clinical Guidelines 2023** document into a searchable, web-based site using **MkDocs + Material theme**.

The prototype demonstrates a repeatable approach that can be applied to many other Ministry documents (PDFs and guideline manuals).

---

## What you get in this prototype

- Left navigation panel with **collapsible chapters and sub-sections**
- Full-text **search**
- “Next/Previous” navigation between pages
- A structure that can scale to hundreds of guideline documents

---

## Repository structure (important)

- `docs/`  
  MkDocs source content.
  - `docs/chapters/` – chapter-level pages (00–24)
  - `docs/chapters_split/` – sub-section pages generated automatically (recommended for navigation)

- `mkdocs.yml`  
  MkDocs configuration (theme, navigation, search, etc.)

- `split_ucg.py`  
  Script that:
  1) Splits the guideline into chapters  
  2) Splits each chapter into sub-sections (e.g., 1.2.1.1)  
  3) Rebuilds the `mkdocs.yml` navigation

---

## How to run locally (for developers)

### 1) Install dependencies
```bash
python3 -m pip install --user mkdocs mkdocs-material
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
