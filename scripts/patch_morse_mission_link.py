from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

old = '''<div class="card" onclick="playSound('radio-transmission-morse-code.mp3',null)"><h3>03 · Netwerk Leiden</h3><p>Onderzoek locaties en onderscheid feit van hypothese.</p><span class="badge">▶ MORSE</span></div>'''
new = '''<div class="card" onclick="location.href='morse.html'" style="cursor:pointer"><h3>03 · Morsepost</h3><p>Haal drie niveaus met de Baumeister T1 en zet een topscore neer.</p><span class="badge">START MORSEPOST →</span></div>'''

if old not in s:
    raise SystemExit('Morse mission source card not found; index.html not changed')

p.write_text(s.replace(old, new, 1), encoding='utf-8')
print('Morse mission linked to morse.html')
