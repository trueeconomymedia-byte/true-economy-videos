#!/usr/bin/env python3
"""TRUE ECONOMY CHART STYLE for bar / line chart Shorts (user-approved 20 Nov 2026, reference card: UK vs France 2026).
Reference build: one chart, old headline (Lora Bold + gold marker), centred key with rough squares, value axis with round
tick values and dotted warm gridlines, black baseline, slim rough bars (Card.rough, option A), values just above the bars
(Inter Medium, all the same size; colour picks out what matters), category labels with flags under the FIRST bar of each
group, footer takeaway + source. STATIC: no draw-on, no flashing, no chevrons, no gold KPI box.
Adapt the form to the data (grouped bars, single bars, horizontal bars, line chart, any axis) but keep this look.
usage: python3 -I make_post_chart.py   (edit DATA below; writes /mnt/user-data/outputs/<slug>.svg)"""
import sys; sys.path.insert(0, "/tmp"); sys.path.insert(0, "/tmp/tev/scripts")
from te_lib import *
OUT = "/mnt/user-data/outputs/chart-style-reference.svg"
c = Card(); c.title("The UK economy is", "20% bigger than France's", mark="20% bigger", accent="none")
c.subtitle("UK vs France · IMF forecasts for 2026 · current US$")
T, B = c.top, c.bottom
UK, FR, gU, gF = 4.2684, 3.5542, 1.27, 0.41
with c.group("key"):                                   # key: one centred line, small rough squares, Inter Medium
    items = [(BLUE, "Size of the economy"), (GREEN, "Growth in 2026")]; SQ = 26; GAP = 90; TS = 30
    tw = sum(SQ + 14 + width("m", t, TS) for _, t in items) + GAP * (len(items) - 1); x = 474 - tw / 2; ky = T + 4
    for col, t in items:
        c.rough(x, ky - SQ / 2, SQ, SQ, col, int(x) + 5); c.text(x + SQ + 14, ky + TS * 0.36, t, TS, INK, "m"); x += SQ + 14 + width("m", t, TS) + GAP
AX = 112; R = 948; top = T + 80; base = B - 95; sc = (base - top) / 5.0     # axis $0..$5tn, round ticks
with c.group("body"):
    for v in range(1, 6): c.line(AX + 8, base - v * sc, R, base - v * sc, "#CFC8B8", 3, "2 9")   # dotted warm gridlines
    c.line(AX, top - 20, AX, base, GREY, 2)                                                       # thin warm-grey value axis
    for v in range(6): c.text(AX - 16, base - v * sc + 9, "$0" if v == 0 else f"${v}tn", 26, GREY, "b", "r")   # Inter Bold warm grey ticks
BW = 90                                                                                            # slim bars (about half the slot)
bars = [(230, UK, BLUE, f"${UK:.2f}tn", INK), (360, UK * gU / 100, GREEN, f"+{gU:.1f}%", GREEN),
        (660, FR, BLUE, f"${FR:.2f}tn", INK), (790, FR * gF / 100, GREEN, f"+{gF:.1f}%", GREEN)]
for x, v, col, lab, lc in bars:
    h = v * sc
    with c.group("body"): c.rough(x - BW / 2, base - h, BW, h, col, int(x))
    with c.group("toplabels"): c.text(x, base - h - 16, lab, 36, lc, "m", "m")
with c.group("toplabels"):
    c.line(AX, base, R, base, INK, 4)                                                             # black baseline on top
    for cx, code, nm in ((230, "UK", "UK"), (660, "FR", "France")):                               # flag + name under the first bar of each group
        w = width("m", nm, 32) + 38; c.flag(cx - w / 2 + 14, base + 42, 14, code); c.text(cx - w / 2 + 38, base + 53, nm, 32, INK, "m")
c.footer("The UK is bigger, and growing faster: 1.3% vs 0.4%")
c.source("Source: IMF WEO Oct 2026 (via Worldometers, Admirals) · growth bars drawn to scale")
c.save(OUT)
