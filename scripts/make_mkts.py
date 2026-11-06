#!/usr/bin/env python3
"""True Economy 'Stock Market Today' card. Usage: python3 make_mkts.py data.json
Canvas 948x1300 = the safe zone of the white card (fills edge to edge). Transparent SVG, text outlined."""
import json, sys, re
from fontTools.ttLib import TTFont
from fontTools.t1Lib import T1Font
from fontTools.agl import UV2AGL
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.basePen import NullPen

W, H = 948, 1300
RED, BLUE, YEL = "#E23B3B", "#0760F1", "#FFF205"
BLUE_D, BLUE_L, BLUE_XL = "#0548B5", "#5B9BFF", "#8DB8FF"
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
X0=0; CW=948
l1="Stock market"
TX=38; size=min(92.0, (948-TX)/width("cb",l1,1)); b1=66; pitch=size*0.93
out.append('<g id="title">')
wt=width("cb","today.",size)
rect(X0, b1-size*0.70, 12, size*0.70+pitch, INK)
rect(X0+TX-6, b1+pitch-size*0.76, wt+12, size*0.93, YEL)
text(X0+TX,b1,l1,size,INK,"cb"); text(X0+TX,b1+pitch,"today.",size,INK,"cb")
text(X0,b1+pitch+52,d["date"]+" · US close",24,GREY,"m")
out.append('</g>')
GREEN="#6CBF3F"; CHH=int(__import__("os").environ.get("CHH","380"))
UP=d["sp_pts"][-1][1]>=d["sp_ref"]
TC=GREEN if UP else RED
TL_="#DDF2E5" if UP else "#FBE0DE"
def pct(v): return f"{v:+.2f}%".replace("-","−")
y0=b1+pitch+52+95
out.append('<g id="kpis">')
BS=min(140,948/width("b",d["big"],1)); SH=0.72*(BS-104)
text(X0,y0+34+SH,d["big"],BS,TC,"b")
text(X0,y0+74+SH,d["big_cap"],26,INK,"sb")
out.append('</g>')
# ---- S&P 500 price action (verified key points only)
HY=y0+112+SH+30
CY0,CY1=HY+22,y0+112+CHH      # plot top/bottom
PX0,PX1=X0+4,X0+CW-4
_v=[v for _,v in d["sp_pts"]]+[d["sp_ref"]]; _sp=max(max(_v)-min(_v),0.003*_v[0]); lo_,hi_=min(_v)-0.1*_sp,max(_v)+0.1*_sp
def PY(v): return CY1-(v-lo_)/(hi_-lo_)*(CY1-CY0)
pts=[(PX0+(PX1-PX0)*f,PY(v)) for f,v in d["sp_pts"]]
out.append('<g id="segments">')
poly=" ".join(f"{x:.1f},{y:.1f}" for x,y in pts)
out.append(f'<polygon points="{pts[0][0]:.1f},{CY1} {poly} {pts[-1][0]:.1f},{CY1}" fill="{TL_}"/>')
yref=PY(d["sp_ref"])
out.append(f'<line x1="{PX0}" x2="{PX1}" y1="{yref:.1f}" y2="{yref:.1f}" stroke="#999" stroke-width="2" stroke-dasharray="7 7"/>')
out.append(f'<polyline points="{poly}" fill="none" stroke="{TC}" stroke-width="7" stroke-linejoin="round" stroke-linecap="round"/>')
for i,(x,y) in enumerate(pts):
    if i not in (0,len(pts)-1) and len(pts)>2: continue
    r=11 if i==len(pts)-1 else 8
    out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#FAFAFA" stroke="{TC}" stroke-width="5"/>')
out.append('</g>')
out.append('<g id="labels">')
text(PX0+8,yref-12,d["sp_ref_lab"],16,GREY,"sb")
m1_,m2_=d["sp_lab_end"]
text(PX0,HY,"S&P 500",38,INK,"b"); text(PX0+width("b","S&P 500",38)+16,HY,m2_,38,TC,"b")
LW=max(width("sb",m1_,19),width("b",m2_,36))+14
ex,ey=pts[-1]; xs0=PX1-LW-6
near=[y for x,y in pts if x>=xs0-10]
if UP: by=max(near)+26          # label sits below the line (inside fill)
else: by=min(near)-26-62        # label sits above the line
by=max(CY0+4,min(by,CY1-66))
text(PX1,by+20,m1_,19,INK,"sb","r"); text(PX1,by+58,m2_,36,TC,"b","r")
for f,lab in [(0,d["prev_lab"]),(1,d["today_lab"])]:
    x=PX0+(PX1-PX0)*f; text(x,CY1+30,lab,16,GREY,"sb","l" if f==0 else ("r" if f==1 else "m"))
text(PX1,CY1+54,d["chart_note"],14,GREY,"m","r")
out.append('</g>')
# ---- world grid with circle flags
def flag(cx,cy,r,code,uid):
    o=[f'<clipPath id="c{uid}"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath><g clip-path="url(#c{uid})">']
    x0_,y0_,w_=cx-r,cy-r,2*r
    if code=="US":
        o.append(f'<rect x="{x0_}" y="{y0_}" width="{w_}" height="{w_}" fill="#FFFFFF"/>')
        for i in range(0,7,2): o.append(f'<rect x="{x0_}" y="{y0_+i*w_/7:.1f}" width="{w_}" height="{w_/7:.1f}" fill="#D22F27"/>')
        o.append(f'<rect x="{x0_}" y="{y0_}" width="{w_*0.55:.1f}" height="{w_*4/7:.1f}" fill="#1F3C88"/>')
    elif code=="JP":
        o.append(f'<rect x="{x0_}" y="{y0_}" width="{w_}" height="{w_}" fill="#FFFFFF"/><circle cx="{cx}" cy="{cy}" r="{r*0.42:.1f}" fill="#D7243A"/>')
    elif code=="KR":
        o.append(f'<rect x="{x0_}" y="{y0_}" width="{w_}" height="{w_}" fill="#FFFFFF"/>')
        rr=r*0.42
        o.append(f'<path d="M{cx-rr:.1f},{cy} A{rr:.1f},{rr:.1f} 0 0 1 {cx+rr:.1f},{cy} A{rr/2:.1f},{rr/2:.1f} 0 0 1 {cx:.1f},{cy} A{rr/2:.1f},{rr/2:.1f} 0 0 0 {cx-rr:.1f},{cy} Z" fill="#D7243A"/>')
        o.append(f'<path d="M{cx+rr:.1f},{cy} A{rr:.1f},{rr:.1f} 0 0 1 {cx-rr:.1f},{cy} A{rr/2:.1f},{rr/2:.1f} 0 0 1 {cx:.1f},{cy} A{rr/2:.1f},{rr/2:.1f} 0 0 0 {cx+rr:.1f},{cy} Z" fill="#1F4E9E"/>')
        for ang in (-45,45,135,225):
            o.append(f'<g transform="rotate({ang} {cx} {cy})"><rect x="{cx-r*0.18:.1f}" y="{cy-r*0.86:.1f}" width="{r*0.36:.1f}" height="{r*0.06:.1f}" fill="#111"/><rect x="{cx-r*0.18:.1f}" y="{cy-r*0.74:.1f}" width="{r*0.36:.1f}" height="{r*0.06:.1f}" fill="#111"/><rect x="{cx-r*0.18:.1f}" y="{cy-r*0.62:.1f}" width="{r*0.36:.1f}" height="{r*0.06:.1f}" fill="#111"/></g>')
    elif code=="UK":
        o.append(f'<rect x="{x0_}" y="{y0_}" width="{w_}" height="{w_}" fill="#1F3C88"/>')
        o.append(f'<path d="M{x0_},{y0_} L{x0_+w_},{y0_+w_} M{x0_+w_},{y0_} L{x0_},{y0_+w_}" stroke="#FFFFFF" stroke-width="{w_*0.2:.1f}"/>')
        o.append(f'<path d="M{x0_},{y0_} L{x0_+w_},{y0_+w_} M{x0_+w_},{y0_} L{x0_},{y0_+w_}" stroke="#D22F27" stroke-width="{w_*0.07:.1f}"/>')
        o.append(f'<path d="M{cx},{y0_} V{y0_+w_} M{x0_},{cy} H{x0_+w_}" stroke="#FFFFFF" stroke-width="{w_*0.34:.1f}"/>')
        o.append(f'<path d="M{cx},{y0_} V{y0_+w_} M{x0_},{cy} H{x0_+w_}" stroke="#D22F27" stroke-width="{w_*0.2:.1f}"/>')
    elif code=="HK":
        o.append(f'<rect x="{x0_}" y="{y0_}" width="{w_}" height="{w_}" fill="#DE2910"/>')
        for k in range(5):
            o.append(f'<ellipse cx="{cx}" cy="{cy-r*0.3:.1f}" rx="{r*0.17:.1f}" ry="{r*0.3:.1f}" fill="#FFFFFF" transform="rotate({k*72} {cx} {cy})"/>')
    o.append('</g>'); o.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#00000022" stroke-width="1.5"/>')
    return "".join(o)
GY=CY1+54+58
cwid=(CW-28)/3; rh=100
TILES=[]
out.append('<g id="tiles">')
for i,(nm,p,code,sub) in enumerate(d["world"]):
    cx_=X0+(i%3)*(cwid+14); cy_=GY+22+(i//3)*(rh+14)
    rect(cx_,cy_,cwid,rh,"#EEEEEC",1,6); TILES.append([cx_,cy_,cwid,rh,1 if p>=0 else -1])
out.append('</g>')
out.append('<g id="spine">')
text(X0,GY,"Around the world",22,INK,"b")
for i,(nm,p,code,sub) in enumerate(d["world"]):
    cx_=X0+(i%3)*(cwid+14); cy_=GY+22+(i//3)*(rh+14)
    out.append(flag(cx_+44,cy_+rh/2,26,code,i))
    col=RED if p<0 else GREEN
    text(cx_+86,cy_+32,nm,20,INK,"sb"); text(cx_+86,cy_+51,sub,14,GREY,"m"); text(cx_+86,cy_+88,pct(p),34,col,"b")
gbottom=GY+22+2*rh+14
out.append('</g>')
print("grid bottom",gbottom,"footer top",H-130)
out.append('<g id="footer">'); text(X0,H-40,d["footer"],30,INK,"b"); out.append('</g>')
out.append('<g id="source">'); text(X0,H-4,d["source"],15,GREY,"m"); out.append('</g>')
path=d["out"]
open(path,"w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W*2}" height="{H*2}">\n'+"\n".join(out)+"\n</svg>\n")
json.dump(TILES,open(path.replace(".svg",".tiles.json"),"w"))
json.dump({"up":UP},open(path.replace(".svg",".theme.json"),"w"))
json.dump([[round(x,1),round(y,1)] for x,y in pts],open(path.replace(".svg",".pts.json"),"w"))
print("wrote",path)
