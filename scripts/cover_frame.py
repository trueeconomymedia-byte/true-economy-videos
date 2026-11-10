#!/usr/bin/env python3
"""True Economy: put the best frame of the whole video on the first 0.2 s so it becomes the thumbnail/cover.
Usage: python3 cover_frame.py SRC TARGET OUT.mp4 [SLOT_Y SLOT_H] [--hold 0.2] [--at SECONDS]
  SRC    = original clip (frames are chosen from here)
  TARGET = the video that gets posted (the 9:16 Short, or the vertical clip itself)
  SLOT_Y SLOT_H = where the video sits inside TARGET (landscape Short: y=(1920-h)//2, h=round(1080*sh/sw) made even).
                  Omit for a vertical clip: the frame then covers the whole picture.
Nothing changes size or position: the chosen frame is laid over the first HOLD seconds, in the same slot,
so audio, sync, title and layout are untouched. Candidates are written next to OUT as OUT.cand1..5.jpg.
Needs ffmpeg, numpy, scipy, Pillow."""
import sys, json, subprocess, os, tempfile, numpy as np
from PIL import Image
from scipy.ndimage import laplace
a=[x for x in sys.argv[1:]]
def opt(n,d):
    if n in a:
        i=a.index(n); v=a[i+1]; del a[i:i+2]; return float(v)
    return d
hold=opt('--hold',0.2); at=opt('--at',None)
src,tgt,out=a[0],a[1],a[2]
def probe(f):
    p=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=width,height,duration,r_frame_rate','-select_streams','v:0','-of','json',f]))['streams'][0]
    fmt=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','json',f]))['format']
    n,d=p['r_frame_rate'].split('/'); return p['width'],p['height'],float(fmt['duration']),float(n)/float(d)
sw,sh,dur,_=probe(src); tw,th,_,fps=probe(tgt)
if len(a)>=5: sy,shh=int(a[3]),int(a[4])
else: sy,shh=0,th
tmp=tempfile.mkdtemp(); step=1.0
ts=[t for t in np.arange(0.5,max(dur-0.5,0.6),step)]
cands=[]
for t in ts:
    f=f'{tmp}/f{t:.2f}.png'
    subprocess.check_call(['ffmpeg','-v','error','-y','-ss',f'{t:.2f}','-i',src,'-frames:v','1','-vf','scale=640:-2',f])
    im=np.asarray(Image.open(f).convert('RGB')).astype(float); g=im.mean(2)
    sharp=laplace(g).var(); con=g.std(); m=g.mean()
    rg=im[...,0]-im[...,1]; yb=.5*(im[...,0]+im[...,1])-im[...,2]; col=np.hypot(rg.std(),yb.std())
    # edge density = busy/readable subject; penalise dark/blown-out frames and flat frames
    score=np.log1p(sharp)*1.0+con/40+col/40
    if m<35 or m>225: score-=3
    if con<20: score-=2
    cands.append((score,t))
cands.sort(reverse=True)
best=cands[0][1] if at is None else at
for i,(s,t) in enumerate(cands[:5],1):
    subprocess.check_call(['ffmpeg','-v','error','-y','-ss',f'{t:.2f}','-i',src,'-frames:v','1','-vf','scale=540:-2','-q:v','3',f'{out}.cand{i}.jpg'])
print('candidates',[(round(s,2),round(t,2)) for s,t in cands[:5]],'chosen',best)
cover=f'{tmp}/cover.png'
subprocess.check_call(['ffmpeg','-v','error','-y','-ss',f'{best:.2f}','-i',src,'-frames:v','1','-vf',f'scale={tw}:{shh}:flags=lanczos',cover])
subprocess.check_call(['ffmpeg','-v','error','-y','-i',tgt,'-i',cover,'-filter_complex',
 f"[0:v][1:v]overlay=0:{sy}:enable='lt(t,{hold})',format=yuv420p[o]",
 '-map','[o]','-map','0:a?','-c:v','libx264','-preset','veryfast','-crf','17','-c:a','copy','-movflags','+faststart',out])
print('done',out,'cover from',best,'s, held',hold,'s')
