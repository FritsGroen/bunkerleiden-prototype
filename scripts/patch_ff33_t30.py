from pathlib import Path
from datetime import datetime

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='FF33-T30-PATCH-20260819'
if marker in s:
    print('Patch already present')
    raise SystemExit(0)

# Backup current live index before touching it.
backup=Path('index_BACKUP_2026-08-19_1104.html')
if not backup.exists():
    backup.write_text(s,encoding='utf-8')

# Add T30 tile immediately after the existing FF33 tile.
old="""<article class=\"techpanel\" onclick=\"ff33()\"><img src=\"ff33.png\"><div class=\"inner\"><div class=\"k\">FERNSPRECHDIENST</div><h3>FF33 · Feldfernsprecher 33</h3><p>Robuuste OB-veldtelefoon uit 1933: lokale batterij, Kurbelgenerator, La/Lb-E en verbinding over één of twee aders.</p><span class=\"badge\">OPEN DOSSIER</span></div></article>"""
new=old+"""<article class=\"techpanel\" onclick=\"t30()\"><img src=\"T30%20cell%20element.jpg\"><div class=\"inner\"><div class=\"k\">ORTSBATTERIE · VOEDING</div><h3>T30 · Element / batterij</h3><p>1,5 V element voor de lokale voeding van de FF33.</p><span class=\"badge\">OPEN DOSSIER</span></div></article>"""
if old not in s:
    raise SystemExit('FF33 techniektegel niet gevonden')
s=s.replace(old,new,1)

# Enrich existing FF33 modal with historical context photos.
needle="""<h3>Één ader of twee?</h3>"""
insert="""<h3>HISTORISCHE CONTEXT</h3><div class='thumbrow'><img onclick=\"photo('ff33%20control%20room.jpg','FF33 · control room')\" src=\"ff33%20control%20room.jpg\" alt=\"FF33 in control room\"><img onclick=\"photo('ff33%20in%20de%20loopgraven.jpg','FF33 · gebruik in de loopgraven')\" src=\"ff33%20in%20de%20loopgraven.jpg\" alt=\"FF33 in de loopgraven\"><img onclick=\"photo('ff33%20soldaat.jpg','FF33 · soldaat met veldtelefoon')\" src=\"ff33%20soldaat.jpg\" alt=\"Soldaat met FF33\"></div><h3>Één ader of twee?</h3>"""
if needle not in s:
    raise SystemExit('FF33 dossier invoegpunt niet gevonden')
s=s.replace(needle,insert,1)

# Add T30 dossier function before festungs38.
needle2='function festungs38(){'
t30fun="""function t30(){modal(`<div class='k'>TECHNISCH DOSSIER · ORTSBATTERIE</div><h2>T30 · ELEMENT / BATTERIJ</h2><div class='techdetail'><img src=\"T30%20cell%20element.jpg\" alt=\"T30 element batterij\"><div><p class='copy'>De T30 is het 1,5 V element dat als lokale batterij in de FF33 wordt gebruikt. De FF33 heeft deze batterij nodig voor de spreekkring; de oproep zelf gebeurt met de Kurbelgenerator.</p><div class='techfacts'><div>TOEPASSING</div><div>lokale voeding van de FF33</div><div>SPANNING</div><div>1,5 V</div><div>PLAATSING</div><div>in het batterijvak van de FF33</div></div><p class='warn'>Deze beschrijving is beperkt tot wat door de aanwezige foto’s en het bestaande FF33-dossier wordt ondersteund.</p></div></div><h3>IN DE FF33</h3><img src=\"T30%20cell%20zichtbaart%20in%20de%20ff33.webp\" alt=\"T30 element zichtbaar in de FF33\" style=\"width:100%;max-height:56vh;object-fit:contain;background:#070907;border:1px solid var(--line);border-radius:8px\">`,true)}\n"""
if needle2 not in s:
    raise SystemExit('Function insertion point not found')
s=s.replace(needle2,t30fun+needle2,1)

# Marker for idempotency.
s=s.replace('</body>',f'<!-- {marker} -->\n</body>',1)
p.write_text(s,encoding='utf-8')
print('FF33/T30 patch applied; backup created')
