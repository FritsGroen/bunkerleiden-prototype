from pathlib import Path

p=Path('morse.html')
s=p.read_text(encoding='utf-8')
backup=Path('morse_BACKUP_2026-08-23_1302.html')
if not backup.exists():
    backup.write_text(s,encoding='utf-8')

needle="const MUSEUM_WEB_MODE = new URLSearchParams(location.search).get('museum') === '1';"
if "const DIRECT_SERIAL_MODE" not in s:
    s=s.replace(needle,needle+"\nconst DIRECT_SERIAL_MODE = new URLSearchParams(location.search).get('serial') === '1';",1)

old="async function toggleEsp32(){\n  if(isMuseumHost()){connectMuseumBridge(true);return}\n  if(espPort){await disconnectEsp32();return}"
new="async function toggleEsp32(){\n  if(typeof MUSEUM_WEB_MODE!=='undefined'&&MUSEUM_WEB_MODE){connectMuseumLan(true);return}\n  if(isMuseumHost()){connectMuseumBridge(true);return}\n  if(typeof DIRECT_SERIAL_MODE!=='undefined'&&!DIRECT_SERIAL_MODE){setSerialStatus('MUIS ACTIEF');return}\n  if(espPort){await disconnectEsp32();return}"
if old in s:s=s.replace(old,new,1)

s=s.replace("if(isMuseumHost())setTimeout(()=>connectMuseumBridge(false),250);\nelse setTimeout(autoReconnectEsp32,450);","if(isMuseumHost())setTimeout(()=>connectMuseumBridge(false),250);\nelse if(new URLSearchParams(location.search).get('serial')==='1')setTimeout(autoReconnectEsp32,450);",1)
s=s.replace("if(isMuseumHost())setTimeout(()=>connectMuseumBridge(false),250);\nelse if(typeof DIRECT_SERIAL_MODE!=='undefined'&&DIRECT_SERIAL_MODE)setTimeout(autoReconnectEsp32,450);","if(isMuseumHost())setTimeout(()=>connectMuseumBridge(false),250);\nelse if(new URLSearchParams(location.search).get('serial')==='1')setTimeout(autoReconnectEsp32,450);",1)

# Hide the hardware-connect button on the normal public page; museum mode keeps it.
marker="if(MUSEUM_WEB_MODE){\n  window.toggleEsp32=function(){connectMuseumLan(true)};\n  setTimeout(()=>connectMuseumLan(false),900);\n}"
if marker in s and "PUBLIC_MOUSE_ONLY" not in s:
    s=s.replace(marker,marker+"\nelse if(!DIRECT_SERIAL_MODE){\n  // PUBLIC_MOUSE_ONLY\n  const b=$('serialBtn');if(b)b.style.display='none';\n  setSerialStatus('MUIS ACTIEF');\n}",1)

p.write_text(s,encoding='utf-8')
print('Disabled serial chooser and hid hardware button on ordinary public Morse page')
# workflow trigger 2026-08-23 13:05
