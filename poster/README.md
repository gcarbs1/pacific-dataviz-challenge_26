# Where the Rain Went

Static A4 art poster for the Pacific Dataviz Challenge 2026.

**Narrative.** The climate crisis is not only heating the Pacific, it is
redistributing its water. Comparing each territory's average annual rainfall
anomaly across the record's first twenty years (1979–1998) and its last
twenty (2006–2025) — one generation apart — the west and south (Tonga, Niue,
Micronesia, the Solomons, Palau, Wallis & Futuna) are getting markedly
wetter, while the atolls along the dateline (Nauru, Kiribati, Tuvalu,
Tokelau) together with New Caledonia and French Polynesia are drying out.
Fifteen territories now catch more rain, seven catch less.

## The artwork — the rain wheel

One circular artwork fills the page; narration lives in the sky corners and a
single quiet legend line sits at the foot — nothing is written over the art.

1. **The ring** is each territory's old balance — its average rain of
   1979–1998, the record's first twenty years. The ocean lies inside the
   ring, the sky outside. The 22 territories sit around it **ordered by the
   shift itself**, each berth sized to give its drop room to breathe (the
   deep drops near the centre get wider sectors), every one wearing its
   simplified flag: the driest territory (Nauru) starts clockwise of the
   12-o'clock gap, directly beneath the page's sun; the shift rises through
   zero; the wettest (Tonga) closes the circle on the far side of the gap.
   Read clockwise, the wheel is one revolution of the water cycle —
   evaporation under the sun, rain returning on the other side — and the
   two record-holders flank the ruler in the gap. The 15 : 7 split is
   itself the message: most of the wheel now rains, and the drought
   gathers on one arc — the dateline atolls plus New Caledonia and French
   Polynesia — while the wetting arc is the west and south.
2. **The ocean** — engraved water: dozens of hairline contour rings over a
   soft depth gradient, like the line-work of an etching; each territory sits
   at a gently hand-jittered angle so the compass breathes instead of ticking
   like a clock.
3. **Flag-drops** rendered as glass — a specular pair lit by the page's one
   sun (top-right), inner shading, a soft cast shadow on the water — fall
   inward where rain increased (the drop has arrived in the ocean) and
   evaporate outward, faded behind a warm solid outline, where rain
   decreased. Distance from the ring + drop size = the shift in % of a
   normal year's rain, measured against the radial ruler in the
   12-o'clock gap.
4. **Threads** — every drop hangs from its berth on the ring by the same
   fine solid thread: blue threads reach down into the ocean, warm ones
   rise into the sky.
5. **Radial labels** read outward like compass spokes, one uniform two-line
   format for all 22 territories — country name, shift beneath it (the
   three driest and three wettest in bold) — placed
   past the drop so no text is ever written over the artwork. Two emblems
   hold the sky at the same height, one per corner: the sun over the drying
   side, three grey rain clouds over the raining side, each corner's
   headline and count sharing the same baselines. The centre of the ocean
   is left empty. Record notes in the
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
`DF_CLIMATE_CHANGE`, indicator `RAIN_ANOM`, 22 Pacific Island countries and
territories, 1979–2025.

**Units.** The values are annual rainfall anomalies expressed as a
percentage of each territory's 1991–2020 normal (the PDH CSV mislabels the
unit as `MM`). The 1991–2020 reference period is stated in the official
PDH codelist description of `RAIN_ANOM`; the percentage reading is
verified three ways: the 1991–2020 mean is exactly zero for every
territory, the ENSO years land where they should (El Niño 1997/2015 wet in
Nauru and Kiribati, La Niña 1999/2011 dry), and Nauru's 2015 (+49.5) and
1999 (−54.4) match its real totals of roughly 3100 mm and 950 mm against a
normal of about 2080 mm — while read as mm the official example itself
(Wallis & Futuna −20.5 in the severe 1998 El Niño) would be an invisible
0.7% dip. Percent-of-1991–2020-normal is also the standard presentation
for this indicator in the region: the WMO's *State of the Climate in the
South-West Pacific* reports express precipitation anomalies "as a
percentage of the 1991–2020 average". The build asserts the zero-baseline
property, so a silent unit change in the source would break the build.
Percentages also make the artwork fairer: every territory is measured
against its own climate, so a dry atoll and a soaked high island are
directly comparable.

**Choosing the time cut.** Five candidate cuts were compared on the data
before settling on "first twenty years vs last twenty" (1979–1998 vs
2006–2025): the 2020s vs everything before, the record's two halves, the
20 v 20 ends, the fitted 47-year trend, and the 2020s vs the official
normal. The 20 v 20 cut tracks the full 47-year trend almost perfectly
(rank correlation 0.98, against 0.91 for the 2020s window), is the most
internally stable choice (comparing odd years with even years reproduces
the ranking at 0.90, against 0.76 for the 2020s window, because each
20-year window swallows several full ENSO cycles), gives the strongest
mid-field signal (median absolute shift 7.2 points), and needs no
statistics to explain. It also surfaces protagonists the short window
hid: Tonga becomes the biggest gainer and New Caledonia the second
biggest loser, both consistent with the long-term trend. The footnote's
trend claim is asserted at build time.

## Rebuild & export

```sh
poster/export_pdf.sh
```

(Regenerates `a4.html` from the CSV, then prints it to a vector A4 PDF with
headless Chrome.)
