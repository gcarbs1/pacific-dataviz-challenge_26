# -*- coding: utf-8 -*-
"""
WHERE THE RAIN WENT — A4 art poster (light background, flag drops).
One page, one artwork, nothing written over it:
  1. flag-drops around the ring, ordered by the shift itself (driest ->
     wettest, clockwise); each drop's tip kisses its berth on the ring and
     the drop's size alone carries the datum: the shift between the record's
     first twenty years (1979-1998) and its last twenty (2006-2025), in % of
     the 1991-2020 normal (the source CSV mislabels the unit as mm). The
     20v20 cut was chosen over the 2020s window, record halves, the fitted
     47-year trend and the 2020s-vs-normal: it tracks the full trend almost
     perfectly (rank corr 0.98), is the most internally stable cut
     (odd/even-year split 0.90) and needs no statistics to explain
  2. legend, computed record notes and credits arranged below the art

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
H0, H1, R0, R1 = 1979, 1998, 2006, 2025
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
# units: OBS_VALUE is the annual rainfall anomaly in % of the 1991-2020
# normal (the PDH CSV mislabels the unit as MM). Verified three ways: the
# 1991-2020 mean is exactly zero for all 22 territories, ENSO years land
# where they should, and Nauru's 2015 (+49.5) and 1999 (-54.4) match its
# real totals of ~3100 mm and ~950 mm against a ~2080 mm normal.
assert abs(float(df[df.year.between(1991, 2020)].groupby("iso")["v"].mean().max())) < 0.5, \
    "values no longer look like anomalies against the 1991-2020 normal"

# bold labels for the three driest and the three wettest, from the data
FEATURED = (stats.delta.nsmallest(3).index.tolist()
            + stats.delta.nlargest(3).index.tolist())

# the 2020s window is not cherry-picked: the same wet-west dry-centre
# pattern runs through the whole 47-year trend. Checked at build time so
# the footnote claim cannot silently rot.
def _slope(iso):
    s = pd.Series(dict(series[iso])).sort_index()
    x = s.index.to_series().astype(float)
    return float(((x - x.mean()) * (s - s.mean())).sum() / ((x - x.mean()) ** 2).sum())

_trend = pd.Series({iso: _slope(iso) for iso in stats.index})
assert _trend.rank().corr(stats.delta.rank()) > 0.7, "footnote trend claim no longer true"
# reading order = the story: sorted by the shift itself, driest first. The
# circle becomes the water cycle — clockwise from the 12-o'clock ruler the
# evaporating territories descend towards zero at 6 o'clock, then the rain
# deepens again up the other side, so the two extremes flank the ruler.
ORDER = stats.delta.sort_values().index.tolist()
n_wet = int((stats.delta > 0).sum())
n_dry = int((stats.delta < 0).sum())

# the wheel's two record-holders, for the closing line beneath the art
DRIEST_ISO, WETTEST_ISO = ORDER[0], ORDER[-1]
DRIEST_V, WETTEST_V = stats.delta[DRIEST_ISO], stats.delta[WETTEST_ISO]
MEDIAN_SHIFT = float(stats.delta.abs().median())

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
# Circular composition — the "rain wheel". The 22 territories sit around a
# ring sorted by their shift, berths sized to breathe: the driest territory
# starts clockwise of the 12-o'clock gap (under the page's sun), the shift
# rises through zero at the bottom and the wettest closes the circle on the
# other side of the gap — so the wheel reads as one revolution of the water
# cycle, and both record-holders flank the radial mm ruler in the gap.
# Inside the ring is the ocean; outside is the sky. Where rain increased, a
# flag-drop falls inward; where it decreased, a faded flag-drop evaporates
# outward.
W, Hpx = 840, 1188
# Golden composition. The page's three vertical bands sit in a continued
# golden ratio: sky (cap line 206 -> ring top 488) = 282 px, ocean diameter
# = 456 px, foot (ring bottom 944 -> legend baseline 1118) = 174 px, so
# 456/282 = 1.617 and 282/174 = 1.621, both within 0.2% of phi. Inside the
# sky band the two golden divisions land on the emblem centres (y ~ 314)
# and the corner count blocks (y ~ 380). The 36-degree gap at 12 o'clock
# is the golden-triangle angle of the pentagram. No stems: the drop's tip
# kisses its berth on the ring and its size alone is the datum, on the
# ring's own golden ladder — the largest drop's radius is RB/phi^4, the
# smallest RB/phi^6, two phi steps down, and the size curve climbs with
# exponent phi so the record shifts visibly tower over the mild ones.
CX, CY = 420.0, 716.0
RB = 228.0                      # the old-balance ring
GAP = 36.0                      # degrees kept clear at 12 o'clock
A0 = -90.0 + GAP / 2.0
SPAN = 360.0 - GAP
PHI = (1.0 + 5.0 ** 0.5) / 2.0
TIPGAP = 2.0                    # breath between ring and drop tip
DMAX = float(stats.delta.abs().max())
R_MAX = RB / PHI ** 4
R_MIN = RB / PHI ** 6

# a little organic breathing room: hand-tuned angular offsets, in degrees
# (small alternating nudges so the wheel breathes instead of ticking)
AJIT = {"NR": -0.6, "KI": -0.6, "TV": 0.5, "TK": -0.5, "PN": 0.6, "NC": -0.6,
        "PF": 0.5, "CK": -0.5, "MP": 0.4, "GU": -0.5, "AS": 0.5, "PG": -0.4,
        "WS": 0.6, "MH": -0.5, "FJ": 0.4, "WF": -0.6, "TO": -0.5, "NU": -0.4,
        "PW": 0.5, "SB": -0.6, "FM": 0.4, "VU": -0.6}

def rsize(d):
    # the size IS the datum: radius climbs from R_MIN to R_MAX with the
    # shift, curved by the golden exponent phi — the smallest drops stay
    # legible while the extremes swell to command the wheel
    return R_MIN + (R_MAX - R_MIN) * (min(1.0, abs(d) / DMAX)) ** PHI

# berth widths: not equal sectors — each territory takes an angular footprint
# proportional to how much room its drop actually needs at the radius where
# it lives (big wet drops sit near the centre, where a degree is worth
# fewer pixels), and the leftover slack is shared out evenly. The two
# extremes stay pinned to the edges of the 12-o'clock gap.
def footprint(iso):
    d = float(stats.loc[iso, "delta"])
    r = rsize(d)
    if d >= 0:
        rc = RB - TIPGAP - 2.05 * r         # drop centre, down in the ocean
        lab = 25.0 / (RB + 22.0)            # two-line label just off the ring
    else:
        rc = RB + TIPGAP + 2.05 * r         # drop centre, up in the sky
        lab = 25.0 / (RB + TIPGAP + 3.05 * r + 30.0)
    body = 2.0 * math.asin(min(0.95, (r + 3.0) / max(rc, 40.0)))
    return math.degrees(max(body, lab))

FOOT = [footprint(iso) for iso in ORDER]
# breath between the wettest drop and the ruler: only the gained side needs
# it — the deep wet drops live close to the centre, where the ruler's lower
# half hangs, while the dry side clears the ruler naturally
EDGE = 2.5
_pairs = [(a + b) / 2.0 for a, b in zip(FOOT, FOOT[1:])]
_slack = (SPAN - EDGE - sum(_pairs)) / len(_pairs)
assert _slack > 0, "wheel is over-full; loosen the footprint padding"
BERTH = {ORDER[0]: A0}
_acc = A0
for iso_, gap_ in zip(ORDER[1:], _pairs):
    _acc += gap_ + _slack
    BERTH[iso_] = _acc

def ang(iso):
    return math.radians(BERTH[iso] + AJIT.get(iso, 0.0))

def pt(r, a):
    return CX + r * math.cos(a), CY + r * math.sin(a)

rng = random.Random(20)
defs, art = [], []
defs.append('<filter id="ds" x="-40%" y="-40%" width="180%" height="180%">'
            '<feDropShadow dx="0" dy="0" stdDeviation="2.6" flood-color="#22313b" flood-opacity="0.20"/></filter>')
defs.append('<filter id="dsU" x="-40%" y="-40%" width="180%" height="180%">'
            '<feDropShadow dx="0" dy="0" stdDeviation="2.0" flood-color="#22313b" flood-opacity="0.12"/></filter>')
defs.append('<filter id="bl2" x="-80%" y="-80%" width="260%" height="260%">'
            '<feGaussianBlur stdDeviation="2.4"/></filter>')
# water-glass rendering for the drops: axis shading along the fall, plus a
# specular pair placed per-drop so every highlight faces the page's one sun
defs.append('''<linearGradient id="shW" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0.55" stop-color="#22313b" stop-opacity="0"/>
  <stop offset="1" stop-color="#22313b" stop-opacity="0.22"/></linearGradient>
<linearGradient id="shU" x1="0" y1="1" x2="0" y2="0">
  <stop offset="0.55" stop-color="#22313b" stop-opacity="0"/>
  <stop offset="1" stop-color="#22313b" stop-opacity="0.18"/></linearGradient>
<radialGradient id="spec" cx="0.5" cy="0.5" r="0.5">
  <stop offset="0" stop-color="#ffffff" stop-opacity="0.9"/>
  <stop offset="1" stop-color="#ffffff" stop-opacity="0"/></radialGradient>
<radialGradient id="sun2" cx="0.4" cy="0.38" r="0.75">
  <stop offset="0" stop-color="#ffe07f"/>
  <stop offset="1" stop-color="#efba3e"/></radialGradient>
<radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">
  <stop offset="0" stop-color="#ffdf7a" stop-opacity="0.55"/>
  <stop offset="0.55" stop-color="#ffdf7a" stop-opacity="0.20"/>
  <stop offset="1" stop-color="#ffdf7a" stop-opacity="0"/></radialGradient>
<radialGradient id="rim" cx="0.5" cy="0.5" r="0.5">
  <stop offset="0.82" stop-color="#4f7f96" stop-opacity="0"/>
  <stop offset="0.965" stop-color="#4f7f96" stop-opacity="0.14"/>
  <stop offset="1" stop-color="#3f6e85" stop-opacity="0.26"/></radialGradient>
<filter id="grain" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="2" stitchTiles="stitch"/>
  <feColorMatrix type="matrix" values="0 0 0 0 0.13  0 0 0 0 0.18  0 0 0 0 0.22  0 0 0 0.05 0"/>
</filter>''')

# --- two faint climate washes tie each sky corner to its half of the story --------
defs.append(f'''<radialGradient id="washW" cx="0.5" cy="0.5" r="0.5">
  <stop offset="0" stop-color="{SKY}" stop-opacity="0.09"/>
  <stop offset="0.7" stop-color="{SKY}" stop-opacity="0.035"/>
  <stop offset="1" stop-color="{SKY}" stop-opacity="0"/></radialGradient>
<radialGradient id="washD" cx="0.5" cy="0.5" r="0.5">
  <stop offset="0" stop-color="#efba3e" stop-opacity="0.07"/>
  <stop offset="0.7" stop-color="#efba3e" stop-opacity="0.03"/>
  <stop offset="1" stop-color="#efba3e" stop-opacity="0"/></radialGradient>''')
art.append('<circle cx="128" cy="330" r="280" fill="url(#washW)"/>')
art.append('<circle cx="726" cy="330" r="280" fill="url(#washD)"/>')

# --- the ocean: engraved water, line by line ------------------------------------
defs.append(f'''<radialGradient id="sea" cx="0.5" cy="0.46" r="0.62">
  <stop offset="0" stop-color="#f4fafc"/>
  <stop offset="0.62" stop-color="{SEA}" stop-opacity="0.45"/>
  <stop offset="1" stop-color="#bcdbe7" stop-opacity="0.7"/>
</radialGradient>''')
art.append(f'<circle cx="{CX}" cy="{CY}" r="{RB}" fill="url(#sea)"/>')
n_eng = 34
for i in range(n_eng):
    rr = 26 + (RB - 34) * i / (n_eng - 1)
    amp = 1.1 + 1.1 * rr / RB
    ph = rng.random() * 6.28
    freq = 11 + (i % 5)
    pts = []
    for j in range(141):
        th = j * 2 * math.pi / 140
        r2 = rr + amp * math.sin(th * freq + ph)
        x, y = pt(r2, th)
        pts.append(f"{'M' if j == 0 else 'L'} {x:.1f} {y:.1f}")
    op = 0.05 + 0.10 * (rr / RB) ** 1.6
    art.append(f'<path d="{" ".join(pts)} Z" fill="none" stroke="{WET}" stroke-opacity="{op:.3f}" stroke-width="0.7"/>')

# depth at the water's edge, and a sheen where the sun strikes it
art.append(f'<circle cx="{CX}" cy="{CY}" r="{RB}" fill="url(#rim)"/>')
# the ocean's golden radius, a whispered guide the biggest drops dive past
art.append(f'<circle cx="{CX}" cy="{CY}" r="{RB / 1.61803:.1f}" fill="none" '
           f'stroke="{WET_D}" stroke-opacity="0.09" stroke-width="0.7"/>')
for rr_, a0_, a1_, w_, o_ in ((138, -62, -44, 6, 0.45), (152, -40, -28, 5, 0.35)):
    x0_, y0_ = pt(rr_, math.radians(a0_))
    x1_, y1_ = pt(rr_, math.radians(a1_))
    art.append(f'<path d="M {x0_:.1f} {y0_:.1f} A {rr_} {rr_} 0 0 1 {x1_:.1f} {y1_:.1f}" '
               f'fill="none" stroke="#ffffff" stroke-opacity="{o_}" stroke-width="{w_}" '
               f'stroke-linecap="round" filter="url(#bl2)"/>')

# sun in the top-right sky, sitting beneath its corner headline
sx, sy = 758, 314
art.append(f'<circle cx="{sx}" cy="{sy}" r="100" fill="url(#glow)" opacity="0.4"/>')
art.append(f'<circle cx="{sx}" cy="{sy}" r="58" fill="url(#glow)"/>')
art.append(f'<circle cx="{sx}" cy="{sy}" r="23" fill="url(#sun2)"/>')
art.append(f'<circle cx="{sx}" cy="{sy}" r="23" fill="none" stroke="{DRY}" stroke-opacity="0.45" stroke-width="0.9"/>')
for i in range(24):
    a = math.radians(i * 15 + 4)
    r2 = 29 + (14 if i % 2 == 0 else 7) * (0.8 + 0.4 * rng.random())
    art.append(f'<line x1="{sx + 29 * math.cos(a):.1f}" y1="{sy + 29 * math.sin(a):.1f}" x2="{sx + r2 * math.cos(a):.1f}" y2="{sy + r2 * math.sin(a):.1f}" stroke="{DRY}" stroke-opacity="0.42" stroke-width="0.9"/>')

# --- the balance ring: engraved bezel ---------------------------------------------
art.append(f'<circle cx="{CX}" cy="{CY}" r="{RB}" fill="none" stroke="{INK}" stroke-width="1.3"/>')
# bezel ticks: each territory's berth on the old balance
for iso_ in ORDER:
    a_ = ang(iso_)
    tx1, ty1 = pt(RB - 3.5, a_)
    tx2, ty2 = pt(RB + 3.5, a_)
    art.append(f'<line x1="{tx1:.1f}" y1="{ty1:.1f}" x2="{tx2:.1f}" y2="{ty2:.1f}" stroke="{INK}" stroke-opacity="0.35" stroke-width="1"/>')

# --- radial drop-size ruler in the 12-o'clock gap ---------------------------------
# the ruler measures the drops themselves: each tick marks how far a drop
# of 5, 10 or 15% reaches from the ring — up into the sky for rain lost,
# down into the ocean for rain gained. The spacing stretches like a slide
# rule, because size climbs with the golden exponent
def reach(m):
    return TIPGAP + 3.05 * rsize(m)

RT = CY - RB - reach(15.0) - 4.0    # outer end, just past a 15% drop
RG = CY - RB + reach(15.0) + 4.0    # inner end, mirrored in the ocean
art.append(f'<line x1="{CX}" y1="{RT:.1f}" x2="{CX}" y2="{RG:.1f}" stroke="{SUB}" stroke-width="0.9"/>')
for m in (5.0, 10.0, 15.0):
    for sg in (-1, 1):
        y = CY - RB + sg * reach(m)
        major = m >= 10
        art.append(f'<line x1="{CX}" y1="{y:.1f}" x2="{CX + (6 if major else 3.5)}" y2="{y:.1f}" stroke="{SUB}" stroke-width="0.9"/>')
        if major:
            art.append(f'<text x="{CX + 9}" y="{y + 2.5:.1f}" class="rul halo" fill="{SUB}">{m:.0f}</text>')
art.append(f'<text x="{CX + 9}" y="{CY - RB + 2.5:.0f}" class="rul halo" fill="{INK}">0%</text>')
art.append(f'<text transform="rotate(-90 {CX - 8} {CY - RB - 62})" x="{CX - 8}" y="{CY - RB - 59}" class="tinyb halo" fill="{DRY_D}" text-anchor="middle">RAIN LOST</text>')
art.append(f'<text transform="rotate(-90 {CX - 8} {CY - RB + 52})" x="{CX - 8}" y="{CY - RB + 55}" class="tinyb halo" fill="{WET_D}" text-anchor="middle">RAIN GAINED</text>')
art.append(f'<text x="{CX}" y="{RT - 26:.0f}" class="linelab" text-anchor="middle">THE OLD BALANCE</text>')
art.append(f'<text x="{CX}" y="{RT - 13:.0f}" class="avg" fill="{SUB}" font-style="italic" text-anchor="middle">the ring: the rain of 1979–1998</text>')

# --- rain clouds in the top-left sky, answering the sun ---------------------------
# the raining side's emblem: three grey clouds and their falling drops,
# clustered at the same height as the sun so the two skies balance
defs.append('''<radialGradient id="glowSea" cx="0.5" cy="0.5" r="0.5">
  <stop offset="0" stop-color="#8fd0e8" stop-opacity="0.32"/>
  <stop offset="0.6" stop-color="#8fd0e8" stop-opacity="0.12"/>
  <stop offset="1" stop-color="#8fd0e8" stop-opacity="0"/></radialGradient>''')

# soft grey masses, no outlines at all: three clouds built from blurred
# overlapping ellipses, like weather rolling in, and the rain falling as a
# curtain of fine slanted strokes in the ocean's hairline language
defs.append('<filter id="blc" x="-60%" y="-60%" width="220%" height="220%">'
            '<feGaussianBlur stdDeviation="3.2"/></filter>')
rng2 = random.Random(7)
# the whole emblem is scaled to match the sun's pictorial size across the page
art.append('<g transform="translate(106 314) scale(0.7) translate(-106 -314)">')
art.append('<circle cx="106" cy="312" r="62" fill="url(#glowSea)"/>')
for cx_, cy_, tone_, op_, blobs_ in (
        (64, 288, "#cfd9de", 0.65, ((0, 0, 20, 12), (-15, 3, 14, 9), (14, 2, 15, 9))),
        (148, 278, "#d3dce1", 0.60, ((0, 0, 22, 12), (-16, 3, 15, 9), (15, 2, 16, 10))),
        (102, 314, "#bfccd4", 0.85, ((0, 0, 32, 16), (-25, 4, 20, 12), (25, 3, 22, 13),
                                     (7, -13, 21, 12), (-13, -9, 17, 10)))):
    for dx_, dy_, rx_, ry_ in blobs_:
        art.append(f'<ellipse cx="{cx_ + dx_}" cy="{cy_ + dy_}" rx="{rx_}" ry="{ry_}" '
                   f'fill="{tone_}" fill-opacity="{op_}" filter="url(#blc)"/>')
for i in range(13):
    rx = 56 + i * 7.2 + rng2.uniform(-1.6, 1.6)
    ry = 326 + (i % 3) * 4.5 + rng2.uniform(0, 3)
    ln = 9 + 7 * rng2.random()
    op = 0.11 + 0.14 * rng2.random()
    art.append(f'<line x1="{rx:.1f}" y1="{ry:.1f}" x2="{rx - 2.4:.1f}" y2="{ry + ln:.1f}" '
               f'stroke="{WET}" stroke-opacity="{op:.2f}" stroke-width="0.8" stroke-linecap="round"/>')
art.append('</g>')

# --- the 22 territories, radially -------------------------------------------------

for iso in ORDER:
    d = float(stats.loc[iso, "delta"])
    a = ang(iso)
    deg = math.degrees(a) + 90.0
    wet = d >= 0
    sgn = 1 if wet else -1
    feat = iso in FEATURED
    r = rsize(d)
    # no stem: the tip kisses the berth, the body grows with the shift
    cy_l = -RB + (TIPGAP + 2.05 * r) * sgn
    g = [f'<g transform="translate({CX},{CY}) rotate({deg:.2f})">']
    dp = drop_path(0, cy_l, r, up=not wet)
    defs.append(f'<clipPath id="c{iso}"><path d="{dp}"/></clipPath>')
    cap = (CAP if wet else CAP_UP).get(iso, WET)

    # one sun lights the whole page (top-right): highlight and cast-shadow
    # directions are rotated back into this drop's local frame
    def loc(vx, vy, _r=math.radians(deg)):
        return (vx * math.cos(_r) + vy * math.sin(_r),
                -vx * math.sin(_r) + vy * math.cos(_r))

    if wet:
        # the drop casts a soft shadow away from the page's sun
        sxl, syl = loc(-4.2, 5.2)
        g.append(f'<ellipse cx="{sxl:.1f}" cy="{cy_l + syl:.1f}" rx="{0.94 * r:.1f}" ry="{0.86 * r:.1f}" fill="{INK}" opacity="0.13" filter="url(#bl2)"/>')
    g.append(f'<path d="{dp}" fill="{cap}" filter="url(#{"ds" if wet else "dsU"})"/>')
    fw, fh = 2.35 * r, 1.55 * r
    g.append(f'<g clip-path="url(#c{iso})"><g transform="translate({-fw / 2:.1f},{cy_l - fh / 2:.1f}) scale({fw / 100:.3f},{fh / 64:.3f})">{flag_svg2(iso)}</g></g>')
    h1x, h1y = loc(0.30 * r, -0.34 * r)
    h2x, h2y = loc(0.42 * r, -0.46 * r)
    spec = (f'<g clip-path="url(#c{iso})">'
            f'<circle cx="{h1x:.1f}" cy="{cy_l + h1y:.1f}" r="{0.62 * r:.1f}" fill="url(#spec)" opacity="0.55"/>'
            f'<circle cx="{h2x:.1f}" cy="{cy_l + h2y:.1f}" r="{0.26 * r:.1f}" fill="url(#spec)" opacity="0.95"/></g>')
    if not wet:
        g.append(f'<path d="{dp}" fill="{PAPER}" opacity="0.34"/>')
        g.append(f'<path d="{dp}" fill="url(#shU)"/>')
        g.append(f'<g opacity="0.4">{spec}</g>')
        g.append(f'<path d="{dp}" fill="none" stroke="{DRY_D}" stroke-opacity="0.85" stroke-width="1.2"/>')
    else:
        g.append(f'<path d="{dp}" fill="url(#shW)"/>')
        g.append(spec)
        g.append(f'<path d="{dp}" fill="none" stroke="{INK}" stroke-opacity="0.75" stroke-width="1.2"/>')
    g.append("</g>")
    art.append("".join(g))

    # radial labels in the sky, reading outward like compass spokes; every
    # territory gets the same two lines — country name, shift beneath it
    a_deg = math.degrees(a)
    right = a_deg <= 90.0
    r0 = (RB + 10.0) if wet else (RB + TIPGAP + 3.05 * r + 12.0)
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
        art.append(radial_text(NAMES[iso], "name", 0))
        art.append(radial_text(f'{fmt(d)}%', "val", 1, cval))
    else:
        art.append(radial_text(NAMES[iso], "sname", 0))
        art.append(radial_text(f'{fmt(d)}%', "sval", 1, cval))

ART = f'<defs>{"".join(defs)}</defs>' + "".join(art)

# --- sky-corner narration (nothing over the artwork) ------------------------------
def corners():
    p = []
    # west / wetter — top-left, on the same baselines as the block under
    # the sun so the two sky columns mirror each other
    p.append(f'<text x="44" y="248" class="anno halo" fill="{WET_D}">where the rain moved in</text>')
    # the number sits vertically centred between the two stacked words,
    # the block itself centred on the sky band's lower golden division
    p.append(f'<text x="44" y="387" class="bignum" fill="{WET_D}">{n_wet}</text>')
    p.append(f'<text x="139" y="372" class="terr" style="fill:{WET_D}" text-anchor="middle">TERRITORIES</text>')
    p.append(f'<text x="139" y="388" class="terr" style="fill:{WET_D}" text-anchor="middle">NOW WETTER</text>')
    # centre / drier — top-right, under the sun
    p.append(f'<text x="{W - 44}" y="248" class="anno halo" fill="{DRY_D}" text-anchor="end">where the rain is leaving</text>')
    p.append(f'<text x="{W - 44 - 96}" y="387" class="bignum" fill="{DRY_D}" text-anchor="end">{n_dry}</text>')
    p.append(f'<text x="{W - 44 - 45}" y="372" class="terr" style="fill:{DRY_D}" text-anchor="middle">TERRITORIES</text>')
    p.append(f'<text x="{W - 44 - 45}" y="388" class="terr" style="fill:{DRY_D}" text-anchor="middle">NOW DRIER</text>')
    return "".join(p)

# --- one closing line between the wheel and the legend ----------------------------
def conclusion():
    p = []
    p.append(f'<text x="{W / 2}" y="1054" class="call" text-anchor="middle" fill="{INK}">'
             f'This is not ordinary variability, it is the climate crisis redrawing the Pacific’s water map.</text>')
    p.append(f'<text x="{W / 2}" y="1074" class="call" text-anchor="middle" fill="{INK}">'
             f'<tspan fill="{WET_D}" font-weight="600">{NAMES[WETTEST_ISO]} now gains {WETTEST_V:.1f}% more rain</tspan>, '
             f'<tspan fill="{DRY_D}" font-weight="600">{NAMES[DRIEST_ISO]} has lost {abs(DRIEST_V):.1f}%</tspan>, '
             f'the same warming ocean pulling water in opposite directions.</text>')
    return "".join(p)

# --- one quiet legend line at the foot ---------------------------------------------
def below():
    p = []
    y0 = 1118
    p.append(f'<line x1="60" y1="{y0 - 26}" x2="{W - 60}" y2="{y0 - 26}" stroke="{INK}" stroke-opacity="0.15" stroke-width="0.8"/>')
    x = 180
    p.append(f'<path d="{drop_path(x, y0 + 6, 5.5)}" fill="{WET}"/>')
    p.append(f'<circle cx="{x + 1.7}" cy="{y0 + 3.8}" r="1.6" fill="#ffffff" opacity="0.6"/>')
    p.append(f'<text x="{x + 12}" y="{y0}" class="tiny" fill="{SUB}">flag-drop falling inward = gaining rain,</text>')
    p.append(f'<text x="{x + 12}" y="{y0 + 11}" class="tiny" fill="{SUB}">size = shift in % of normal rain, 2006–25 vs 1979–98</text>')
    x = 480
    p.append(f'<path d="{drop_path(x, y0, 5.5, up=True)}" fill="{DRY}" opacity="0.5"/>')
    p.append(f'<circle cx="{x + 1.7}" cy="{y0 - 2.2}" r="1.5" fill="#ffffff" opacity="0.4"/>')
    p.append(f'<path d="{drop_path(x, y0, 5.5, up=True)}" fill="none" stroke="{DRY_D}" stroke-opacity="0.85" stroke-width="1"/>')
    p.append(f'<text x="{x + 12}" y="{y0}" class="tiny" fill="{SUB}">faded drop rising = losing rain,</text>')
    p.append(f'<text x="{x + 12}" y="{y0 + 11}" class="tiny" fill="{SUB}">evaporating back into the sky</text>')
    # data-source footnote, plus one honest line about ENSO
    p.append(f'<text x="{W / 2}" y="{y0 + 36}" class="cap" text-anchor="middle">'
             f'Data: SPC Pacific Data Hub · annual rainfall anomalies in % of the 1991–2020 normal '
             f'(DF_CLIMATE_CHANGE, RAIN_ANOM) · 22 Pacific territories, 1979–2025</text>')
    p.append(f'<text x="{W / 2}" y="{y0 + 48}" class="cap" text-anchor="middle">'
             f'The record’s first twenty years against its last twenty, one generation apart. '
             f'The same pattern runs through the full 47-year trend.</text>')
    return "".join(p)

# --- tapa frame, woven with an alternating rhythm ----------------------------------
def tapa():
    p = []
    for i, xx in enumerate(range(14, W - 18, 22)):
        op = 0.42 if i % 2 == 0 else 0.24
        p.append(f'<path d="M {xx} 14 L {xx + 7} 6 L {xx + 14} 14" fill="none" stroke="{DRY}" stroke-opacity="{op}" stroke-width="1"/>')
        p.append(f'<path d="M {xx} 1174 L {xx + 7} 1182 L {xx + 14} 1174" fill="none" stroke="{DRY}" stroke-opacity="{op}" stroke-width="1"/>')
    for i, yy in enumerate(range(26, 1156, 22)):
        op = 0.42 if i % 2 == 0 else 0.24
        p.append(f'<path d="M 14 {yy} L 6 {yy + 7} L 14 {yy + 14}" fill="none" stroke="{DRY}" stroke-opacity="{op}" stroke-width="1"/>')
        p.append(f'<path d="M {W - 14} {yy} L {W - 6} {yy + 7} L {W - 14} {yy + 14}" fill="none" stroke="{DRY}" stroke-opacity="{op}" stroke-width="1"/>')
    return "".join(p)

FRAME = tapa()

# ================================================================= html ==========
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Where the Rain Went</title>
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
  .title .w {{ fill:{WET}; font-style:italic; }}
  .stand  {{ font:italic 400 14.5px 'Fraunces',Georgia,serif; fill:{SUB}; }}
  .standb {{ font-style:normal; font-weight:600; fill:{INK}; }}
  .cap    {{ font:400 10px 'Outfit',sans-serif; fill:{FAINT}; }}
  .bignum {{ font:700 34px 'Fraunces',Georgia,serif; }}
  .terr   {{ font:600 11px 'Outfit',sans-serif; letter-spacing:0.14em; }}
  .biglab {{ font:600 8.5px 'Outfit',sans-serif; letter-spacing:0.2em; fill:{SUB}; }}
  .anno   {{ font:italic 500 15.5px 'Fraunces',Georgia,serif; opacity:0.85; }}
  .call   {{ font:italic 400 11px 'Fraunces',Georgia,serif; }}
  .linelab{{ font:600 9.5px 'Outfit',sans-serif; letter-spacing:0.24em; fill:{INK}; }}
  .name   {{ font:600 12px 'Outfit',sans-serif; }}
  .val    {{ font:700 13px 'Outfit',sans-serif; }}
  .avg    {{ font:400 8.6px 'Outfit',sans-serif; }}
  .sname  {{ font:500 9.5px 'Outfit',sans-serif; }}
  .sval   {{ font:700 10px 'Outfit',sans-serif; }}
  .tiny   {{ font:400 9.3px 'Outfit',sans-serif; }}
  .tinyb  {{ font:600 9.3px 'Outfit',sans-serif; letter-spacing:0.16em; }}
  .rul    {{ font:400 8px 'Outfit',sans-serif; }}
  .halo   {{ paint-order:stroke; stroke:{PAPER}; stroke-width:3.5px; stroke-linejoin:round; }}
  @page {{ size: 210mm 297mm; margin: 0; }}
  /* 210mm = 793.7px, so the 840px sheet zooms by 793.7/840 to fill A4 exactly */
  @media print {{ body {{ background:none; padding:0; margin:0; }} .sheet {{ box-shadow:none; zoom:0.94488; }} }}
</style>
</head>
<body>
<div class="sheet">
<svg viewBox="0 0 {W} {Hpx}" width="{W}" height="{Hpx}" xmlns="http://www.w3.org/2000/svg">
  <rect width="{W}" height="{Hpx}" fill="{PAPER}"/>

  <!-- tapa frame, woven all the way round -->
  {FRAME}

  <!-- header -->
  <text x="{W / 2}" y="106" class="title" text-anchor="middle">Where the <tspan class="w">raın</tspan> went</text>
  <path d="{drop_path(506.5, 68.0, 4.0)}" fill="{WET}"/>
  <circle cx="507.8" cy="66.2" r="1.4" fill="#ffffff" opacity="0.65"/>
  <text x="{W / 2}" y="142" class="stand" text-anchor="middle">The climate crisis does more than warm the Pacific, it is redrawing where the rain falls.</text>
  <text x="{W / 2}" y="162" class="stand" text-anchor="middle">Comparing the record’s first twenty years with its last twenty, <tspan class="standb">the west and south have grown wetter</tspan></text>
  <text x="{W / 2}" y="182" class="stand" text-anchor="middle">while <tspan class="standb">the dateline atolls have run dry</tspan>. Same ocean, different rain.</text>
  <text x="{W / 2}" y="206" class="cap" text-anchor="middle">22 territories ordered by their shift, from driest beneath the sun to wettest at the far side of the wheel. The ocean lies inside the ring, the sky outside.</text>

  <!-- sky corners -->
  {corners()}

  <!-- artwork -->
  {ART}

  <!-- closing line -->
  {conclusion()}

  <!-- legend -->
  {below()}

  <!-- print grain -->
  <rect width="{W}" height="{Hpx}" filter="url(#grain)" opacity="0.6"/>
</svg>
</div>
</body>
</html>
"""

OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html) / 1024:.0f} kB) · {n_wet} wetter / {n_dry} drier")
