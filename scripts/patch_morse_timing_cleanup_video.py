from pathlib import Path
import re

ROOT = Path('.')
MORSE = ROOT / 'morse.html'
INDEX = ROOT / 'index.html'

morse = MORSE.read_text(encoding='utf-8')
index = INDEX.read_text(encoding='utf-8')

# Backups before this patch.
mb = ROOT / 'morse_BACKUP_2026-08-23_1103.html'
ib = ROOT / 'index_BACKUP_2026-08-23_1103.html'
if not mb.exists():
    mb.write_text(morse, encoding='utf-8')
if not ib.exists():
    ib.write_text(index, encoding='utf-8')

# Museum-facing copy: remove implementation/prototype wording.
morse = morse.replace(
    'De bestaande Morse-trainer, nu speelbaar met de Baumuster T1 op het scherm. Houd de muisknop kort ingedrukt voor een punt en langer voor een streep. De toon is 800 Hz; de punt/streepgrens is 250 ms.',
    'Test je morsvaardigheid in drie stappen: luisteren, herkennen en zelf seinen. Voltooi elk niveau binnen de doeltijd om het volgende vrij te spelen.'
)
morse = morse.replace(
    'De toets geeft tijdens het indrukken direct een 800 Hz-zijtoon. De afbeelding wisselt tussen de statische en geanimeerde Baumuster T1 uit deze website.',
    'Sein met de muis op de Baumuster T1. Kort indrukken geeft een punt, langer indrukken een streep. Na 700 ms stilte wordt de letter beoordeeld.'
)

# Level 1: minimum 3 characters and a fixed, sharper time schedule.
morse = morse.replace(
    '<input id="l1word" class="word" maxlength="12" value="FRITS" aria-label="Woord">',
    '<input id="l1word" class="word" minlength="3" maxlength="12" value="FRITS" aria-label="Woord">'
)
morse = morse.replace(
    '<input id="l1threshold" class="number" type="number" min="5" max="600" value="60">',
    '<input id="l1threshold" class="number" type="number" value="35" readonly aria-label="Automatische doeltijd">'
)
morse = morse.replace(
    'function suggestedThreshold(w){return Math.max(45,Math.max((w||\'\').length,5)*12)}',
    "function suggestedThreshold(w){const n=Math.max(3,(w||'').length);if(n<=3)return 25;if(n===4)return 30;if(n===5)return 35;if(n===6)return 40;return 40+(n-6)*5}"
)

# Start Level 1 always uses the automatic threshold and rejects <3 characters.
pattern = re.compile(r"function startL1\(\)\{.*?\n\}\nfunction randomL1\(\)", re.S)
replacement = """function startL1(){
  initAudio();stopInput();
  const typed=cleanWord($('l1word').value,12);
  if(typed.length<3){
    setMsg('l1msg','Vul minimaal 3 letters in om Level 1 te starten.','bad');
    return;
  }
  if(!isCleanL1Word(typed)){
    $('l1word').value='';
    $('l1threshold').value=suggestedThreshold('FRITS');
    setMsg('l1msg','Dat woord gebruiken we niet in de museumopdracht. Kies een ander, net woord.','bad');
    return;
  }
  const word=typed;
  const target=suggestedThreshold(word);
  $('l1word').value=word;
  $('l1threshold').value=target;
  l1={active:true,word,index:0,attempts:0,mistakes:0,start:performance.now(),threshold:target};
  renderL1();setMsg('l1msg','Luister naar letter 1 en sein hem daarna terug.');setTimeout(()=>beginL1Letter(),300)
}
function randomL1()"""
morse, count = pattern.subn(replacement, morse, count=1)
if count != 1:
    raise SystemExit('Could not patch startL1')

morse = morse.replace('const passed=l1.word.length>=5&&ms<=l1.threshold*1000;', 'const passed=l1.word.length>=3&&ms<=l1.threshold*1000;')
morse = morse.replace('Voor Level 2: minimaal 5 letters binnen ', 'Voor Level 2: minimaal 3 letters binnen ')
morse = morse.replace("threshold:60", "threshold:35")

# Keep automatic time display in sync while typing; no manual time editing.
# Existing input listener already calls suggestedThreshold(v).

# Missions page: correct Baumuster and add new hover-play video under Morsepost.
old_card = '''<div class="card" onclick="location.href='morse.html'" style="cursor:pointer"><h3>03 · Morsepost</h3><p>Haal drie niveaus met de Baumeister T1 en zet een topscore neer.</p><span class="badge">START MORSEPOST →</span></div>'''
new_card = '''<div class="card" onclick="location.href='morse.html'" style="cursor:pointer" onmouseenter="var v=this.querySelector('video');if(v)v.play().catch(function(){})" onmouseleave="var v=this.querySelector('video');if(v){v.pause();v.currentTime=0}"><h3>03 · Morsepost</h3><p>Haal drie niveaus met de Baumuster T1 en zet een topscore neer.</p><video src="bunker%20morse%20video.mp4" muted playsinline preload="metadata" style="display:block;width:100%;aspect-ratio:16/9;object-fit:cover;margin:12px 0;border:1px solid rgba(228,183,25,.35);border-radius:6px;background:#050705"></video><span class="badge">START MORSEPOST →</span></div>'''
if old_card in index:
    index = index.replace(old_card, new_card)
elif 'bunker%20morse%20video.mp4' not in index:
    raise SystemExit('Could not find Morse mission card')

MORSE.write_text(morse, encoding='utf-8')
INDEX.write_text(index, encoding='utf-8')
print('patched morse.html and index.html')
