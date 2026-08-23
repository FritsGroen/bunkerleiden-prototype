from pathlib import Path

p=Path('morse.html')
s=p.read_text(encoding='utf-8')
backup=Path('morse_BACKUP_2026-08-23_1311.html')
if not backup.exists():
    backup.write_text(s,encoding='utf-8')

old="""async function toggleEsp32(){
  if(typeof MUSEUM_WEB_MODE!=='undefined'&&MUSEUM_WEB_MODE){connectMuseumLan(true);return}
  if(isMuseumHost()){connectMuseumBridge(true);return}
  if(typeof DIRECT_SERIAL_MODE!=='undefined'&&!DIRECT_SERIAL_MODE){setSerialStatus('MUIS ACTIEF');return}
  if(espPort){await disconnectEsp32();return}"""
new="""async function toggleEsp32(){
  const q=new URLSearchParams(location.search);
  if(q.get('museum')==='1'){connectMuseumLan(true);return}
  if(!isMuseumHost()&&q.get('serial')!=='1'){
    q.set('museum','1');q.delete('serial');
    location.href=location.pathname+'?'+q.toString();
    return;
  }
  if(isMuseumHost()){connectMuseumBridge(true);return}
  if(espPort){await disconnectEsp32();return}"""
if old not in s:
    raise SystemExit('toggleEsp32 block not found')
s=s.replace(old,new,1)

old="""else if(!DIRECT_SERIAL_MODE){
  // PUBLIC_MOUSE_ONLY
  const b=$('serialBtn');if(b)b.style.display='none';
  setSerialStatus('MUIS ACTIEF');
}"""
new="""else if(!DIRECT_SERIAL_MODE){
  // Public web page: keep the real-key button visible, but route it to the
  // museum bridge instead of opening Chrome's direct serial-port chooser.
  const b=$('serialBtn');
  if(b){
    b.style.display='inline-flex';
    b.textContent='ECHTE TASTER · MUSEUMSTAND';
    b.onclick=()=>{
      const q=new URLSearchParams(location.search);
      q.set('museum','1');q.delete('serial');
      location.href=location.pathname+'?'+q.toString();
    };
  }
  setSerialStatus('MUIS ACTIEF');
}"""
if old not in s:
    raise SystemExit('public mouse block not found')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Public Morse real-key button now redirects to ?museum=1')
