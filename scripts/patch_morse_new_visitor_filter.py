from pathlib import Path
from datetime import datetime

p = Path('morse.html')
s = p.read_text(encoding='utf-8')

# Backup the exact pre-patch page in the repository.
stamp = datetime.now().strftime('%Y-%m-%d_%H%M')
backup = Path(f'morse_BACKUP_{stamp}.html')
if not backup.exists():
    backup.write_text(s, encoding='utf-8')

old = "function cleanWord(v,max=12){return (v||'').toUpperCase().replace(/[^A-Z0-9]/g,'').slice(0,max)}"
new = """function cleanWord(v,max=12){return (v||'').toUpperCase().replace(/[^A-Z0-9]/g,'').slice(0,max)}
// Museum-safe Level 1 input filter. Short ambiguous terms are exact-match only;
// longer profanity/slurs are also caught inside variants. Leetspeak is normalized.
const L1_BLOCK_EXACT=['KUT','LUL','SLET','HOER','GVD','SEX','DICK','COCK','CUNT','SLUT','WHORE','HURE','FOTZE'];
const L1_BLOCK_PARTS=['FUCK','SHIT','BITCH','KLOOTZAK','KLOTE','GODVER','TERING','TYFUS','KANKER','NEUK','PORNO','PIEMEL','PENIS','VAGINA','SCHEIS','ARSCHLOCH','FICK','WICHSER','BASTARD','ASSHOLE','NIGGER','NEGER'];
function normalizeForFilter(v){
  const map={0:'O',1:'I',3:'E',4:'A',5:'S',7:'T',8:'B'};
  return cleanWord(v,12).split('').map(c=>map[c]||c).join('');
}
function isCleanL1Word(v){
  const n=normalizeForFilter(v);
  if(!n)return true;
  const collapsed=n.replace(/(.)\\1{1,}/g,'$1');
  return !L1_BLOCK_EXACT.includes(n) && !L1_BLOCK_EXACT.includes(collapsed) &&
         !L1_BLOCK_PARTS.some(x=>n.includes(x)||collapsed.includes(x));
}
function purgeUnsafeL1Scores(){
  let changed=false;
  for(const w of Object.keys(scores.l1||{})){if(!isCleanL1Word(w)){delete scores.l1[w];changed=true}}
  for(const w of Object.keys(scores.l1Attempts||{})){if(!isCleanL1Word(w)){delete scores.l1Attempts[w];changed=true}}
  if(changed)saveScores();
}"""
if old not in s:
    raise SystemExit('cleanWord anchor not found')
s = s.replace(old, new, 1)

old = "let scores=loadScores();\nlet unlocks=loadUnlocks();"
new = "let scores=loadScores();\npurgeUnsafeL1Scores();\nlet unlocks=loadUnlocks();"
if old not in s:
    raise SystemExit('scores anchor not found')
s = s.replace(old, new, 1)

old = "function startL1(){initAudio();stopInput();const word=cleanWord($('l1word').value,12)||WORDS[Math.floor(Math.random()*WORDS.length)];$('l1word').value=word;l1={active:true,word,index:0,attempts:0,mistakes:0,start:performance.now(),threshold:Math.max(5,parseFloat($('l1threshold').value)||suggestedThreshold(word))};renderL1();setMsg('l1msg','Luister naar letter 1 en sein hem daarna terug.');setTimeout(()=>beginL1Letter(),300)}"
new = """function startL1(){
  initAudio();stopInput();
  const typed=cleanWord($('l1word').value,12);
  if(typed&&!isCleanL1Word(typed)){
    $('l1word').value='';
    setMsg('l1msg','Dat woord gebruiken we niet in de museumopdracht. Kies een ander, net woord.','bad');
    return;
  }
  const word=typed||WORDS[Math.floor(Math.random()*WORDS.length)];
  $('l1word').value=word;
  l1={active:true,word,index:0,attempts:0,mistakes:0,start:performance.now(),threshold:Math.max(5,parseFloat($('l1threshold').value)||suggestedThreshold(word))};
  renderL1();setMsg('l1msg','Luister naar letter 1 en sein hem daarna terug.');setTimeout(()=>beginL1Letter(),300)
}"""
if old not in s:
    raise SystemExit('startL1 anchor not found')
s = s.replace(old, new, 1)

old = "$('l1word').addEventListener('input',()=>{const v=cleanWord($('l1word').value,12);$('l1word').value=v;$('l1threshold').value=suggestedThreshold(v)});"
new = """$('l1word').addEventListener('input',()=>{
  const v=cleanWord($('l1word').value,12);
  if(v&&!isCleanL1Word(v)){
    $('l1word').value='';
    $('l1threshold').value=suggestedThreshold('FRITS');
    setMsg('l1msg','Dat woord is niet toegestaan. Kies een ander, net woord.','bad');
    renderScores();
    return;
  }
  $('l1word').value=v;$('l1threshold').value=suggestedThreshold(v)
});"""
if old not in s:
    raise SystemExit('input listener anchor not found')
s = s.replace(old, new, 1)

old = "function newVisitor(){unlocks={l1:true,l2:false,l3:false};sessionStorage.setItem(SESSION,JSON.stringify(unlocks));l1.active=l2.active=l3.active=false;stopInput();selectedLevel=1;showLevel(1);setMsg('l1msg','Nieuwe bezoeker gestart. Topscores zijn behouden.','good')}"
new = """function newVisitor(){
  unlocks={l1:true,l2:false,l3:false};
  sessionStorage.setItem(SESSION,JSON.stringify(unlocks));
  stopInput();
  l1={active:false,word:'FRITS',index:0,attempts:0,mistakes:0,start:0,threshold:60};
  l2={active:false,sequence:[],index:0,phase:'idle',attempts:0,mistakes:0,start:0};
  l3={active:false,word:'',order:[],step:0,solved:new Set(),phase:'idle',attempts:0,mistakes:0,start:0};
  $('l1word').value='FRITS';$('l1threshold').value=suggestedThreshold('FRITS');
  $('l1time').textContent='0.0 s';$('l2time').textContent='0.0 s';$('l3time').textContent='0.0 s';
  $('l2speaker').textContent='NOG NIET GESTART';$('l2sub').textContent='Start de klinkerronde.';
  selectedLevel=1;showLevel(1);renderL1();renderL2();renderL3Word();renderL3Meta();renderScores();
  setMsg('l1msg','Nieuwe bezoeker gestart op Level 1. Topscores zijn behouden.','good')
}"""
if old not in s:
    raise SystemExit('newVisitor anchor not found')
s = s.replace(old, new, 1)

s = s.replace('>NIEUWE BEZOEKER</button>', '>NIEUWE BEZOEKER · RESET</button>', 1)

p.write_text(s, encoding='utf-8')
print(f'patched morse.html; backup={backup}')
