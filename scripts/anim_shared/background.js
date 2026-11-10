// SHARED BACKGROUND for every Animated Shorts series (user rule, 10 Nov 2026: the background is EXACTLY the same
// across all animation series; only the title position may differ between series).
// Paper colour #F2EFE8 under two fixed texture layers (embossed paper tooth, multiply 55%; fine specks, 35%).
// Usage in a renderer:  const bg = require('../anim_shared/background.js'); const {tex1, tex2} = await bg.textures(page);
// then draw the page on PAPER and lay tex1 (mix-blend-mode:multiply; opacity:.55) and tex2 (opacity:.35) on top,
// full frame 1080x1920, above everything else. Never change these values per series.
const PAPER = '#F2EFE8';
async function textures(page) {
  await page.setContent(`<body style="margin:0"><svg id="a" width="1080" height="1920" style="display:block;background:#fff"><defs>
<filter id="paper" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="3" seed="4" result="n"/><feDiffuseLighting in="n" lighting-color="#fff" surfaceScale="1.4"><feDistantLight azimuth="235" elevation="58"/></feDiffuseLighting><feColorMatrix type="matrix" values="0 0 0 0 0.45  0 0 0 0 0.42  0 0 0 0 0.38  -1 0 0 0 1"/></filter>
<filter id="speck"><feTurbulence type="fractalNoise" baseFrequency="1.6" numOctaves="2" seed="9"/><feColorMatrix type="matrix" values="0 0 0 0 0.95 0 0 0 0 0.94 0 0 0 0 0.91 0 0 0 -2.2 1.25"/></filter></defs>
<rect width="1080" height="1920" filter="url(#paper)"/></svg><svg id="b" width="1080" height="1920" style="display:block"><rect width="1080" height="1920" filter="url(#speck)"/></svg></body>`);
  const tex1 = 'data:image/png;base64,' + (await (await page.$('#a')).screenshot()).toString('base64');
  const tex2 = 'data:image/png;base64,' + (await (await page.$('#b')).screenshot({omitBackground: true})).toString('base64');
  return {tex1, tex2, paper: PAPER};
}
module.exports = {textures, PAPER};
