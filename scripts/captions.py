#!/usr/bin/env python3
"""True Economy: burn spoken captions UNDER the video of a landscape->Short (user-approved style B, 11 Nov 2026).
Usage: python3 captions.py SHORT.mp4 CAPTIONS.json OUT.mp4 SLOT_Y SLOT_H
CAPTIONS.json = {"phrases":[{"text":"bonds can cushion the fall","mark":"the fall","start":66.2,"end":67.4}, ...]}
  text  : 2-5 spoken words, one line, <= 24 characters (longer text is shrunk to fit the safe width)
  mark  : the ONE key word/number/short phrase to highlight in gold (exact substring of text, same case) or "" for none
Style: Inter Bold 58 px, ink #111111, centred, gold #FACB3A marker on the lower half of the marked words (the title has
no marker any more: gold appears only in the captions). One line, top 48 px below the video, kept inside every
platform's safe zone (x 120-960, nothing below y 1440). Each phrase shows from its start until the next phrase starts
(gaps over 0.6 s go blank). Video re-encoded H.264 CRF 17, audio copied. Needs ffmpeg and Pillow."""
import sys, json, os, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont
here=os.path.dirname(os.path.abspath(__file__))
FONT=os.path.join(here,'assets','Inter-Bold.otf')
GOLD=(250,203,58,255); INK=(17,17,17,255)
W,H=1080,1920; SAFE_L,SAFE_R,SAFE_BOTTOM=120,960,1440
src,cj,out,sy,sh=sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4]),int(sys.argv[5])
ph=sorted(json.load(open(cj))['phrases'],key=lambda p:p['start'])
dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',src]))
top=sy+sh+48
tmp=tempfile.mkdtemp()
def card(text,mark,path):
    size=58
    while True:
        f=ImageFont.truetype(FONT,size); d0=ImageDraw.Draw(Image.new('RGBA',(1,1)))
        tw=d0.textlength(text,font=f)
        if tw<=SAFE_R-SAFE_L or size<=40: break
        size-=2
    im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    tx=(W-tw)/2; y=top
    if top+size*1.3>SAFE_BOTTOM: y=SAFE_BOTTOM-size*1.3
    if mark and mark in text:
        hx=tx+d.textlength(text[:text.index(mark)],font=f); hw=d.textlength(mark,font=f)
        d.rectangle([hx-8,y+int(size*0.55),hx+hw+8,y+int(size*1.12)],fill=GOLD)
    elif mark: print('WARNING mark not in text:',mark,'|',text)
    d.text((tx,y),text,font=f,fill=INK)
    im.save(path)
blank=os.path.join(tmp,'blank.png'); Image.new('RGBA',(W,H),(0,0,0,0)).save(blank)
lines=[]; t=0.0
for i,p in enumerate(ph):
    s=max(p['start'],t); nxt=ph[i+1]['start'] if i+1<len(ph) else dur
    e=nxt if nxt-p['end']<=0.6 else p['end']+0.25
    e=min(e,dur)
    if e<=s: continue
    if s>t+0.01: lines+= [f"file '{blank}'",f"duration {s-t:.3f}"]
    fp=os.path.join(tmp,f'p{i:03d}.png'); card(p['text'],p.get('mark',''),fp)
    lines+= [f"file '{fp}'",f"duration {e-s:.3f}"]; t=e
if t<dur: lines+= [f"file '{blank}'",f"duration {dur-t:.3f}"]
lines.append(f"file '{blank}'")
lst=os.path.join(tmp,'list.txt'); open(lst,'w').write('\n'.join(lines)+'\n')
subprocess.run(['ffmpeg','-v','error','-y','-i',src,'-f','concat','-safe','0','-i',lst,
  '-filter_complex','[1:v]fps=30,format=rgba[c];[0:v][c]overlay=0:0:eof_action=pass:shortest=0,format=yuv420p[v]',
  '-map','[v]','-map','0:a?','-c:v','libx264','-crf','17','-preset','medium','-c:a','copy','-movflags','+faststart',out],check=True)
print('done',out,len(ph),'phrases')
