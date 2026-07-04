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
2. **The ocean** — engraved water: dozens of hairline contour rings over a
   soft depth gradient, like the line-work of an etching; each territory sits
   at a gently hand-jittered angle so the compass breathes instead of ticking
   like a clock.
3. **Flag-drops** rendered as glass — a specular pair lit by the page's one
   sun (top-right), inner shading, a soft cast shadow on the water — fall
   inward where rain increased (the drop has arrived in the ocean) and
   evaporate outward, faded behind a warm solid outline, where rain
   decreased. Distance from the ring + drop size = the shift in mm,
   measured against the radial ruler in the 12-o'clock gap.
4. **Threads** — every drop hangs from its berth on the ring by a fine
   thread: solid for the nine largest shifts, dotted for the rest; blue
   threads reach down into the ocean, warm ones rise into the sky.
5. **Radial labels** read outward like compass spokes, one uniform two-line
   format for all 22 territories — country name, shift beneath it — placed
   past the drop so no text is ever written over the artwork. A small
   compass with the W→E arrow sits at the centre. Record notes in the
   corners are computed from the data at build time (the build fails if a
   claim stops being true).

## Files

- `a4.html` — the poster (open in any browser; prints clean on A4).
- `where-the-rain-went-a4.pdf` — print-ready vector A4 export (text and
  artwork stay vector, resolution-independent).
- `build_a4.py` — generates `a4.html` from the raw data. No hand-edited
  numbers: every figure on the page is computed from the CSV.
- `export_pdf.sh` — rebuilds the HTML and exports the PDF in one step.

## Data

`data/rainfall_anomalies/data.csv` — SPC Pacific Data Hub, dataflow
`DF_CLIMATE_CHANGE`, indicator `RAIN_ANOM` (annual rainfall anomalies, mm),
22 Pacific Island countries and territories, 1979–2025.

## Rebuild & export

```sh
poster/export_pdf.sh
```

(Regenerates `a4.html` from the CSV, then prints it to a vector A4 PDF with
headless Chrome.)
