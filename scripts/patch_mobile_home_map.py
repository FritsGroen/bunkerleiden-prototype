from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = 'MOBILE-HOME-MAP-FIRST-20260819'
if marker in s:
    print('already patched')
    raise SystemExit(0)

style = r'''
<style id="MOBILE-HOME-MAP-FIRST-20260819">
@media(max-width:850px){
  #home .home-shell{display:flex;flex-direction:column;padding:0 0 90px!important}
  #home .home-control{display:contents!important}
  #home .home-mapcol{order:1;padding:10px 10px 0;min-width:0}
  #home .home-head{order:2;display:block;padding:18px 18px 8px!important}
  #home .home-left{order:3;padding:10px 12px!important;display:grid;grid-template-columns:1fr;gap:10px}
  #home .home-right{order:4;padding:0 12px 16px!important;display:grid;grid-template-columns:1fr;gap:10px}
  #home .home-mapcol .mapframe{height:52vh!important;min-height:360px!important;max-height:520px!important;border-radius:10px}
  #home .home-head h1{font-size:clamp(31px,10vw,46px);line-height:1.03;margin:7px 0 12px}
  #home .home-head p{font-size:12px;line-height:1.55;margin:0;max-width:none}
  #home .targetbar{top:9px;right:9px;left:auto;bottom:auto}
  #home .zoom{left:9px;bottom:9px}
}
@media(max-width:430px){
  #home .home-mapcol .mapframe{height:48vh!important;min-height:330px!important}
}
</style>
'''

script = r'''
<script id="mobile-home-map-center-20260819">
(function(){
  function mobileCenterHomeMap(){
    if(!window.matchMedia('(max-width:850px)').matches) return;
    const frame=document.getElementById('mapframe'), world=document.getElementById('mapworld');
    if(!frame||!world||typeof centerR616!=='function') return;
    const h=world.offsetHeight||1;
    const fill=Math.max(1.05,Math.min(1.55,(frame.clientHeight/h)*1.03));
    centerR616(fill);
  }
  window.addEventListener('load',()=>setTimeout(mobileCenterHomeMap,80));
  window.addEventListener('resize',()=>requestAnimationFrame(mobileCenterHomeMap));
  document.addEventListener('click',e=>{
    const b=e.target.closest('button');
    if(b && (b.dataset.s==='home' || /HOME/i.test(b.textContent||''))) setTimeout(mobileCenterHomeMap,60);
  });
  const img=document.querySelector('#mapworld .mapimg');
  if(img) img.addEventListener('load',()=>setTimeout(mobileCenterHomeMap,30));
})();
</script>
'''

if '</head>' not in s or '</body>' not in s:
    raise SystemExit('expected HTML markers missing')
s = s.replace('</head>', style + '\n</head>', 1)
s = s.replace('</body>', script + '\n</body>', 1)
p.write_text(s, encoding='utf-8')
print('patched mobile home map-first layout')
