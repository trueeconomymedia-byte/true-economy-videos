import sys, json; sys.path.insert(0, "/tmp")
from te_lib import *
OUT = sys.argv[1]
D = json.load(open("/tmp/post.json"))["data_m"]
order = ["India", "China", "United States", "Indonesia", "Pakistan", "Nigeria", "Brazil", "Bangladesh", "Russia", "Ethiopia"]   # India (red) first = drawn behind
lab = {"United States": "US"}
flags = {"India": "IN", "China": "CN", "United States": "US", "Russia": "RU", "Brazil": "BR", "Indonesia": "ID", "Pakistan": "PK", "Nigeria": "NG", "Bangladesh": "BD", "Ethiopia": "ET"}
col = {n: BLUE_L for n in order}; col["India"] = RED; col["China"] = BLUE
V0 = {n: D["1950"][n] for n in order}; V1 = {n: D["2026"][n] for n in order}
fmt = lambda v: f"{v/1000:.2f}bn" if v >= 1000 else f"{v:,.0f}m"
lead50 = V0["China"] - V0["India"]; lead26 = V1["India"] - V1["China"]
print("leads", lead50, lead26)

def flag(c, cx, cy, r, code):
    """real flags for the five codes te_lib lacks; same clip-path construction as Card.flag"""
    if code not in ("ID", "PK", "NG", "BD", "ET"): return c.flag(cx, cy, r, code)
    Card._uid += 1; u = f"f{Card._uid}"; x, y, w = cx - r, cy - r, 2 * r
    o = [f'<clipPath id="{u}"><circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}"/></clipPath><g clip-path="url(#{u})">']
    R = lambda xx, yy, ww, hh, f: o.append(f'<rect x="{xx:.1f}" y="{yy:.1f}" width="{ww:.1f}" height="{hh:.1f}" fill="{f}"/>')
    if code == "ID": R(x, y, w, w, "#FFFFFF"); R(x, y, w, r, "#CE1126")
    elif code == "NG": R(x, y, w, w, "#FFFFFF"); R(x, y, w / 3, w, "#008751"); R(x + 2 * w / 3, y, w / 3 + 1, w, "#008751")
    elif code == "BD": R(x, y, w, w, "#006A4E"); o.append(f'<circle cx="{cx - r*0.1:.1f}" cy="{cy:.1f}" r="{r*0.48:.1f}" fill="#F42A41"/>')
    elif code == "ET":
        R(x, y, w, w / 3 + 0.5, "#078930"); R(x, y + w / 3, w, w / 3 + 0.5, "#FCDD09"); R(x, y + 2 * w / 3, w, w / 3 + 1, "#DA121A")
        o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r*0.42:.1f}" fill="#0F47AF"/>')
    elif code == "PK":
        R(x, y, w, w, "#01411C"); R(x, y, w * 0.27, w, "#FFFFFF")
        o.append(f'<circle cx="{cx + r*0.22:.1f}" cy="{cy:.1f}" r="{r*0.46:.1f}" fill="#FFFFFF"/><circle cx="{cx + r*0.36:.1f}" cy="{cy - r*0.1:.1f}" r="{r*0.38:.1f}" fill="#01411C"/>')
    o.append(f'</g><circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="none" stroke="#00000022" stroke-width="1.5"/>')
    c._o("".join(o))

c = Card()
T1, MK = "Population: India vs China", "Population"; TX = 0
size = min(92.0, (948 - TX) / width("cb", T1, 1)); b1 = max(66, math.ceil(size * 0.76) + 3)
with c.group("title"):
    i = T1.index(MK); wp = width("cb", T1[:i], size); wn = width("cb", MK, size)
    c.rect(TX + wp - 6, b1 - size * 0.25, wn + 12, size * 0.40, YEL, 1, 3)
    c.text(TX, b1, T1, size, INK, "cb")
    c.text(0, b1 + 44, "Today's 10 biggest countries, traced back · 1950 vs 2026 · ribbon width = people", 22, GREY, "m")
c.top = b1 + 44 + 30
NW, GR, PITCH = 16, 5, 22
yt, yb = c.top + 44, c.bottom - 8
k = (yb - yt - GR * 9) / sum(V1.values())
o0 = sorted(order, key=lambda n: -V0[n]); o1 = sorted(order, key=lambda n: -V1[n])
# 1950 stack, bottom-aligned: 5px gaps, widened only as far as needed so every label sits level with its own node
h0 = {n: V0[n] * k for n in order}
gaps = [max(GR, PITCH - (h0[a] + h0[b]) / 2) for a, b in zip(o0, o0[1:])]
G0 = {}; y = yb - (sum(h0.values()) + sum(gaps))
for j, n in enumerate(o0):
    G0[n] = (y, y + h0[n]); y += h0[n] + (gaps[j] if j < len(gaps) else 0)
G1 = {}; y = yt
for n in o1:
    G1[n] = (y, y + V1[n] * k); y += V1[n] * k + GR
# left label column exactly as wide as its longest label, so nothing is wasted on the left
def l0(n):
    big = n in ("China", "India"); fn, fv = (20, 16) if big else (16, 15)
    return width("b", lab.get(n, n), fn) + 8 + width("sb", fmt(V0[n]), fv)
# India / China labels touch the safe-zone edges (x=0 and x=948); longer names may run a little past them (user 18 Nov)
XL = math.ceil(max(8 + width("sb", fmt(V0[n]), 16) + 7 + 22 + 7 + width("b", n, 20) for n in ("China", "India")))
XR = 948 - NW - math.ceil(12 + 30 + max(width("b", n, 22) for n in ("China", "India")))
with c.group("body"):
    for n in order: c.ribbon(XL + NW, G0[n][0], G0[n][1], XR, G1[n][0], G1[n][1], col[n], 0.6, True)
    for n in order:
        c.rect(XL, G0[n][0], NW, h0[n], col[n]); c.rect(XR, G1[n][0], NW, G1[n][1] - G1[n][0], col[n])
    top0 = G0[o0[0]][0]
    c.text(XL + NW, top0 - 16, "1950", 30, INK, "cb", "r"); c.text(XR + NW, yt - 16, "2026", 30, INK, "cb", "r")
    for n in order:                      # 1950 labels: one line each, level with the node, no leader lines
        cy = (G0[n][0] + G0[n][1]) / 2; big = n in ("China", "India"); fn, fv = (20, 16) if big else (16, 15)
        vt = fmt(V0[n]); wv = width("sb", vt, fv); r = 11 if big else 9
        c.text(XL - 8, cy + fv * 0.36, vt, fv, GREY, "sb", "r"); flag(c, XL - 8 - wv - 7 - r, cy, r, flags[n])
        c.text(XL - 8 - wv - 7 - 2 * r - 7, cy + fn * 0.36, lab.get(n, n), fn, INK, "b", "r")
    for n in order:                      # 2026 labels right of the nodes
        y0, y1 = G1[n]; cy = (y0 + y1) / 2; nm = lab.get(n, n); h = y1 - y0; x = XR + NW + 12
        big = n in ("India", "China"); fn, fv = (22, 17) if big else (16, 15)
        flag(c, x + 11, cy, 13 if big else 10, flags[n]); c.text(x + 30, cy + fn * 0.36, nm, fn, INK, "b")
with c.group("toplabels"):                # 2026 values inside the ribbon ends (white on red / main blue, ink on light blue)
    for n in order:
        cy = (G1[n][0] + G1[n][1]) / 2; big = n in ("India", "China"); fv = 26 if big else 17
        c.text(XR - 12, cy + fv * 0.36, fmt(V1[n]), fv, INK, "b", "r")
c.anim["red_behind"] = True
c.footer("India added 1.13bn people; China added 869m"); c.source("Source: UN World Population Prospects 2024 (via Our World in Data, StatisticsTimes) · 2026 projection")
c.save(OUT)
for n in order:
    assert abs(h0[n] / k - V0[n]) < 1e-6 and abs((G1[n][1] - G1[n][0]) / k - V1[n]) < 1e-6
print("scale ok %.4f px/m, XL %d, left stack top %.0f" % (k, XL, top0))
