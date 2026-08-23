from pathlib import Path
import re

p = Path('morse.html')
text = p.read_text(encoding='utf-8')
backup = Path('morse_BACKUP_2026-08-23_1034.html')
if not backup.exists():
    backup.write_text(text, encoding='utf-8')

repls = [
    (
        '<p>Hoor een klinker, kies de juiste morsecode en sein hem daarna zelf terug.</p>',
        '<p>Luister naar een morsecode, kies het juiste patroon en sein die code daarna zelf terug.</p>'
    ),
    (
        '<p class="copy">Luister naar de uitgesproken klinker, kies de juiste morsecode en sein die code daarna correct terug.</p>',
        '<p class="copy">Luister naar de morsecode van een klinker. Kies het patroon dat je hoorde en sein diezelfde code daarna zelf terug.</p>'
    ),
    (
        '<div class="row"><button class="primary" onclick="startL2()">START LEVEL 2</button><button class="ghost" onclick="speakCurrentVowel()">HERHAAL KLINKER</button><button class="ghost" onclick="replayExpected()">HERHAAL MORSE</button></div>',
        '<div class="row"><button class="primary" onclick="startL2()">START LEVEL 2</button><button class="ghost" onclick="replayExpected()">HERHAAL SIGNAAL</button></div>'
    ),
]
for old, new in repls:
    if old not in text:
        raise SystemExit(f'Expected HTML fragment not found: {old[:80]}')
    text = text.replace(old, new, 1)

old_next = "function nextL2(){if(!l2.active)return;l2.phase='listen';expectedLetter=l2.sequence[l2.index];inputMode=null;$('l2speaker').textContent='LUISTER NAAR DE KLINKER';$('l2sub').textContent='Kies daarna de juiste morsecode.';setMsg('l2msg','Welke morsecode hoort bij de uitgesproken klinker?');speakCurrentVowel();renderL2()}"
new_next = "function nextL2(){if(!l2.active)return;l2.phase='listen';expectedLetter=l2.sequence[l2.index];inputMode=null;$('l2speaker').textContent='LUISTER NAAR HET MORSESIGNAAL';$('l2sub').textContent='Kies daarna precies het patroon dat je hoorde.';setMsg('l2msg','Luister naar de piepjes en kies de juiste morsecode.');renderL2();setTimeout(()=>playLetter(expectedLetter),180)}"
if old_next not in text:
    raise SystemExit('nextL2 block not found')
text = text.replace(old_next, new_next, 1)

# Restore the original browser speech function (removing the added recorded vowel files).
pattern = re.compile(r"const VOWEL_AUDIO=\{.*?\};\s*let vowelAudio=null;\s*function speakCurrentVowel\(\)\{.*?\n\}", re.S)
original_speech = "function speakCurrentVowel(){if(!l2.active||!l2.sequence.length)return;const letter=l2.sequence[l2.index];if('speechSynthesis'in window){speechSynthesis.cancel();const u=new SpeechSynthesisUtterance('Klinker '+letter);u.lang='nl-NL';u.rate=.75;speechSynthesis.speak(u)}}"
text, n = pattern.subn(original_speech, text, count=1)
if n != 1:
    raise SystemExit(f'Expected recorded-vowel block once, found {n}')

old_wrong = "else{l2.mistakes++;setMsg('l2msg','Dat is niet de juiste code. Luister opnieuw.','bad');setTimeout(speakCurrentVowel,500)}renderL2()}"
new_wrong = "else{l2.mistakes++;setMsg('l2msg','Dat is niet de juiste code. Luister opnieuw naar het morsesignaal.','bad');setTimeout(()=>playLetter(target),500)}renderL2()}"
if old_wrong not in text:
    raise SystemExit('Level 2 wrong-answer block not found')
text = text.replace(old_wrong, new_wrong, 1)

p.write_text(text, encoding='utf-8')
print('Patched Level 2: hear Morse -> choose pattern -> key it back; restored original speech code.')
