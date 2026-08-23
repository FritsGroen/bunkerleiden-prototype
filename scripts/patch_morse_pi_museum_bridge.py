from pathlib import Path

p = Path('morse.html')
s = p.read_text(encoding='utf-8')
backup = Path('morse_BACKUP_2026-08-23_1221.html')
if not backup.exists():
    backup.write_text(s, encoding='utf-8')

old = "<div class=\"instructions\">Sein met de muis op de Baumuster T1. Kort indrukken geeft een punt, langer indrukken een streep. Na 700 ms stilte wordt de letter beoordeeld.</div>"
new = "<div class=\"instructions\">Sein met de muis of met de fysieke Baumuster T1. Kort indrukken geeft een punt, langer indrukken een streep. Na 700 ms stilte wordt de letter beoordeeld.</div>"
if old in s:
    s = s.replace(old, new, 1)

old = "// Museum mode: physical Morse key -> ESP32 -> USB Web Serial -> same game logic.\n// Proven ESP32 protocol: 115200 baud, TONE:ON / TONE:OFF. Other protocol lines\n// (MARK, INPUT, LETTER, RESULT, READY) may still arrive and are safely ignored here.\nlet espPort=null,espReader=null,espReading=false,espBuffer='';"
new = "// Physical Morse key support. Public site: optional direct Web Serial.\n// Museum: Baumuster T1 -> ESP32 -> Orange Pi -> local WebSocket -> same game logic.\n// Proven ESP32 protocol: 115200 baud, TONE:ON / TONE:OFF.\nlet espPort=null,espReader=null,espReading=false,espBuffer='';\nlet museumSocket=null,museumReconnectTimer=null;"
if old not in s:
    raise SystemExit('ESP32 marker not found')
s = s.replace(old, new, 1)

old = """function setSerialStatus(message,state=''){
  const box=$('serialStatus'),txt=$('serialStatusText'),btn=$('serialBtn');
  if(!box||!txt||!btn)return;
  txt.textContent=message;box.className='serialstatus'+(state?' '+state:'');
  btn.classList.toggle('connected',!!espPort);
  btn.textContent=espPort?'ECHTE TASTER · VERBREKEN':'ECHTE TASTER · VERBINDEN';
}"""
new = """function setSerialStatus(message,state=''){
  const box=$('serialStatus'),txt=$('serialStatusText'),btn=$('serialBtn');
  if(!box||!txt||!btn)return;
  const museumConnected=!!(museumSocket&&museumSocket.readyState===WebSocket.OPEN);
  const connected=!!espPort||museumConnected;
  txt.textContent=message;box.className='serialstatus'+(state?' '+state:'');
  btn.classList.toggle('connected',connected);
  if(isMuseumHost())btn.textContent=museumConnected?'MUSEUMTASTER · VERBONDEN':'MUSEUMTASTER · VERBINDEN';
  else btn.textContent=espPort?'ECHTE TASTER · VERBREKEN':'ECHTE TASTER · VERBINDEN';
}"""
if old not in s:
    raise SystemExit('setSerialStatus block not found')
s = s.replace(old, new, 1)

old = "async function toggleEsp32(){\n  if(espPort){await disconnectEsp32();return}"
new = "async function toggleEsp32(){\n  if(isMuseumHost()){connectMuseumBridge(true);return}\n  if(espPort){await disconnectEsp32();return}"
if old not in s:
    raise SystemExit('toggleEsp32 marker not found')
s = s.replace(old, new, 1)

marker = "if('serial' in navigator){\n  navigator.serial.addEventListener('disconnect',()=>{espPort=null;espReading=false;setSerialStatus('ESP32 LOSGEKOPPELD · MUIS ACTIEF','bad')});\n}\nsetTimeout(autoReconnectEsp32,450);"
insert = """function isMuseumHost(){
  const h=(location.hostname||'').toLowerCase();
  return location.protocol==='http:' && (
    h==='orangepizero2w'||h==='orangepizero2w.local'||h==='localhost'||h==='127.0.0.1'||
    /^192\\.168\\./.test(h)||/^10\\./.test(h)||/^172\\.(1[6-9]|2\\d|3[01])\\./.test(h)
  );
}
function scheduleMuseumReconnect(){
  if(!isMuseumHost())return;
  clearTimeout(museumReconnectTimer);
  museumReconnectTimer=setTimeout(()=>connectMuseumBridge(false),1800);
}
function handleMuseumLine(raw){
  const upper=(raw||'').trim().toUpperCase();if(!upper)return;
  if(upper==='BRIDGE:CONNECTED'){
    setSerialStatus('MUSEUMTASTER · ORANGE PI VERBONDEN','on');return;
  }
  if(upper==='BRIDGE:SERIAL_ON'||upper==='READY'){
    setSerialStatus('MUSEUMTASTER · ESP32 GEREED','on');return;
  }
  if(upper==='BRIDGE:SERIAL_OFF'){
    setSerialStatus('ORANGE PI BEREIKBAAR · ESP32 NIET GEVONDEN','bad');return;
  }
  if(upper==='TONE:ON'||upper==='TONE:OFF')handleEspLine(upper);
}
function connectMuseumBridge(force=false){
  if(!isMuseumHost())return;
  if(museumSocket&&(museumSocket.readyState===WebSocket.OPEN||museumSocket.readyState===WebSocket.CONNECTING)){
    if(!force)return;
    try{museumSocket.close()}catch{}
  }
  clearTimeout(museumReconnectTimer);
  setSerialStatus('MUSEUMTASTER · VERBINDEN…');
  try{
    const scheme=location.protocol==='https:'?'wss':'ws';
    museumSocket=new WebSocket(scheme+'://'+location.host+'/ws');
    museumSocket.onopen=()=>setSerialStatus('MUSEUMTASTER · ORANGE PI VERBONDEN','on');
    museumSocket.onmessage=e=>handleMuseumLine(e.data);
    museumSocket.onerror=()=>setSerialStatus('MUSEUMTASTER · GEEN VERBINDING','bad');
    museumSocket.onclose=()=>{museumSocket=null;setSerialStatus('MUSEUMTASTER · OPNIEUW VERBINDEN…','bad');scheduleMuseumReconnect()};
  }catch(e){
    museumSocket=null;setSerialStatus('MUSEUMTASTER · GEEN VERBINDING','bad');scheduleMuseumReconnect();
  }
}
if('serial' in navigator){
  navigator.serial.addEventListener('disconnect',()=>{espPort=null;espReading=false;setSerialStatus('ESP32 LOSGEKOPPELD · MUIS ACTIEF','bad')});
}
if(isMuseumHost())setTimeout(()=>connectMuseumBridge(false),250);
else setTimeout(autoReconnectEsp32,450);"""
if marker not in s:
    raise SystemExit('final serial marker not found')
s = s.replace(marker, insert, 1)

p.write_text(s, encoding='utf-8')
print('Patched morse.html for Orange Pi museum bridge')
