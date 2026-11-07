#!/usr/bin/env python3
"""True Economy 'How X makes money?' money-flow chart. Usage: python3 make_flow.py data.json
Canvas 948x1300 = the safe zone of the white card (fills edge to edge). Transparent SVG, text outlined."""
import json, sys, re
from fontTools.ttLib import TTFont
from fontTools.t1Lib import T1Font
from fontTools.agl import UV2AGL
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.basePen import NullPen

W, H = 948, 1300
RED, BLUE, YEL = "#E23B3B", "#3362CE", "#FFF205"
BLUE_D, BLUE_L, BLUE_XL = "#3362CE", "#A4BBE8", "#A4BBE8"
INK, GREY = "#111111", "#555555"
IF = "/usr/share/fonts/opentype/inter/Inter-%s.otf"

class F:
    def __init__(s, path, t1=False):
        s.t1 = t1
        if t1:
            f = T1Font(path); f.parse(); s.gs = f.getGlyphSet(); s.upem = 1000
        else:
            f = TTFont(path); s.f = f; s.gs = f.getGlyphSet(); s.cm = f.getBestCmap(); s.upem = f['head'].unitsPerEm
    def name(s, ch):
        return UV2AGL.get(ord(ch)) if s.t1 else s.cm.get(ord(ch))
    def adv(s, n):
        if n is None or n not in s.gs: return 0
        if s.t1:
            g = s.gs[n]; g.draw(NullPen()); return g.width
        return s.f['hmtx'][n][0]
fonts = {"b": F(IF % "Bold"), "sb": F(IF % "SemiBold"), "m": F(IF % "Medium"), "xb": F(IF % "ExtraBold"),
         "cb": F("/usr/share/fonts/X11/Type1/c0632bt_.pfb", True)}
def width(fk, t, size):
    f = fonts[fk]; return sum(f.adv(f.name(c)) for c in t) * size / f.upem
out = []
RIBBONS = []
def text(x, y, t, size, fill=INK, fk="b", anchor="l"):
    f = fonts[fk]; w = width(fk, t, size)
    if anchor == "r": x -= w
    elif anchor == "m": x -= w / 2
    s = size / f.upem; pen = SVGPathPen(f.gs); cx = x
    for c in t:
        n = f.name(c)
        if n in f.gs: f.gs[n].draw(TransformPen(pen, (s, 0, 0, -s, cx, y)))
        cx += f.adv(n) * s
    out.append(f'<path d="{pen.getCommands()}" fill="{fill}"/>')
def solid(hexc, op, bg=(250, 250, 250)):
    """Bake opacity into a solid colour (Canva keeps SVGs as vectors more reliably without transparency)."""
    if op == 1: return hexc
    c = [int(hexc[i:i+2], 16) for i in (1, 3, 5)]
    return "#%02X%02X%02X" % tuple(round(op * c[i] + (1 - op) * bg[i]) for i in range(3))
def rect(x, y, w, h, fill, op=1, r=0):
    fill = solid(fill, op)
    if r:
        out.append(f'<path d="M{x+r:.1f},{y:.1f} H{x+w-r:.1f} Q{x+w:.1f},{y:.1f} {x+w:.1f},{y+r:.1f} V{y+h-r:.1f} Q{x+w:.1f},{y+h:.1f} {x+w-r:.1f},{y+h:.1f} H{x+r:.1f} Q{x:.1f},{y+h:.1f} {x:.1f},{y+h-r:.1f} V{y+r:.1f} Q{x:.1f},{y:.1f} {x+r:.1f},{y:.1f} Z" fill="{fill}"/>')
    else:
        out.append(f'<path d="M{x:.1f},{y:.1f} H{x+w:.1f} V{y+h:.1f} H{x:.1f} Z" fill="{fill}"/>')
def ribbon(xs, ys0, ys1, xd, yd0, yd1, fill, op):
    RIBBONS.append([xs, ys0, ys1, xd, yd0, yd1, fill])
    xm = (xs + xd) / 2
    out.append(f'<path d="M{xs:.1f},{ys0:.1f} C{xm:.1f},{ys0:.1f} {xm:.1f},{yd0:.1f} {xd:.1f},{yd0:.1f} L{xd:.1f},{yd1:.1f} '
               f'C{xm:.1f},{yd1:.1f} {xm:.1f},{ys1:.1f} {xs:.1f},{ys1:.1f} Z" fill="{solid(fill, op)}"/>')
def money(v):
    return f"${v:,.1f}B" if v >= 1 else f"${v*1000:,.0f}M"

d = json.load(open(sys.argv[1]))
co = d["company"]
rev, cogs, opex, oth, tax = d["rev"], d["cogs"], d["opex"], d["other"], d["tax"]
gp = rev - cogs; op = gp - opex; pbt = op + oth; ni = pbt - tax
assert min(gp, op, pbt, ni) > 0 and oth >= 0, "losses/negative other income need a manual adaptation"
pr = d["prior"]  # prior-year rev, gp, op, ni
yoy = lambda a, b: f"{(a / b - 1) * 100:+.0f}% YoY"

X0 = 0
# ---- title (same look as the template: bold serif, yellow marker behind company name)
line1 = f"How {co} makes"
TX = 38
size = min(92.0, (948 - TX) / width("cb", line1, 1))
b1 = 66; pitch = size * 0.93
out.append('<g id="title">')
wp = width("cb", "How ", size); wn = width("cb", co, size)
rect(X0, b1 - size * 0.70, 12, size * 0.70, BLUE_D)   # short accent bar beside line 1 (user choice, 7 Nov)
rect(X0 + TX + wp - 6, b1 - size * 0.76, wn + 12, size * 0.93, YEL)
text(X0 + TX, b1, line1, size, INK, "cb")
text(X0 + TX, b1 + pitch, "money?", size, INK, "cb")
text(X0, b1 + pitch + 52, f"Where each quarter’s revenue goes · {d['period']}", 24, GREY, "m")
out.append('</g>')

# ---- KPI strip
ky = b1 + pitch + 52 + 70
out.append('<g id="kpis">')
kp = [("Revenue", rev, yoy(rev, pr["rev"]), "#EEEEEC"), ("Gross profit", gp, yoy(gp, pr["gp"]), "#EEEEEC"),
      ("Operating profit", op, yoy(op, pr["op"]), "#EEEEEC"), ("Net income", ni, yoy(ni, pr["ni"]), YEL)]
bw, gap = 226.5, 14
for i, (lab, val, yy, col) in enumerate(kp):
    bx = X0 + i * (bw + gap)
    text(bx + bw / 2, ky, lab, 19, INK, "sb", "m")
    rect(bx, ky + 14, bw, 92, col, 1, 4)
    text(bx + bw / 2, ky + 62, money(val), 34, INK, "b", "m")
    text(bx + bw / 2, ky + 90, yy, 16, INK if col == YEL else BLUE_D, "sb", "m")
out.append('</g>')

# ---- sankey geometry
NW = 14
_s = 934/840
XA, XR, XG, XO, XP, XF = [X0 + v*_s for v in (175, 300, 435, 570, 705, 840)]
segs = d["segments"]; nseg = len(segs)
TOP = ky + 14 + 92 + 70       # top of the sankey block
BOT = H - 90                 # lowest point allowed
TG = 54
fixed = 2 * TG + 46
k = min((BOT - TOP - fixed) / (oth + pbt + opex + cogs), (BOT - TOP - 14 * (nseg - 1) - oth * 6) / rev, 6.2)
H_rev, H_gp, H_op, H_oi, H_pbt, H_ni, H_tax = rev*k, gp*k, op*k, oth*k, pbt*k, ni*k, tax*k
y_pbt = TOP; yT = y_pbt + H_oi
yN = y_pbt; yTax = yN + H_ni + TG; yOpx = yTax + H_tax + TG; yCog = yOpx + opex*k + TG
cols = [BLUE, BLUE_D, BLUE_L, BLUE_XL]

out.append('<g id="segments">')
ya, yr, lastcy = yT, yT, -1e9
for i, s in enumerate(segs):
    h = s["value"] * k; col = cols[i % 4]
    ribbon(XA + NW, ya, ya + h, XR, yr, yr + h, col, 0.28)
    rect(XA, ya, NW, h, col)
    cy = max(ya + h / 2, lastcy + 50); lastcy = cy
    lines = s["lines"]; xr_ = XA - 12
    vcol = BLUE_D if col in (BLUE_L, BLUE_XL) else col
    if len(lines) == 1:
        text(xr_, cy - 3, money(s["value"]), 22, vcol, "b", "r"); text(xr_, cy + 17, lines[0], 15, INK, "sb", "r")
    else:
        text(xr_, cy - 14, money(s["value"]), 22, vcol, "b", "r")
        for j, ln in enumerate(lines): text(xr_, cy + 6 + j * 17, ln, 15, INK, "sb", "r")
    ya += h + 14; yr += h
out.append('</g>')

out.append('<g id="spine">')
ribbon(XR + NW, yT, yT + H_gp, XG, yT, yT + H_gp, BLUE, 0.16)
ribbon(XR + NW, yT + H_gp, yT + H_gp + cogs*k, XF, yCog, yCog + cogs*k, RED, 0.22)
ribbon(XG + NW, yT, yT + H_op, XO, yT, yT + H_op, BLUE, 0.16)
ribbon(XG + NW, yT + H_op, yT + H_gp, XF, yOpx, yOpx + opex*k, RED, 0.22)
ribbon(XO + NW, yT, yT + H_op, XP, yT, yT + H_op, BLUE, 0.16)
if oth > 0: ribbon(XO + NW, y_pbt, yT, XP, y_pbt, yT, BLUE_XL, 0.45)
ribbon(XP + NW, y_pbt, y_pbt + H_ni, XF, yN, yN + H_ni, YEL, 0.5)
ribbon(XP + NW, y_pbt + H_ni, y_pbt + H_pbt, XF, yTax, yTax + H_tax, RED, 0.22)
rect(XR, yT, NW, H_rev, BLUE); rect(XG, yT, NW, H_gp, BLUE); rect(XO, yT, NW, H_op, BLUE)
if oth > 0: rect(XO, y_pbt, NW, H_oi, BLUE_XL)
rect(XP, y_pbt, NW, H_pbt, BLUE); rect(XF, yN, NW, H_ni, YEL)
rect(XF, yTax, NW, H_tax, RED); rect(XF, yOpx, NW, opex*k, RED); rect(XF, yCog, NW, cogs*k, RED)
out.append('</g>')

out.append('<g id="labels">')
def stage(x, y, name, val, col=BLUE_D):
    text(x, y, name, 17, INK, "sb"); text(x, y + 29, money(val), 26, col, "b")
c = lambda a: f"{round(a / rev * 100)}¢ per $1"
stage(XR + NW + 12, yT + 32, "Revenue", rev)
stage(XG + NW + 12, yT + 32, "Gross profit", gp); text(XG + NW + 12, yT + 96, c(gp), 15, GREY, "sb")
text(XO + NW + 12, yT + 32, "Operating", 17, INK, "sb"); text(XO + NW + 12, yT + 52, "profit", 17, INK, "sb")
text(XO + NW + 12, yT + 82, money(op), 26, BLUE_D, "b"); text(XO + NW + 12, yT + 106, c(op), 15, GREY, "sb")
stage(XP + NW + 12, yT + 32, "Pre-tax profit", pbt)
stage(XP + NW + 12, yN + 150, "Nvidia keeps".replace("Nvidia", co) if len(co) < 12 else "Company keeps", ni, INK)
text(XP + NW + 12, yN + 214, f"{round(ni / rev * 100)}¢ per $1", 15, INK, "sb")
if oth > 0: text(XO + NW + 10, y_pbt - 10, f"+{money(oth)} {d['other_label']}", 16, BLUE_D, "b")
def term(y, h, val, name):
    cy = y + h / 2
    text(XF - 12, cy - 2, "−" + money(val), 23, RED, "b", "r"); text(XF - 12, cy + 18, name, 16, RED, "sb", "r")
term(yTax, H_tax, tax, d["tax_name"]); term(yOpx, opex*k, opex, d["opex_name"]); term(yCog, cogs*k, cogs, d["cogs_name"])
out.append('</g>')

out.append('<g id="footer">')
text(X0, H - 40, f"{round(ni / rev * 100)}¢ of every $1 of revenue became profit", 30, INK, "b")
out.append('</g>')
out.append('<g id="source">')
text(X0, H - 4, d["source"], 15, GREY, "m")
out.append('</g>')

slug = re.sub(r"[^a-z0-9]+", "-", co.lower()).strip("-")
path = d.get("out", f"/mnt/user-data/outputs/{slug}-flow-fit.svg")
open(path, "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W*2}" height="{H*2}">\n' + "\n".join(out) + "\n</svg>\n")
stages = [[(XA + XR) / 2 + 30, yT + 300],
          [XG + 80, yT + 310],
          [XO + 80, yT + 310],
          [XP + 50, y_pbt + 300],
          [XF - 70, yN + 330]]
json.dump(stages, open(path.replace(".svg", ".stages.json"), "w"))
json.dump(RIBBONS, open(path.replace(".svg", ".ribbons.json"), "w"))
print("wrote", path, "k=%.2f" % k, "bottom", yCog + cogs*k)
