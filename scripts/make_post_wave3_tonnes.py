import sys, json; sys.path.insert(0, "/tmp")
from te_lib import *
OUT = sys.argv[1]
D = json.load(open("/tmp/post_t.json"))["data_m"]
order = ["China", "United States", "Russia", "Japan", "Germany", "India", "Ukraine", "United Kingdom", "Canada", "Italy", "Iran", "Indonesia", "Saudi Arabia", "South Korea"]   # China (red) first = drawn behind
lab = {"United States": "US", "United Kingdom": "UK"}
flags = {"India": "IN", "China": "CN", "United States": "US", "Russia": "RU", "Japan": "JP", "Germany": "DE", "Ukraine": "UA", "United Kingdom": "UK", "Canada": "CA", "Italy": "IT", "Iran": "IR", "Indonesia": "ID", "Saudi Arabia": "SA", "South Korea": "KR"}
col = {n: BLUE_L for n in order}; col["China"] = RED; col["United States"] = BLUE
V0 = {n: D["1990"][n] for n in order if n in D["1990"]}; V1 = {n: D["2024"][n] for n in order if n in D["2024"]}
both = [n for n in order if n in V0 and n in V1]
fmt = lambda v: f"{v:.1f}bn"

def flag(c, cx, cy, r, code):
    """real flags for the five codes te_lib lacks; same clip-path construction as Card.flag"""
    if code not in ("ID", "PK", "NG", "BD", "ET", "UA", "IR", "SA"): return c.flag(cx, cy, r, code)
    Card._uid += 1; u = f"f{Card._uid}"; x, y, w = cx - r, cy - r, 2 * r
    o = [f'<clipPath id="{u}"><circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}"/></clipPath><g clip-path="url(#{u})">']
    R = lambda xx, yy, ww, hh, f: o.append(f'<rect x="{xx:.1f}" y="{yy:.1f}" width="{ww:.1f}" height="{hh:.1f}" fill="{f}"/>')
    if code == "ID": R(x, y, w, w, "#FFFFFF"); R(x, y, w, r, "#CE1126")
    elif code == "NG": R(x, y, w, w, "#FFFFFF"); R(x, y, w / 3, w, "#008751"); R(x + 2 * w / 3, y, w / 3 + 1, w, "#008751")
    elif code == "BD": R(x, y, w, w, "#006A4E"); o.append(f'<circle cx="{cx - r*0.1:.1f}" cy="{cy:.1f}" r="{r*0.48:.1f}" fill="#F42A41"/>')
    elif code == "ET":
        R(x, y, w, w / 3 + 0.5, "#078930"); R(x, y + w / 3, w, w / 3 + 0.5, "#FCDD09"); R(x, y + 2 * w / 3, w, w / 3 + 1, "#DA121A")
        o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r*0.42:.1f}" fill="#0F47AF"/>')
    elif code == "UA": R(x, y, w, w / 2 + 0.5, "#0057B7"); R(x, y + w / 2, w, w / 2 + 1, "#FFD700")
    elif code == "IR": R(x, y, w, w / 3 + 0.5, "#239F40"); R(x, y + w / 3, w, w / 3 + 0.5, "#FFFFFF"); R(x, y + 2 * w / 3, w, w / 3 + 1, "#DA0000")
    elif code == "SA": R(x, y, w, w, "#006C35"); R(x + w * 0.2, y + w * 0.62, w * 0.6, w * 0.06, "#FFFFFF"); R(x + w * 0.25, y + w * 0.36, w * 0.5, w * 0.06, "#FFFFFF")
    elif code == "PK":
        R(x, y, w, w, "#01411C"); R(x, y, w * 0.27, w, "#FFFFFF")
        o.append(f'<circle cx="{cx + r*0.22:.1f}" cy="{cy:.1f}" r="{r*0.46:.1f}" fill="#FFFFFF"/><circle cx="{cx + r*0.36:.1f}" cy="{cy - r*0.1:.1f}" r="{r*0.38:.1f}" fill="#01411C"/>')
    o.append(f'</g><circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="none" stroke="#00000022" stroke-width="1.5"/>')
    c._o("".join(o))

c = Card()
L1, L2, MK = "Which country emits the", "most CO2?", "most CO2"
size = min(76.0, 948 / width("cb", L1, 1)); b1 = math.ceil(size * 0.76) + 3; pitch = size * 0.93
with c.group("title"):
    for ln, by in ((L1, b1), (L2, b1 + pitch)):
        if MK in ln:
            i = ln.index(MK); wp = width("cb", ln[:i], size); wn = width("cb", MK, size)
            c.rect(wp - 6, by - size * 0.25, wn + 12, size * 0.40, YEL, 1, 3)
        c.text(0, by, ln, size, INK, "cb")
    c.text(0, b1 + pitch + 44, "Billions of tonnes of CO2,", 22, GREY, "m")
    c.text(0, b1 + pitch + 72, "10 biggest emitters · 1990 vs 2024", 22, GREY, "m")
print("title size", size, "line1 w", width("cb", L1, size), "line2 w", width("cb", L2, size))
c.top = b1 + 78 - 44          # chart rises beside line 2: its peak is on the right, where line 2 and the subtitle leave the paper empty
NW, GR, PITCH = 16, 5, 22
yt, yb = c.top + 44, c.bottom - 8
k = (yb - yt - GR * 9) / sum(V1.values())
o0 = sorted(V0, key=lambda n: -V0[n]); o1 = sorted(V1, key=lambda n: -V1[n])
# 1950 stack, bottom-aligned: 5px gaps, widened only as far as needed so every label sits level with its own node
h0 = {n: V0[n] * k for n in V0}
gaps = [max(GR, PITCH - (h0[a] + h0[b]) / 2) for a, b in zip(o0, o0[1:])]
G0 = {}; y = yb - (sum(h0.values()) + sum(gaps))
for j, n in enumerate(o0):
    G0[n] = (y, y + h0[n]); y += h0[n] + (gaps[j] if j < len(gaps) else 0)
G1 = {}; y = yt
for n in o1:
    G1[n] = (y, y + V1[n] * k); y += V1[n] * k + GR
# left label column exactly as wide as its longest label, so nothing is wasted on the left
def l0(n):
    big = n in ("China", "United States"); fn, fv = (20, 16) if big else (16, 15)
    return width("b", lab.get(n, n), fn) + 8 + width("sb", fmt(V0[n]), fv)
# India / China labels touch the safe-zone edges (x=0 and x=948); longer names may run a little past them (user 18 Nov)
XL = math.ceil(max(8 + width("sb", fmt(V0[n]), 16) + 7 + 22 + 7 + width("b", n, 20) for n in ("China", "United States")))
XR = 948 - NW - math.ceil(12 + 30 + max(width("b", n, 22) for n in ("China", "United States")))
with c.group("body"):
    for n in both: c.ribbon(XL + NW, G0[n][0], G0[n][1], XR, G1[n][0], G1[n][1], col[n], 0.6, True)
    for n in V0: c.rect(XL, G0[n][0], NW, h0[n], col[n])
    for n in V1: c.rect(XR, G1[n][0], NW, G1[n][1] - G1[n][0], col[n])
    top0 = G0[o0[0]][0]
    c.text(XL + NW, top0 - 16, "1990", 30, INK, "cb", "r"); c.text(XR + NW, yt - 16, "2024", 30, INK, "cb", "r")
    for n in V0:                         # 1990 labels: one line each, level with the node, no leader lines
        cy = (G0[n][0] + G0[n][1]) / 2; big = n in ("China", "United States"); fn, fv = (20, 16) if big else (16, 15)
        vt = fmt(V0[n]); wv = width("sb", vt, fv); r = 11 if big else 9
        c.text(XL - 8, cy + fv * 0.36, vt, fv, GREY, "sb", "r"); flag(c, XL - 8 - wv - 7 - r, cy, r, flags[n])
        c.text(XL - 8 - wv - 7 - 2 * r - 7, cy + fn * 0.36, lab.get(n, n), fn, INK, "b", "r")
    for n in V1:                         # 2024 labels right of the nodes
        y0, y1 = G1[n]; cy = (y0 + y1) / 2; nm = lab.get(n, n); h = y1 - y0; x = XR + NW + 12
        big = n in ("United States", "China"); fn, fv = (22, 17) if big else (16, 15)
        flag(c, x + 11, cy, 13 if big else 10, flags[n]); c.text(x + 30, cy + fn * 0.36, nm, fn, INK, "b")
with c.group("toplabels"):                # 2026 values inside the ribbon ends (white on red / main blue, ink on light blue)
    for n in V1:
        cy = (G1[n][0] + G1[n][1]) / 2; big = n in ("United States", "China"); fv = 26 if big else 17
        c.text(XR - 12, cy + fv * 0.36, fmt(V1[n]), fv, INK, "b", "r")
c.anim["red_behind"] = True
c.footer("China emits 5x more than in 1990; the US, 4% less"); c.source("Source: Global Carbon Project via Our World in Data · fossil CO2 and cement · 1990 USSR split by republic")
c.save(OUT)
for n in V1:
    assert abs((G1[n][1] - G1[n][0]) / k - V1[n]) < 1e-6
for n in V0:
    assert abs(h0[n] / k - V0[n]) < 1e-6
print("scale ok %.4f px/m, XL %d, left stack top %.0f" % (k, XL, top0))
