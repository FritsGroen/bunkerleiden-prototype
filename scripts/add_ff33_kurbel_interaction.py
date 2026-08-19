from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='FF33-KURBEL-HOLD-PATCH-20260819'
if marker in s:
    print('already patched')
    raise SystemExit(0)

backup=Path('index_BACKUP_2026-08-19_1155.html')
if not backup.exists():
    backup.write_text(s,encoding='utf-8')

needle="""<h3>HISTORISCHE CONTEXT</h3>"""
kurbel="""<h3>KURBELGENERATOR · PROBEER ZELF</h3><div class='kurbel-demo' id='kurbelDemo' onpointerdown='startKurbel(event)' onpointerup='stopKurbel()' onpointercancel='stopKurbel()' onpointerleave='stopKurbel()'><img id='kurbelImg' src='ff33.png' alt='FF33 Kurbelgenerator interactief'><div class='kurbel-overlay'><b>↻ HOUD INGEDRUKT OM TE DRAAIEN</b><span>De Kurbelgenerator wekt de oproepspanning op. Zolang je vasthoudt, draait de Kurbel en hoor je de bel.</span></div></div><h3>HISTORISCHE CONTEXT</h3>"""
if needle not in s:
    raise SystemExit('FF33 context anchor not found')
s=s.replace(needle,kurbel,1)

css="""
<style id='FF33-KURBEL-HOLD-PATCH-20260819'>
.kurbel-demo{position:relative;max-width:720px;margin:10px auto 18px;border:1px solid var(--gold);border-radius:9px;overflow:hidden;background:#070907;cursor:grab;touch-action:none;user-select:none;-webkit-user-select:none}.kurbel-demo:active{cursor:grabbing}.kurbel-demo img{display:block;width:100%;height:min(46vh,420px);object-fit:contain;background:#070907;pointer-events:none}.kurbel-overlay{position:absolute;left:10px;right:10px;bottom:10px;padding:10px 12px;background:#050705e8;border-left:3px solid var(--a);font:10px/1.45 monospace;color:#c8bea6;pointer-events:none}.kurbel-overlay b{display:block;color:var(--a2);font-size:11px;margin-bottom:4px}.kurbel-demo.running{box-shadow:0 0 28px #e4b71938}.kurbel-demo.running .kurbel-overlay b{color:#fff08a}.kurbel-demo.running .kurbel-overlay b:before{content:'● ';color:#73c66a}@media(max-width:700px){.kurbel-demo img{height:38vh;min-height:250px}.kurbel-overlay{font-size:9px}.kurbel-overlay b{font-size:10px}}
</style>
"""
s=s.replace('</head>',css+'\n</head>',1)

js="""
<script id='ff33-kurbel-hold-js'>
let kurbelRing=null;
function startKurbel(e){
  const box=document.getElementById('kurbelDemo'),img=document.getElementById('kurbelImg');
  if(!box||!img)return;
  if(e&&box.setPointerCapture){try{box.setPointerCapture(e.pointerId)}catch(_){}}
  box.classList.add('running');
  img.src='kurbel_kast_vloeiende%20beweging.gif?run='+Date.now();
  if(kurbelRing){try{kurbelRing.pause()}catch(_){}}
  kurbelRing=new Audio('telephone-ring-old-german-w48-.mp3');
  kurbelRing.loop=true;kurbelRing.volume=.72;
  kurbelRing.play().catch(()=>{});
}
function stopKurbel(){
  const box=document.getElementById('kurbelDemo'),img=document.getElementById('kurbelImg');
  if(box)box.classList.remove('running');
  if(img)img.src='ff33.png';
  if(kurbelRing){try{kurbelRing.pause();kurbelRing.currentTime=0}catch(_){ }kurbelRing=null}
}
document.addEventListener('visibilitychange',()=>{if(document.hidden)stopKurbel()});
window.addEventListener('blur',stopKurbel);
</script>
<!-- FF33-KURBEL-HOLD-PATCH-20260819 -->
"""
s=s.replace('</body>',js+'\n</body>',1)
p.write_text(s,encoding='utf-8')
print('FF33 Kurbel interaction added')
