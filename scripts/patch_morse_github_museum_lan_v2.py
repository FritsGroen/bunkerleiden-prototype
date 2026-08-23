from pathlib import Path

p = Path('morse.html')
s = p.read_text(encoding='utf-8')
backup = Path('morse_BACKUP_2026-08-23_1245.html')
if not backup.exists():
    backup.write_text(s, encoding='utf-8')

marker = "setTimeout(autoReconnectEsp32,450);\n\n</script>"
if marker not in s:
    raise SystemExit('serial end marker not found')

block = r'''setTimeout(autoReconnectEsp32,450);

// Museum web mode: keep the public GitHub Pages dashboard, but bridge the
// physical key through the Orange Pi on the bunker LAN. Activate with ?museum=1.
const MUSEUM_WEB_MODE = new URLSearchParams(location.search).get('museum') === '1';
const MUSEUM_BRIDGE_URL = new URLSearchParams(location.search).get('bridge') || 'ws://192.168.0.68:8765/ws';
let museumLanSocket = null, museumLanRetry = null;

function setMuseumLanStatus(message,state=''){
  const box=$('serialStatus'),txt=$('serialStatusText'),btn=$('serialBtn');
  if(txt)txt.textContent=message;
  if(box)box.className='serialstatus'+(state?' '+state:'');
  if(btn){
    const on=!!(museumLanSocket&&museumLanSocket.readyState===WebSocket.OPEN);
    btn.classList.toggle('connected',on);
    btn.textContent=on?'MUSEUMTASTER · VERBONDEN':'MUSEUMTASTER · VERBINDEN';
  }
}
function scheduleMuseumLanReconnect(){
  if(!MUSEUM_WEB_MODE)return;
  clearTimeout(museumLanRetry);
  museumLanRetry=setTimeout(()=>connectMuseumLan(false),1800);
}
function handleMuseumLanMessage(raw){
  const u=(raw||'').trim().toUpperCase();if(!u)return;
  if(u==='BRIDGE:CONNECTED'){
    setMuseumLanStatus('MUSEUMTASTER · ORANGE PI VERBONDEN','on');return;
  }
  if(u==='BRIDGE:SERIAL_ON'||u==='READY'){
    setMuseumLanStatus('MUSEUMTASTER · ESP32 GEREED','on');return;
  }
  if(u==='BRIDGE:SERIAL_OFF'){
    setMuseumLanStatus('ORANGE PI BEREIKBAAR · ESP32 NIET GEVONDEN','bad');return;
  }
  if(u==='TONE:ON'||u==='TONE:OFF')handleEspLine(u);
}
function connectMuseumLan(force=false){
  if(!MUSEUM_WEB_MODE)return;
  if(museumLanSocket&&(museumLanSocket.readyState===WebSocket.OPEN||museumLanSocket.readyState===WebSocket.CONNECTING)){
    if(!force)return;
    try{museumLanSocket.close()}catch{}
  }
  clearTimeout(museumLanRetry);
  setMuseumLanStatus('MUSEUMTASTER · LOKAAL NETWERK VERBINDEN…');
  try{
    museumLanSocket=new WebSocket(MUSEUM_BRIDGE_URL);
    museumLanSocket.onopen=()=>setMuseumLanStatus('MUSEUMTASTER · ORANGE PI VERBONDEN','on');
    museumLanSocket.onmessage=e=>handleMuseumLanMessage(e.data);
    museumLanSocket.onerror=()=>setMuseumLanStatus('STA LOKAAL NETWERK TOE IN CHROME','bad');
    museumLanSocket.onclose=()=>{
      museumLanSocket=null;
      setMuseumLanStatus('MUSEUMTASTER · OPNIEUW VERBINDEN…','bad');
      scheduleMuseumLanReconnect();
    };
  }catch(e){
    museumLanSocket=null;
    setMuseumLanStatus('STA LOKAAL NETWERK TOE IN CHROME','bad');
    scheduleMuseumLanReconnect();
  }
}
if(MUSEUM_WEB_MODE){
  window.toggleEsp32=function(){connectMuseumLan(true)};
  setTimeout(()=>connectMuseumLan(false),900);
}

</script>'''

s = s.replace(marker, block, 1)
p.write_text(s, encoding='utf-8')
print('Patched GitHub Morse page for museum LAN bridge mode')
