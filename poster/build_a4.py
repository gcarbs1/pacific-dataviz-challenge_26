# -*- coding: utf-8 -*-
"""
WHERE THE RAIN WENT — A4 art poster (light background, flag drops).
One page, one artwork, nothing written over it:
  1. flag-drops: x = geography (west->east), distance from the "old balance"
     line + drop size = shift between 1979-2000 and 2020-2025 averages
  2. each featured stem is a year-by-year barcode (47 annual anomalies)
  3. legend, computed record notes and credits arranged below the art

Builds poster/a4.html from data/rainfall_anomalies/data.csv.
"""
import math
import random
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / "a4.html"

# ---------------------------------------------------------------- data ------
df = pd.read_csv(ROOT / "data" / "rainfall_anomalies" / "data.csv")
df = df[["GEO_PICT", "TIME_PERIOD", "OBS_VALUE"]].rename(
    columns={"GEO_PICT": "iso", "TIME_PERIOD": "year", "OBS_VALUE": "v"}
)
H0, H1, R0, R1 = 1979, 2000, 2020, 2025
hist = df[df.year.between(H0, H1)].groupby("iso")["v"].mean()
rec = df[df.year.between(R0, R1)].groupby("iso")["v"].mean()
stats = pd.DataFrame({"hist": hist, "rec": rec})
stats["delta"] = stats["rec"] - stats["hist"]
series = {iso: list(zip(g.sort_values("year")["year"], g.sort_values("year")["v"]))
          for iso, g in df.groupby("iso")}

NAMES = {
    "FM": "Micronesia", "SB": "Solomon Is.", "VU": "Vanuatu", "PW": "Palau",
    "TO": "Tonga", "NU": "Niue", "WF": "Wallis & Futuna", "MH": "Marshall Is.",
    "FJ": "Fiji", "WS": "Samoa", "PG": "Papua N. Guinea", "AS": "Am. Samoa",
    "GU": "Guam", "MP": "N. Marianas", "CK": "Cook Is.", "PF": "Fr. Polynesia",
    "PN": "Pitcairn", "TK": "Tokelau", "NC": "New Caledonia", "KI": "Kiribati",
    "TV": "Tuvalu", "NR": "Nauru",
}
LONG = {
    "PW": 134.6, "GU": 144.0, "PG": 144.5, "MP": 145.7, "FM": 150.5,
    "SB": 159.8, "NC": 165.3, "NR": 166.9, "VU": 167.3, "MH": 169.2,
    "KI": 174.5, "FJ": 178.4, "TV": 179.2, "WF": 183.6, "TO": 184.8,
    "WS": 187.9, "TK": 188.2, "NU": 190.1, "AS": 190.6, "CK": 200.2,
    "PF": 211.5, "PN": 229.9,
}
FEAT_WET = ["FM", "SB", "VU", "PW"]
FEAT_DRY = ["NR", "TV", "KI", "NC", "TK"]
FEATURED = FEAT_WET + FEAT_DRY
ORDER = sorted(LONG, key=LONG.get)
n_wet = int((stats.delta > 0).sum())
n_dry = int((stats.delta < 0).sum())

# facts for callouts, verified from the data at build time
nr = dict(series["NR"])
NR_2019, NR_2022 = nr[2019], nr[2022]
fm_top3 = sorted(series["FM"], key=lambda t: -t[1])[:3]
assert min(y for y, _ in fm_top3) >= 2019, "FSM callout no longer true"
SB_REC_YEAR, SB_REC_V = max(series["SB"], key=lambda t: t[1])

# ------------------------------------------------------------- palette ------
PAPER = "#fbf7ee"
INK = "#22313b"
SUB = "#5f7280"
FAINT = "#9aa9b2"
WET = "#1b87b4"
WET_D = "#0e5f83"
DRY = "#c2762e"
DRY_D = "#9a571c"
SKY = "#8fb3c4"
SEA = "#cfe6ee"

def fmt(v):
    return f"{v:+.1f}".replace("-", "−")

# ---------------------------------------------------------------- shapes ----
def drop_path(cx, cy, r, up=False):
    s = -1 if up else 1
    tip = cy - s * 2.05 * r
    return (
        f"M {cx:.1f} {tip:.1f} "
        f"C {cx + 0.55 * r:.1f} {cy - s * 1.1 * r:.1f} {cx + r:.1f} {cy - s * 0.45 * r:.1f} {cx + r:.1f} {cy:.1f} "
        f"A {r:.1f} {r:.1f} 0 1 {1 if s == 1 else 0} {cx - r:.1f} {cy:.1f} "
        f"C {cx - r:.1f} {cy - s * 0.45 * r:.1f} {cx - 0.55 * r:.1f} {cy - s * 1.1 * r:.1f} {cx:.1f} {tip:.1f} Z"
    )

def star_pts(cx, cy, r, rot=-90.0, n=5, inner=0.42):
    pts = []
    for i in range(n * 2):
        rr = r if i % 2 == 0 else r * inner
        a = math.radians(rot + i * 180.0 / n)
        pts.append(f"{cx + rr * math.cos(a):.1f},{cy + rr * math.sin(a):.1f}")
    return " ".join(pts)

def S(cx, cy, r, fill="#fff", rot=-90.0, n=5, inner=0.42):
    return f'<polygon points="{star_pts(cx, cy, r, rot, n, inner)}" fill="{fill}"/>'

# ------------------------------------------------------ simplified flags ----
NS = 'vector-effect="non-scaling-stroke"'

def flag_svg(iso):
    f = []
    if iso == "PW":
        f.append('<rect width="100" height="64" fill="#4AADD6"/>')
        f.append('<circle cx="42" cy="32" r="19" fill="#FFDE00"/>')
    elif iso == "FM":
        f.append('<rect width="100" height="64" fill="#75B2DD"/>')
        for cx, cy in ((50, 11), (27, 32), (73, 32), (50, 53)):
            f.append(S(cx, cy, 8))
    elif iso == "SB":
        f.append('<rect width="100" height="64" fill="#3D8E33"/>')
        f.append('<polygon points="0,0 100,0 0,64" fill="#215B9E"/>')
        f.append('<polygon points="0,56 87,0 100,0 100,8 13,64 0,64" fill="#FCD116"/>')
        f.append('<polygon points="0,56 87,0 100,0 0,64" fill="#215B9E"/>')
        for cx, cy in ((11, 9), (25, 9), (18, 19), (11, 29), (25, 29)):
            f.append(S(cx, cy, 4.6))
    elif iso == "VU":
        f.append('<rect width="100" height="28" fill="#D21034"/>')
        f.append('<rect y="36" width="100" height="28" fill="#009543"/>')
        f.append('<rect y="28" width="100" height="8" fill="#000"/>')
        f.append('<rect y="30.5" width="100" height="3" fill="#FDCE12"/>')
        f.append('<polygon points="0,0 42,32 0,64" fill="#000"/>')
        f.append(f'<path d="M 0 5 L 36 32 L 0 59" fill="none" stroke="#FDCE12" stroke-width="1.6" {NS}/>')
    elif iso == "NR":
        f.append('<rect width="100" height="64" fill="#002B7F"/>')
        f.append('<rect y="28" width="100" height="7" fill="#FFC61E"/>')
        f.append(S(25, 48, 9, n=6, inner=0.5))
    elif iso == "TV":
        f.append('<rect width="100" height="64" fill="#75B2DD"/>')
        f.append('<rect width="50" height="32" fill="#012169"/>')
        f.append(f'<path d="M0,0 L50,32 M50,0 L0,32" stroke="#fff" stroke-width="2.6" {NS}/>')
        f.append(f'<path d="M0,0 L50,32 M50,0 L0,32" stroke="#C8102E" stroke-width="1.1" {NS}/>')
        f.append(f'<path d="M25,0 V32 M0,16 H50" stroke="#fff" stroke-width="3.4" {NS}/>')
        f.append(f'<path d="M25,0 V32 M0,16 H50" stroke="#C8102E" stroke-width="1.8" {NS}/>')
        for cx, cy in ((63, 12), (76, 8), (88, 14), (70, 26), (84, 28),
                       (94, 30), (64, 42), (77, 44), (90, 46)):
            f.append(S(cx, cy, 3.6, fill="#FFCE00"))
    elif iso == "KI":
        f.append('<rect width="100" height="38" fill="#CE1126"/>')
        f.append('<rect y="38" width="100" height="26" fill="#fff"/>')
        for i in range(9):
            a = math.radians(180 + i * 22.5)
            x1, y1 = 50 + 15 * math.cos(a), 38 + 15 * math.sin(a)
            x2, y2 = 50 + 23 * math.cos(a), 38 + 23 * math.sin(a)
            f.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#FCD116" stroke-width="2.4" {NS}/>')
        f.append('<path d="M36,38 A14,14 0 0 1 64,38 Z" fill="#FCD116"/>')
        f.append(f'<path d="M0,46 Q12,41 25,46 T50,46 T75,46 T100,46" fill="none" stroke="#005BBB" stroke-width="3" {NS}/>')
        f.append(f'<path d="M0,56 Q12,51 25,56 T50,56 T75,56 T100,56" fill="none" stroke="#005BBB" stroke-width="3" {NS}/>')
    elif iso == "NC":
        f.append('<rect width="100" height="22" fill="#0035AD"/>')
        f.append('<rect y="22" width="100" height="21" fill="#ED4135"/>')
        f.append('<rect y="43" width="100" height="21" fill="#009543"/>')
        f.append(f'<circle cx="33" cy="32" r="16" fill="#FAE600" stroke="#000" stroke-width="1.4" {NS}/>')
        f.append('<polygon points="33,15 35.5,24 35.5,42 33,48 30.5,42 30.5,24" fill="#000"/>')
        f.append('<rect x="27" y="24" width="12" height="2.4" fill="#000"/>')
        f.append('<rect x="28" y="34" width="10" height="2.2" fill="#000"/>')
    elif iso == "TK":
        f.append('<rect width="100" height="64" fill="#00247D"/>')
        f.append('<path d="M28,54 C48,50 72,42 90,26 C86,44 62,56 30,56 Z" fill="#FED100"/>')
        f.append(S(15, 13, 4.2))
        f.append(S(10, 27, 3.4))
        f.append(S(19, 36, 3.4))
        f.append(S(23, 22, 2.8))
    return "".join(f)

CAP = {
    "PW": "#4AADD6", "FM": "#75B2DD", "SB": "#215B9E", "VU": "#D21034",
    "NR": "#002B7F", "TV": "#75B2DD", "KI": "#CE1126", "NC": "#0035AD", "TK": "#00247D",
}
CAP_UP = {"NR": "#002B7F", "TV": "#75B2DD", "KI": "#005BBB", "NC": "#009543", "TK": "#00247D"}

# ================================================================ poster =====
W, Hpx = 840, 1188
ML, MR = 52, 40
LINE_Y = 632
SEA_BOT = 968
K = 7.4
def rsize(d): return 7.0 + abs(d) * 0.55

rng = random.Random(20)
art = []

# --- sky & sea washes --------------------------------------------------------
art.append(f'<rect x="0" y="{LINE_Y}" width="{W}" height="{SEA_BOT - LINE_Y}" fill="{SEA}" opacity="0.35"/>')
for i in range(4):
    y = SEA_BOT - 42 + i * 11
    seg, x = [f"M -10 {y}"], -10
    while x < W + 10:
        seg.append(f"q 14 {-5 if (x // 14) % 2 == 0 else 5} 28 0")
        x += 28
    art.append(f'<path d="{" ".join(seg)}" fill="none" stroke="{WET}" stroke-opacity="{0.20 - i * 0.04:.2f}" stroke-width="1.1"/>')
for _ in range(150):
    x = rng.random() ** 1.7 * 320
    y = 246 + rng.random() * (LINE_Y - 276)
    ln = 6 + rng.random() * 13
    art.append(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x + 1.5:.0f}" y2="{y + ln:.0f}" stroke="{WET}" stroke-opacity="{0.06 + rng.random() * 0.15:.2f}" stroke-width="1"/>')
for i in range(13):
    y = 242 + i * 5.2
    amp = 3 + rng.random() * 3
    width = 290 - i * 9 + rng.random() * 30
    seg, x = [f"M 0 {y:.0f}"], 0
    while x < width:
        seg.append(f"q 11 {-amp:.1f} 22 0")
        x += 22
    art.append(f'<path d="{" ".join(seg)}" fill="none" stroke="{SKY}" stroke-opacity="{0.55 - i * 0.03:.2f}" stroke-width="1.2"/>')
sx, sy = 766, 300
art.append(f'<circle cx="{sx}" cy="{sy}" r="23" fill="#f3c34e" opacity="0.9"/>')
art.append(f'<circle cx="{sx}" cy="{sy}" r="23" fill="none" stroke="{DRY}" stroke-opacity="0.5" stroke-width="1"/>')
for i in range(16):
    a = math.radians(i * 22.5)
    r2 = 30 + (15 if i % 2 == 0 else 8)
    art.append(f'<line x1="{sx + 30 * math.cos(a):.1f}" y1="{sy + 30 * math.sin(a):.1f}" x2="{sx + r2 * math.cos(a):.1f}" y2="{sy + r2 * math.sin(a):.1f}" stroke="{DRY}" stroke-opacity="0.5" stroke-width="1.1"/>')

art.append(f'<text x="56" y="402" class="anno" fill="{WET_D}">the west fills up</text>')
art.append(f'<text x="{W - 40}" y="404" class="anno" fill="{DRY_D}" text-anchor="end">the centre dries out</text>')

# --- mm ruler (left margin) --------------------------------------------------
RX = 26
art.append(f'<line x1="{RX}" y1="{LINE_Y - 30 * K:.0f}" x2="{RX}" y2="{LINE_Y + 20 * K:.0f}" stroke="{SUB}" stroke-width="0.9"/>')
for m in range(-20, 31, 5):
    y = LINE_Y - m * K
    major = m % 10 == 0
    art.append(f'<line x1="{RX}" y1="{y:.0f}" x2="{RX + (6 if major else 3.5)}" y2="{y:.0f}" stroke="{SUB}" stroke-width="0.9"/>')
    if major and m != 0:
        art.append(f'<text x="{RX + 9}" y="{y + 2.5:.0f}" class="rul" fill="{SUB}">{abs(m)}</text>')
art.append(f'<text x="{RX + 9}" y="{LINE_Y + 2.5}" class="rul" fill="{INK}">0 mm</text>')
art.append(f'<text transform="rotate(-90 14 {LINE_Y - 108})" x="14" y="{LINE_Y - 108}" class="tinyb" fill="{DRY_D}" text-anchor="middle">RAIN LOST</text>')
art.append(f'<text transform="rotate(-90 14 {LINE_Y + 80})" x="14" y="{LINE_Y + 80}" class="tinyb" fill="{WET_D}" text-anchor="middle">RAIN GAINED</text>')

# --- the balance line ----------------------------------------------------
art.append(f'<line x1="{RX}" y1="{LINE_Y}" x2="{W - MR + 18}" y2="{LINE_Y}" stroke="{INK}" stroke-width="1.3"/>')
art.append(f'<text x="64" y="{LINE_Y - 23}" class="linelab">THE OLD BALANCE</text>')
art.append(f'<text x="64" y="{LINE_Y - 10}" class="avg" fill="{SUB}" font-style="italic">average rain of 1979–2000</text>')
art.append(f'<text x="{RX}" y="{SEA_BOT + 16}" class="tiny" fill="{FAINT}">← WEST</text>')
art.append(f'<text x="{W - MR + 18}" y="{SEA_BOT + 16}" class="tiny" fill="{FAINT}" text-anchor="end">EAST →</text>')
art.append(f'<text x="{W / 2}" y="{SEA_BOT + 16}" class="tiny" fill="{FAINT}" text-anchor="middle">territories ordered by longitude, west to east</text>')

# --- drops -------------------------------------------------------------------
NUDGE = {"FM": (-16, -4), "SB": (16, 28), "VU": (4, 0), "PW": (0, 0),
         "NR": (0, -8), "TV": (14, 0), "KI": (-14, 0), "NC": (-18, 0), "TK": (0, 0)}
DRIFT = {"FM": -8, "SB": 9}

slot = (W - ML - MR) / len(ORDER)
defs, late = [], []
for i, iso in enumerate(ORDER):
    d = stats.loc[iso, "delta"]
    x = ML + (i + 0.5) * slot + DRIFT.get(iso, 0)
    wet = d >= 0
    feat = iso in FEATURED
    stem = abs(d) * K
    sgn = 1 if wet else -1
    if feat:
        r = rsize(d)
        cy = LINE_Y + (stem + 2.05 * r) * sgn
        tip_y = LINE_Y + stem * sgn
        far_y = cy + r * sgn
        # stem = year-by-year barcode: 1979 at the line -> 2025 at the drop
        yrs = series[iso]
        n = len(yrs)
        for j, (yr_, v) in enumerate(yrs):
            ty = LINE_Y + sgn * (4 + (stem - 8) * j / (n - 1))
            half = min(8.0, 0.8 + abs(v) * 0.115)
            c = WET if v >= 0 else DRY
            art.append(f'<line x1="{x - half:.1f}" y1="{ty:.1f}" x2="{x + half:.1f}" y2="{ty:.1f}" stroke="{c}" stroke-opacity="0.8" stroke-width="1"/>')
        if iso in ("PW", "NR"):  # teach the encoding once per side
            art.append(f'<text x="{x + 12}" y="{LINE_Y + sgn * 8 + 2:.0f}" class="rul halo" fill="{FAINT}">1979</text>')
            art.append(f'<text x="{x + 12}" y="{tip_y - sgn * 2 + 2:.0f}" class="rul halo" fill="{FAINT}">2025</text>')
        dp = drop_path(x, cy, r, up=not wet)
        defs.append(f'<clipPath id="c{iso}"><path d="{dp}"/></clipPath>')
        cap = (CAP if wet else CAP_UP).get(iso, WET)
        art.append(f'<path d="{dp}" fill="{cap}"/>')
        fw, fh = 2.35 * r, 1.55 * r
        art.append(f'<g clip-path="url(#c{iso})"><g transform="translate({x - fw / 2:.1f},{cy - fh / 2:.1f}) scale({fw / 100:.3f},{fh / 64:.3f})">{flag_svg(iso)}</g></g>')
        if not wet:
            art.append(f'<path d="{dp}" fill="{PAPER}" opacity="0.34"/>')
            art.append(f'<path d="{dp}" fill="none" stroke="{DRY_D}" stroke-width="1.2" stroke-dasharray="4 3"/>')
        else:
            art.append(f'<path d="{dp}" fill="none" stroke="{INK}" stroke-opacity="0.75" stroke-width="1.2"/>')
        h_, r_ = stats.loc[iso, "hist"], stats.loc[iso, "rec"]
        cval = WET_D if wet else DRY_D
        if iso == "NC":
            # label beside the drop, in the clear western sky
            lx = x - 26
            art.append(f'<text x="{lx:.0f}" y="{far_y + 1:.0f}" class="val halo" fill="{cval}" text-anchor="end">{fmt(d)} mm</text>')
            art.append(f'<text x="{lx:.0f}" y="{far_y + 15:.0f}" class="name halo" fill="{INK}" text-anchor="end">{NAMES[iso]}</text>')
            art.append(f'<text x="{lx:.0f}" y="{far_y + 29:.0f}" class="avg halo" fill="{SUB}" text-anchor="end">avg {fmt(h_)} → {fmt(r_)}</text>')
        else:
            ndx, ndy = NUDGE.get(iso, (0, 0))
            if wet:
                vy, ny, ay = far_y + 19 + ndy, far_y + 34 + ndy, far_y + 47 + ndy
            else:
                ay, ny, vy = far_y - 46 - ndy, far_y - 33 - ndy, far_y - 18 - ndy
            art.append(f'<text x="{x + ndx:.0f}" y="{vy:.0f}" class="val halo" fill="{cval}" text-anchor="middle">{fmt(d)} mm</text>')
            art.append(f'<text x="{x + ndx:.0f}" y="{ny:.0f}" class="name halo" fill="{INK}" text-anchor="middle">{NAMES[iso]}</text>')
            art.append(f'<text x="{x + ndx:.0f}" y="{ay:.0f}" class="avg halo" fill="{SUB}" text-anchor="middle">avg {fmt(h_)} → {fmt(r_)}</text>')
    else:
        r = 2.6 + abs(d) * 0.34
        cy = LINE_Y + (stem + 2.05 * r) * sgn
        tip_y = LINE_Y + stem * sgn
        c = WET if wet else DRY
        art.append(f'<line x1="{x:.1f}" y1="{LINE_Y + 4 * sgn}" x2="{x:.1f}" y2="{tip_y:.1f}" stroke="{c}" stroke-opacity="0.45" stroke-width="1" stroke-dasharray="2 3"/>')
        art.append(f'<path d="{drop_path(x, cy, r, up=not wet)}" fill="{c}" opacity="0.75"/>')
        ly = cy + (r + 12) * sgn + (3 if wet else 0)
        art.append(f'<text x="{x:.0f}" y="{ly:.0f}" class="tiny halo" fill="{SUB}" text-anchor="middle">{iso}</text>')

ART = f'<defs>{"".join(defs)}</defs>' + "".join(art)

# --- legend + record notes, arranged below the art ---------------------------
def below():
    p = []
    y0 = 1022
    p.append(f'<line x1="{RX}" y1="{y0 - 24}" x2="{W - MR + 18}" y2="{y0 - 24}" stroke="{INK}" stroke-opacity="0.15" stroke-width="0.8"/>')
    # legend: three quiet groups
    x = RX + 10
    p.append(f'<path d="{drop_path(x, y0 + 6, 5.5)}" fill="{WET}"/>')
    p.append(f'<text x="{x + 12}" y="{y0}" class="tiny" fill="{SUB}">flag-drop falling = gaining rain; distance &amp; size</text>')
    p.append(f'<text x="{x + 12}" y="{y0 + 11}" class="tiny" fill="{SUB}">= the shift in mm, avg 2020–25 vs avg 1979–2000</text>')
    x = RX + 268
    p.append(f'<path d="{drop_path(x, y0, 5.5, up=True)}" fill="{DRY}" opacity="0.5"/>')
    p.append(f'<path d="{drop_path(x, y0, 5.5, up=True)}" fill="none" stroke="{DRY_D}" stroke-width="1" stroke-dasharray="2.5 2"/>')
    p.append(f'<text x="{x + 12}" y="{y0}" class="tiny" fill="{SUB}">faded drop rising = losing rain, evaporating</text>')
    p.append(f'<text x="{x + 12}" y="{y0 + 11}" class="tiny" fill="{SUB}">back into the sky; plain drops = the other 13</text>')
    x = RX + 522
    for j, hw in enumerate((3, 6, 2, 7, 4)):
        c = WET if j in (1, 3) else DRY
        p.append(f'<line x1="{x - hw:.0f}" y1="{y0 - 5 + j * 5}" x2="{x + hw:.0f}" y2="{y0 - 5 + j * 5}" stroke="{c}" stroke-width="1"/>')
    p.append(f'<text x="{x + 13}" y="{y0}" class="tiny" fill="{SUB}">each stem: one tick per year, 1979 at the line</text>')
    p.append(f'<text x="{x + 13}" y="{y0 + 11}" class="tiny" fill="{SUB}">→ 2025 at the drop; width = that year’s anomaly</text>')
    # computed record notes
    ny = y0 + 46
    p.append(f'<path d="{drop_path(RX + 14, ny - 3, 3.4)}" fill="{DRY}" opacity="0.85"/>')
    p.append(f'<text x="{RX + 26}" y="{ny}" class="call" fill="{INK}">Nauru’s sky has turned manic: <tspan fill="{WET_D}" font-weight="600">{fmt(NR_2019)} mm</tspan> in 2019, its wettest year on record — then <tspan fill="{DRY_D}" font-weight="600">{fmt(NR_2022)} mm</tspan> in 2022.</text>')
    p.append(f'<path d="{drop_path(RX + 14, ny + 15, 3.4)}" fill="{WET}" opacity="0.85"/>')
    p.append(f'<text x="{RX + 26}" y="{ny + 18}" class="call" fill="{INK}">Micronesia’s three wettest years on record have all come since 2019; the Solomons’ record fell in {SB_REC_YEAR} ({fmt(SB_REC_V)} mm).</text>')
    return "".join(p)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Where the Rain Went — A4</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,400;1,9..144,500&family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:#e8e4da; display:flex; justify-content:center; padding:24px 0;
         font-family:'Outfit',sans-serif; }}
  .sheet {{ width:{W}px; height:{Hpx}px; background:{PAPER}; box-shadow:0 8px 40px rgba(40,50,60,0.25); }}
  svg {{ display:block; }}
  .kick   {{ font:600 10px 'Outfit',sans-serif; letter-spacing:0.32em; fill:{SUB}; }}
  .title  {{ font:600 58px 'Fraunces',Georgia,serif; fill:{INK}; }}
  .title .w {{ fill:{WET}; }}
  .stand  {{ font:italic 400 14.5px 'Fraunces',Georgia,serif; fill:{SUB}; }}
  .standb {{ font-style:normal; font-weight:600; fill:{INK}; }}
  .bignum {{ font:700 27px 'Fraunces',Georgia,serif; }}
  .biglab {{ font:600 8.5px 'Outfit',sans-serif; letter-spacing:0.2em; fill:{SUB}; }}
  .anno   {{ font:italic 500 15.5px 'Fraunces',Georgia,serif; opacity:0.85; }}
  .call   {{ font:italic 400 11.5px 'Fraunces',Georgia,serif; }}
  .linelab{{ font:600 9.5px 'Outfit',sans-serif; letter-spacing:0.24em; fill:{INK}; }}
  .sect   {{ font:600 11px 'Outfit',sans-serif; letter-spacing:0.22em; }}
  .name   {{ font:600 12.5px 'Outfit',sans-serif; }}
  .val    {{ font:700 13.5px 'Outfit',sans-serif; }}
  .avg    {{ font:400 8.6px 'Outfit',sans-serif; }}
  .mname  {{ font:600 8.6px 'Outfit',sans-serif; }}
  .mval   {{ font:700 10px 'Outfit',sans-serif; }}
  .tiny   {{ font:400 9.3px 'Outfit',sans-serif; }}
  .tinyb  {{ font:600 9.3px 'Outfit',sans-serif; letter-spacing:0.16em; }}
  .rul    {{ font:400 8px 'Outfit',sans-serif; }}
  .foot   {{ font:400 8.6px 'Outfit',sans-serif; fill:{FAINT}; }}
  .halo   {{ paint-order:stroke; stroke:{PAPER}; stroke-width:3.5px; stroke-linejoin:round; }}
  @media print {{ body {{ background:none; padding:0; }} .sheet {{ box-shadow:none; }} }}
</style>
</head>
<body>
<div class="sheet">
<svg viewBox="0 0 {W} {Hpx}" width="{W}" height="{Hpx}" xmlns="http://www.w3.org/2000/svg">
  <rect width="{W}" height="{Hpx}" fill="{PAPER}"/>

  <!-- tapa frame -->
  {"".join(f'<path d="M {xx} 14 L {xx + 7} 6 L {xx + 14} 14" fill="none" stroke="{DRY}" stroke-opacity="0.4" stroke-width="1"/>' for xx in range(14, W - 18, 22))}
  {"".join(f'<path d="M {xx} 1174 L {xx + 7} 1182 L {xx + 14} 1174" fill="none" stroke="{DRY}" stroke-opacity="0.4" stroke-width="1"/>' for xx in range(14, W - 18, 22))}

  <!-- header -->
  <text x="{W / 2}" y="48" class="kick" text-anchor="middle">PACIFIC DATAVIZ CHALLENGE 2026 · RAINFALL ANOMALIES · 22 TERRITORIES · 1979→2025</text>
  <text x="{W / 2}" y="106" class="title" text-anchor="middle">Where the <tspan class="w">rain</tspan> went</text>
  <text x="{W / 2}" y="142" class="stand" text-anchor="middle">The climate crisis doesn’t just bring more heat — it redistributes the water.</text>
  <text x="{W / 2}" y="162" class="stand" text-anchor="middle">Compared with the rain they knew in 1979–2000, the same sky that now <tspan class="standb">floods the western Pacific</tspan></text>
  <text x="{W / 2}" y="182" class="stand" text-anchor="middle">is <tspan class="standb">emptying over the atolls of the centre</tspan>. Same ocean, different rain.</text>

  <!-- score, in the sky corners -->
  <text x="56" y="436" class="bignum halo" fill="{WET_D}">{n_wet}</text>
  <text x="56" y="452" class="biglab halo">TERRITORIES NOW WETTER</text>
  <text x="{W - 40}" y="436" class="bignum halo" fill="{DRY_D}" text-anchor="end">{n_dry}</text>
  <text x="{W - 40}" y="452" class="biglab halo" text-anchor="end">TERRITORIES NOW DRIER</text>

  <!-- artwork -->
  {ART}

  <!-- legend & notes -->
  {below()}

  <!-- footer -->
  <line x1="{RX}" y1="1124" x2="{W - MR + 18}" y2="1124" stroke="{INK}" stroke-opacity="0.18" stroke-width="0.8"/>
  <text x="{RX}" y="1142" class="foot"><tspan style="font-weight:600">Data</tspan> SPC Pacific Data Hub · dataflow DF_CLIMATE_CHANGE · indicator RAIN_ANOM (annual rainfall anomaly, mm) · 22 Pacific territories, 1979–2025.</text>
  <text x="{RX}" y="1156" class="foot">The 2020–25 window includes the 2020–23 triple-dip La Niña, which amplifies — but does not create — the west-wet / centre-dry contrast.</text>
  <text x="{RX}" y="1170" class="foot"><tspan style="font-weight:600">Where the Rain Went</tspan> · Pacific Dataviz Challenge 2026 · Gabriel Carbinatto</text>
</svg>
</div>
</body>
</html>
"""

OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html) / 1024:.0f} kB)")
