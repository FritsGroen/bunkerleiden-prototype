from pathlib import Path

p = Path('morse.html')
s = p.read_text(encoding='utf-8')

# Correct the on-screen equipment designation; keep lowercase asset filenames unchanged.
s = s.replace('Baumeister T1', 'Baumuster T1')

s = s.replace(
    '<h3>02 · KLINKERS ONTHOUDEN</h3><p>Luister naar een morsecode, kies het juiste patroon en sein die code daarna zelf terug.</p>',
    '<h3>02 · KLINKERS ONTHOUDEN</h3><p>Hoor een klinker, kies de juiste morsecode en sein hem daarna zelf terug.</p>'
)

s = s.replace(
    '<p class="copy">Luister naar de morsecode van een klinker. Kies het patroon dat je hoorde en sein diezelfde code daarna zelf terug.</p>',
    '<p class="copy">Luister naar de uitgesproken klinker, kies de juiste morsecode en sein die code daarna correct terug.</p>'
)

s = s.replace(
    '<div class="row"><button class="primary" onclick="startL2()">START LEVEL 2</button><button class="ghost" onclick="replayExpected()">HERHAAL SIGNAAL</button></div>',
    '<div class="row"><button class="primary" onclick="startL2()">START LEVEL 2</button><button class="ghost" onclick="speakCurrentVowel()">HERHAAL KLINKER</button><button class="ghost" onclick="replayExpected()">HERHAAL MORSE</button></div>'
)

old_next = "function nextL2(){if(!l2.active)return;l2.phase='listen';expectedLetter=l2.sequence[l2.index];inputMode=null;$('l2speaker').textContent='LUISTER NAAR HET MORSESIGNAAL';$('l2sub').textContent='Kies daarna precies het patroon dat je hoorde.';setMsg('l2msg','Luister naar de piepjes en kies de juiste morsecode.');renderL2();setTimeout(()=>playLetter(expectedLetter),180)}"
new_next = "function nextL2(){if(!l2.active)return;l2.phase='listen';expectedLetter=l2.sequence[l2.index];inputMode=null;$('l2speaker').textContent='LUISTER NAAR DE KLINKER';$('l2sub').textContent='Kies daarna de juiste morsecode.';setMsg('l2msg','Welke morsecode hoort bij de uitgesproken klinker?');speakCurrentVowel();renderL2()}"
if old_next not in s:
    raise SystemExit('nextL2 pattern not found')
s = s.replace(old_next, new_next)

old_choose = "function chooseL2(code){if(!l2.active||l2.phase!=='listen')return;l2.attempts++;const target=l2.sequence[l2.index];if(code===VOWELS[target]){l2.phase='morse';expectedLetter=target;inputMode='l2';$('l2speaker').textContent='SEIN DE CODE TERUG';$('l2sub').textContent='Gebruik nu de Baumuster T1.';setMsg('l2msg','Juist gekozen. Luister naar de code en sein hem na.','good');playCode(code)}else{l2.mistakes++;setMsg('l2msg','Dat is niet de juiste code. Luister opnieuw naar het morsesignaal.','bad');setTimeout(()=>playLetter(target),500)}renderL2()}"
# In case the prior capitalization correction has not yet happened at this point in a future rerun.
old_choose_alt = old_choose.replace('Baumuster T1', 'Baumeister T1')
new_choose = "function chooseL2(code){if(!l2.active||l2.phase!=='listen')return;l2.attempts++;const target=l2.sequence[l2.index];if(code===VOWELS[target]){l2.phase='morse';expectedLetter=target;inputMode='l2';$('l2speaker').textContent='SEIN DE CODE TERUG';$('l2sub').textContent='Gebruik nu de Baumuster T1.';setMsg('l2msg','Juist gekozen. Luister naar de code en sein hem na.','good');playCode(code)}else{l2.mistakes++;setMsg('l2msg','Dat is niet de juiste code. Luister opnieuw naar de klinker.','bad');setTimeout(speakCurrentVowel,500)}renderL2()}"
if old_choose in s:
    s = s.replace(old_choose, new_choose)
elif old_choose_alt in s:
    s = s.replace(old_choose_alt, new_choose)
else:
    raise SystemExit('chooseL2 pattern not found')

p.write_text(s, encoding='utf-8')
print('patched morse.html')
