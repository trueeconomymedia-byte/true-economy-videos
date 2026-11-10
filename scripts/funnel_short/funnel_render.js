// True Economy funnel Short renderer.
// node funnel_render.js <data.json> <outdir> <slug>
// Writes: <slug>-funnel-auto.mp4 (cold open: full chart first, for Buffer), <slug>-funnel-youtube.mp4 (starts on the hook),
//         <slug>-thumb-tease.png, <slug>-thumb-answer.png, <slug>-beats-auto.json, <slug>-beats-youtube.json (silent videos;
//         funnel_short.py adds the sound).
const {chromium}=require('playwright');const {spawn}=require('child_process');
const fs=require('fs'),path=require('path');
const [,,dataPath,outdir,slug]=process.argv;
const HERE=__dirname, ASSETS=path.join(HERE,'..','assets');
const D=JSON.parse(fs.readFileSync(dataPath,'utf8'));
const b64=(p,mime)=>`data:${mime};base64,`+fs.readFileSync(p).toString('base64');
(async()=>{
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
 // paper textures (same recipe as the approved test)
 await p.setContent(`<body style="margin:0"><svg id="a" width="1080" height="1920" style="display:block;background:#fff"><defs>
<filter id="paper" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="3" seed="4" result="n"/><feDiffuseLighting in="n" lighting-color="#fff" surfaceScale="1.4"><feDistantLight azimuth="235" elevation="58"/></feDiffuseLighting><feColorMatrix type="matrix" values="0 0 0 0 0.45  0 0 0 0 0.42  0 0 0 0 0.38  -1 0 0 0 1"/></filter>
<filter id="speck"><feTurbulence type="fractalNoise" baseFrequency="1.6" numOctaves="2" seed="9"/><feColorMatrix type="matrix" values="0 0 0 0 0.95 0 0 0 0 0.94 0 0 0 0 0.91 0 0 0 -2.2 1.25"/></filter></defs>
<rect width="1080" height="1920" filter="url(#paper)"/></svg><svg id="b" width="1080" height="1920" style="display:block"><rect width="1080" height="1920" filter="url(#speck)"/></svg></body>`);
 const tex1='data:image/png;base64,'+(await (await p.$('#a')).screenshot()).toString('base64');
 const tex2='data:image/png;base64,'+(await (await p.$('#b')).screenshot({omitBackground:true})).toString('base64');
 // optional logo: data.logo path, else scripts/assets/logos/<company-slug>.(png|svg)
 let logo=null;const cs=D.company.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
 for(const c of [D.logo,path.join(ASSETS,'logos',cs+'.png'),path.join(ASSETS,'logos',cs+'.svg')]){
  if(c&&fs.existsSync(c)){logo=b64(c,c.endsWith('.svg')?'image/svg+xml':'image/png');break}}
 const url='file://'+path.join(HERE,'funnel.html');
 for(const [variant,cold] of [['auto',1],['youtube',0]]){
  await p.goto(url);await p.waitForTimeout(300);
  // fonts must be loaded BEFORE building: the headline marker and the title fit are measured from the real glyphs
  await p.evaluate(async()=>{await document.fonts.load('700 86px Lora');await document.fonts.load('800 54px Inter');await document.fonts.load('600 28px Inter');await document.fonts.ready});
  await p.evaluate(d=>BUILD(d),{...D,tex1,tex2,logo,cold});await p.waitForTimeout(300);
  const beats=await p.evaluate(()=>BEATS);
  fs.writeFileSync(path.join(outdir,`${slug}-beats-${variant}.json`),JSON.stringify(beats));
  if(variant==='auto'){
   await p.evaluate(()=>tease());await p.screenshot({path:path.join(outdir,`${slug}-thumb-tease.png`)});
   await p.evaluate(()=>answer());await p.screenshot({path:path.join(outdir,`${slug}-thumb-answer.png`)});
  }
  const N=Math.round(beats.total*30), tmp=path.join(outdir,`${slug}-${variant}-silent.tmp.mp4`);
  const ff=spawn('ffmpeg',['-y','-v','error','-f','image2pipe','-framerate','30','-c:v','mjpeg','-i','-','-c:v','libx264','-crf','17','-preset','veryfast','-pix_fmt','yuv420p',tmp],{stdio:['pipe','inherit','inherit']});
  for(let f=0;f<N;f++){await p.evaluate(t=>setTime(t),f/30);const buf=await p.screenshot({type:'jpeg',quality:92});
   if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));}
  ff.stdin.end();const code=await new Promise(r=>ff.on('close',r));
  if(code!==0){console.error('ffmpeg failed',variant);process.exit(1)}
  fs.renameSync(tmp,path.join(outdir,`${slug}-${variant}-silent.mp4`));
  console.log('rendered',variant,beats.total.toFixed(2)+'s',logo?'with logo':'no logo');
 }
 await b.close();
})();
