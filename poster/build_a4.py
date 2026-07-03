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

# ------------------------------------------------ flags for the other 13 ----
def uj(w=44.0, h=26.0):
    """Simplified Union Jack canton, w x h."""
    return (
        f'<rect width="{w}" height="{h}" fill="#012169"/>'
        f'<path d="M0,0 L{w},{h} M{w},0 L0,{h}" stroke="#fff" stroke-width="{h * 0.16:.1f}" {NS}/>'
        f'<path d="M0,0 L{w},{h} M{w},0 L0,{h}" stroke="#C8102E" stroke-width="{h * 0.07:.1f}" {NS}/>'
        f'<path d="M{w / 2},0 V{h} M0,{h / 2} H{w}" stroke="#fff" stroke-width="{h * 0.24:.1f}" {NS}/>'
        f'<path d="M{w / 2},0 V{h} M0,{h / 2} H{w}" stroke="#C8102E" stroke-width="{h * 0.13:.1f}" {NS}/>'
    )

def flag_svg2(iso):
    base = flag_svg(iso)
    if base:
        return base
    f = []
    if iso == "GU":
        f.append('<rect width="100" height="64" fill="#1F3F7A"/>')
        f.append(f'<rect x="3" y="3" width="94" height="58" fill="none" stroke="#C62139" stroke-width="5" {NS}/>')
        f.append('<path d="M50,10 C64,22 64,42 50,54 C36,42 36,22 50,10 Z" fill="#3C8FA8"/>')
        f.append('<path d="M40,46 Q50,40 60,46 L60,50 Q50,46 40,50 Z" fill="#F7D117"/>')
        f.append(f'<path d="M50,40 V22 M50,24 Q42,20 40,14 M50,24 Q58,20 60,14 M50,30 Q44,27 42,22 M50,30 Q56,27 58,22" fill="none" stroke="#2E6B4F" stroke-width="1.6" {NS}/>')
    elif iso == "PG":
        f.append('<rect width="100" height="64" fill="#000"/>')
        f.append('<polygon points="0,0 100,0 100,64" fill="#CE1126"/>')
        for cx, cy in ((25, 30), (20, 42), (28, 52), (36, 42), (30, 37)):
            f.append(S(cx, cy, 3.2))
        f.append('<path d="M60,28 Q70,12 86,14 Q78,18 76,24 Q70,20 64,30 Q66,34 62,36 Q58,32 60,28 Z" fill="#FCD116"/>')
    elif iso == "MP":
        f.append('<rect width="100" height="64" fill="#0071BC"/>')
        f.append('<rect x="45" y="20" width="10" height="26" rx="4" fill="#8D9093"/>')
        f.append('<ellipse cx="50" cy="20" rx="7" ry="4.5" fill="#B5B8BB"/>')
        f.append(S(50, 34, 13, fill="#fff"))
    elif iso == "MH":
        f.append('<rect width="100" height="64" fill="#003893"/>')
        f.append('<polygon points="0,58 100,6 100,16 0,64" fill="#DD7500"/>')
        f.append('<polygon points="0,64 100,16 100,26 6,64" fill="#fff"/>')
        f.append(S(24, 16, 10, n=12, inner=0.45))
    elif iso == "FJ":
        f.append('<rect width="100" height="64" fill="#68BFE5"/>')
        f.append(uj())
        f.append(f'<rect x="62" y="30" width="20" height="24" fill="#fff" stroke="#C8102E" stroke-width="1.4" {NS}/>')
        f.append('<rect x="62" y="30" width="20" height="7" fill="#C8102E"/>')
        f.append(f'<path d="M72,37 V54 M62,44 H82" stroke="#C8102E" stroke-width="2" {NS}/>')
    elif iso == "WF":
        f.append('<rect width="100" height="64" fill="#CE1126"/>')
        f.append('<rect width="12" height="20" fill="#002395"/>')
        f.append('<rect x="12" width="12" height="20" fill="#fff"/>')
        f.append('<rect x="24" width="12" height="20" fill="#CE1126"/>')
        f.append(f'<rect x="24" width="12" height="20" fill="none" stroke="#fff" stroke-width="1.2" {NS}/>')
        f.append(f'<path d="M56,18 L84,46 M84,18 L56,46" stroke="#fff" stroke-width="7" {NS}/>')
    elif iso == "TO":
        f.append('<rect width="100" height="64" fill="#C10000"/>')
        f.append('<rect width="42" height="28" fill="#fff"/>')
        f.append('<path d="M17,6 h8 v6 h6 v8 h-6 v6 h-8 v-6 h-6 v-8 h6 Z" fill="#C10000"/>')
    elif iso == "WS":
        f.append('<rect width="100" height="64" fill="#CE1126"/>')
        f.append('<rect width="46" height="30" fill="#002B7F"/>')
        for cx, cy, rr in ((23, 6, 3.4), (30, 13, 3.0), (23, 20, 3.4), (13, 14, 2.6), (16, 25, 3.0)):
            f.append(S(cx, cy, rr))
    elif iso == "NU":
        f.append('<rect width="100" height="64" fill="#FCD116"/>')
        f.append(uj())
        f.append(S(22, 13, 6, fill="#FCD116"))
    elif iso == "AS":
        f.append('<rect width="100" height="64" fill="#002B7F"/>')
        f.append('<polygon points="100,0 0,32 100,64" fill="#BD1021"/>')
        f.append('<polygon points="100,4 8,32 100,60" fill="#fff"/>')
        f.append('<path d="M88,20 Q70,26 62,32 Q70,38 88,44 Q80,32 88,20 Z" fill="#7B5230"/>')
    elif iso == "CK":
        f.append('<rect width="100" height="64" fill="#012169"/>')
        f.append(uj())
        for i in range(15):
            a = math.radians(i * 24)
            f.append(S(70 + 15 * math.cos(a), 34 + 15 * math.sin(a), 2.6))
    elif iso == "PF":
        f.append('<rect width="100" height="64" fill="#CE1126"/>')
        f.append('<rect y="16" width="100" height="32" fill="#fff"/>')
        f.append('<circle cx="50" cy="32" r="12" fill="#FCD116"/>')
        f.append(f'<path d="M40,36 Q45,33 50,36 T60,36" fill="none" stroke="#003893" stroke-width="2.2" {NS}/>')
        f.append(f'<path d="M42,30 H58 M50,30 V24 M44,24 H56" fill="none" stroke="#CE1126" stroke-width="2" {NS}/>')
    elif iso == "PN":
        f.append('<rect width="100" height="64" fill="#012169"/>')
        f.append(uj())
        f.append(f'<path d="M66,22 L86,22 L86,40 Q76,50 66,40 Z" fill="#316D3A" stroke="#FCD116" stroke-width="1.6" {NS}/>')
        f.append(f'<path d="M76,26 V44 M70,32 Q76,38 82,32" fill="none" stroke="#FCD116" stroke-width="2" {NS}/>')
    return "".join(f)

CAP.update({"GU": "#1F3F7A", "PG": "#CE1126", "MP": "#0071BC", "MH": "#003893",
            "FJ": "#68BFE5", "WF": "#CE1126", "TO": "#C10000", "WS": "#CE1126",
            "NU": "#FCD116", "AS": "#002B7F"})
CAP_UP.update({"CK": "#012169", "PF": "#CE1126", "PN": "#012169"})

# ================================================================ poster =====
# Circular composition — the "rain compass". The 22 territories sit around a
# ring in west->east order, one equal sector each. Inside the ring is the
# ocean; outside is the sky. Where rain increased, a flag-drop falls inward;
# where it decreased, a faded flag-drop evaporates outward. The nine largest
# shifts carry their 47-year barcode stem. A radial mm ruler sits in the
# 12-o'clock gap.
W, Hpx = 840, 1188
CX, CY = 420.0, 662.0
RB = 215.0                      # the old-balance ring
K = 4.4                         # px per mm of shift
GAP = 36.0                      # degrees kept clear at 12 o'clock
A0 = -90.0 + GAP / 2.0
SPAN = 360.0 - GAP

def ang(iso):
    return math.radians(A0 + SPAN * ORDER.index(iso) / (len(ORDER) - 1))

def pt(r, a):
    return CX + r * math.cos(a), CY + r * math.sin(a)

def rsize(d):
    return 6.0 + abs(d) * 0.42

rng = random.Random(20)
defs, art = [], []

# --- ocean disc, wave rings, sky ----------------------------------------------
art.append(f'<circle cx="{CX}" cy="{CY}" r="{RB}" fill="{SEA}" opacity="0.35"/>')
for i, rr in enumerate((RB - 16, RB - 30, RB - 44, RB - 58)):
    pts = []
    for j in range(121):
        th = j * 2 * math.pi / 120
        r2 = rr + 2.2 * math.sin(th * 18 + i * 1.7)
        x, y = pt(r2, th)
        pts.append(f"{'M' if j == 0 else 'L'} {x:.1f} {y:.1f}")
    art.append(f'<path d="{" ".join(pts)} Z" fill="none" stroke="{WET}" stroke-opacity="{0.20 - i * 0.045:.2f}" stroke-width="1.1"/>')
# sun in the top-right sky
sx, sy = 758, 288
art.append(f'<circle cx="{sx}" cy="{sy}" r="23" fill="#f3c34e" opacity="0.9"/>')
art.append(f'<circle cx="{sx}" cy="{sy}" r="23" fill="none" stroke="{DRY}" stroke-opacity="0.5" stroke-width="1"/>')
for i in range(16):
    a = math.radians(i * 22.5)
    r2 = 30 + (15 if i % 2 == 0 else 8)
    art.append(f'<line x1="{sx + 30 * math.cos(a):.1f}" y1="{sy + 30 * math.sin(a):.1f}" x2="{sx + r2 * math.cos(a):.1f}" y2="{sy + r2 * math.sin(a):.1f}" stroke="{DRY}" stroke-opacity="0.5" stroke-width="1.1"/>')

# --- the balance ring -----------------------------------------------------------
art.append(f'<circle cx="{CX}" cy="{CY}" r="{RB}" fill="none" stroke="{INK}" stroke-width="1.3"/>')

# --- radial mm ruler in the 12-o'clock gap ---------------------------------------
RT = CY - RB - 30 * K           # outer end (30 mm lost)
RG = CY - RB + 20 * K           # inner end (20 mm gained)
art.append(f'<line x1="{CX}" y1="{RT:.0f}" x2="{CX}" y2="{RG:.0f}" stroke="{SUB}" stroke-width="0.9"/>')
for m in range(-20, 31, 5):
    y = CY - RB - m * K
    major = m % 10 == 0
    art.append(f'<line x1="{CX}" y1="{y:.0f}" x2="{CX + (6 if major else 3.5)}" y2="{y:.0f}" stroke="{SUB}" stroke-width="0.9"/>')
    if major and m != 0:
        art.append(f'<text x="{CX + 9}" y="{y + 2.5:.0f}" class="rul" fill="{SUB}">{abs(m)}</text>')
art.append(f'<text x="{CX + 9}" y="{CY - RB + 2.5:.0f}" class="rul" fill="{INK}">0 mm</text>')
art.append(f'<text transform="rotate(-90 {CX - 8} {CY - RB - 62})" x="{CX - 8}" y="{CY - RB - 59}" class="tinyb" fill="{DRY_D}" text-anchor="middle">RAIN LOST</text>')
art.append(f'<text transform="rotate(-90 {CX - 8} {CY - RB + 52})" x="{CX - 8}" y="{CY - RB + 55}" class="tinyb" fill="{WET_D}" text-anchor="middle">RAIN GAINED</text>')
art.append(f'<text x="{CX}" y="{RT - 26:.0f}" class="linelab" text-anchor="middle">THE OLD BALANCE</text>')
art.append(f'<text x="{CX}" y="{RT - 13:.0f}" class="avg" fill="{SUB}" font-style="italic" text-anchor="middle">the ring — average rain of 1979–2000</text>')

# --- centre compass: reading direction --------------------------------------------
art.append(f'<circle cx="{CX}" cy="{CY}" r="2.6" fill="{SUB}"/>')
for i in range(8):
    a = math.radians(-90 + i * 45)
    rr = 14 if i % 2 == 0 else 9
    art.append(f'<line x1="{CX + 6 * math.cos(a):.1f}" y1="{CY + 6 * math.sin(a):.1f}" '
               f'x2="{CX + rr * math.cos(a):.1f}" y2="{CY + rr * math.sin(a):.1f}" '
               f'stroke="{SUB}" stroke-opacity="0.7" stroke-width="1"/>')
ca0, ca1 = math.radians(-64), math.radians(-6)
cx0, cy0 = pt(30, ca0)
cx1, cy1 = pt(30, ca1)
art.append(f'<path d="M {cx0:.1f} {cy0:.1f} A 30 30 0 0 1 {cx1:.1f} {cy1:.1f}" '
           f'fill="none" stroke="{SUB}" stroke-opacity="0.7" stroke-width="1"/>')
tx, ty = math.cos(ca1 + math.pi / 2), math.sin(ca1 + math.pi / 2)
art.append(f'<polygon points="{cx1 + 3.2 * math.cos(ca1):.1f},{cy1 + 3.2 * math.sin(ca1):.1f} '
           f'{cx1 - 3.2 * math.cos(ca1) + 5.5 * tx:.1f},{cy1 - 3.2 * math.sin(ca1) + 5.5 * ty:.1f} '
           f'{cx1 - 3.2 * math.cos(ca1) - 0.5 * tx:.1f},{cy1 - 3.2 * math.sin(ca1) - 0.5 * ty:.1f}" '
           f'fill="{SUB}" fill-opacity="0.8"/>')
wx, wy = pt(41, math.radians(-72))
ex, ey = pt(41, math.radians(2))
art.append(f'<text x="{wx:.0f}" y="{wy + 3:.0f}" class="rul" fill="{SUB}" text-anchor="middle">W</text>')
art.append(f'<text x="{ex:.0f}" y="{ey + 3:.0f}" class="rul" fill="{SUB}" text-anchor="middle">E</text>')

# --- the 22 territories, radially -------------------------------------------------
NUDGE = {"NC": -14, "NR": -12}   # hand-tuned extra radial offset for a label, in px

for iso in ORDER:
    d = float(stats.loc[iso, "delta"])
    a = ang(iso)
    deg = math.degrees(a) + 90.0
    wet = d >= 0
    sgn = 1 if wet else -1
    feat = iso in FEATURED
    stem = abs(d) * K
    r = rsize(d)
    cy_l = -RB + (stem + 2.05 * r) * sgn
    tip_l = -RB + stem * sgn
    g = [f'<g transform="translate({CX},{CY}) rotate({deg:.2f})">']
    if feat:
        # barcode stem: one tick per year, 1979 at the ring -> 2025 at the drop
        yrs = series[iso]
        n = len(yrs)
        for j, (yr_, v) in enumerate(yrs):
            ty = -RB + sgn * (4 + (stem - 8) * j / (n - 1))
            half = min(8.0, 0.8 + abs(v) * 0.115)
            c = WET if v >= 0 else DRY
            g.append(f'<line x1="{-half:.1f}" y1="{ty:.1f}" x2="{half:.1f}" y2="{ty:.1f}" stroke="{c}" stroke-opacity="0.8" stroke-width="1"/>')
    else:
        c = WET if wet else DRY
        g.append(f'<line x1="0" y1="{-RB + 4 * sgn}" x2="0" y2="{tip_l:.1f}" stroke="{c}" stroke-opacity="0.45" stroke-width="1" stroke-dasharray="2 3"/>')
    dp = drop_path(0, cy_l, r, up=not wet)
    defs.append(f'<clipPath id="c{iso}"><path d="{dp}"/></clipPath>')
    cap = (CAP if wet else CAP_UP).get(iso, WET)
    g.append(f'<path d="{dp}" fill="{cap}"/>')
    fw, fh = 2.35 * r, 1.55 * r
    g.append(f'<g clip-path="url(#c{iso})"><g transform="translate({-fw / 2:.1f},{cy_l - fh / 2:.1f}) scale({fw / 100:.3f},{fh / 64:.3f})">{flag_svg2(iso)}</g></g>')
    if not wet:
        g.append(f'<path d="{dp}" fill="{PAPER}" opacity="0.34"/>')
        g.append(f'<path d="{dp}" fill="none" stroke="{DRY_D}" stroke-width="1.2" stroke-dasharray="4 3"/>')
    else:
        g.append(f'<path d="{dp}" fill="none" stroke="{INK}" stroke-opacity="0.75" stroke-width="1.2"/>')
    g.append("</g>")
    art.append("".join(g))

    # radial labels in the sky, reading outward like compass spokes
    a_deg = math.degrees(a)
    right = a_deg <= 90.0
    r0 = (RB + 10) if wet else (RB + stem + 3.05 * r + 10)
    r0 += NUDGE.get(iso, 0)
    perp = (-math.sin(a), math.cos(a))
    off_sign = 1 if right else -1
    cval = WET_D if wet else DRY_D

    def radial_text(txt, cls, line, dominant_col=INK):
        x0, y0 = pt(r0, a)
        x0 += perp[0] * 12.5 * line * off_sign
        y0 += perp[1] * 12.5 * line * off_sign
        if right:
            tr = f'transform="rotate({a_deg:.1f} {x0:.1f} {y0:.1f})"'
            anc = "start"
        else:
            tr = f'transform="rotate({a_deg + 180:.1f} {x0:.1f} {y0:.1f})"'
            anc = "end"
        return (f'<text x="{x0:.1f}" y="{y0:.1f}" class="{cls} halo" fill="{dominant_col}" '
                f'text-anchor="{anc}" dominant-baseline="middle" {tr}>{txt}</text>')

    if feat:
        h_, r_ = stats.loc[iso, "hist"], stats.loc[iso, "rec"]
        art.append(radial_text(f'{NAMES[iso]} <tspan fill="{cval}">{fmt(d)} mm</tspan>', "name", 0))
        art.append(radial_text(f'avg {fmt(h_)} → {fmt(r_)}', "avg", 1, SUB))
    else:
        art.append(radial_text(f'{NAMES[iso]} <tspan fill="{cval}" font-weight="700">{fmt(d)}</tspan>', "sname", 0))

ART = f'<defs>{"".join(defs)}</defs>' + "".join(art)

# --- sky-corner narration (nothing over the artwork) ------------------------------
def corners():
    p = []
    # west / wetter — top-left
    p.append(f'<text x="44" y="330" class="anno" fill="{WET_D}">the west fills up</text>')
    p.append(f'<text x="44" y="364" class="bignum" fill="{WET_D}">{n_wet}</text>')
    p.append(f'<text x="44" y="380" class="biglab">TERRITORIES NOW WETTER</text>')
    p.append(f'<text x="44" y="404" class="call" fill="{INK}">Micronesia’s three wettest years on</text>')
    p.append(f'<text x="44" y="418" class="call" fill="{INK}">record have all come since 2019; the</text>')
    p.append(f'<text x="44" y="432" class="call" fill="{INK}">Solomons’ record fell in {SB_REC_YEAR} ({fmt(SB_REC_V)}).</text>')
    # centre / drier — top-right, under the sun
    p.append(f'<text x="{W - 40}" y="366" class="anno" fill="{DRY_D}" text-anchor="end">the centre dries out</text>')
    p.append(f'<text x="{W - 40}" y="400" class="bignum" fill="{DRY_D}" text-anchor="end">{n_dry}</text>')
    p.append(f'<text x="{W - 40}" y="416" class="biglab" text-anchor="end">TERRITORIES NOW DRIER</text>')
    p.append(f'<text x="{W - 40}" y="440" class="call" fill="{INK}" text-anchor="end">Nauru’s sky has turned</text>')
    p.append(f'<text x="{W - 40}" y="454" class="call" fill="{INK}" text-anchor="end">manic: <tspan fill="{WET_D}" font-weight="600">{fmt(NR_2019)} mm</tspan> in 2019,</text>')
    p.append(f'<text x="{W - 40}" y="468" class="call" fill="{INK}" text-anchor="end">its wettest year — then</text>')
    p.append(f'<text x="{W - 40}" y="482" class="call" fill="{INK}" text-anchor="end"><tspan fill="{DRY_D}" font-weight="600">{fmt(NR_2022)} mm</tspan> in 2022.</text>')
    return "".join(p)

# --- one quiet legend line at the foot ---------------------------------------------
def below():
    p = []
    y0 = 1118
    p.append(f'<line x1="60" y1="{y0 - 26}" x2="{W - 60}" y2="{y0 - 26}" stroke="{INK}" stroke-opacity="0.15" stroke-width="0.8"/>')
    x = 72
    p.append(f'<path d="{drop_path(x, y0 + 6, 5.5)}" fill="{WET}"/>')
    p.append(f'<text x="{x + 12}" y="{y0}" class="tiny" fill="{SUB}">flag-drop falling inward = gaining rain;</text>')
    p.append(f'<text x="{x + 12}" y="{y0 + 11}" class="tiny" fill="{SUB}">distance &amp; size = shift, avg 2020–25 vs 1979–2000</text>')
    x = 330
    p.append(f'<path d="{drop_path(x, y0, 5.5, up=True)}" fill="{DRY}" opacity="0.5"/>')
    p.append(f'<path d="{drop_path(x, y0, 5.5, up=True)}" fill="none" stroke="{DRY_D}" stroke-width="1" stroke-dasharray="2.5 2"/>')
    p.append(f'<text x="{x + 12}" y="{y0}" class="tiny" fill="{SUB}">faded drop rising = losing rain,</text>')
    p.append(f'<text x="{x + 12}" y="{y0 + 11}" class="tiny" fill="{SUB}">evaporating back into the sky</text>')
    x = 570
    for j, hw in enumerate((3, 6, 2, 7, 4)):
        c = WET if j in (1, 3) else DRY
        p.append(f'<line x1="{x - hw:.0f}" y1="{y0 - 5 + j * 5}" x2="{x + hw:.0f}" y2="{y0 - 5 + j * 5}" stroke="{c}" stroke-width="1"/>')
    p.append(f'<text x="{x + 13}" y="{y0}" class="tiny" fill="{SUB}">the nine biggest shifts carry a stem: one tick per year,</text>')
    p.append(f'<text x="{x + 13}" y="{y0 + 11}" class="tiny" fill="{SUB}">1979 at the ring → 2025 at the drop; width = anomaly</text>')
    return "".join(p)

# ================================================================= html ==========
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
  .cap    {{ font:400 10px 'Outfit',sans-serif; fill:{FAINT}; }}
  .bignum {{ font:700 27px 'Fraunces',Georgia,serif; }}
  .biglab {{ font:600 8.5px 'Outfit',sans-serif; letter-spacing:0.2em; fill:{SUB}; }}
  .anno   {{ font:italic 500 15.5px 'Fraunces',Georgia,serif; opacity:0.85; }}
  .call   {{ font:italic 400 11px 'Fraunces',Georgia,serif; }}
  .linelab{{ font:600 9.5px 'Outfit',sans-serif; letter-spacing:0.24em; fill:{INK}; }}
  .name   {{ font:600 12px 'Outfit',sans-serif; }}
  .val    {{ font:700 13px 'Outfit',sans-serif; }}
  .avg    {{ font:400 8.6px 'Outfit',sans-serif; }}
  .sname  {{ font:500 9.5px 'Outfit',sans-serif; }}
  .tiny   {{ font:400 9.3px 'Outfit',sans-serif; }}
  .tinyb  {{ font:600 9.3px 'Outfit',sans-serif; letter-spacing:0.16em; }}
  .rul    {{ font:400 8px 'Outfit',sans-serif; }}
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
  <text x="{W / 2}" y="48" class="kick" text-anchor="middle">PACIFIC DATAVIZ CHALLENGE 2026 · RAINFALL ANOMALIES · SPC PACIFIC DATA HUB · 1979→2025</text>
  <text x="{W / 2}" y="106" class="title" text-anchor="middle">Where the <tspan class="w">rain</tspan> went</text>
  <text x="{W / 2}" y="142" class="stand" text-anchor="middle">The climate crisis doesn’t just bring more heat — it redistributes the water.</text>
  <text x="{W / 2}" y="162" class="stand" text-anchor="middle">Compared with the rain they knew in 1979–2000, the same sky that now <tspan class="standb">floods the western Pacific</tspan></text>
  <text x="{W / 2}" y="182" class="stand" text-anchor="middle">is <tspan class="standb">emptying over the atolls of the centre</tspan>. Same ocean, different rain.</text>
  <text x="{W / 2}" y="206" class="cap" text-anchor="middle">22 territories in west → east order around the ring, one sector each · the ocean lies inside the ring, the sky outside</text>

  <!-- sky corners -->
  {corners()}

  <!-- artwork -->
  {ART}

  <!-- legend -->
  {below()}
</svg>
</div>
</body>
</html>
"""

OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html) / 1024:.0f} kB) · {n_wet} wetter / {n_dry} drier")
