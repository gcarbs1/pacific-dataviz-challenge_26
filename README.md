# Pacific Dataviz Challenge 2026

## Overview

This project transforms official Pacific Data Hub time series into a reproducible visual story about changing rainfall across the Pacific. **Where the Rain Went** compares the average annual rainfall anomaly in the first twenty years of the record, 1979–1998, with the last twenty, 2006–2025, for 22 Pacific Island countries and territories.

The analysis collects climate, disaster-impact, and agricultural-yield indicators, preserves their lineage, validates the rainfall unit, and generates a static A4 poster for the Pacific Dataviz Challenge 2026.

## Structure

- `notebooks/`: ordered collection, exploration, and processing pipeline.
- `data/raw/`: original Pacific Data Hub files, excluded from version control.
- `data/processed/`: standardized datasets and quality manifest.
- `data/geo/`: Pacific coastline geometry used by the map.
- `scripts/`: deterministic poster generator and export helper.
- `index.html` and `html/`: GitHub Pages poster, styles, and export behavior.
- `viz/`: print-ready PDF and PNG outputs.

## Reproduction

Create the Python environment, run the three notebooks in order, and rebuild the poster:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/jupyter nbconvert --to notebook --execute --inplace notebooks/00-data_collection.ipynb
.venv/bin/jupyter nbconvert --to notebook --execute --inplace notebooks/01-data_exploration.ipynb
.venv/bin/jupyter nbconvert --to notebook --execute --inplace notebooks/02-data_processing.ipynb
.venv/bin/python scripts/build_a4.py
```

On macOS with Google Chrome installed, `scripts/export_pdf.sh` rebuilds the page and exports the A4 PDF and PNG.
