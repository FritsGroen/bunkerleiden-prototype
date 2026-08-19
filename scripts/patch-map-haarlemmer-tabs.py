from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='MAP-HAARLEMMER-TABS-20260819'
if marker in s:
    print('already patched')
    raise SystemExit(0)

# Add breathing question-mark marker CSS + mobile nav centering polish.
css=r'''
<style id="MAP-HAARLEMMER-TABS-20260819">
.map-question{position:absolute;z-index:13;left:42.6%;top:10.7%;width:44px;height:44px;transform:translate(-50%,-50%) scale(var(--inv,1));transform-origin:center;background:none;border:0;padding:0;cursor:pointer;color:var(--a2)}
.map-question span{display:grid;place-items:center;width:100%;height:100%;border:2px dashed var(--a);border-radius:50%;background:#090c09dc;color:var(--a2);font:800 25px monospace;box-shadow:0 0 0 0 rgba(255,216,75,.45);animation:qbreath 2.2s ease-in-out infinite}
.map-question:hover span{border-style:solid;filter:brightness(1.2)}
@keyframes qbreath{0%,100%{transform:scale(.90);opacity:.58;box-shadow:0 0 0 0 rgba(255,216,75,.30)}50%{transform:scale(1.12);opacity:1;box-shadow:0 0 22px 7px rgba(255,216,75,.22)}}
@media(max-width:850px){header nav{scroll-behavior:smooth}.map-question{width:36px;height:36px}.map-question span{font-size:20px}}
</style>
'''
s=s.replace('</head>',css+'\n</head>',1)

# Add marker to historical map, just after Boommarkt reticle.
needle='<button class="reticle small boommarkt" onclick="boommarkt();event.stopPropagation()"><span class="r1"></span><span class="r2"></span><i></i></button>'
insert=needle+'<button class="map-question" title="Haarlemmerweg · mogelijke locatie" aria-label="Haarlemmerweg · mogelijke locatie" onclick="haarlemmerweg();event.stopPropagation()"><span>?</span></button>'
if needle not in s:
    raise SystemExit('Boommarkt reticle anchor not found')
s=s.replace(needle,insert,1)

# Make centered reset/focus use enough zoom to avoid blank bars on any viewport.
old="function centerR616(scale=1){let r=mapframe.getBoundingClientRect(),w=mapworld.offsetWidth,h=mapworld.offsetHeight;if(!w||!h)return;mapScale=Math.max(1,Math.min(5,scale));panX=r.width/2-.3175*w*mapScale;panY=r.height/2-.3903*h*mapScale;applyMap();document.querySelectorAll('.targetbar button').forEach(b=>b.classList.remove('active'));tbM.classList.add('active')}"
new="function centerR616(scale=1){let r=mapframe.getBoundingClientRect(),w=mapworld.offsetWidth,h=mapworld.offsetHeight;if(!w||!h)return;const x=.3175,y=.3903;const fill=Math.max(1,(r.width/2)/(x*w),(r.width/2)/((1-x)*w),(r.height/2)/(y*h),(r.height/2)/((1-y)*h));mapScale=Math.max(fill,Math.min(5,scale));panX=r.width/2-x*w*mapScale;panY=r.height/2-y*h*mapScale;applyMap();document.querySelectorAll('.targetbar button').forEach(b=>b.classList.remove('active'));tbM.classList.add('active')}"
if old not in s:
    raise SystemExit('centerR616 function not found')
s=s.replace(old,new,1)

# Center the active top navigation tab on mobile after every tab change.
oldgo="function go(id){document.querySelectorAll('.screen').forEach(x=>x.classList.remove('active'));document.getElementById(id).classList.add('active');document.querySelectorAll('[data-s]').forEach(x=>x.classList.toggle('active',x.dataset.s===id));document.body.classList.toggle('home-view',id==='home');scrollTo(0,0);if(id==='home')requestAnimationFrame(()=>centerR616(1));if(id==='three')requestAnimationFrame(init3D)}"
newgo="function go(id){document.querySelectorAll('.screen').forEach(x=>x.classList.remove('active'));document.getElementById(id).classList.add('active');document.querySelectorAll('[data-s]').forEach(x=>x.classList.toggle('active',x.dataset.s===id));document.body.classList.toggle('home-view',id==='home');scrollTo(0,0);if(window.innerWidth<=850){const topTab=document.querySelector('header nav [data-s=\\\"'+id+'\\\"]');if(topTab)requestAnimationFrame(()=>topTab.scrollIntoView({behavior:'smooth',block:'nearest',inline:'center'}))}if(id==='home')requestAnimationFrame(()=>centerR616(1));if(id==='three')requestAnimationFrame(init3D)}"
if oldgo not in s:
    raise SystemExit('go() function not found')
s=s.replace(oldgo,newgo,1)

p.write_text(s,encoding='utf-8')
print('patched')
