# True Economy funnel Short sound design (approved 10 Nov 2026: news-graphics style, quiet swooshes, louder ticker).
# Usage: python3 funnel_audio.py beats.json out.wav
# Documentary / news-graphics sound: calm piano-pad bed, airy swells, soft low impacts, no game-like blips.
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
# ---------- music bed: A minor-ish, 8 s per chord cycle quarter, loops at 30 s ----------
bpm=96; beat=60/bpm
chords=[[57,60,64,69],[53,57,60,65],[48,52,55,60],[55,59,62,67]]  # Am F C G (MIDI)
mf=lambda m:440*2**((m-69)/12)
bar=4*beat; t=0.0; ci=0
while t<DUR:
    ch=chords[ci%4]
    for m in ch: add('bed',padnote(mf(m-12),bar+1.4),t,0.05)
    add('bed',padnote(mf(ch[0]-24),bar+1.4)*0.9,t,0.07)
    # sparse felt-piano motif on beats 1 and 3 (quiet, documentary underscore)
    for b,m in [(0,ch[-1]+12),(2,ch[1]+12),(3,ch[2]+12)]:
        add('bed',epiano(mf(m),2.2,0.5),t+b*beat,0.06,(-0.25 if b%2 else 0.25))
    # muted pulse: soft low tick on 8ths, very quiet (news underscore feel)
    for e in range(8): add('bed',softclick(0.6 if e%2==0 else 0.35),t+e*beat/2,0.05)
    t+=bar; ci+=1
# ---------- effects synced to picture (from the renderer's beats json) ----------
S=[(s['a'],s['b'],s['kind']) for s in BEATS['steps']]; KT=BEATS['kt']; C0=BEATS['cold']; RB=BEATS['revbar']
if C0>0:
    add('fx',glide(1.2),0.45,0.05)                  # cold open: the chart rewinds into the funnel
add('fx',glide(3.6),C0+0.6,0.045)                  # opening pour + camera move
add('fx',swell(1.0,300,3000),RB-1.0,0.08)
add('fx',impact(0.55),RB,0.5)
for a,b,kind in S:
    add('fx',glide(b-a),a,0.03,0.2)
    add('fx',swell(1.1),b-0.15-1.1,0.09,0.15)
    add('fx',impact(1.0 if kind=='cost' else 0.6),b-0.15,0.62)
    ts=b+0.05+(1-(1-np.linspace(0,1,9))**2)*0.95
    for j_,tt in enumerate(ts): add('fx',tickr(0.8+0.2*(j_==8)),tt,0.34)
for t0 in BEATS['glides']: add('fx',glide(2.2),t0,0.05)
add('fx',swell(1.4,250,3500),KT-1.4,0.10); add('fx',impact(0.9),KT,0.75)
add('fx',stinger([mf(m) for m in (57,64,69,72,76)]),KT,0.22)
add('fx',glide(2.7),BEATS['pull0'],0.06)
add('fx',stinger([mf(m) for m in (53,60,65,69,72)],3.5),BEATS['pull1']-0.1,0.16)
# ---------- mix: duck bed under hits, gentle room reverb, master ----------
duck=np.ones(N)
for tt in [RB]+[b-0.15 for a,b,_ in S]+[KT,BEATS['pull1']-0.1]:
    i=int(tt*SR); n=int(1.6*SR); d=1-0.45*np.exp(-np.arange(n)/SR*2.2)
    duck[i:i+n]=np.minimum(duck[i:i+n],d[:N-i])
mix=bus['bed']*duck[:,None]+bus['fx']
ir_n=int(2.2*SR); tt=np.arange(ir_n)/SR
ir=np.stack([rng.standard_normal(ir_n),rng.standard_normal(ir_n)],1)*np.exp(-tt*2.8)[:,None]
ir=np.stack([lp(ir[:,0],4500),lp(ir[:,1],4500)],1); ir/=np.abs(ir).sum(0)*0.02
wet=np.stack([fftconvolve(mix[:,c],ir[:,c])[:N] for c in range(2)],1)
out=mix*0.82+wet*0.18
out=hp(out.T,35).T
# loop: crossfade tail into head so the restart is seamless
k=int(0.7*SR); fade=np.linspace(0,1,k)[:,None]
out[-k:]=out[-k:]*(1-fade)+out[:k]*fade*0.0+out[-k:]*0  if False else out[-k:]*(1-fade*0.6)
out=np.tanh(out*1.3)/1.3; out/=np.abs(out).max(); out*=0.86
w=wave.open(OUT,'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((out*32767).astype('<i2').tobytes()); w.close(); print('ok')
