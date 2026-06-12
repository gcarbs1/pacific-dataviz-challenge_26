# Where the Rain Went

Static long-form visualization for the Pacific Dataviz Challenge 2026.

**Narrative.** The climate crisis is not only heating the Pacific — it is
redistributing its water. Comparing each territory's average annual rainfall
anomaly in 1979–2000 with 2020–2025, the far western Pacific (Micronesia,
Solomon Islands, Vanuatu, Palau) is getting markedly wetter, while a corridor
of atoll nations along the equator and the dateline (Nauru, Tuvalu, Kiribati,
Tokelau) and New Caledonia are drying out.

## Files

### A4 art poster (main deliverable)
- `a4.html` — single A4 page, light background: one artwork where flag-drops fall
  below "the old balance" line for territories gaining rain (west) and fade upward
  where rain is being lost (central corridor). x = geography (west→east),
  drop size + distance from the line = size of the shift.
- `where-the-rain-went-a4.png` — print-ready export (1680×2376, A4 ratio).
- `build_a4.py` — generates `a4.html` from the raw data.

### Long-form exploratory page
- `index.html` — self-contained long page (map, slope chart, per-island rain gauges).
- `where-the-rain-went.png` — high-resolution (2×) static export of the full page.
- `build_poster.py` — generates `index.html` from the raw data.

No hand-edited numbers in either: every figure is computed from the CSV.

## Data

`data/rainfall_anomalies/data.csv` — SPC Pacific Data Hub, dataflow
`DF_CLIMATE_CHANGE`, indicator `RAIN_ANOM` (annual rainfall anomalies, mm),
22 Pacific Island countries and territories, 1979–2025.

## Rebuild

```sh
venv/bin/python poster/build_a4.py      # A4 poster
venv/bin/python poster/build_poster.py  # long page
```

## Re-export the PNGs

```sh
# A4 poster (crop removes the 24px body padding, scaled 2x)
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --hide-scrollbars \
  --force-device-scale-factor=2 --window-size=840,1236 \
  --screenshot=/tmp/a4_2x.png "file://$PWD/poster/a4.html"
venv/bin/python -c "from PIL import Image; Image.open('/tmp/a4_2x.png').crop((0,48,1680,2424)).save('poster/where-the-rain-went-a4.png')"

# long page
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --hide-scrollbars \
  --force-device-scale-factor=2 --window-size=1180,5910 \
  --screenshot=poster/where-the-rain-went.png \
  "file://$PWD/poster/index.html"
```
