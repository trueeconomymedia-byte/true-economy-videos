import sys; sys.path.insert(0,"/tmp")
from te_lib import *
c=Card()
c.title("How the US builds","its national debt",mark="national debt",accent="none")
c.subtitle("US federal government, fiscal year 2026 · each dot is money moving")
INKC="#171615"
y0=c.top+18; k=89.0; G=24
tx,bw_,sp,inn,oth=5.4,2.0,7.4,1.1,6.3
X1,X2,X3=0,439,878; NW=70
# nodes
a1=y0; b1=y0+tx*k+G
t2=y0+8
t3=y0; i3=y0+oth*k+G
anim_flow=[];anim_pulse=[]
with c.group("body"):
    for x,t in ((0,"WHERE IT COMES FROM"),):
        c.text(0,c.top+2,t,17,GREY,"sb")
    c.text(474,c.top+2,"THE GOVERNMENT",17,GREY,"sb","m"); c.text(948,c.top+2,"WHERE IT GOES",17,GREY,"sb","r")
    rib=lambda xs,ys0,ys1,xd,yd0,yd1,col: c.ribbon(xs,ys0,ys1,xd,yd0,yd1,col,0.30,animate=False)
    # ribbons (light tint) then nodes
    rib(X1+NW,a1,a1+tx*k,X2,t2,t2+tx*k,BLUE)
    rib(X1+NW,b1,b1+bw_*k,X2,t2+tx*k,t2+sp*k,RED)
    rib(X2+NW,t2,t2+oth*k,X3,t3,t3+oth*k,BLUE)
    rib(X2+NW,t2+oth*k,t2+sp*k,X3,i3,i3+inn*k,RED)
    c.rect(X1,a1,NW,tx*k,BLUE); c.rect(X1,b1,NW,bw_*k,RED)
    c.rect(X2,t2,NW,sp*k,INKC)
    c.rect(X3,t3,NW,oth*k,BLUE); c.rect(X3,i3,NW,inn*k,RED)
    end=i3+inn*k
    # sum line
    sy=end+44
    c.text(474,sy,"$5.4tn collected + $2.0tn borrowed = $7.4tn spent",25,INK,"b","m")
    # debt strip
    dy=sy+62
    c.text(0,dy,"The borrowing piles up as the national debt",26,INK,"b")
    sc=948/32.4; A=30.3*sc
    c.rect(0,dy+18,A,66,BLUE_L); c.rect(A,dy+18,2.1*sc,66,RED)
    c.text(14,dy+18+42,"$30.3tn debt at the end of 2025",23,INK,"b")
    c.text(948,dy+18+66+34,"+$2.1tn this year = $32.4tn owed, about 100% of US GDP",20,INK,"b","r")
    print("end",dy+18+66+34,"limit",c.bottom)
with c.group("toplabels"):
    ymid=lambda a,h:a+h/2
    c.text(104,ymid(a1,tx*k)-6,"Taxes collected",24,INK,"sb"); c.text(104,ymid(a1,tx*k)+48,"$5.4tn",62,INK,"b")
    c.text(104,ymid(b1,bw_*k)-4,"Borrowed",24,INK,"sb"); c.text(104,ymid(b1,bw_*k)+44,"$2.0tn",50,RED,"b")
    c.text(543,ymid(t3,oth*k)-6,"Everything else",24,INK,"sb"); c.text(543,ymid(t3,oth*k)+48,"$6.3tn",62,INK,"b")
    c.text(543,ymid(i3,inn*k)+9,"Interest on debt $1.1tn",25,RED,"b")
# animation, sequenced across the loop
F=[[X1+NW,a1,a1+tx*k,X2,t2,t2+tx*k,"#3670D0",[0.03,0.30]],
   [X1+NW,b1,b1+bw_*k,X2,t2+tx*k,t2+sp*k,"#D94437",[0.28,0.48]],
   [X2+NW,t2,t2+oth*k,X3,t3,t3+oth*k,"#3670D0",[0.46,0.72]],
   [X2+NW,t2+oth*k,t2+sp*k,X3,i3,i3+inn*k,"#D94437",[0.55,0.78]]]
P=[[X1,b1,NW,bw_*k,[255,255,255],None,0,[0.26,0.48]],
   [X2,t2,NW,sp*k,[255,255,255],None,0,[0.44,0.56]],
   [A,dy+18,2.1*sc,66,[255,255,255],None,4,[0.76,0.96]]]
c.footer("Spend more than you collect, and the gap lands on the debt.")
c.source("Source: CBO (Oct 2026), US Treasury via American Action Forum · FY2026 · dots illustrative")
c.save("/mnt/user-data/outputs/national-debt-flow.svg",anim={"flow":F,"pulse":P})
