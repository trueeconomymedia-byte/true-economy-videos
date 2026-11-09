import sys; sys.path.insert(0,"/tmp")
from te_lib import *
c=Card()
c.title("US vs UK: rates match,","unemployment doesn't",mark="unemployment",accent="none")
c.subtitle("Latest official figures, October–November 2026")
AX=474; HALF=300; SC=6.6; BH=88
RED_L=solid(RED,0.45)
# (header, sublabel, us, uk, ustxt, uktxt, us_strong, uk_strong, verdict)
rows=[("Inflation","prices vs a year ago · Sep 2026 · lower is better",3.7,3.5,"3.7%","3.5%",False,True,"UK prices rise 0.2 points slower"),
      ("Central bank rate","Fed 28 Oct · BoE 5 Nov · no winner",3.875,4.0,"3.75–4.00%","4.00%",True,True,"Both central banks sit at about 4%"),
      ("Unemployment","US Oct · UK Jun–Aug 2026 · lower is better",4.1,4.7,"4.1%","4.7%",True,False,"UK unemployment is 0.6 points higher")]
y0=c.top-6; pitch=(c.bottom-y0+8)/3
vals=[]
with c.group("body"):
    for i,(hd,sub,us,uk,ust,ukt,uss,uks,verd) in enumerate(rows):
        y=y0+i*pitch
        c.text(AX,y+30,hd,32,INK,"b","m"); c.text(AX,y+58,sub,fit("m",sub,18,900),GREY,"m","m")
        by=y+78
        uw=us/SC*HALF; kw=uk/SC*HALF
        if i==1:  # fed range: solid to 3.75, light cap to 4.00
            sw=3.75/SC*HALF
            c.rect(AX-sw,by,sw,BH,BLUE); c.rect(AX-uw*0-4.0/SC*HALF,by,4.0/SC*HALF-sw,BH,BLUE_L)
            uw=4.0/SC*HALF
        else:
            c.rect(AX-uw,by,uw,BH,BLUE if uss else BLUE_L)
        c.rect(AX,by,kw,BH,RED if uks else RED_L)
        c.rect(AX-2,by-10,4,BH+20,INK)
        vals.append((AX-uw-14,by+BH/2+16,ust,"r")); vals.append((AX+kw+14,by+BH/2+16,ukt,"l"))
        vy=by+BH+14
        # verdict sits straight on the paper: no box, no rule (user 9 Nov)
        c.text(AX,vy+33,verd,fit("b",verd,25,490),INK,"b","m")
with c.group("toplabels"):
    for i,(hd,sub,us,uk,ust,ukt,uss,uks,verd) in enumerate(rows):
        by=y0+i*pitch+78
        c.text(AX-18,by+BH/2+9,"US",26,"#FFFFFF" if uss else INK,"b","r")
        c.text(AX+18,by+BH/2+9,"UK",26,"#FFFFFF" if uks else INK,"b","l")
    for x,y,t,a in vals: c.text(x,y,t,38 if len(t)>6 else 46,INK,"b",a)
c.footer("Rates match; the UK has more people out of work")
c.source("Source: BLS, Federal Reserve, ONS, Bank of England · Sep–Nov 2026")
c.save("/mnt/user-data/outputs/us-vs-uk-economy-now-axis.svg")
