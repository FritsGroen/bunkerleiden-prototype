from pathlib import Path
import shutil

p = Path('morse.html')
text = p.read_text(encoding='utf-8')
backup = Path('morse_BACKUP_2026-08-23_1126.html')
if not backup.exists():
    shutil.copy2(p, backup)

# 1) Visitor-facing ESP32 connection controls.
css_anchor = ".sessionbar{display:flex;justify-content:space-between;gap:10px;align-items:center;margin-top:12px}.statusok{color:var(--green)}"
css_add = css_anchor + ".serialbar{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:0 0 10px}.serialbtn{border:1px solid var(--gold);background:#0b0f0b;color:var(--a2);padding:9px 11px;border-radius:5px;font:800 10px monospace}.serialbtn:hover{border-color:var(--a);background:#e4b7190a}.serialbtn.connected{border-color:#73c66a88;color:var(--green)}.serialstatus{display:inline-flex;align-items:center;gap:6px;color:#9f9785;font:10px monospace}.serialdot{width:8px;height:8px;border-radius:50%;background:#5a5548;box-shadow:0 0 8px transparent}.serialstatus.on{color:var(--green)}.serialstatus.on .serialdot{background:var(--green);box-shadow:0 0 10px #73c66a}.serialstatus.bad{color:#f0aaa5}.serialstatus.bad .serialdot{background:var(--red)}"
if '.serialbar{' not in text:
    if css_anchor not in text:
        raise SystemExit('CSS anchor not found')
    text = text.replace(css_anchor, css_add, 1)

markup_anchor = '      <div class="k">BAUMUSTER T1 · VIRTUELE TASTER</div><h2 style="margin-top:5px">SEIN MET DE MUIS</h2>\n      <div id="keywrap" class="keywrap" role="button" tabindex="0" aria-label="Virtuele morsetaster: houd ingedrukt om te seinen">'
markup_new = '      <div class="k">BAUMUSTER T1 · MORSETASTER</div><h2 style="margin-top:5px">SEIN MET MUIS OF ECHTE TASTER</h2>\n      <div class="serialbar"><button id="serialBtn" class="serialbtn" type="button" onclick="toggleEsp32()">ECHTE TASTER · VERBINDEN</button><span id="serialStatus" class="serialstatus"><span class="serialdot"></span><span id="serialStatusText">MUIS ACTIEF</span></span></div>\n      <div id="keywrap" class="keywrap" role="button" tabindex="0" aria-label="Virtuele morsetaster: houd ingedrukt om te seinen">'
if 'id="serialBtn"' not in text:
    if markup_anchor not in text:
        raise SystemExit('Key panel markup anchor not found')
    text = text.replace(markup_anchor, markup_new, 1)

# 2) Add Web Serial bridge. It listens to the proven ESP32 protocol:
# TONE:ON / TONE:OFF over 115200 baud and routes those transitions through
# the exact same key timing/scoring path as the mouse.
serial_js = r'''
// Museum mode: physical Morse key -> ESP32 -> USB Web Serial -> same game logic.
// Proven ESP32 protocol: 115200 baud, TONE:ON / TONE:OFF. Other protocol lines
// (MARK, INPUT, LETTER, RESULT, READY) may still arrive and are safely ignored here.
let espPort=null,espReader=null,espReading=false,espBuffer='';
function setSerialStatus(message,state=''){
  const box=$('serialStatus'),txt=$('serialStatusText'),btn=$('serialBtn');
  if(!box||!txt||!btn)return;
  txt.textContent=message;box.className='serialstatus'+(state?' '+state:'');
  btn.classList.toggle('connected',!!espPort);
  btn.textContent=espPort?'ECHTE TASTER · VERBREKEN':'ECHTE TASTER · VERBINDEN';
}
async function espSend(command){
  if(!espPort||!espPort.writable)return false;
  let writer;
  try{writer=espPort.writable.getWriter();await writer.write(new TextEncoder().encode(command+'\n'));return true}
  catch(e){return false}
  finally{try{writer&&writer.releaseLock()}catch{}}
}
function handleEspLine(raw){
  const line=(raw||'').trim();if(!line)return;
  const upper=line.toUpperCase();
  if(upper==='TONE:ON'){
    // Route the real key through the same timer, 800 Hz sidetone and animation.
    keyPressStart({});
  }else if(upper==='TONE:OFF'){
    keyPressEnd({});
  }else if(upper==='READY'){
    setSerialStatus('ESP32 · TASTER GEREED','on');
  }
}
async function readEsp32(){
  if(!espPort||!espPort.readable)return;
  espReading=true;const decoder=new TextDecoder();espBuffer='';
  try{
    espReader=espPort.readable.getReader();
    while(espReading){
      const {value,done}=await espReader.read();if(done)break;
      espBuffer+=decoder.decode(value,{stream:true});
      const lines=espBuffer.split(/\r?\n/);espBuffer=lines.pop()||'';
      lines.forEach(handleEspLine);
    }
  }catch(e){
    if(espReading)setSerialStatus('VERBINDING VERBROKEN','bad');
  }finally{
    try{espReader&&espReader.releaseLock()}catch{}
    espReader=null;
  }
}
async function openEsp32(port,automatic=false){
  try{
    espPort=port;await espPort.open({baudRate:115200});
    setSerialStatus('ESP32 · ECHTE TASTER ACTIEF','on');
    // Prevent the older standalone trainer target from doing its own comparison.
    await espSend('RESET');await espSend('CLEARTARGET');
    readEsp32();
    return true;
  }catch(e){
    espPort=null;
    setSerialStatus(automatic?'ESP32 BESCHIKBAAR · KLIK VERBINDEN':'POORT NIET BESCHIKBAAR','bad');
    return false;
  }
}
async function disconnectEsp32(){
  espReading=false;
  try{if(espReader)await espReader.cancel()}catch{}
  try{if(keyDownAt)keyPressEnd({})}catch{}
  try{if(espPort)await espPort.close()}catch{}
  espPort=null;espReader=null;setSerialStatus('MUIS ACTIEF');
}
async function toggleEsp32(){
  if(espPort){await disconnectEsp32();return}
  if(!('serial' in navigator)){
    setSerialStatus('ECHTE TASTER VEREIST EDGE/CHROME','bad');return;
  }
  try{
    const port=await navigator.serial.requestPort();
    await openEsp32(port,false);
  }catch(e){
    if(e&&e.name==='NotFoundError')setSerialStatus('MUIS ACTIEF');
    else setSerialStatus('ESP32 VERBINDEN MISLUKT','bad');
  }
}
async function autoReconnectEsp32(){
  if(!('serial' in navigator)){
    setSerialStatus('MUIS ACTIEF · ECHTE TASTER VIA EDGE/CHROME');return;
  }
  try{
    const ports=await navigator.serial.getPorts();
    if(ports.length)await openEsp32(ports[0],true);
  }catch{}
}
if('serial' in navigator){
  navigator.serial.addEventListener('disconnect',()=>{espPort=null;espReading=false;setSerialStatus('ESP32 LOSGEKOPPELD · MUIS ACTIEF','bad')});
}
setTimeout(autoReconnectEsp32,450);
'''
if 'async function toggleEsp32()' not in text:
    closing = '</script>'
    if closing not in text:
        raise SystemExit('script closing tag not found')
    text = text.replace(closing, serial_js + '\n' + closing, 1)

p.write_text(text, encoding='utf-8')
print('Patched morse.html with ESP32 Web Serial support')
