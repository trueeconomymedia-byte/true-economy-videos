import sys; sys.path.insert(0,"/tmp")
from te_lib import *
BD="#2A62AE"
L=[("VAT (20%)",1.67,BLUE_L,0.60),("Alcohol duty",0.60,BLUE_L,0.60),("Beer supply",1.50,BLUE,0.40),("Staff",1.70,BLUE,0.40),("Rent and property",2.50,BLUE,0.40),("Other overheads",1.00,BLUE,0.40),("Pub profit",1.03,YEL,0.55)]
assert abs(sum(l[1] for l in L)-10)<1e-9
c=Card(); c.title("Where a £10 pint","really goes",mark="really goes",accent="tall")
c.subtitle("Illustrative London pub example · follow the pint")
ytop=c.top+36; k=62; wtop,wbot=330,250; x0=16
cx=x0+wtop/2
def hw(y): return (wtop+(wbot-wtop)*(y-ytop)/(10*k))/2
gap=[0,0,26,26,26,26,38]; tx=560; y=ytop+8; tg=[]
for i,l in enumerate(L):
    y+=gap[i]; tg.append((y,y+l[1]*k)); y+=l[1]*k
ys=[];y=ytop
for l in L: ys.append((y,y+l[1]*k)); y+=l[1]*k
with c.group("body"):
    # ribbons (light tint, streaks run along them in the video)
    for (n,v,col,op),(y1,y2),(t1,t2) in zip(L,ys,tg):
        xs=cx+hw((y1+y2)/2)+2
        c.ribbon(xs,y1,y2,tx,t1,t2,col,op)
    # glass layers
    for i,((n,v,col,op),(y1,y2)) in enumerate(zip(L,ys)):
        c.polygon([(cx-hw(y1),y1),(cx+hw(y1),y1),(cx+hw(y2),y2),(cx-hw(y2),y2)],col)
        if i: c.line(cx-hw(y1),y1,cx+hw(y1),y1,"#FBF8F1",3)
    yb=ytop+10*k
    # glass outline: open top, thick base
    c.polyline([(cx-hw(ytop)-7,ytop-8),(cx-hw(yb)-7,yb+16),(cx+hw(yb)+7,yb+16),(cx+hw(ytop)+7,ytop-8)],INK,9)
    for (n,v,col,op),(t1,t2) in zip(L,tg):
        c.rect(tx,t1,12,t2-t1,col); m=(t1+t2)/2
        c.text(tx+30,m+11,f"£{v:.2f}",34,BD if col!=YEL else INK,"b"); c.text(tx+142,m+9,n,22,INK,"sb")
    c.text(0,H-100-26-12,"£2.27 tax + £6.70 costs + £1.03 profit = £10.00",27,INK,"b")
c.footer("The taxman takes more than twice what the pub keeps.")
c.source("Source: UHY Hacker Young (May 2026), gov.uk duty rates · illustrative, rounded")
c.save("/tmp/ideas/pint-flow.svg")
