# Where the Rain Went

Static A4 art poster for the Pacific Dataviz Challenge 2026.

**Narrative.** The climate crisis is not only heating the Pacific — it is
redistributing its water. Comparing each territory's average annual rainfall
anomaly in 1979–2000 with 2020–2025, the far western Pacific (Micronesia,
Solomon Islands, Vanuatu, Palau) is getting markedly wetter, while a corridor
of atoll nations along the equator and the dateline (Nauru, Tuvalu, Kiribati,
Tokelau) and New Caledonia are drying out.

## The artwork, layer by layer

One artwork fills the page; legend, record notes and credits are arranged
below it — nothing is written over the art.

1. **Flag-drops** — territories sit at their real west→east order. Drops fall
   below "the old balance" line where rain increased; faded drops evaporate
   upward where it decreased. Distance from the line + drop size = the shift
   (mm), measured against the ruler on the left margin.
2. **Barcode stems** — each highlighted stem is the full 47-year series:
   one tick per year (1979 at the line → 2025 at the drop), tick width = that
   year's anomaly, colour = wet/dry year.
3. **Record notes** — computed from the data at build time (the build fails
   if a claim stops being true), set below the sea next to the legend.

## Files

- `a4.html` — the poster (open in any browser; prints clean on A4).
- `where-the-rain-went-a4.png` — print-ready export (1680×2376, A4 ratio).
- `build_a4.py` — generates `a4.html` from the raw data. No hand-edited
  numbers: every figure on the page is computed from the CSV.

## Data

`data/rainfall_anomalies/data.csv` — SPC Pacific Data Hub, dataflow
`DF_CLIMATE_CHANGE`, indicator `RAIN_ANOM` (annual rainfall anomalies, mm),
22 Pacific Island countries and territories, 1979–2025.

## Rebuild & export

```sh
venv/bin/python poster/build_a4.py

"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --hide-scrollbars \
  --force-device-scale-factor=2 --window-size=840,1236 \
  --screenshot=/tmp/a4_2x.png "file://$PWD/poster/a4.html"
venv/bin/python -c "from PIL import Image; Image.open('/tmp/a4_2x.png').crop((0,48,1680,2424)).save('poster/where-the-rain-went-a4.png')"
```
