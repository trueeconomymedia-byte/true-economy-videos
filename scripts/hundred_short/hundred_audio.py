# True Economy "If it were 100" series sound (approved by the user 23 Nov 2026). Same instruments as the shared Animated Shorts sound (anim_shared/beats_audio.py), but its OWN feel so the series
# is not a copy of the others: key of D minor (the shared bed is A minor), 108 bpm (shared 96), a rolling piano arpeggio
# instead of the sparse motif, and two signature effects: a soft "stack" knock as each chunk lands on the left
# (beats 'stacks': [[t,g]]) and a smooth "pour" whoosh as each ribbon flows across (beats 'pours': [[t,d]]), plus low soft stacking thuds as each % counts up (beats 'counts': [[t0,t1]]).
# Usage: python3 hundred_audio.py beats.json out.wav
import numpy as np, wave, json, sys
BEATS=json.load(open(sys.argv[1])); OUT=sys.argv[2]
from scipy.signal import butter, sosfilt, fftconvolve
SR=44100; DUR=BEATS['total']; N=int(round(SR*DUR)); rng=np.random.default_rng(11)
def lp(x,f,o=2): return sosfilt(butter(o,f/(SR/2),output='sos'),x)
def hp(x,f,o=2): return sosfilt(butter(o,f/(SR/2),'high',output='sos'),x)
def bp(x,a,b,o=2): return sosfilt(butter(o,[a/(SR/2),b/(SR/2)],'band',output='sos'),x)
bus={'bed':np.zeros((N,2)),'fx':np.zeros((N,2))}
def add(name,sig,t,g=1.0,pan=0.0):
    if sig.ndim==1: sig=np.stack([sig*(1-max(pan,0)),sig*(1+min(pan,0))],1)
    i=int(t*SR); n=min(len(sig),N-i)
    if n>0 and i>=0: bus[name][i:i+n]+=sig[:n]*g
def adsr(n,a,r):
    e=np.ones(n); a=max(1,int(a*SR)); r=max(1,int(r*SR)); e[:a]=np.sin(np.linspace(0,np.pi/2,a))**2; e[-r:]*=np.cos(np.linspace(0,np.pi/2,r))**2; return e
# ---------- instruments ----------
def epiano(f,d=3.0,vel=1.0):
    n=int(d*SR); t=np.arange(n)/SR
    s=(np.sin(2*np.pi*f*t)+0.35*np.sin(2*np.pi*2*f*t)*np.exp(-t*3)+0.12*np.sin(2*np.pi*3*f*t)*np.exp(-t*6))
    s*=np.exp(-t*1.1)*(1-np.exp(-t*300))
    return lp(s,2500)*vel
def padnote(f,d):
    n=int(d*SR); t=np.arange(n)/SR; s=np.zeros(n)
    for det in (-0.12,0,0.12):  # gentle chorus, sine-ish saw
        ph=2*np.pi*f*(1+det/100)*t
        s+=np.sin(ph)+0.3*np.sin(2*ph)+0.12*np.sin(3*ph)
    return lp(s,900)*adsr(n,1.2,1.4)
def swell(d,f0=200,f1=2400,g=1.0):
    # airy rising noise: filter opens over time, ends right at the hit
    n=int(d*SR); x=rng.standard_normal(n); out=np.zeros(n); B=1024
    for i in range(0,n,B):
        p=(i/n)**1.6; fc=f0*(f1/f0)**p
        seg=bp(x[max(0,i-4*B):i+B],fc*0.6,min(fc*1.6,19000))[-min(B,n-i):]
        out[i:i+len(seg)]=seg
    e=(np.arange(n)/n)**2.2; e[-int(.03*SR):]*=np.linspace(1,0,int(.03*SR))
    return out*e*g
def glide(d):
    # soft air movement for camera moves
    n=int(d*SR); x=rng.standard_normal(n)
    a=bp(x,180,1200)*0.8+bp(x,1200,4000)*0.15
    return a*np.sin(np.pi*np.arange(n)/n)**2
def impact(g=1.0):
    # low cinematic "felt" hit: sub sine drop + muffled body, no click
    n=int(1.4*SR); t=np.arange(n)/SR
    f=62+28*np.exp(-t*14); sub=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*3.2)
    body=lp(rng.standard_normal(n),260)*np.exp(-t*16)*2.0
    s=(sub+body*0.6)*(1-np.exp(-t*900)); return s*g
def softclick(g=1.0):
    # muted paper/data tick (low, short, no pitch)
    n=int(0.05*SR); t=np.arange(n)/SR
    s=bp(rng.standard_normal(n),900,3200)*np.exp(-t*140); return s*g
def tickr(g=1.0):
    # crisp but warm counter tick: short woody click, slightly pitched, no beep
    n=int(0.06*SR); t=np.arange(n)/SR
    s=bp(rng.standard_normal(n),1400,5200)*np.exp(-t*170)+0.5*np.sin(2*np.pi*1650*t)*np.exp(-t*220)
    return s*g
def stinger(chord,d=4.0):
    n=int(d*SR); s=np.zeros(n)
    for j,f in enumerate(chord):
        e=epiano(f,d,0.9-0.12*j); s[int(j*0.012*SR):]+=e[:n-int(j*0.012*SR)]
    sh=np.zeros(n); tt=np.arange(n)/SR
    for f in chord[1:]: sh+=0.12*np.sin(2*np.pi*2*f*tt)*np.exp(-tt*0.9)*(1-np.exp(-tt*8))  # soft shimmer
    return s+lp(sh,4000)
# ---------- music bed: one of the rotating SOUND TEMPLATES (scripts/anim_shared/sound_templates.py) ----------
import os as _os; sys.path.insert(0,_os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),'anim_shared'))
import sound_templates as ST
TPL=ST.get(BEATS.get('sound'),'bright')
mf=ST.bed(TPL,add,padnote,epiano,softclick,DUR)   # mf transposes every pitched sound below into the template's key
# ---------- effects from the renderer's beats ----------
B=BEATS; hits=[]
if B.get('cold',0)>0: add('fx',glide(1.2),0.45,0.05)                # cold open: the grid rewinds into Day 1
if B.get('rewind'):                                                  # tape-rewind: noise swept high -> low, year ticks spinning back
    t0,d,k=B['rewind']; n=int(d*SR); x=rng.standard_normal(n); out=np.zeros(n); seg=int(0.03*SR)
    for j in range(0,n,seg):
        u=j/n; fc=3200*(1-u)+260*u; out[j:j+seg]=bp(x[j:j+seg] if j+seg<=n else x[j:],fc*0.6,fc*1.6)[:len(out[j:j+seg])]
    out*=np.sin(np.pi*np.arange(n)/n)**1.5; add('fx',out/np.abs(out).max(),t0,0.16)
    for j in range(k):
        u=(j+0.5)/k; add('fx',tickr(0.55),t0+d*(0.5-0.5*np.cos(np.pi*u)),0.12)
for j,tt in enumerate(B['ticks']): add('fx',tickr(0.75+0.25*(j%8==7)),tt,0.30)          # day 1: one tick per hour
for t0,t1,n,g in B['patter']:
    for j in range(n):
        u=rng.random()**0.8; add('fx',softclick(0.8),t0+(t1-t0)*u,g,rng.uniform(-.5,.5))
for t0,t1,k in B['rolls']:                                                           # counter rolling
    for j in range(k):
        u=(j+1)/(k+1); add('fx',tickr(0.6+0.3*u),t0+(t1-t0)*u,0.22)
for t0,d in B['glides']: add('fx',glide(d),t0,0.05)
for te,d in B['swells']: add('fx',swell(d,250,3000 if d<2 else 4200),te-d,0.08 if d<2 else 0.11)
for tt,g in B['lands']: add('fx',impact(g),tt,0.45+0.25*(g>=1)); hits.append(tt)
def knock(g=1.0,f0=110):
    # soft "stack": a short felt thud with a little woody body, no click
    n=int(0.5*SR); t=np.arange(n)/SR
    f=f0+0.55*f0*np.exp(-t*30); sub=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*11)
    body=bp(rng.standard_normal(n),300*f0/110,1100*f0/110)*np.exp(-t*45)*0.9
    return (sub+body)*(1-np.exp(-t*700))*g
def pour(d):
    # smooth flowing whoosh: band of air that opens as the ribbon travels and settles as it lands
    n=int(d*SR); x=rng.standard_normal(n); out=np.zeros(n); Bk=1024
    for i in range(0,n,Bk):
        u=i/n; fc=260*(2600/260)**(np.sin(np.pi*min(1,u*1.15))**1.3)
        seg=bp(x[max(0,i-4*Bk):i+Bk],fc*0.55,fc*1.7)[-min(Bk,n-i):]; out[i:i+len(seg)]=seg
    return out*np.sin(np.pi*np.arange(n)/n)**1.6
for tt,g in B.get('stacks',[]): add('fx',knock(g),tt,0.5)
for t0,d in B.get('pours',[]):
    add('fx',pour(d),t0,0.05)    # quieter than the count thuds (user 23 Nov 2026)
    for j in range(10): add('fx',softclick(0.6),t0+d*(0.15+0.75*rng.random()),0.05,rng.uniform(-.5,.5))
# count-up (user 23 Nov 2026: no high ring or chime): LOW soft stacking thuds as the % climbs on the right - four quiet
# low knocks that settle into one fuller, lower thud as the number lands
for t0,t1 in B.get('counts',[]):
    for j in range(4):
        u=j/4; add('fx',knock(0.55+0.1*j,78),t0+(t1-t0)*(1-(1-u)**1.5),0.46,0.3)
    add('fx',knock(1.0,62),t1-0.02,0.80,0.3)
for tt,m in B['notes']: add('fx',epiano(mf(m),2.5,0.6),tt,0.09)
add('fx',impact(0.45),B['hold'],0.35)
# THIS SERIES' OWN REVEAL (user 23 Nov 2026: different from the other series, and no high ring): a quick "flip" sweep for
# the rotating title, a deep double thud (the last block landing), then a warm LOW piano-and-pad chord that settles
R=B['reveal']; hits.append(R)
def flip(d=0.32):
    n=int(d*SR); x=rng.standard_normal(n); out=np.zeros(n); Bk=512
    for i in range(0,n,Bk):
        u=i/n; fc=500*(3200/500)**(1-abs(2*u-1))
        seg=bp(x[max(0,i-4*Bk):i+Bk],fc*0.6,fc*1.5)[-min(Bk,n-i):]; out[i:i+len(seg)]=seg
    return out*np.sin(np.pi*np.arange(n)/n)**2
add('fx',swell(0.9,200,1800),R-0.9,0.07); add('fx',flip(),R-0.05,0.10); add('fx',flip(),R+0.12,0.07)
add('fx',knock(1.0,70),R,0.9); add('fx',knock(1.2,48),R+0.16,1.0); add('fx',impact(0.8),R+0.16,0.5)
for j,m in enumerate((33,45,52,57,60)):                                     # low root-fifth-root-third shape in the template's key: warm, no shimmer
    add('fx',lp(epiano(mf(m),4.2,0.9-0.1*j),1800),R+0.16+j*0.02,0.26)
    if m>=45: add('fx',padnote(mf(m),3.6),R+0.16,0.06)
duck=np.ones(N)
for tt in hits:
    i=int(tt*SR); n=int(1.6*SR); d=1-0.45*np.exp(-np.arange(n)/SR*2.2)
    duck[i:i+n]=np.minimum(duck[i:i+n],d[:N-i])
mix=bus['bed']*duck[:,None]+bus['fx']
ir_n=int(2.2*SR); tt=np.arange(ir_n)/SR
ir=np.stack([rng.standard_normal(ir_n),rng.standard_normal(ir_n)],1)*np.exp(-tt*2.8)[:,None]
ir=np.stack([lp(ir[:,0],4500),lp(ir[:,1],4500)],1); ir/=np.abs(ir).sum(0)*0.02
wet=np.stack([fftconvolve(mix[:,c],ir[:,c])[:N] for c in range(2)],1)
out=mix*0.82+wet*0.18
out=hp(out.T,35).T
k=int(1.2*SR); out[-k:]*=np.linspace(1,0,k)[:,None]**1.5
out=np.tanh(out*1.3)/1.3; out/=np.abs(out).max(); out*=0.86
w=wave.open(OUT,'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((out*32767).astype('<i2').tobytes()); w.close(); print('ok')
