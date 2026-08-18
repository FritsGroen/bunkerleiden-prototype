from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
old = "function boommarkt(){modal(`<div class='k'>ONDERZOEKSDOSSIER</div><h2>TELEFOONBUNKER BOOMMARKT</h2><img src=\"oude%20locatie%20bunker%20boommarkt.jpg\"><p class='copy'>Historische locatie aan de Boommarkt; verdere documentatie wordt toegevoegd naarmate het onderzoek vordert.</p>`) }"
# tolerate current no-space form
old2 = "function boommarkt(){modal(`<div class='k'>ONDERZOEKSDOSSIER</div><h2>TELEFOONBUNKER BOOMMARKT</h2><img src=\"oude%20locatie%20bunker%20boommarkt.jpg\"><p class='copy'>Historische locatie aan de Boommarkt; verdere documentatie wordt toegevoegd naarmate het onderzoek vordert.</p>`)}"
new = "function boommarkt(){photo('oude%20locatie%20bunker%20boommarkt.jpg','Boommarkt · historische locatie')}"
if new in s:
    print('already patched')
elif old2 in s:
    s = s.replace(old2, new, 1)
elif old in s:
    s = s.replace(old, new, 1)
else:
    raise SystemExit('boommarkt function not found')
p.write_text(s, encoding='utf-8')
