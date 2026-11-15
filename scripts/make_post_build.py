import sys; sys.path.insert(0,"/tmp")
from te_lib import *
BD="#2A62AE"
# verified inputs (BLS CPI Oct 2026): Sep-2026 relative importance and Oct monthly % changes (SA)
w=dict(shelter=35.238, food=13.447, energy=7.649, core=78.905); chg=dict(shelter=0.3, food=0.5, energy=0.7, core=0.3)
con=dict(shelter=w['shelter']*chg['shelter']/100,
         core_ex=(w['core']*chg['core']-w['shelter']*chg['shelter'])/100,
         food=w['food']*chg['food']/100, energy=w['energy']*chg['energy']/100)
tot=sum(con.values()); print({k:round(v,3) for k,v in con.items()}, round(tot,3))
r2={k:round(v,2) for k,v in con.items()}; print(r2, round(sum(r2.values()),2))
share={k:v/tot*100 for k,v in con.items()}; print({k:round(v) for k,v in share.items()})
c=Card()
c.title("Why prices keep","climbing",mark="climbing",accent="none")
c.subtitle("What pushed US prices up 0.4% in October 2026")
cols=[("Housing","35% of spending","× +0.3% rise",con['shelter'],BLUE),
      ("Everything else","44% of spending","× about +0.3% rise",con['core_ex'],BLUE),
      ("Food","13% of spending","× +0.5% rise",con['food'],BLUE),
      ("Energy","8% of spending","× +0.7% rise",con['energy'],BLUE)]
base=905; k=1330.0; bw=124; pitch=190; x0=95
with c.group("hdr"):
    c.text(474,c.top+4,"Each block = share of spending × its price rise",24,INK,"b","m")
    c.text(474,c.top+32,"measured in percentage points of the monthly rise",18,GREY,"m","m")
with c.group("body"):
    c.line(0,base,948,base,INK,3)
    cum=0; tops=[]
    for i,(nm,l1,l2,v,col) in enumerate(cols):
        cx=x0+i*pitch; y_top=base-(cum+v)*k; y_bot=base-cum*k
        c.rect(cx-bw/2,y_top,bw,y_bot-y_top,col,1,2)
        c.text(cx,y_top-12,f"+{v:.2f}",32,BD,"b","m")
        tops.append((cx,y_top)); cum+=v
        c.text(cx,base+34,nm,22,INK,"b","m"); c.text(cx,base+58,l1,16,GREY,"m","m"); c.text(cx,base+78,l2,16,GREY,"m","m")
        c.text(cx,(y_top+y_bot)/2+6,f"{share[['shelter','core_ex','food','energy'][i]]:.0f}%",24,"#FFFFFF","b","m") if (y_bot-y_top)>54 else None
    for i in range(len(cols)-1):  # dotted connectors between tops
        (xa,ya),(xb,yb)=tops[i],tops[i+1]; c.line(xa+bw/2,ya,xb-bw/2,ya,"#CFC8B8",2,"5 5")
    tx=x0+4*pitch; ty=base-tot*k
    c.line(tops[3][0]+bw/2,ty,tx-bw/2,ty,"#CFC8B8",2,"5 5")
    c.rect(tx-bw/2,ty,bw,base-ty,RED,1,2)
    c.text(tx,ty-12,"≈ +0.36",32,RED,"b","m")
    c.text(tx,base+34,"Total",22,INK,"b","m"); c.text(tx,base+58,"reported as",16,GREY,"m","m"); c.text(tx,base+78,"+0.4% (rounded)",16,GREY,"m","m")
    c.text(tx,(ty+base)/2+6,"100%",24,"#FFFFFF","b","m")
    c.text(0,base+122,"0.11 + 0.13 + 0.07 + 0.05 ≈ 0.36, reported as +0.4%",24,INK,"b")
    c.text(0,base+148,"White % = each part's share of the rise. Approximate: basket weight × rounded monthly change.",16,GREY,"m")
c.kpi_row([("US price rise in October 2026, all items","+0.4%","above the 0.3% economists expected")],y=H-80-106-4,hi=0)
c.footer("Housing is 35% of spending and drove about 30% of the rise.")
c.source("Source: US BLS CPI, Oct 2026 (seasonally adjusted; Sep 2026 basket weights) · contributions computed, approximate")
c.save("/mnt/user-data/outputs/why-prices-climbing.svg")
