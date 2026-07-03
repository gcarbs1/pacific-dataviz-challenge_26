# Where the Rain Went

Static A4 art poster for the Pacific Dataviz Challenge 2026.

**Narrative.** The climate crisis is not only heating the Pacific — it is
redistributing its water. Comparing each territory's average annual rainfall
anomaly in 1979–2000 with 2020–2025, the far western Pacific (Micronesia,
Solomon Islands, Vanuatu, Palau) is getting markedly wetter, while a corridor
of atoll nations along the equator and the dateline (Nauru, Tuvalu, Kiribati,
Tokelau) and New Caledonia are drying out.

## The artwork — the rain compass

One circular artwork fills the page; narration lives in the sky corners and a
single quiet legend line sits at the foot — nothing is written over the art.

1. **The ring** is each territory's old balance — its average rain of
   1979–2000. The ocean lies inside the ring, the sky outside. The 22
   territories sit around it in west→east order (west at the top, clockwise),
   one equal sector each, every one wearing its simplified flag.
2. **Flag-drops** fall inward where rain increased (the drop has arrived in
   the ocean) and evaporate outward, faded and dash-outlined, where rain
   decreased. Distance from the ring + drop size = the shift in mm, measured
   against the radial ruler in the 12-o'clock gap.
3. **Barcode stems** — the nine largest shifts carry their full 47-year
   series: one tick per year (1979 at the ring → 2025 at the drop), tick
   width = that year's anomaly, colour = wet/dry year.
4. **Radial labels** read outward like compass spokes; a small compass with
   the W→E arrow sits at the centre. Record notes in the corners are computed
   from the data at build time (the build fails if a claim stops being true).

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
