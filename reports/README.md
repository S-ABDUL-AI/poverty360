# Annual reports

## Published downloads (premium)

The site links to these files from the Foundation Years timeline:

- `2019-annual-report.pdf`
- `2020-annual-report.pdf`
- `2021-annual-report.pdf`

They are **McKinsey-style memoranda** generated from the same verified figures shown on [Poverty 360](https://s-abdul-ai.github.io/poverty360/): dark cover, executive summary, financial snapshot table, programme narrative, KPI grid, and Risk · Implication · Action cards, plus footers on each body page.

### Regenerate after editing copy

```bash
cd reports
pip install -r requirements.txt
python build_premium_reports.py
```

That overwrites the three `*-annual-report.pdf` files in this folder.

### Legacy uploads

If you previously dropped `2019.pdf`, `2020.pdf`, or `2021.pdf` here, the build script moves them once into `archive/legacy_uploads/` before writing the new premium PDFs. They are **not** merged into the new files (the old exports were mostly image-heavy and inconsistent with the new template).

### Optional: merge legacy detail pages

If you need the old PDF appendices back, open `archive/legacy_uploads/*.pdf` in Acrobat (or similar), copy the pages you want, and append them after the generated memorandum.
