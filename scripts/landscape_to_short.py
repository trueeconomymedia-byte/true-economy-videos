#!/usr/bin/env python3
"""True Economy: landscape video -> 9:16 Short.
Usage: python3 landscape_to_short.py IN.mov OUT.mp4 "Title line 1" "Title line 2" "words to mark gold"
Layout: whole video full-width, centred vertically on the Shorts paper (no crop);
centred two-line Lora Bold title above it with the gold #FACB3A marker; no box, no bar.
Needs: ffmpeg, numpy, scipy, Pillow, Lora-Variable.ttf (set LORA below)."""
import sys, json, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.ndimage import gaussian_filter
LORA='/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf'
src,out,line1,line2,hl=sys.argv[1:6]
W,H=1080,1920
p=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','json',src]))['streams'][0]
sw,sh=p['width'],p['height']
if sw<=sh: sys.exit('Not landscape - skip')
vh=round(W*sh/sw); vh-=vh%2; vy=(H-vh)//2
# paper: warm greige +6%, embossed watercolour tooth lit from top-left
rng=np.random.default_rng(11)
h=gaussian_filter(rng.normal(0,1,(H,W)),1.1)+gaussian_filter(rng.normal(0,1,(H,W)),3.5)*2.2; h/=h.std()
gy,gx=np.gradient(h); s=-(gx*0.6+gy*0.8); s/=s.std()
paper=np.array([237,234,227])*1.06+s[...,None]*3.2+h[...,None]*0.8
bg=Image.fromarray(paper.clip(0,255).astype('uint8')).convert('RGBA')
m=Image.new('L',(W,H),0); ImageDraw.Draw(m).rectangle([0,vy+8,W,vy+vh+8],fill=70)
bg=Image.composite(Image.new('RGBA',(W,H),(50,40,30,255)),bg,m.filter(ImageFilter.GaussianBlur(16)))
f=ImageFont.truetype(LORA,76); f.set_variation_by_name('Bold')
d=ImageDraw.Draw(bg); lh=96
ty=vy-80-2*lh   # title block sits just above the video
for i,t in enumerate([line1,line2]):
    tw=d.textlength(t,font=f); tx=(W-tw)/2; y=ty+i*lh
    if hl and hl in t:
        hx=tx+d.textlength(t[:t.index(hl)],font=f); hw=d.textlength(hl,font=f)
        d.rectangle([hx-6,y+46,hx+hw+6,y+88],fill=(250,203,58,255))
    d.text((tx,y+2),t,font=f,fill=(17,17,17,255))
bgp=out+'.bg.png'; bg.convert('RGB').filter(ImageFilter.UnsharpMask(1.2,60,2)).save(bgp)
subprocess.check_call(['ffmpeg','-v','error','-y','-loop','1','-i',bgp,'-i',src,'-filter_complex',
 f'[1:v]scale={W}:{vh}:flags=lanczos,setsar=1[v];[0:v][v]overlay=0:{vy}:shortest=1,format=yuv420p[o]',
 '-map','[o]','-map','1:a?','-c:v','libx264','-preset','veryfast','-crf','17','-c:a','aac','-b:a','192k',
 '-shortest','-movflags','+faststart',out])
print('done',out)
