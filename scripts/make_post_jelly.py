#!/usr/bin/env python3
"""JELLYFISH FLOW (user-approved 26 Nov 2026, DEFAULT form for the where_tax_goes series).
A top-to-bottom flow chart: a narrow "bell" at the top (money in) merges into one total bar, then the ribbons fan out
wider and further apart the lower they go ("tentacles"), each ending in a node with a big value + short name below.
Rules the user set while iterating (26 Nov): ONE unit across the whole chart (e.g. cents per $1 of tax; trillions only in
the subtitle), ONE idea, no KPI table (the chart is the hero), no step tags or equation bands, a colour per output group,
pastel ribbons with dark edge bars (Meta money-flow style), moving streaks on every ribbon (anim "vflow", rendered by
video_card.py -> video_card_flat.py). More layers going down (e.g. groups -> items) are allowed when they paint a clearer
picture, but keep it simple: the 8-way + 4-group + step-tag version was judged too complex.
Reference: videos/where_tax_goes-tax-dollar-jelly-2026-11-26.mp4. usage: python3 -I make_post_jelly.py"""
import sys; sys.path.insert(0, "/tmp"); sys.path.insert(0, "/tmp/tev/scripts")
from te_lib import *
OUT="/mnt/user-data/outputs/tax-dollar-us-2026-jelly4.svg"
rec, outl = 5403.327, 7395.800
GRAPH="#3B3A38"
outs=[("Pensions","Social Security",1667,BLUE),("Health","incl. Medicare, Medicaid",1073+1026,BLUE_L),("Interest","on the debt",1052,YEL),
      ("Defence","& veterans",965+416,GRAPH),("Everything","else",694+503,"#C4BFB6")]
assert sum(o[2] for o in outs)==7396
cents=[round(o[2]/rec*100) for o in outs]; print(cents, sum(cents)); assert sum(cents)==137
c=Card(); c.title("For every $1 of tax,","the US spends $1.37",mark="$1.37",accent="none")
c.subtitle("US federal budget, fiscal 2026 · $5.40tn in tax, $7.40tn spent")
k=3.9; EB=14
c.anim["vflow"]=[]
def vrib(ys, xs0, xs1, yd, xd0, xd1, col, op=None):
    op = op or {GRAPH:0.2, BLUE_L:0.6, "#C4BFB6":0.45}.get(col,0.30)
    c.anim["vflow"].append([ys, xs0, xs1, yd, xd0, xd1, col]); ym=(ys+yd)/2
    c._o(f'<path d="M{xs0:.1f},{ys:.1f} C{xs0:.1f},{ym:.1f} {xd0:.1f},{ym:.1f} {xd0:.1f},{yd:.1f} L{xd1:.1f},{yd:.1f} C{xd1:.1f},{ym:.1f} {xs1:.1f},{ym:.1f} {xs1:.1f},{ys:.1f} Z" fill="{solid(col,op)}"/>')
T=c.top; y0=T+96; y1=y0+230; y3=c.bottom-128
tax_c, bor_c = rec/rec*100, (outl-rec)/rec*100
wt, wb = tax_c*k, bor_c*k; sg=30
xt=(948-(wt+wb+sg))/2; xbr=xt+wt+sg
ws=wt+wb; xs0=(948-ws)/2
ow=[o[2]/rec*100*k for o in outs]; GAP=(946-sum(ow))/(len(outs)-1); x=1; ox=[]
for w in ow: ox.append(x); x+=w+GAP
with c.group("body"):
    vrib(y0+EB,xt,xt+wt,y1,xs0,xs0+wt,GREEN); vrib(y0+EB,xbr,xbr+wb,y1,xs0+wt,xs0+ws,RED)
    cx=xs0
    for o,x,w in zip(outs,ox,ow): vrib(y1+EB,cx,cx+w,y3,x,x+w,o[3]); cx+=w
    c.rect(xt,y0,wt,EB,GREEN); c.rect(xbr,y0,wb,EB,RED)
    c.rect(xs0,y1,wt,EB,GREEN); c.rect(xs0+wt,y1,wb,EB,RED)
    for o,x,w in zip(outs,ox,ow): c.rect(x,y3,w,EB,o[3])
with c.group("toplabels"):
    c.text(xt+wt/2,y0-50,"$1.00",44,GREEN,"b","m"); c.text(xt+wt/2,y0-16,"of tax collected",20,INK,"m","m")
    c.text(xbr+wb/2,y0-50,"+37¢",44,RED,"b","m"); c.text(xbr+wb/2,y0-16,"borrowed",20,INK,"m","m")
    c.text(xs0-18,y1+6,"$1.37",40,INK,"b","r"); c.text(xs0-18,y1+34,"spent",20,INK,"m","r")
    for o,x,w,cc in zip(outs,ox,ow,cents):
        m=min(max(x+w/2,60),888)
        c.text(m,y3+EB+44,f"{cc}¢",40,INK,"b","m"); c.text(m,y3+EB+72,o[0],20,INK,"sb","m")
        if o[1]: c.text(m,y3+EB+96,o[1],17,GREY,"m","m")
c.footer("The extra 37¢ on every tax dollar is borrowed")
c.source("Source: US Treasury Monthly Treasury Statement (Sep 2026), CBO · FY2026 Oct–Sep · cents per $1 of tax")
c.save(OUT)
