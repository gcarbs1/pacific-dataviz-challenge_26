# Where the Rain Went

Static long-form visualization for the Pacific Dataviz Challenge 2026.

**Narrative.** The climate crisis is not only heating the Pacific — it is
redistributing its water. Comparing each territory's average annual rainfall
anomaly in 1979–2000 with 2020–2025, the far western Pacific (Micronesia,
Solomon Islands, Vanuatu, Palau) is getting markedly wetter, while a corridor
of atoll nations along the equator and the dateline (Nauru, Tuvalu, Kiribati,
Tokelau) and New Caledonia are drying out.

## Files

- `index.html` — the deliverable: a single self-contained long page (open in any browser).
- `where-the-rain-went.png` — high-resolution (2×) static export of the full page.
- `build_poster.py` — generates `index.html` from the raw data. No hand-edited numbers:
  every figure on the page is computed from the CSV.

## Data

`data/rainfall_anomalies/data.csv` — SPC Pacific Data Hub, dataflow
`DF_CLIMATE_CHANGE`, indicator `RAIN_ANOM` (annual rainfall anomalies, mm),
22 Pacific Island countries and territories, 1979–2025.

## Rebuild

```sh
venv/bin/python poster/build_poster.py
```

## Re-export the PNG

```sh
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --hide-scrollbars \
  --force-device-scale-factor=2 --window-size=1180,5910 \
  --screenshot=poster/where-the-rain-went.png \
  "file://$PWD/poster/index.html"
```
