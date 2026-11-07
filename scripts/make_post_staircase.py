# TEMPLATE for data_surprise cards. POSITIVE story = green family: light green #A5CCAD context columns, dark green #4A9A51 focal beat (ink text). MISS/negative story = light blue context + red #E23B3B focal; neutral = blues. See feedback.md.
import sys; sys.path.insert(0,'/tmp')
from te_lib import *
c=Card()
c.title("US employers add","165,000 jobs",mark="165,000")
c.subtitle("October 2026 jobs report vs the forecast and the usual pace")
base=1000; k=640/165.0; bw=300; gap=24
cols=[(0,48,"48,000","1. The usual pace","Average jobs added a month,","over the past 12 months"),
      (1,65,"about 65,000","2. What economists expected","Forecasts ranged from","59,000 to 70,000"),
      (2,165,"165,000","3. What actually happened","US employers added 165,000","jobs in October")]
GRID="#DADAD6"
with c.group("grid"):                    # Y axis: faint gridlines + small labels, drawn BEHIND the columns
    for v in (50,100,150):
        yy=base-v*k
        c.rect(0,yy-0.75,948,1.5,GRID)
        c.text(0,yy-8,f"{v}k",18,GREY,"m")
with c.group("body"):
    c.rect(0,base,948,3,INK)
    for i,v,val,l1,l2,l3 in cols:
        x=i*(bw+gap)
        if i<2:
            c.rect(x,base-v*k,bw,v*k,GREEN_L)   # context columns = light blue so the focal column 3 stands out
        else:
            c.rect(x,base-65*k,bw,65*k,GREEN_L)
            c.rect(x,base-165*k,bw,100*k,GREEN)
        c.text(x+bw/2,base-v*k-16,val,fit("b",val,38,bw),INK,"b","m")
        c.text(x,base+44,l1,fit("b",l1,24,bw),INK,"b")
        c.text(x,base+72,l2,fit("m",l2,20,bw),GREY,"m")
        c.text(x,base+96,l3,fit("m",l3,20,bw),GREY,"m")
with c.group("toplabels"):      # drawn ABOVE the pulse layer so the text stays crisp
    x=2*(bw+gap)
    c.text(x+bw/2,base-165*k+(100*k)/2-2,"+100,000",42,INK,"b","m")
    c.text(x+bw/2,base-165*k+(100*k)/2+34,"above the forecast",23,INK,"sb","m")
with c.group("note"):
    c.rect(0,1125,948,84,PALE,1,6)
    t="Unemployment 4.1% (from 4.2%)  ·  Pay +0.4% in the month  ·  Aug–Sep revised up 84,000"
    c.text(474,1175,t,fit("sb",t,22,900),INK,"sb","m")
c.arrows(2*(bw+gap),base-165*k,bw,100*k,(255,255,255),n=28,alpha=0.6,size=13,shape="chevron")   # small chevrons flow constantly UPWARD through the focal green block (replaces the flash)
c.footer("The US added about 100,000 more jobs than economists expected")
c.source("Source: US Bureau of Labor Statistics, 6 Nov 2026 · forecasts: Bloomberg, Dow Jones, Yahoo Finance")
c.save("/mnt/user-data/outputs/us-jobs-october-v9b.svg")
