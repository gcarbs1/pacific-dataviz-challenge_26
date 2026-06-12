# -*- coding: utf-8 -*-
"""
WHERE THE RAIN WENT — Pacific Dataviz Challenge 2026
Builds a single long-form static page (poster/index.html) from
data/rainfall_anomalies/data.csv (SPC Pacific Data Hub, DF_CLIMATE_CHANGE).

Comparison windows: 1979-2000 (historical) vs 2020-2025 (recent).
"""
import math
import random
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / "index.html"

# ---------------------------------------------------------------- data ------
df = pd.read_csv(ROOT / "data" / "rainfall_anomalies" / "data.csv")
df = df[["GEO_PICT", "TIME_PERIOD", "OBS_VALUE"]].rename(
    columns={"GEO_PICT": "iso", "TIME_PERIOD": "year", "OBS_VALUE": "v"}
)

H0, H1 = 1979, 2000   # historical window
R0, R1 = 2020, 2025   # recent window

hist = df[df.year.between(H0, H1)].groupby("iso")["v"].mean()
rec = df[df.year.between(R0, R1)].groupby("iso")["v"].mean()
stats = pd.DataFrame({"hist": hist, "rec": rec})
stats["delta"] = stats["rec"] - stats["hist"]
stats = stats.sort_values("delta", ascending=False)

series = {iso: g.sort_values("year") for iso, g in df.groupby("iso")}

NAMES = {
    "FM": "Micronesia (FSM)", "SB": "Solomon Islands", "VU": "Vanuatu",
    "PW": "Palau", "TO": "Tonga", "NU": "Niue", "WF": "Wallis & Futuna",
    "MH": "Marshall Islands", "FJ": "Fiji", "WS": "Samoa",
    "PG": "Papua New Guinea", "AS": "American Samoa", "GU": "Guam",
    "MP": "Northern Marianas", "CK": "Cook Islands", "PF": "French Polynesia",
    "PN": "Pitcairn", "TK": "Tokelau", "NC": "New Caledonia",
    "KI": "Kiribati", "TV": "Tuvalu", "NR": "Nauru",
}
FEAT_WET = ["FM", "SB", "VU", "PW"]
FEAT_DRY = ["NR", "TV", "KI", "NC", "TK"]
FEATURED = FEAT_WET + FEAT_DRY

n_wetter = int((stats.delta > 0).sum())
n_drier = int((stats.delta < 0).sum())

# ------------------------------------------------------------- palette ------
BG0, BG1 = "#050b13", "#0a1521"
INK = "#eaf2f5"
SUB = "#9db1bd"
FAINT = "#5e7585"
WET, WET_HI, WET_DEEP = "#3fc1d9", "#8df0ff", "#15607d"
DRY, DRY_HI, DRY_DEEP = "#d9a258", "#f2cf8f", "#8a5a28"
ALARM = "#e8original"  # placeholder guard (unused)
ALARM = "#ee8a5f"

def col(delta):
    return WET if delta >= 0 else DRY

def fmt(v, signed=True):
    s = f"{v:+.1f}" if signed else f"{v:.1f}"
    return s.replace("-", "−")  # proper minus sign

# ---------------------------------------------------------------- helpers ---
def dodge(ys, gap, lo, hi):
    """Push labels apart vertically; ys is a list (will be returned adjusted)."""
    order = sorted(range(len(ys)), key=lambda i: ys[i])
    adj = [ys[i] for i in order]
    for i in range(1, len(adj)):
        adj[i] = max(adj[i], adj[i - 1] + gap)
    over = adj[-1] - hi
    if over > 0:
        for i in range(len(adj)):
            adj[i] -= over
        for i in range(len(adj) - 2, -1, -1):
            adj[i] = min(adj[i], adj[i + 1] - gap)
        for i in range(len(adj)):
            adj[i] = max(adj[i], lo + i * 0)
    out = [0.0] * len(ys)
    for k, i in enumerate(order):
        out[i] = adj[k]
    return out

def drop_path(cx, cy, r, up=False):
    """Teardrop: round bulb radius r centred (cx,cy), tip above (or below if up)."""
    s = -1 if up else 1
    tip = cy - s * 2.05 * r
    return (
        f"M {cx:.1f} {tip:.1f} "
        f"C {cx + 0.55 * r:.1f} {cy - s * 1.1 * r:.1f} {cx + r:.1f} {cy - s * 0.45 * r:.1f} {cx + r:.1f} {cy:.1f} "
        f"A {r:.1f} {r:.1f} 0 1 {1 if s == 1 else 0} {cx - r:.1f} {cy:.1f} "
        f"C {cx - r:.1f} {cy - s * 0.45 * r:.1f} {cx - 0.55 * r:.1f} {cy - s * 1.1 * r:.1f} {cx:.1f} {tip:.1f} Z"
    )

# ================================================================ HERO ======
def hero_svg():
    rng = random.Random(7)
    W, H = 1180, 560
    p = [f'<svg class="block" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="A water drop split in two: one half full, one half empty">']
    p.append(f'''<defs>
      <linearGradient id="hsky" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="{BG0}"/><stop offset="1" stop-color="{BG1}"/>
      </linearGradient>
      <linearGradient id="hwet" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="{WET_HI}"/><stop offset="0.55" stop-color="{WET}"/><stop offset="1" stop-color="{WET_DEEP}"/>
      </linearGradient>
      <radialGradient id="hglow" cx="0.5" cy="0.45" r="0.65">
        <stop offset="0" stop-color="{WET}" stop-opacity="0.30"/><stop offset="1" stop-color="{WET}" stop-opacity="0"/>
      </radialGradient>
      <radialGradient id="hglow2" cx="0.5" cy="0.45" r="0.65">
        <stop offset="0" stop-color="{DRY}" stop-opacity="0.16"/><stop offset="1" stop-color="{DRY}" stop-opacity="0"/>
      </radialGradient>
      <clipPath id="cutL"><rect x="0" y="0" width="{W/2}" height="{H}"/></clipPath>
      <clipPath id="cutR"><rect x="{W/2}" y="0" width="{W/2}" height="{H}"/></clipPath>
    </defs>''')
    p.append(f'<rect width="{W}" height="{H}" fill="url(#hsky)"/>')

    # rain field: teal streaks dense on the left, fading to sparse amber dashes right
    for _ in range(560):
        x = rng.random() ** 0.9 * W
        t = x / W
        keep_wet = rng.random() > t * 1.12
        y = rng.random() * H
        if keep_wet:
            ln = 7 + rng.random() * 22 * (1 - 0.5 * t)
            op = 0.06 + rng.random() * 0.30 * (1 - t)
            p.append(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x + 2:.0f}" y2="{y + ln:.0f}" stroke="{WET}" stroke-opacity="{op:.2f}" stroke-width="1.1" stroke-linecap="round"/>')
        elif rng.random() < (t - 0.18):
            op = 0.05 + rng.random() * 0.22
            p.append(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x + 4:.0f}" y2="{y + 3:.0f}" stroke="{DRY}" stroke-opacity="{op:.2f}" stroke-width="1.1" stroke-linecap="round"/>')

    cx, cy, r = W / 2, H * 0.52, 118
    p.append(f'<ellipse cx="{cx - 130}" cy="{cy}" rx="430" ry="300" fill="url(#hglow)"/>')
    p.append(f'<ellipse cx="{cx + 150}" cy="{cy}" rx="380" ry="280" fill="url(#hglow2)"/>')

    d = drop_path(cx, cy, r)
    # left half: full of water
    p.append(f'<g clip-path="url(#cutL)"><path d="{d}" fill="url(#hwet)"/>'
             f'<path d="{d}" fill="none" stroke="{WET_HI}" stroke-opacity="0.8" stroke-width="1.4"/>'
             f'<ellipse cx="{cx - 42}" cy="{cy - 58}" rx="14" ry="30" fill="#ffffff" opacity="0.30" transform="rotate(18 {cx - 42} {cy - 58})"/></g>')
    # right half: empty outline, draining away as dashes
    p.append(f'<g clip-path="url(#cutR)"><path d="{d}" fill="none" stroke="{DRY}" stroke-width="1.6" stroke-dasharray="7 6" stroke-opacity="0.95"/>')
    for i in range(4):
        yy = cy - 60 + i * 38
        p.append(f'<line x1="{cx + r + 16 + i * 9}" y1="{yy}" x2="{cx + r + 52 + i * 16}" y2="{yy - 14}" stroke="{DRY}" stroke-opacity="{0.55 - i * 0.1:.2f}" stroke-width="1.3" stroke-linecap="round"/>')
    p.append('</g>')
    # split seam
    p.append(f'<line x1="{cx}" y1="{cy - 2.2 * r - 26}" x2="{cx}" y2="{cy + r + 30}" stroke="{INK}" stroke-opacity="0.5" stroke-width="1" stroke-dasharray="2 5"/>')
    p.append(f'<text x="{cx - 138}" y="{cy + r + 46}" class="t-tag" fill="{WET}" text-anchor="middle">EXCESS</text>')
    p.append(f'<text x="{cx + 138}" y="{cy + r + 46}" class="t-tag" fill="{DRY}" text-anchor="middle">SCARCITY</text>')
    p.append('</svg>')
    return "".join(p)

# ================================================================= MAP ======
COORDS = {
    "PW": (134.6, 7.5), "FM": (150.5, 6.9), "MP": (145.7, 15.2), "GU": (144.0, 12.6),
    "MH": (169.2, 7.3), "NR": (166.9, -0.5), "KI": (174.5, 1.6), "PG": (144.5, -6.6),
    "SB": (159.8, -8.6), "TV": (179.2, -8.3), "TK": (188.2, -9.2), "WF": (183.6, -13.3),
    "WS": (187.9, -13.8), "AS": (190.6, -14.3), "VU": (167.3, -16.6), "FJ": (178.4, -17.9),
    "TO": (184.8, -21.2), "NU": (190.1, -19.1), "CK": (200.2, -21.2), "PF": (211.5, -17.5),
    "NC": (165.3, -21.6), "PN": (229.9, -25.1),
}
# manual label nudges (dx, dy, anchor)
LBL = {
    "PW": (0, -1, "e"), "FM": (0, -1, "e"), "GU": (-14, 4, "w"), "MP": (0, -1, "e"),
    "MH": (12, -8, "e"), "NR": (-14, 2, "w"), "KI": (14, -4, "e"), "PG": (-2, 16, "w"),
    "SB": (-14, 8, "w"), "TV": (-12, -10, "w"), "TK": (10, -10, "e"), "WF": (-16, 6, "w"),
    "WS": (4, 19, "e"), "AS": (14, -9, "e"), "VU": (-14, 4, "w"), "FJ": (4, 18, "e"),
    "TO": (-4, 18, "w"), "NU": (12, 2, "e"), "CK": (4, 18, "e"), "PF": (0, -1, "e"),
    "NC": (-6, 18, "w"), "PN": (-10, -8, "w"),
}

def map_svg():
    rng = random.Random(11)
    W, H = 1180, 640
    LON0, LON1, LAT0, LAT1 = 126.5, 237, 21.5, -30.5
    def X(lon): return (lon - LON0) / (LON1 - LON0) * W
    def Y(lat): return (LAT0 - lat) / (LAT0 - LAT1) * H

    p = [f'<svg class="block" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Map of Pacific territories: western islands gained rain, central-Pacific islands lost it">']
    p.append(f'''<defs>
      <radialGradient id="mwet" cx="0.5" cy="0.4" r="0.75">
        <stop offset="0" stop-color="{WET_HI}"/><stop offset="0.6" stop-color="{WET}"/><stop offset="1" stop-color="{WET_DEEP}"/>
      </radialGradient>
      <linearGradient id="msea" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="#081523"/><stop offset="1" stop-color="#060e18"/>
      </linearGradient>
    </defs>''')
    p.append(f'<rect width="{W}" height="{H}" fill="url(#msea)"/>')
    # ocean dust
    for _ in range(700):
        x, y = rng.random() * W, rng.random() * H
        p.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{0.5 + rng.random() * 0.7:.1f}" fill="{INK}" opacity="{0.02 + rng.random() * 0.05:.3f}"/>')
    # graticule: equator + dateline
    p.append(f'<line x1="0" y1="{Y(0):.0f}" x2="{W}" y2="{Y(0):.0f}" stroke="{FAINT}" stroke-opacity="0.4" stroke-width="0.8" stroke-dasharray="1 6"/>')
    p.append(f'<text x="10" y="{Y(0) - 7:.0f}" class="t-tag" fill="{FAINT}">EQUATOR</text>')
    p.append(f'<line x1="{X(180):.0f}" y1="0" x2="{X(180):.0f}" y2="{H}" stroke="{FAINT}" stroke-opacity="0.3" stroke-width="0.8" stroke-dasharray="1 6"/>')
    p.append(f'<text x="{X(180) + 6:.0f}" y="16" class="t-tag" fill="{FAINT}">180°</text>')

    # the dry corridor wash (central Pacific equatorial band)
    p.append(f'<ellipse cx="{X(180):.0f}" cy="{Y(-4):.0f}" rx="270" ry="140" fill="{DRY}" opacity="0.05"/>')
    p.append(f'<ellipse cx="{X(152):.0f}" cy="{Y(-4):.0f}" rx="230" ry="170" fill="{WET}" opacity="0.05"/>')
    # editorial annotations
    p.append(f'<text x="{X(137):.0f}" y="{Y(-1.5):.0f}" class="t-anno" fill="{WET}" fill-opacity="0.75">the filling west</text>')
    p.append(f'<text x="{X(190.5):.0f}" y="{Y(2.2):.0f}" class="t-anno" fill="{DRY}" fill-opacity="0.8">the drying corridor</text>')

    order = list(stats.sort_values("delta", key=abs).index)  # draw small first
    for iso in order:
        d = stats.loc[iso, "delta"]
        x, y = X(COORDS[iso][0]), Y(COORDS[iso][1])
        feat = iso in FEATURED
        r = 3.6 + abs(d) * 0.62
        if d >= 0:
            op = 1.0 if feat else 0.55
            p.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r * 2.1:.0f}" fill="{WET}" opacity="{0.10 if feat else 0.05}"/>')
            p.append(f'<path d="{drop_path(x, y, r)}" fill="url(#mwet)" opacity="{op}"/>')
        else:
            op = 1.0 if feat else 0.5
            p.append(f'<path d="{drop_path(x, y, r, up=True)}" fill="none" stroke="{DRY}" stroke-width="{1.7 if feat else 1.2}" stroke-dasharray="4 3.5" opacity="{op}"/>')
            for i in range(3):
                p.append(f'<line x1="{x:.0f}" y1="{y + r + 7 + i * 6:.0f}" x2="{x:.0f}" y2="{y + r + 10 + i * 6:.0f}" stroke="{DRY}" stroke-opacity="{(0.5 - i * 0.13) * op:.2f}" stroke-width="1.2"/>')
        dx, dy, anch = LBL.get(iso, (0, -1, "e"))
        lx = x + (r + 9 + dx if anch == "e" else -(r + 9) + dx)
        ly = y + (4 if dy == -1 else dy)
        ta = "start" if anch == "e" else "end"
        cls = "t-lab-b" if feat else "t-lab"
        fill = (WET_HI if d >= 0 else DRY_HI) if feat else SUB
        p.append(f'<text x="{lx:.0f}" y="{ly:.0f}" class="{cls}" fill="{fill}" text-anchor="{ta}">{NAMES[iso]}'
                 f'<tspan fill="{col(d)}" dx="6">{fmt(d)}</tspan></text>')

    # legend
    lx, ly = 30, H - 92
    p.append(f'<path d="{drop_path(lx + 10, ly + 4, 7)}" fill="url(#mwet)"/>')
    p.append(f'<text x="{lx + 28}" y="{ly + 8}" class="t-lab" fill="{SUB}">wetter than its 20th-century self</text>')
    p.append(f'<path d="{drop_path(lx + 10, ly + 32, 7, up=True)}" fill="none" stroke="{DRY}" stroke-width="1.4" stroke-dasharray="4 3.5"/>')
    p.append(f'<text x="{lx + 28}" y="{ly + 36}" class="t-lab" fill="{SUB}">drier — the drop is emptying upward</text>')
    p.append(f'<circle cx="{lx + 4}" cy="{ly + 58}" r="2.5" fill="{INK}" opacity="0.7"/><circle cx="{lx + 16}" cy="{ly + 58}" r="5.5" fill="{INK}" opacity="0.7"/>')
    p.append(f'<text x="{lx + 28}" y="{ly + 62}" class="t-lab" fill="{SUB}">size = change between the two eras (mm of annual rainfall anomaly)</text>')
    p.append('</svg>')
    return "".join(p)

# =============================================================== SLOPE ======
def slope_svg():
    W, H = 1180, 860
    ML, MR, MT, MB = 285, 285, 78, 64
    iw, ih = W - ML - MR, H - MT - MB
    v_lo, v_hi = -29, 15
    def Y(v): return MT + (v_hi - v) / (v_hi - v_lo) * ih
    XL, XR = ML, W - MR

    p = [f'<svg class="block" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Slope chart comparing each territory’s average rainfall anomaly in 1979–2000 versus 2020–2025">']
    p.append(f'''<defs>
      <linearGradient id="szoneW" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="{WET}" stop-opacity="0.07"/><stop offset="1" stop-color="{WET}" stop-opacity="0"/>
      </linearGradient>
      <linearGradient id="szoneD" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="{DRY}" stop-opacity="0"/><stop offset="1" stop-color="{DRY}" stop-opacity="0.09"/>
      </linearGradient>
    </defs>''')
    p.append(f'<rect x="{XL}" y="{MT}" width="{iw}" height="{Y(0) - MT:.0f}" fill="url(#szoneW)"/>')
    p.append(f'<rect x="{XL}" y="{Y(0):.0f}" width="{iw}" height="{MT + ih - Y(0):.0f}" fill="url(#szoneD)"/>')

    # zero line = the old balance
    p.append(f'<line x1="{XL - 8}" y1="{Y(0):.0f}" x2="{XR + 8}" y2="{Y(0):.0f}" stroke="{INK}" stroke-opacity="0.35" stroke-width="1" stroke-dasharray="2 4"/>')
    p.append(f'<text x="{W / 2:.0f}" y="{Y(0) - 8:.0f}" class="t-tag" fill="{FAINT}" text-anchor="middle">0 — THE OLD BALANCE</text>')
    p.append(f'<text x="{XL - 14}" y="{MT + 6}" class="t-tag" fill="{WET}" text-anchor="end">WETTER ↑</text>')
    p.append(f'<text x="{XL - 14}" y="{MT + ih}" class="t-tag" fill="{DRY}" text-anchor="end">DRIER ↓</text>')

    # era columns
    for x, t1, t2 in ((XL, "1979–2000", "the rain they grew up with"), (XR, "2020–2025", "the rain they live with now")):
        p.append(f'<line x1="{x}" y1="{MT - 6}" x2="{x}" y2="{MT + ih + 6}" stroke="{INK}" stroke-opacity="0.18" stroke-width="1"/>')
        p.append(f'<text x="{x}" y="{MT - 40}" class="t-era" fill="{INK}" text-anchor="middle">{t1}</text>')
        p.append(f'<text x="{x}" y="{MT - 22}" class="t-lab" fill="{FAINT}" text-anchor="middle">{t2}</text>')

    # label dodging
    isos = list(stats.index)
    yl = dodge([Y(stats.loc[i, "hist"]) for i in isos], 15.5, MT - 10, MT + ih + 10)
    yr = dodge([Y(stats.loc[i, "rec"]) for i in isos], 15.5, MT - 10, MT + ih + 10)
    yl = dict(zip(isos, yl)); yr = dict(zip(isos, yr))

    for iso in sorted(isos, key=lambda i: abs(stats.loc[i, "delta"])):
        h, r, d = stats.loc[iso, "hist"], stats.loc[iso, "rec"], stats.loc[iso, "delta"]
        feat = iso in FEATURED
        c = col(d)
        sw = 1.1 + abs(d) * 0.34
        op = 0.95 if feat else 0.28
        y1, y2 = Y(h), Y(r)
        mx = (XL + XR) / 2
        path = f"M {XL} {y1:.1f} C {XL + iw * 0.42:.0f} {y1:.1f} {XR - iw * 0.42:.0f} {y2:.1f} {XR} {y2:.1f}"
        if feat:
            p.append(f'<path d="{path}" fill="none" stroke="{c}" stroke-opacity="0.18" stroke-width="{sw + 5:.1f}" stroke-linecap="round"/>')
        p.append(f'<path d="{path}" fill="none" stroke="{c}" stroke-opacity="{op}" stroke-width="{sw:.1f}" stroke-linecap="round"/>')
        p.append(f'<circle cx="{XL}" cy="{y1:.1f}" r="{3 if feat else 2}" fill="{c}" opacity="{op}"/>')
        p.append(f'<circle cx="{XR}" cy="{y2:.1f}" r="{3 if feat else 2}" fill="{c}" opacity="{op}"/>')
        cls = "t-lab-b" if feat else "t-lab"
        fl = (WET_HI if d >= 0 else DRY_HI) if feat else FAINT
        p.append(f'<text x="{XL - 14}" y="{yl[iso] + 4:.0f}" class="{cls}" fill="{fl}" text-anchor="end">{NAMES[iso]} <tspan fill="{FAINT}" class="t-lab">{fmt(h)}</tspan></text>')
        p.append(f'<text x="{XR + 14}" y="{yr[iso] + 4:.0f}" class="{cls}" fill="{fl}">'
                 f'<tspan class="t-lab" fill="{FAINT}">{fmt(r)}</tspan> {NAMES[iso]}'
                 f'<tspan dx="6" fill="{c}">{fmt(d)}</tspan></text>')
        if abs(yl[iso] - y1) > 7:
            p.append(f'<line x1="{XL - 10}" y1="{yl[iso]:.0f}" x2="{XL - 3}" y2="{y1:.0f}" stroke="{FAINT}" stroke-opacity="0.4" stroke-width="0.7"/>')
        if abs(yr[iso] - y2) > 7:
            p.append(f'<line x1="{XR + 3}" y1="{y2:.0f}" x2="{XR + 10}" y2="{yr[iso]:.0f}" stroke="{FAINT}" stroke-opacity="0.4" stroke-width="0.7"/>')
    p.append('</svg>')
    return "".join(p)

# =============================================================== CARDS ======
YEARS = list(range(1979, 2026))
VMAX = 68.0  # shared scale; max |yearly anomaly| in the dataset is 66.6 (Nauru, 2019)

def card_svg(iso, big=True):
    W, H = (525, 240) if big else (525, 240)
    ML, MR, MT, MB = 14, 14, 52, 26
    iw, ih = W - ML - MR, H - MT - MB
    cy = MT + ih / 2
    def Y(v): return cy - (v / VMAX) * (ih / 2)
    def X(year): return ML + (year - YEARS[0]) / (YEARS[-1] - YEARS[0]) * iw
    s = series[iso]
    h, r, d = stats.loc[iso, "hist"], stats.loc[iso, "rec"], stats.loc[iso, "delta"]
    c = col(d)
    chi = WET_HI if d >= 0 else DRY_HI

    p = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{NAMES[iso]}: yearly rainfall anomalies 1979–2025">']
    # window shading
    p.append(f'<rect x="{X(H0):.0f}" y="{MT}" width="{X(H1) - X(H0):.0f}" height="{ih}" fill="{INK}" opacity="0.035"/>')
    p.append(f'<rect x="{X(R0):.0f}" y="{MT}" width="{X(R1) - X(R0):.0f}" height="{ih}" fill="{c}" opacity="0.08"/>')
    p.append(f'<line x1="{ML}" y1="{cy:.0f}" x2="{W - MR}" y2="{cy:.0f}" stroke="{INK}" stroke-opacity="0.25" stroke-width="0.8" stroke-dasharray="1 4"/>')
    # yearly bars
    bw = iw / len(YEARS) * 0.55
    for _, row in s.iterrows():
        v, yr_ = row["v"], row["year"]
        x = X(yr_)
        cc = WET if v >= 0 else DRY
        p.append(f'<line x1="{x:.1f}" y1="{cy:.1f}" x2="{x:.1f}" y2="{Y(v):.1f}" stroke="{cc}" stroke-opacity="0.85" stroke-width="{bw:.1f}" stroke-linecap="round"/>')
    # window means
    p.append(f'<line x1="{X(H0):.0f}" y1="{Y(h):.1f}" x2="{X(H1):.0f}" y2="{Y(h):.1f}" stroke="{INK}" stroke-width="1.6" stroke-opacity="0.9"/>')
    p.append(f'<line x1="{X(R0):.0f}" y1="{Y(r):.1f}" x2="{X(R1):.0f}" y2="{Y(r):.1f}" stroke="{chi}" stroke-width="2.2"/>')
    p.append(f'<path d="M {X(2012):.0f} {Y(h):.1f} C {X(2017):.0f} {Y(h):.1f} {X(2016):.0f} {Y(r):.1f} {X(2019.4):.0f} {Y(r):.1f}" fill="none" stroke="{chi}" stroke-width="1" stroke-opacity="0.6" stroke-dasharray="3 3"/>')
    # header
    p.append(f'<text x="{ML}" y="24" class="t-card" fill="{INK}">{NAMES[iso]}</text>')
    p.append(f'<text x="{ML}" y="41" class="t-lab" fill="{FAINT}">{fmt(h)} mm → {fmt(r)} mm</text>')
    p.append(f'<text x="{W - MR}" y="32" class="t-big" fill="{chi}" text-anchor="end">{fmt(d)}</text>')
    p.append(f'<text x="{W - MR}" y="46" class="t-tag" fill="{FAINT}" text-anchor="end">MM SHIFT</text>')
    # axis years
    for yr_ in (1979, 2000, 2020, 2025):
        anch = "start" if yr_ == 1979 else ("end" if yr_ == 2025 else "middle")
        p.append(f'<text x="{X(yr_):.0f}" y="{H - 8}" class="t-tag" fill="{FAINT}" text-anchor="{anch}">{yr_}</text>')
    p.append('</svg>')
    return "".join(p)

# ============================================================ MINI GRID =====
def mini_svg(iso):
    W, H = 184, 70
    ML, MR, MT, MB = 6, 6, 26, 6
    iw, ih = W - ML - MR, H - MT - MB
    cy = MT + ih / 2
    def Y(v): return cy - (v / VMAX) * (ih / 2)
    def X(year): return ML + (year - YEARS[0]) / (YEARS[-1] - YEARS[0]) * iw
    s = series[iso]
    d = stats.loc[iso, "delta"]
    p = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">']
    p.append(f'<text x="{ML}" y="13" class="t-lab" fill="{SUB}">{NAMES[iso]}</text>')
    p.append(f'<text x="{W - MR}" y="13" class="t-lab-b" fill="{col(d)}" text-anchor="end">{fmt(d)}</text>')
    p.append(f'<line x1="{ML}" y1="{cy:.0f}" x2="{W - MR}" y2="{cy:.0f}" stroke="{INK}" stroke-opacity="0.18" stroke-width="0.6"/>')
    for _, row in s.iterrows():
        v = row["v"]
        x = X(row["year"])
        cc = WET if v >= 0 else DRY
        p.append(f'<line x1="{x:.1f}" y1="{cy:.1f}" x2="{x:.1f}" y2="{Y(v):.1f}" stroke="{cc}" stroke-opacity="0.8" stroke-width="2"/>')
    p.append('</svg>')
    return "".join(p)

# ============================================================== ASSEMBLE ====
avg_wet = stats.loc[FEAT_WET, "delta"].mean()
avg_dry = stats.loc[FEAT_DRY, "delta"].mean()

def tapa_divider():
    rng = random.Random(3)
    W, Hh = 1180, 26
    p = [f'<svg class="block divider" viewBox="0 0 {W} {Hh}" xmlns="http://www.w3.org/2000/svg">']
    x = 0
    while x < W:
        w = 14
        p.append(f'<path d="M {x} {Hh - 6} L {x + w / 2} 8 L {x + w} {Hh - 6}" fill="none" stroke="{DRY}" stroke-opacity="0.35" stroke-width="1"/>')
        x += w + 8
    p.append('</svg>')
    return "".join(p)

cards_wet = "\n".join(f'<div class="card wet">{card_svg(i)}</div>' for i in FEAT_WET)
cards_dry = "\n".join(f'<div class="card dry">{card_svg(i)}</div>' for i in FEAT_DRY)
minis = "\n".join(f'<div class="mini">{mini_svg(i)}</div>' for i in stats.index)

css = """
:root { color-scheme: dark; }
* { margin:0; padding:0; box-sizing:border-box; }
body {
  background:%(BG0)s; color:%(INK)s;
  font-family:'Outfit','Helvetica Neue',Arial,sans-serif;
  -webkit-font-smoothing:antialiased;
}
.page { width:1180px; margin:0 auto; padding:0 0 90px; }
svg.block { display:block; width:100%%; height:auto; }
svg { overflow:visible; }
.t-tag   { font:600 10px 'Outfit',sans-serif; letter-spacing:0.22em; }
.t-lab   { font:400 11.5px 'Outfit',sans-serif; letter-spacing:0.02em; }
.t-lab-b { font:600 11.5px 'Outfit',sans-serif; letter-spacing:0.02em; }
.t-anno  { font:italic 500 17px 'Fraunces',Georgia,serif; letter-spacing:0.12em; }
text.t-lab, text.t-lab-b, text.t-tag {
  paint-order:stroke; stroke:%(BG0)s; stroke-width:3px; stroke-linejoin:round; }
.t-era   { font:600 20px 'Fraunces',Georgia,serif; }
.t-card  { font:600 17px 'Fraunces',Georgia,serif; }
.t-big   { font:700 26px 'Fraunces',Georgia,serif; }

.kicker { text-align:center; padding:54px 0 6px;
  font:600 12px 'Outfit',sans-serif; letter-spacing:0.38em; color:%(FAINT)s; }
h1 { text-align:center; font:600 88px/0.98 'Fraunces',Georgia,serif;
  letter-spacing:0.01em; padding:10px 40px 0; }
h1 .wet { color:%(WET_HI)s; } h1 .dry { color:%(DRY_HI)s; }
.standfirst { width:760px; margin:26px auto 8px; text-align:center;
  font:400 19px/1.65 'Fraunces',Georgia,serif; color:%(SUB)s; }
.standfirst strong { color:%(INK)s; font-weight:600; }

.stats { display:flex; justify-content:center; gap:70px; padding:46px 0 10px; }
.stat { text-align:center; }
.stat .n { font:700 56px 'Fraunces',Georgia,serif; }
.stat .l { font:600 11px 'Outfit',sans-serif; letter-spacing:0.25em; color:%(FAINT)s; margin-top:8px; }
.n.wet { color:%(WET_HI)s; } .n.dry { color:%(DRY_HI)s; } .n.ink { color:%(INK)s; }

section { padding:64px 0 0; }
.sec-head { display:flex; align-items:baseline; gap:18px; padding:0 6px 8px; }
.sec-num { font:600 13px 'Outfit',sans-serif; letter-spacing:0.3em; color:%(DRY)s; }
h2 { font:600 38px 'Fraunces',Georgia,serif; }
.sec-sub { padding:0 6px 30px; width:740px; font:400 15.5px/1.7 'Outfit',sans-serif; color:%(SUB)s; }
.sec-sub em { color:%(INK)s; font-style:normal; font-weight:600; }

.groups { display:grid; grid-template-columns:1fr 1fr; gap:0 36px; }
.ghead { padding:10px 6px 16px; }
.ghead .gt { font:600 24px 'Fraunces',Georgia,serif; }
.ghead .gt.wet { color:%(WET_HI)s; } .ghead .gt.dry { color:%(DRY_HI)s; }
.ghead .gs { font:400 13.5px/1.6 'Outfit',sans-serif; color:%(SUB)s; margin-top:6px; }
.cards { display:flex; flex-direction:column; gap:18px; }
.card { background:%(BG1)s; border:1px solid rgba(234,242,245,0.07); border-radius:10px; padding:14px 12px 8px; }
.card.wet { box-shadow:inset 3px 0 0 %(WET)s; }
.card.dry { box-shadow:inset 3px 0 0 %(DRY)s; }
.note { flex:1; border:1px dashed rgba(234,242,245,0.16); border-radius:10px;
  padding:24px 26px; font:400 14px/1.75 'Outfit',sans-serif; color:%(SUB)s;
  display:flex; flex-direction:column; justify-content:center; }
.note .nt { font:600 19px 'Fraunces',Georgia,serif; color:%(INK)s; margin-bottom:10px; }
.card svg { display:block; width:100%%; height:auto; }

.minigrid { display:grid; grid-template-columns:repeat(5,1fr); gap:14px 18px; padding-top:6px; }
.mini { background:%(BG1)s; border:1px solid rgba(234,242,245,0.06); border-radius:8px; padding:8px 6px 4px; }
.mini svg { display:block; width:100%%; height:auto; }

.quote { width:840px; margin:90px auto 0; text-align:center;
  font:500 30px/1.5 'Fraunces',Georgia,serif; color:%(INK)s; }
.quote .wet { color:%(WET_HI)s; } .quote .dry { color:%(DRY_HI)s; }
.divider { margin:36px 0 0; }

footer { margin-top:70px; padding:26px 6px 0; border-top:1px solid rgba(234,242,245,0.1);
  display:flex; justify-content:space-between; gap:40px;
  font:400 11.5px/1.7 'Outfit',sans-serif; color:%(FAINT)s; }
footer b { color:%(SUB)s; font-weight:600; }
footer .colL { width:560px; } footer .colR { text-align:right; }
""" % dict(BG0=BG0, BG1=BG1, INK=INK, SUB=SUB, FAINT=FAINT,
           WET=WET, WET_HI=WET_HI, DRY=DRY, DRY_HI=DRY_HI)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=1180">
<title>Where the Rain Went — Pacific Dataviz Challenge 2026</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>{css}</style>
</head>
<body>
<div class="page">

  <div class="kicker">PACIFIC DATAVIZ CHALLENGE 2026 · CLIMATE CHANGE · RAINFALL ANOMALIES</div>
  <h1>Where the<br><span class="wet">rain</span> <span style="color:{FAINT}">went</span></h1>
  <div class="standfirst">The climate crisis is not only heating the Pacific —
    <strong>it is redistributing its water.</strong> Compared with the rain they knew in
    1979–2000, some island nations now live with a growing surplus, while their
    neighbours watch the sky close. Same ocean, different rain.</div>

  {hero_svg()}

  <div class="stats">
    <div class="stat"><div class="n wet">{n_wetter}</div><div class="l">TERRITORIES NOW WETTER</div></div>
    <div class="stat"><div class="n ink">22</div><div class="l">TERRITORIES MEASURED · 1979–2025</div></div>
    <div class="stat"><div class="n dry">{n_drier}</div><div class="l">TERRITORIES NOW DRIER</div></div>
  </div>

  <section>
    <div class="sec-head"><div class="sec-num">I</div><h2>The new geography of rain</h2></div>
    <div class="sec-sub">Average annual rainfall anomaly in <em>2020–2025</em> minus the average of
      <em>1979–2000</em>. The pattern is not random: the far western Pacific — Palau, Micronesia,
      the Solomon Islands, Vanuatu — is filling up, while a corridor of atoll nations along the
      equator and the dateline — Nauru, Kiribati, Tuvalu, Tokelau — and New Caledonia in the south
      are drying out. The rain has not vanished. <em>It has moved.</em></div>
    {map_svg()}
  </section>

  <section>
    <div class="sec-head"><div class="sec-num">II</div><h2>Two eras, one tilt</h2></div>
    <div class="sec-sub">Each thread is one territory, flowing from its average rainfall anomaly in
      <em>1979–2000</em> to its average in <em>2020–2025</em>. Thicker threads moved further.
      Almost every thread crosses the old balance line — the water is being poured
      from one side of the ocean to the other.</div>
    {slope_svg()}
  </section>

  <section>
    <div class="sec-head"><div class="sec-num">III</div><h2>Island by island, year by year</h2></div>
    <div class="sec-sub">Forty-seven years of annual rainfall anomalies (vertical bars, shared scale)
      for the nine territories where the shift is sharpest. The white tick marks the 1979–2000 mean;
      the coloured tick, the 2020–2025 mean.</div>
    <div class="groups">
      <div>
        <div class="ghead">
          <div class="gt wet">The islands the rain found</div>
          <div class="gs">Average shift <b style="color:{WET_HI}">{fmt(avg_wet)} mm</b> — more water,
            but also more floods, landslides and crop rot.</div>
        </div>
        <div class="cards">{cards_wet}
          <div class="note">
            <div class="nt">Why the tilt points west</div>
            A warming Pacific concentrates convection over the western warm pool,
            where the ocean surface is hottest. Strengthened trade winds — amplified by
            the 2020–2023 “triple-dip” La Niña — drag moisture away from the central
            atolls and pile it onto Melanesia and the far west. The water that no longer
            falls on Nauru’s tanks falls instead on Vanuatu’s rivers.
          </div>
        </div>
      </div>
      <div>
        <div class="ghead">
          <div class="gt dry">The islands the rain left</div>
          <div class="gs">Average shift <b style="color:{DRY_HI}">{fmt(avg_dry)} mm</b> — on atolls with
            no rivers, every missing millimetre is drinking water.</div>
        </div>
        <div class="cards">{cards_dry}</div>
      </div>
    </div>
  </section>

  <section>
    <div class="sec-head"><div class="sec-num">IV</div><h2>The full picture</h2></div>
    <div class="sec-sub">All 22 Pacific territories in the dataset, ordered from the largest gain
      to the deepest loss.</div>
    <div class="minigrid">{minis}</div>
  </section>

  <div class="quote">“The climate crisis doesn’t just bring more heat.
    It redistributes the water — <span class="wet">excess</span> for some,
    <span class="dry">scarcity</span> for others.”</div>
  {tapa_divider()}

  <footer>
    <div class="colL">
      <b>Data.</b> SPC Pacific Data Hub — Dataflow DF_CLIMATE_CHANGE, indicator RAIN_ANOM
      (annual rainfall anomalies, mm, relative to the series baseline), 22 Pacific Island
      countries and territories, 1979–2025.<br>
      <b>Method.</b> Each territory’s shift is the difference between its mean anomaly in
      2020–2025 and in 1979–2000. The recent window includes the 2020–2023 “triple-dip” La Niña,
      which amplifies — but does not create — the west-wet / centre-dry contrast.
    </div>
    <div class="colR">
      <b>Where the Rain Went</b><br>
      Pacific Dataviz Challenge 2026 · static visualization<br>
      Gabriel Carbinatto
    </div>
  </footer>

</div>
</body>
</html>
"""

OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html) / 1024:.0f} kB)")
print(stats.round(2))
