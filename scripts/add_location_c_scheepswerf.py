from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
backup = Path('index_BACKUP_2026-08-22_1332.html')
if not backup.exists():
    backup.write_text(s, encoding='utf-8')

repls = []

# 1. CSS: add exact C position and dashed style for the smaller masonry bunker.
old = ".reticle.morsweg{left:31.75%;top:39.03%}.reticle.boommarkt{left:40.30%;top:41.91%}.reticle.boommarkt .r1,.reticle.boommarkt .r2{border-style:dashed}"
new = ".reticle.morsweg{left:31.75%;top:39.03%}.reticle.boommarkt{left:40.30%;top:41.91%}.reticle.scheepswerf{left:79.45%;top:38.84%}.reticle.boommarkt .r1,.reticle.boommarkt .r2,.reticle.scheepswerf .r1,.reticle.scheepswerf .r2{border-style:dashed}"
repls.append((old,new,'C marker CSS'))

# 2. Left-side location list: C becomes Scheepswerf Boot; Haarlemmerweg remains a question mark without a letter.
old = "<div class=\"locationrow\"><div class=\"locdot\">B</div><div><b>Boommarkt</b><p>Telefoonbunker.</p></div></div><div class=\"locationrow\" onclick=\"haarlemmerweg()\" style=\"cursor:pointer\"><div class=\"locdot\">C</div><div><b>Haarlemmerweg</b><p>Telefoonbunker · onderzoek.</p></div></div>"
new = "<div class=\"locationrow\"><div class=\"locdot\">B</div><div><b>Boommarkt</b><p>Telefoonbunker.</p></div></div><div class=\"locationrow\" onclick=\"scheepswerfBoot()\" style=\"cursor:pointer\"><div class=\"locdot\">C</div><div><b>Scheepswerf Boot</b><p>Kleine gemetselde bunker · 1945.</p></div></div><div class=\"locationrow\" onclick=\"haarlemmerweg()\" style=\"cursor:pointer\"><div class=\"locdot\">?</div><div><b>Haarlemmerweg</b><p>Telefoonbunker · onderzoek.</p></div></div>"
repls.append((old,new,'location list'))

# 3. Map marker, label and targetbar button.
old = "<button class=\"reticle small boommarkt\" onclick=\"boommarkt();event.stopPropagation()\"><span class=\"r1\"></span><span class=\"r2\"></span><i></i></button><button class=\"map-question\" title=\"Haarlemmerweg · mogelijke locatie\""
new = "<button class=\"reticle small boommarkt\" onclick=\"boommarkt();event.stopPropagation()\"><span class=\"r1\"></span><span class=\"r2\"></span><i></i></button><button class=\"reticle small scheepswerf\" onclick=\"scheepswerfBoot();event.stopPropagation()\"><span class=\"r1\"></span><span class=\"r2\"></span><i></i></button><button class=\"map-question\" title=\"Haarlemmerweg · mogelijke locatie\""
repls.append((old,new,'map C marker'))

old = "<div class=\"targetlabel mw\"><b>A · R616 MORSWEG</b>GROSSSCHALTSTELLE</div><div class=\"targetlabel bm\"><b>B · BOOMMARKT</b>TELEFOONBUNKER</div></div><div class=\"targetbar\"><button id=\"tbM\" class=\"active\" onclick=\"focusTarget('morsweg')\">R616</button><button id=\"tbB\" onclick=\"focusTarget('boommarkt')\">BOOMMARKT</button></div>"
new = "<div class=\"targetlabel mw\"><b>A · R616 MORSWEG</b>GROSSSCHALTSTELLE</div><div class=\"targetlabel bm\"><b>B · BOOMMARKT</b>TELEFOONBUNKER</div><div class=\"targetlabel sw\"><b>C · SCHEEPSWERF BOOT</b>KLEINE GEMETSELDE BUNKER</div></div><div class=\"targetbar\"><button id=\"tbM\" class=\"active\" onclick=\"focusTarget('morsweg')\">R616</button><button id=\"tbB\" onclick=\"focusTarget('boommarkt')\">BOOMMARKT</button><button id=\"tbC\" onclick=\"focusTarget('scheepswerf')\">C · WERF</button></div>"
repls.append((old,new,'C label and target button'))

# 4. Status panel.
old = "<div class=\"statusline\"><span>BOOMMARKT</span><span>ONDERZOEK</span></div><div class=\"statusline\"><span>HAARLEMMERWEG</span><span>ONDERZOEK</span></div>"
new = "<div class=\"statusline\"><span>BOOMMARKT</span><span>ONDERZOEK</span></div><div class=\"statusline\"><span>SCHEEPSWERF BOOT</span><b>1945 BRON</b></div><div class=\"statusline\"><span>HAARLEMMERWEG</span><span>ONDERZOEK</span></div>"
repls.append((old,new,'status panel'))

# 5. JS label handling.
old = "const labelMW=mapworld.querySelector('.targetlabel.mw'),labelBM=mapworld.querySelector('.targetlabel.bm');\n[labelMW,labelBM].forEach(el=>{mapframe.appendChild(el);el.style.textRendering='geometricPrecision';el.style.webkitFontSmoothing='antialiased'});"
new = "const labelMW=mapworld.querySelector('.targetlabel.mw'),labelBM=mapworld.querySelector('.targetlabel.bm'),labelSW=mapworld.querySelector('.targetlabel.sw');\n[labelMW,labelBM,labelSW].forEach(el=>{mapframe.appendChild(el);el.style.textRendering='geometricPrecision';el.style.webkitFontSmoothing='antialiased'});"
repls.append((old,new,'label JS init'))

old = "function positionLabels(){const w=mapworld.offsetWidth,h=mapworld.offsetHeight;if(!w||!h)return;[[labelMW,.334,.366],[labelBM,.415,.430]].forEach(([el,x,y])=>{el.style.left=Math.round(panX+x*w*mapScale)+'px';el.style.top=Math.round(panY+y*h*mapScale)+'px'})}"
new = "function positionLabels(){const w=mapworld.offsetWidth,h=mapworld.offsetHeight;if(!w||!h)return;[[labelMW,.334,.366],[labelBM,.415,.430],[labelSW,.810,.360]].forEach(([el,x,y])=>{el.style.left=Math.round(panX+x*w*mapScale)+'px';el.style.top=Math.round(panY+y*h*mapScale)+'px'})}"
repls.append((old,new,'C label position'))

old = "function focusTarget(t){let p=t==='morsweg'?[.3175,.3903]:[.4030,.4191],s=1.75,r=mapframe.getBoundingClientRect(),w=mapworld.offsetWidth,h=mapworld.offsetHeight;mapScale=s;panX=r.width/2-p[0]*w*s;panY=r.height/2-p[1]*h*s;applyMap();document.querySelectorAll('.targetbar button').forEach(b=>b.classList.remove('active'));(t==='morsweg'?tbM:tbB).classList.add('active')}"
new = "function focusTarget(t){const targets={morsweg:[.3175,.3903],boommarkt:[.4030,.4191],scheepswerf:[.7945,.3884]},buttons={morsweg:tbM,boommarkt:tbB,scheepswerf:tbC};let p=targets[t]||targets.morsweg,s=1.75,r=mapframe.getBoundingClientRect(),w=mapworld.offsetWidth,h=mapworld.offsetHeight;mapScale=s;panX=r.width/2-p[0]*w*s;panY=r.height/2-p[1]*h*s;applyMap();document.querySelectorAll('.targetbar button').forEach(b=>b.classList.remove('active'));(buttons[t]||tbM).classList.add('active')}"
repls.append((old,new,'focusTarget C'))

# 6. New dossier function, inserted directly before Haarlemmerweg dossier.
anchor = "function haarlemmerweg(){"
dossier = "function scheepswerfBoot(){modal(`<div class='k'>HISTORISCH DOSSIER · LOCATIE C · 25 JULI 1945</div><h2>C · SCHEEPSWERF BOOT</h2><div class='techdetail'><img src=\"oude%20plattegrond%20met%20verdedigingswerken%20op%20een%20kaart%20uit%201928%20bewerkt2.jpg\" alt=\"Gemeentelijke plattegrond Leiden met locatie C bij Scheepswerf Boot\"><div><p class='copy'>Bij de gemeentelijke inventarisatie van permanente defensieve werken van 25 juli 1945 werd locatie <b>C</b> omschreven als een <b>kleine gemetselde bunker op het terrein van Scheepswerf Boot langs de Zijl</b>. De rode C op de gemeentelijke plattegrond lokaliseert het object direct ten noordwesten van de Spanjaardsbrug, op het zuidelijke deel van het voormalige werfterrein.</p><div class='techfacts'><div>LETTER</div><div>C</div><div>TYPE</div><div>kleine gemetselde bunker</div><div>LOCATIE</div><div>Scheepswerf Boot langs de Zijl</div><div>BRON</div><div>Gemeentewerken Leiden · 25 juli 1945</div><div>STATUS</div><div>historisch gelokaliseerd</div></div><p class='warn'>Het latere BRV-overzicht noemt voor Leiden ook <b>Z22 · Scheepstimmerwerf · tekening 143</b>. De koppeling met deze bunker is zeer waarschijnlijk, maar wordt pas definitief zodra de tekening zelf is gecontroleerd.</p></div></div><h3>BRONKAART</h3><img src=\"oude%20plattegrond%20met%20verdedigingswerken%20op%20een%20kaart%20uit%201928%20bewerkt2.jpg\" alt=\"Plattegrond Leiden met A-E verdedigingswerken\" style=\"width:100%;max-height:66vh;object-fit:contain;background:#070907;border:1px solid var(--line);border-radius:8px;cursor:pointer\" onclick=\"photo('oude%20plattegrond%20met%20verdedigingswerken%20op%20een%20kaart%20uit%201928%20bewerkt2.jpg','Gemeentelijke kaart · locatie C Scheepswerf Boot')\">`,true)}\n"
if anchor not in s:
    raise SystemExit('Anchor for Scheepswerf dossier not found')
s = s.replace(anchor, dossier + anchor, 1)

# Apply exact replacements and fail loudly if the page no longer matches expected structure.
for old,new,name in repls:
    if old not in s:
        raise SystemExit(f'Anchor not found: {name}')
    s = s.replace(old,new,1)

p.write_text(s, encoding='utf-8')
print('Added location C Scheepswerf Boot; Haarlemmerweg remains unlettered question mark')
