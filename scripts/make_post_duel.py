#!/usr/bin/env python3
"""COUNTRY DUEL card (country_vs_country series, from 11 Nov 2026).
Split screen: country A on the left half, country B on the right half, flags + names in a header row.
Every measure is ONE row of two vertical columns on a shared baseline and a shared scale (same kind = same colour).
  kind "size": both columns main blue; the smaller one gets a RED stacked block up to the bigger one's height = the gap (labelled).
  kind "rate": winner column teal (white chevrons), other light teal (teal chevrons); chevrons rise with the SAME number of passes per loop,
               so a taller column moves its chevrons faster: the motion speed IS the rate. Negative rate -> red column, chevrons fall.
  kind "level": winner main blue, other light blue, no motion (static context measures such as per-capita income or debt).
Everything is visible at frame 0 (numbers never appear or move); only chevrons move. A gold KPI box closes the card.
usage: python3 make_post_duel.py data.json out.svg
data = {"title":[l1,l2],"mark":..,"accent":"short","subtitle":..,"a":{"code","name"},"b":{...},
        "rows":[{"label","kind","a","b","fmt","better":"higher|lower|null","gap_label"}],"kpi":[big,small],"footer","source"}"""
import sys, json; sys.path.insert(0, "/tmp")
from te_lib import *
D = json.load(open(sys.argv[1])); OUT = sys.argv[2]
c = Card(); c.title(*D["title"], mark=D.get("mark"), accent=D.get("accent", "short")); c.subtitle(D["subtitle"])
CXA, CXB, COLW = 237, 711, 300
y = c.top - 10
TOP = []
with c.group("toplabels"):
    for cx, k in ((CXA, "a"), (CXB, "b")):
        nm = D[k]["name"]; w = width("b", nm, 40) + 64
        c.flag(cx - w / 2 + 24, y + 6, 24, D[k]["code"]); c.text(cx - w / 2 + 64, y + 20, nm, 40, INK, "b")
y += 52
KH = 150; rows = D["rows"]
avail = c.bottom - KH - 24 - y
wts = [1.35 if r["kind"] == "size" else 1.0 for r in rows]; unit = avail / sum(wts)
for i, r in enumerate(rows):
    rh = unit * wts[i]; ry = y
    with c.group("body"):
        c.line(0, ry + 2, 948, ry + 2, "#CFC8B8", 2)
        c.text(0, ry + 36, f"{i+1}  {r['label']}", 26, INK, "b")
    base = ry + rh - 14; ctop = ry + 120; hmax = base - ctop
    va, vb = r["a"], r["b"]; m = max(abs(va), abs(vb)); sc = hmax / m
    fmt = r["fmt"]
    if r["better"] == "higher": win = "a" if va > vb else "b"
    elif r["better"] == "lower": win = "a" if va < vb else "b"
    else: win = None
    with c.group("body"):
        c.line(0, base, 948, base, INK, 2)
        for cx, k, v in ((CXA, "a", va), (CXB, "b", vb)):
            h = abs(v) * sc; x = cx - COLW / 2
            if r["kind"] == "size": col, txt = BLUE, "#FFFFFF"
            elif r["kind"] == "rate":
                col = RED if v < 0 else (GREEN if k == win else GREEN_L)
            else: col = BLUE if (k == win or win is None) else BLUE_L
            c.rect(x, base - h, COLW, h, col)
            if r["kind"] == "size" and abs(v) < m:
                gh = (m - abs(v)) * sc
                gy0, gy1 = base - h - gh, base - h          # the gap = dashed red outline up to the bigger column (not part of the smaller country)
                for (x1_, y1_, x2_, y2_) in ((x, gy0, x + COLW, gy0), (x, gy0, x, gy1), (x + COLW, gy0, x + COLW, gy1)):
                    c.line(x1_, y1_, x2_, y2_, RED, 3, "10 7")
                gl = r.get("gap_label", "the gap")
                c.text(cx, gy0 + gh * 0.42, gl, fit("b", gl, 26, COLW - 30), RED, "b", "m")
                c.text(cx, gy0 + gh * 0.42 + 42, fmt.format(m - abs(v)), 38, RED, "b", "m")
            if r["kind"] == "rate":
                light = col == GREEN_L
                c.arrows(x, base - h, COLW, h, (36, 153, 114) if light else (255, 255, 255), n=max(6, int(14 * h / hmax)),
                         alpha=0.6, size=14, shape="chevron", direction="down" if v < 0 else "up", cycles=2)
    with c.group("toplabels"):
        for cx, k, v in ((CXA, "a"), (CXB, "b")) and ((CXA, "a", va), (CXB, "b", vb)):
            h = abs(v) * sc; topy = base - h
            s = fmt.format(v); c.text(cx, topy - 14, s, 48 if len(s) < 8 else 42, INK, "b", "m")
    if r["kind"] == "rate" and r.get("note"):
        with c.group("body"): c.text(948, ry + 36, r["note"], 17, GREY, "sb", "r")
    y += rh
ky = c.bottom - KH
with c.group("kpis"):
    c.rect(0, ky, 948, KH, YEL, 1, 6)
    c.text(474, ky + 68, D["kpi"][0], fit("b", D["kpi"][0], 40, 900), INK, "b", "m")
    c.text(474, ky + 112, D["kpi"][1], fit("sb", D["kpi"][1], 26, 900), INK, "sb", "m")
c.footer(D["footer"]); c.source(D["source"])
c.save(OUT)
