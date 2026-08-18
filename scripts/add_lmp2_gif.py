from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = 'LMP2_ohmmeter animated.gif'
if marker in s:
    print('LMP2 GIF already present')
    raise SystemExit(0)

needle = "<p><b>Siemens & Halske / Siemens-Schuckert</b></p><p>De LMP2 is een draagbaar meetinstrument voor het controleren van elektrische leidingen en weerstanden. Binnen de bunkercontext hoort het bij het onderhoud en de controle van telefoon- en verbindingsleidingen.</p>"
insert = "<p><b>Siemens & Halske / Siemens-Schuckert</b></p><p>De LMP2 is een draagbaar meetinstrument voor het controleren van elektrische leidingen en weerstanden. Binnen de bunkercontext hoort het bij het onderhoud en de controle van telefoon- en verbindingsleidingen.</p><h3>WERKING · ANIMATIE</h3><img src=\"LMP2_ohmmeter%20animated.gif\" alt=\"Animatie van de LMP2 ohmmeter\" style=\"width:100%;max-height:58vh;object-fit:contain;background:#070907;border:1px solid rgba(255,255,255,.1);border-radius:8px;margin:10px 0\">"

if needle not in s:
    raise SystemExit('Expected LMP2 dossier text not found; index.html left unchanged')

s = s.replace(needle, insert, 1)
p.write_text(s, encoding='utf-8')
print('Added LMP2 animated GIF to dossier')
