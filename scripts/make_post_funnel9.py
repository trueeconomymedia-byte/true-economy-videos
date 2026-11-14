from te_lib import *
import json, numpy as np
d=json.load(open('/tmp/post.json'))
c=Card()
c.title("Inside the US","debt buildup",mark="buildup",accent="none")
c.subtitle("Four groups share the $40.6tn US debt · Nov 2026")
CX=474; MW=900; k=MW/d['tot']; PAPER="#FBF8F1"; BG=(251,248,241)
w0=d['tot']*k; w1=d['pub']*k; w2=(d['pub']-d['fed'])*k; w3=d['frn']*k
top=c.top+30; P=1.35; HF=650; w3_=w3
r1=(w1-w3)/(w0-w3); r2=(w2-w3)/(w0-w3)
u2=1-r1**(1/P); u3=1-r2**(1/P)
h1=round(u2*HF); h2=round(u3*HF)-h1; h3=HF-h1-h2; h4=132
y1=top; y2=y1+h1; y3=y2+h2; y4=y3+h3; y5=y4+h4
def Wd(y):
    u=min(max((y-y1)/(y4-y1),0.0),1.0)
    return w3+(w0-w3)*(1-u)**P
def band(ya,yb,col,sa=0,sb=0,m=40):
    ys=[ya+(yb-ya)*i/m for i in range(m+1)]
    L=[(CX-Wd(y)/2,y) for y in ys]; R=[(CX+Wd(y)/2,y) for y in ys]
    poly=L+R[::-1]
    c.path("M"+" L".join(f"{x:.1f},{y:.1f}" for x,y in poly)+" Z",fill=col,stroke=PAPER,sw=3)
SAG={y1:0,y2:0,y3:0,y4:0}; NECK=0
def wsamp(ya,yb,m=24): return [round(Wd(ya+(yb-ya)*i/m),2) for i in range(m+1)]
def tb(x,y,txt,size,fk="b"):   # text box (for keeping streaks off labels)
    w=width(fk,txt,size); return [x-w/2-8,y-size*0.95,w+16,size*1.25]
avoid={1:[],2:[],3:[],4:[]}
with c.group("body"):
    c.text(CX,top-12,"Total US debt: $40.6tn",24,INK,"b","m")
    band(y1,y2,solid(BLUE,0.6,BG),SAG[y1],SAG[y2]); band(y2,y3,solid(YEL,0.6,BG),SAG[y2],SAG[y3]); band(y3,y4,solid(GREEN,0.6,BG),SAG[y3],SAG[y4]); band(y4,y5,solid(RED,0.6,BG),SAG[y4],NECK)
    def lab(band_i,cy,val,vs,name,ns,sub=None,ss=0):
        c.text(CX,cy,val,vs,INK,"b","m"); avoid[band_i].append(tb(CX,cy,val,vs))
        c.text(CX,cy+ns+10,name,ns,INK,"b","m"); avoid[band_i].append(tb(CX,cy+ns+10,name,ns))
        if sub: c.text(CX,cy+ns+10+ss+8,sub,ss,INK,"sb","m"); avoid[band_i].append(tb(CX,cy+ns+10+ss+8,sub,ss,"sb"))
    lab(1,y1+53,"$7.8tn",50,"US government's own accounts · 19%",25,"mostly Social Security and other trust funds",19)
    # Fed: value and name on one row
    fv="$4.6tn"; fn="Federal Reserve · 11%"; fw=width("b",fv,46)+22+width("b",fn,25); fx=CX-fw/2; fy=y2+h2/2+17
    c.text(fx,fy,fv,46,INK,"b"); c.text(fx+width("b",fv,46)+22,fy,fn,25,INK,"b")
    avoid[2].append([fx-8,fy-46,fw+16,58])
    lab(3,y3+72,"$18.9tn",60,"Other US investors · 47%",25,"funds, banks, pensions, households",19)
    # foreign
    c.text(CX-w3/2-20,y4+62,"Foreign investors",26,INK,"b","r"); c.text(CX-w3/2-20,y4+94,"23% of all US debt",20,GREY,"sb","r")
    rx=CX+w3/2+22
    for i,(code,nm,v) in enumerate([("JP","Japan",d['japan']),("UK","UK",d['uk']),("CN","China",d['china'])]):
        ry=y4+18+i*44; bx=rx+104; sc=(942-bx-88)/d['japan']
        c.flag(rx+11,ry+17,11,code); c.text(rx+30,ry+24,nm,20,INK,"sb")
        c.rect(bx,ry+4,v*sc,28,RED); c.text(bx+v*sc+6,ry+27,f"${v/1000:.2f}tn",20,RED,"b")
with c.group("toplabels"):
    c.text(CX,y4+h4/2+15,"$9.3tn",44,INK,"b","m"); avoid[4].append(tb(CX,y4+h4/2+15,"$9.3tn",44))
gy=y5+22; gh=92
with c.group("kpi"):
    c.rect(0,gy,948,gh,YEL,1,4)
    c.text(24,gy+42,"Only 23% is owed to foreigners",36,INK,"b")
    c.text(24,gy+73,"China holds just 1.5%: $0.59tn of the $40.6tn",20,INK,"sb")
c.footer("Most US debt is owed to Americans, not China")
c.source("Source: US Treasury Fiscal Data (10 Nov 2026), Federal Reserve H.4.1 (11 Nov), Treasury TIC (Aug 2026) · other US holders = remainder")
specs=[(y1,y2,[54,112,208],1,SAG[y1],SAG[y2]),(y2,y3,[232,178,36],2,SAG[y2],SAG[y3]),(y3,y4,[36,153,114],3,SAG[y3],SAG[y4]),(y4,y5,[217,68,55],4,SAG[y4],NECK)]
ANIM={"vflow":[{"cx":CX,"ya":a,"yb":b,"wt":Wd(a),"wb":Wd(b),"ws":wsamp(a,b),"rgb":rgb,"avoid":avoid[i],"sa":sa_,"sb":sb_} for a,b,rgb,i,sa_,sb_ in specs]}
print("end",gy+gh)
c.save("/mnt/user-data/outputs/who-owns-us-debt-funnel9.svg",anim=ANIM)
