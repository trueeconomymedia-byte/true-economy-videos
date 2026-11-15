import sys, math; sys.path.insert(0,"/tmp")
from te_lib import *
c=Card()
c.title("Why prices keep","climbing",mark="climbing",accent="none")
c.subtitle("Where a typical $100 of US spending goes, and how prices rose in October 2026")
PAPER="#FBF8F1"; W_="#FFFFFF"
# name, share, fill, text colour, price-change line(s)
sl=[("Housing",35,BLUE,W_,["+0.3% in Oct"]),
    ("Everything else",44,BLUE_L,INK,["mixed in Oct","used cars −1.2%, medical +0.3%"]),
    ("Food",13,BLUE_L,INK,["+0.5% in Oct"]),
    ("Energy",8,RED,W_,["+0.7%"])]
assert sum(s[1] for s in sl)==100
R=372; cx=474
with c.group("hdr"):
    c.text(474,c.top+4,"Each slice = $ of every $100 spent · small print = price rise in October",20,GREY,"m","m")
cy=c.top+30+R
def pt(a,r): return cx+r*math.sin(math.radians(a)), cy-r*math.cos(math.radians(a))
with c.group("body"):
    a0=0
    for name,v,col,tc,chg in sl:
        a1=a0+v*3.6
        x0,y0=pt(a0,R); x1,y1=pt(a1,R); large=1 if a1-a0>180 else 0
        c.path(f"M{cx},{cy} L{x0:.1f},{y0:.1f} A{R},{R} 0 {large} 1 {x1:.1f},{y1:.1f} Z",fill=col,stroke=PAPER,sw=6)
        rr={35:0.60,44:0.58,13:0.66,8:0.78}[v]
        mx,my=pt((a0+a1)/2,R*rr)
        big={35:78,44:84,13:60,8:46}[v]; nsz={35:28,44:30,13:24,8:20}[v]; csz={35:26,44:26,13:22,8:24}[v]
        lines=[(f"${v}",big,"b"),(name,nsz,"sb")]+[(t,csz if i==0 else 19,"b" if i==0 else "m") for i,t in enumerate(chg)]
        # stack centred on (mx,my)
        gaps=[big*0.95,nsz*1.25]+[csz*1.3 if i==0 else 24 for i in range(len(chg))]
        total=sum(gaps)
        y=my-total/2+big*0.8
        for (t,sz,fk),g in zip(lines,gaps):
            c.text(mx,y,t,sz,tc,fk,"m"); y+=g if False else g
        a0=a1
print("pie bottom",cy+R,"limit",H-80-106)
c.kpi_row([("Prices in one month (Oct 2026)","+0.4%","above the 0.3% economists expected")],y=H-80-106-4,hi=0)
c.footer("Housing is the biggest slice of the basket, so its rises matter.")
c.source("Source: US BLS CPI, Oct 2026 (seasonally adjusted; Sep 2026 basket weights, rounded) · no yearly rate: Oct 2025 not collected")
c.save("/mnt/user-data/outputs/why-prices-climbing.svg")
