# Pacific Dataviz Challenge 2026

Data collection, exploration, and visual storytelling for the Pacific Dataviz
Challenge 2026. The current analysis focuses on climate anomalies, disaster
impacts, and agricultural yields across Pacific Island countries and
territories.

## Structure

- `notebooks/`: ordered notebooks for data collection and exploration.
- `data/raw/`: local source data downloaded from the Pacific Data Hub (ignored by Git).
- `data/processed/`: analysis-ready datasets versioned in the repository.
- `scripts/`: reproducible generators and export helpers.
- `viz/`: final visual outputs and their documentation.

## Setup

The project uses Python 3.12.

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

To work with the notebooks, select `.venv/bin/python` as the Jupyter kernel.

## Pipeline

Run the notebooks in order:

1. `00-data_collection.ipynb`
2. `01-data_exploration.ipynb`
3. `02-data_processing.ipynb`

The first notebook downloads and catalogs the selected datasets in `data/raw/`.
The second notebook explores the source tables. The third standardizes their
schemas, validates the observations, and materializes analysis-ready CSV files
in `data/processed/`.

## Poster

After running the processing notebook, rebuild the HTML poster with:

```sh
.venv/bin/python scripts/build_a4.py
```

On macOS with Google Chrome installed, rebuild and export the PDF and PNG with:

```sh
scripts/export_pdf.sh
```
