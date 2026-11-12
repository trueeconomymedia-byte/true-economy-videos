import sys; sys.path.insert(0,"/tmp")
from te_lib import *
c=Card()
c.title("Where a £10 pint","really goes",mark="really goes",accent="tall")
c.subtitle("Illustrative London pub example · every £10 pint, split 7 ways")
BD="#2A62AE"
items=[("VAT (20%)",1.67,BLUE_L,"t"),("Alcohol duty",0.60,BLUE_L,"t"),("Beer supply",1.50,BLUE,"c"),("Staff",1.70,BLUE,"c"),
       ("Rent and property",2.50,BLUE,"c"),("Other overheads",1.00,BLUE,"c"),("Pub profit",1.03,YEL,"p")]
assert abs(sum(i[1] for i in items)-10)<1e-9
kpi_h=106; sumy=H-80-kpi_h-62
y0=c.top+8; hc=sumy-30-y0; k=hc/10; cx,cw=0,230
print("top",c.top,"scale",k)
ys=[];y=y0
for n,v,col,g in items: ys.append((y,v*k)); y+=v*k
with c.group("body"):
    for i,((yy,hh),(n,v,col,g)) in enumerate(zip(ys,items)):
        c.rect(cx,yy,cw,hh-2,col)
        c.text(cx+cw/2,yy+hh/2+9,str(i+1),26,"#FFFFFF" if col==BLUE else INK,"b","m")
        mid=yy+hh/2
        c.line(cw+6,mid-1,292,mid-1,"#CFC8B8",2)
        c.text(304,mid+11,f"£{v:.2f}",34,BD if g!="p" else INK,"b")
        c.text(420,mid+9,n,24,INK,"sb")
    # group brackets
    def br(a,b,col,top_txt,amt,sub):
        ya=ys[a][0]; yb=ys[b][0]+ys[b][1]-2
        c.rect(690,ya,6,yb-ya,col)
        m=(ya+yb)/2
        c.text(712,m-6,amt,44,col if col!=BLUE_L else BD,"b")
        c.text(712,m+26,sub,21,INK,"sb")
    br(0,1,BLUE_L,"","£2.27","goes to tax")
    br(2,5,BLUE,"","£6.70","pub's costs")
    br(6,6,"#E0A800","","£1.03","left for the pub")
    c.text(0,sumy+12,"£2.27 tax + £6.70 costs + £1.03 profit = £10.00",25,INK,"b")
with c.group("kpis_wrap"):
    pass
c.kpi_row([("The pub's profit on a £10 pint","£1.03","about 10p in every £1, before corporation tax")],y=H-80-kpi_h-4,hi=0)
c.footer("The taxman takes more than twice what the pub keeps.")
c.source("Source: UHY Hacker Young (May 2026), gov.uk duty rates, BBPA/CAMRA ranges · illustrative, rounded")
px,py,pw,ph=cx,ys[6][0],cw,ys[6][1]-2
c.pulse(px,py,pw,ph,(255,255,255))
c.save("/mnt/user-data/outputs/pint-price.svg")
