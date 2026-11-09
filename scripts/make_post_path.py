import sys, math; sys.path.insert(0,"/tmp")
from te_lib import *
c=Card()
c.title("How the US builds","its national debt",mark="national debt",accent="none")
c.subtitle("Follow the money · US federal government, fiscal year 2026")
INKC="#171615"; W_="#FFFFFF"
def bz(p0,p1,p2,p3,n=60):
    out=[]
    for i in range(n+1):
        t=i/n;u=1-t
        out.append((u**3*p0[0]+3*u*u*t*p1[0]+3*u*t*t*p2[0]+t**3*p3[0], u**3*p0[1]+3*u*u*t*p1[1]+3*u*t*t*p2[1]+t**3*p3[1]))
    return out
Y1=410; A=(88,Y1); B=(860,Y1); G=(474,Y1); rA=46; rG=78
E=(200,720); I=(650,720); rE=44; D=(474,1005); rD=58
# paths (polylines); last point = tip of the arrowhead
P1=[(A[0]+rA+6,Y1),(G[0]-rG-6,Y1)]
P2=[(B[0]-rA-6,Y1),(G[0]+rG+6,Y1)]
P3=bz((432,475),(350,555),(200,555),(200,E[1]-rE-8))
P4=bz((516,475),(598,555),(650,555),(650,I[1]-rE-8))
P5=bz((860,Y1+rA+6),(888,730),(760,1005),(D[0]+rD+8,1005))
def tip(pts,col):
    (x1,y1),(x2,y2)=pts[-2],pts[-1]; a=math.atan2(y2-y1,x2-x1); L=18; Wd=11
    bx,by=x2-L*math.cos(a),y2-L*math.sin(a)
    c.polygon([(x2,y2),(bx-Wd*math.sin(a),by+Wd*math.cos(a)),(bx+Wd*math.sin(a),by-Wd*math.cos(a))],col)
    return (bx,by)
def dotted(pts,col):
    (x1,y1),(x2,y2)=pts[-2],pts[-1]; a=math.atan2(y2-y1,x2-x1); bx,by=x2-14*math.cos(a),y2-14*math.sin(a)
    q=pts[:-1]+[(bx,by)]
    d="M"+" L".join(f"{x:.1f},{y:.1f}" for x,y in q)
    c._o(f'<path d="{d}" fill="none" stroke="{solid(col,0.5)}" stroke-width="5" stroke-linecap="round" stroke-dasharray="1 11"/>')
    tip(pts,col)
def lab(cx,y,title,num,col,sz=50,tw=22):
    c.text(cx,y,title,tw,INK,"sb","m"); c.text(cx,y+sz+6,num,sz,col,"b","m")
with c.group("body"):
    for pts,col in ((P1,BLUE),(P2,RED),(P3,BLUE),(P4,RED),(P5,RED)): dotted(pts,col)
    c.circle(*A,rA,BLUE); c.circle(*B,rA,RED); c.circle(*G,rG,INKC)
    c.circle(*E,rE,BLUE); c.circle(*I,rE,RED); c.circle(*D,rD,RED)
    lab(A[0],Y1-rA-70,"Taxes collected","$5.4tn",BLUE)
    lab(B[0]-8,Y1-rA-70,"Borrowed","$2.0tn",RED)
    c.text(G[0],Y1-rG-16,"The US government spends",22,INK,"sb","m")
    lab(E[0],E[1]+rE+30,"Everything else","$6.3tn",BLUE,46)
    lab(I[0],I[1]+rE+30,"Interest on past debt","$1.1tn",RED,46)
    c.text(412,E[1]+8,"$6.3tn + $1.1tn = $7.4tn",21,INK,"b","m")
    c.text(D[0],D[1]+rD+30,"The national debt",24,INK,"sb","m")
    c.text(D[0],D[1]+rD+88,"$32.4tn",54,RED,"b","m")
    c.text(D[0],D[1]+rD+118,"up from $30.3tn: this year's borrowing is added on",20,GREY,"sb","m")
    c.text(728,905,"the borrowing is added to the debt",19,RED,"sb","r")
with c.group("toplabels"):
    # white flat icons
    x,y=A; c.rect(x-26,y-17,52,34,W_,1,5); c.circle(x,y,9,BLUE); c.rect(x-21,y-12,7,4,BLUE,1,2); c.rect(x+14,y+8,7,4,BLUE,1,2)
    x,y=B; c.rect(x-27,y-19,54,38,W_,1,6); c.rect(x-27,y-10,54,9,RED); c.rect(x-21,y+7,18,5,RED,1,2)
    x,y=G; ix,iy=x,y-48
    c.polygon([(ix,iy-15),(ix-24,iy-5),(ix+24,iy-5)],W_)
    for k in (-18,-6,6,18): c.rect(ix+k-3,iy-2,6,16,W_)
    c.rect(ix-26,iy+15,52,5,W_)
    c.text(x,y+22,"$7.4tn",42,W_,"b","m"); c.text(x,y+50,"5.4 + 2.0",18,W_,"sb","m")
    x,y=E
    for dx in (-13,3):
        for dy in (-13,3): c.rect(x+dx,y+dy,11,11,W_,1,3)
    c.text(*I,"",1) if False else None
    x,y=I; c.text(x,y+13,"%",38,W_,"b","m")
    x,y=D; c.rect(x-34,y+12,68,13,W_,1,3); c.rect(x-26,y-4,52,13,W_,1,3); c.rect(x-17,y-20,34,13,W_,1,3)
    c.polygon([(x,y-42),(x-11,y-29),(x+11,y-29)],W_)
c.footer("Spend more than you collect, and the gap lands on the debt.")
c.source("Source: CBO (Oct 2026), US Treasury via American Action Forum · FY2026 · dots illustrative")
def pp(pts): return [[round(a,1),round(b,1)] for a,b in pts]
BL=[54,112,208]; RD=[217,68,55]
paths=[{"pts":pp(P1),"rgb":BL,"win":[0.05,0.22],"n":10},
       {"pts":pp(P2),"rgb":RD,"win":[0.20,0.37],"n":8},
       {"pts":pp(P3),"rgb":BL,"win":[0.45,0.62],"n":10},
       {"pts":pp(P4),"rgb":RD,"win":[0.47,0.64],"n":6},
       {"pts":pp(P5),"rgb":RD,"win":[0.62,0.86],"n":9}]
def pl(c_,r,w): return [c_[0]-r,c_[1]-r,2*r,2*r,[255,255,255],None,r,w]
pulses=[pl(A,rA,[0.02,0.12]),pl(B,rA,[0.17,0.27]),pl(G,rG,[0.36,0.47]),pl(E,rE,[0.60,0.70]),pl(I,rE,[0.62,0.72]),pl(D,rD,[0.84,0.96])]
c.save("/mnt/user-data/outputs/national-debt-path.svg",anim={"paths":paths,"pulse":pulses})
