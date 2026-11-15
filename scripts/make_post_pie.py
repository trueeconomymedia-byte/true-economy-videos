import sys, math; sys.path.insert(0,"/tmp")
from te_lib import *
c=Card()
c.title("Why prices keep","climbing",mark="climbing",accent="none")
c.subtitle("US inflation, October 2026: where $100 of spending goes")
PAPER="#FBF8F1"; W_="#FFFFFF"; BD="#2A62AE"
sl=[("Housing","rent and owning",35,BLUE,W_,"+0.3%","price rise in October",BD),
    ("Everything else","health, transport, clothes, leisure",44,BLUE_L,INK,"mixed","Oct: used cars −1.2%, medical +0.3%",BD),
    ("Food","groceries and eating out",13,BLUE_L,INK,"+0.5%","price rise in October",BD),
    ("Energy","fuel, electricity, gas",8,RED,W_,"+0.7%","price rise in October (fastest)",RED)]
assert sum(s[2] for s in sl)==100
R=206; cx=474
with c.group("hdr"):
    c.text(474,c.top+6,"A typical $100 of US spending, split four ways",26,INK,"b","m")
cy=c.top+30+R
def pt(a,r): return cx+r*math.sin(math.radians(a)), cy-r*math.cos(math.radians(a))
with c.group("body"):
    a0=0
    for name,desc,v,col,tc,chg,sub,ct in sl:
        a1=a0+v*3.6
        x0,y0=pt(a0,R); x1,y1=pt(a1,R); large=1 if a1-a0>180 else 0
        c.path(f"M{cx},{cy} L{x0:.1f},{y0:.1f} A{R},{R} 0 {large} 1 {x1:.1f},{y1:.1f} Z",fill=col,stroke=PAPER,sw=5)
        rr={35:0.60,44:0.58,13:0.68,8:0.78}[v]
        mx,my=pt((a0+a1)/2,R*rr)
        big={35:56,44:62,13:44,8:36}[v]
        if v>=13:
            c.text(mx,my+big*0.2,f"${v}",big,tc,"b","m"); c.text(mx,my+big*0.2+26,name if v!=44 else "Everything else",20,tc,"sb","m")
        else: c.text(mx,my+big*0.3,f"${v}",big,tc,"b","m")
        a0=a1
    y=cy+R+22
    c.text(0,y+14,"Where it goes",18,GREY,"sb"); c.text(948,y+14,"Price change in October",18,GREY,"sb","r")
    c.line(0,y+24,948,y+24,"#CFC8B8",2)
    y+=34; rh=74
    for name,desc,v,col,tc,chg,sub,ct in sl:
        c.rect(0,y,8,rh-20,col)
        c.text(26,y+26,name,28,INK,"b")
        c.text(26,y+50,f"${v} of every $100 · {desc}",18,GREY,"m")
        c.text(948,y+30,chg,38,ct,"b","r")
        c.text(948,y+52,sub,16,GREY,"m","r")
        y+=rh
print("end",y,"limit",H-80-106)
c.kpi_row([("All prices together, in one month (Oct 2026)","+0.4%","above the 0.3% economists expected")],y=H-80-106-4,hi=0)
c.footer("Housing is the biggest slice of the basket, so its rises matter.")
c.source("Source: US BLS CPI, Oct 2026 (seasonally adjusted; Sep 2026 basket weights, rounded) · no yearly rate: Oct 2025 not collected")
c.save("/mnt/user-data/outputs/why-prices-climbing.svg")
