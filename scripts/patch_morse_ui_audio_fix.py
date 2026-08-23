from pathlib import Path

TARGET = Path("morse.html")
BACKUP = Path("morse_BACKUP_2026-08-23_1027.html")

text = TARGET.read_text(encoding="utf-8")
if not BACKUP.exists():
    BACKUP.write_text(text, encoding="utf-8")

old_css = ".keyhud{position:absolute;left:9px;right:9px;bottom:9px;background:#050705e8;border-left:3px solid var(--a);padding:9px 11px;font:10px/1.45 monospace;color:#c8bea6;pointer-events:none}"
new_css = ".keyhud{margin-top:10px;background:#050705e8;border:1px solid var(--line);border-left:3px solid var(--a);border-radius:6px;padding:9px 11px;font:10px/1.45 monospace;color:#c8bea6;pointer-events:none}"
if old_css not in text:
    raise SystemExit("keyhud CSS anchor not found")
text = text.replace(old_css, new_css, 1)

old_markup = '''        <img id="keyimg" src="morse%20baumeister%20t1.png" alt="Baumeister T1 morsetaster">
        <div class="keyhud"><b><span id="keylamp" class="keylamp"></span>HOUD INGEDRUKT OM TE SEINEN</b>Kort &lt; 250 ms = punt · langer = streep · 700 ms pauze sluit de letter af.</div>
      </div>
      <div class="inputread">'''
new_markup = '''        <img id="keyimg" src="morse%20baumeister%20t1.png" alt="Baumeister T1 morsetaster">
      </div>
      <div class="keyhud"><b><span id="keylamp" class="keylamp"></span>HOUD INGEDRUKT OM TE SEINEN</b>Kort &lt; 250 ms = punt · langer = streep · 700 ms pauze sluit de letter af.</div>
      <div class="inputread">'''
if old_markup not in text:
    raise SystemExit("key image markup anchor not found")
text = text.replace(old_markup, new_markup, 1)

old_speech = "function speakCurrentVowel(){if(!l2.active||!l2.sequence.length)return;const letter=l2.sequence[l2.index];if('speechSynthesis'in window){speechSynthesis.cancel();const u=new SpeechSynthesisUtterance('Klinker '+letter);u.lang='nl-NL';u.rate=.75;speechSynthesis.speak(u)}}"
new_speech = '''const VOWEL_AUDIO={A:'audio/vowels/a.ogg',E:'audio/vowels/e.ogg',I:'audio/vowels/i.ogg',O:'audio/vowels/o.ogg',U:'audio/vowels/u.ogg'};
let vowelAudio=null;
function speakCurrentVowel(){
  if(!l2.active||!l2.sequence.length)return;
  const letter=l2.sequence[l2.index];
  if(vowelAudio){try{vowelAudio.pause();vowelAudio.currentTime=0}catch{}}
  vowelAudio=new Audio(VOWEL_AUDIO[letter]);
  vowelAudio.preload='auto';
  vowelAudio.volume=1;
  vowelAudio.play().catch(()=>{
    if('speechSynthesis' in window){
      speechSynthesis.cancel();
      const u=new SpeechSynthesisUtterance(letter);
      u.lang='nl-NL';u.rate=.72;u.volume=1;
      try{speechSynthesis.resume()}catch{}
      speechSynthesis.speak(u);
    }
  });
}'''
if old_speech not in text:
    raise SystemExit("Level 2 speech anchor not found")
text = text.replace(old_speech, new_speech, 1)

TARGET.write_text(text, encoding="utf-8")
print("Patched morse.html: help text moved below key; Level 2 uses local vowel audio.")
