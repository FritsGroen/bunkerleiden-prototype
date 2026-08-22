from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
backup = Path('index_BACKUP_2026-08-22_1338.html')
if not backup.exists():
    backup.write_text(s, encoding='utf-8')

old = '<div class="card" onclick="boommarkt()"><h3>Telefoonbunker Boommarkt</h3><p>Historische opmeting nabij de voormalige PTT-centrale.</p><span class="badge">ONDERZOEK</span></div><div class="card" onclick="haarlemmerweg()"><h3>Telefoonbunker Haarlemmerweg</h3>'
new = '<div class="card" onclick="boommarkt()"><h3>Telefoonbunker Boommarkt</h3><p>Historische opmeting nabij de voormalige PTT-centrale.</p><span class="badge">ONDERZOEK</span></div><div class="card" onclick="scheepswerfBoot()"><h3>C · Bunker Scheepswerf Boot</h3><p>Kleine gemetselde bunker aan de Zijl, gelokaliseerd op de gemeentelijke inventarisatiekaart van 25 juli 1945.</p><span class="badge">OPEN DOSSIER</span></div><div class="card" onclick="haarlemmerweg()"><h3>Telefoonbunker Haarlemmerweg</h3>'

if old not in s:
    if 'C · Bunker Scheepswerf Boot' in s:
        print('C dossier card already present')
        raise SystemExit(0)
    raise SystemExit('Dossiers anchor not found')

s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')
print('Added C Scheepswerf Boot card to DOSSIERS')
