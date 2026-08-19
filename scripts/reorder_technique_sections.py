from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='TECHNIQUE-PRIORITY-REORDER-20260819'
if marker in s:
    print('already patched')
    raise SystemExit(0)

kev='''<article class="techpanel" onclick="kev()"><img src="KEV%20kast%20gietrijzer%203%20aanslutingen.png"><div class="inner"><div class="k">KABELINVOER & VERDELING</div><h3>KEV · Kabelendverschluss</h3><p>Waterdichte eindsluiting én verdeler voor ondergrondse papier-lood telefoonkabels.</p><span class="badge">OPEN DOSSIER</span></div></article>'''
hes='''<article class="techpanel" onclick="hes()"><img src="doorsnede%20technische%20tekening%20HES%201.2.png"><div class="inner"><div class="k">LUFTSCHUTZ</div><h3>HES 1.2 · ventilatie / overdruk</h3><p>Luchtbehandeling en overdruk, gekoppeld aan de huidige schakelruimte.</p><span class="badge">OPEN DOSSIER</span></div></article>'''

if kev not in s or hes not in s:
    raise SystemExit('KEV/HES tiles not found')
s=s.replace(kev,'',1).replace(hes,'',1)

intro='<p class="copy">Technische dossiers van de systemen en functies die de R616 als communicatiebunker lieten functioneren.</p><div class="techgrid">'
intro_new='<p class="copy">Technische dossiers van de systemen en functies die de R616 als communicatiebunker lieten functioneren.</p><h3 style="margin-top:22px">TELEFONIE & MEETTECHNIEK</h3><div class="techgrid">'
if intro not in s:
    raise SystemExit('Technique intro anchor not found')
s=s.replace(intro,intro_new,1)

anchor='<h3 style="margin-top:28px">OVERIGE INSTALLATIES & FUNCTIES</h3><div class="cards">'
other='<h3 style="margin-top:28px">OVERIGE INSTALLATIES & FUNCTIES</h3><div class="techgrid" id="other-techgrid">'+kev+hes+'</div><div class="cards">'
if anchor not in s:
    raise SystemExit('Other installations anchor not found')
s=s.replace(anchor,other,1)

# WT80K is created later by the existing dynamic LMP2/WT80K code. Move it as soon as it appears.
move_script=r'''
<script id="TECHNIQUE-PRIORITY-REORDER-20260819">
(function(){
  function moveWT80K(){
    const target=document.getElementById('other-techgrid');
    const wt=document.getElementById('tech-wt80k-extra');
    if(target && wt && wt.parentElement!==target) target.appendChild(wt);
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',moveWT80K); else moveWT80K();
  new MutationObserver(moveWT80K).observe(document.body,{childList:true,subtree:true});
})();
</script>
'''
s=s.replace('</body>',move_script+'\n</body>',1)
p.write_text(s,encoding='utf-8')
print('Technique sections reordered')
