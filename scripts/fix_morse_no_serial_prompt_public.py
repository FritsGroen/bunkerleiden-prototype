from pathlib import Path

p=Path('morse.html')
s=p.read_text(encoding='utf-8')
backup=Path('morse_BACKUP_2026-08-23_1302.html')
if not backup.exists():
    backup.write_text(s,encoding='utf-8')

# Only allow direct Web Serial when explicitly requested with ?serial=1.
needle="const MUSEUM_WEB_MODE = new URLSearchParams(location.search).get('museum') === '1';"
repl="const MUSEUM_WEB_MODE = new URLSearchParams(location.search).get('museum') === '1';\nconst DIRECT_SERIAL_MODE = new URLSearchParams(location.search).get('serial') === '1';"
if needle not in s:
    raise SystemExit('museum mode marker not found')
s=s.replace(needle,repl,1)

old="async function toggleEsp32(){\n  if(isMuseumHost()){connectMuseumBridge(true);return}\n  if(espPort){await disconnectEsp32();return}"
new="async function toggleEsp32(){\n  if(typeof MUSEUM_WEB_MODE!=='undefined'&&MUSEUM_WEB_MODE){connectMuseumLan(true);return}\n  if(isMuseumHost()){connectMuseumBridge(true);return}\n  if(typeof DIRECT_SERIAL_MODE!=='undefined'&&!DIRECT_SERIAL_MODE){setSerialStatus('MUIS ACTIEF');return}\n  if(espPort){await disconnectEsp32();return}"
if old not in s:
    raise SystemExit('toggleEsp32 marker not found')
s=s.replace(old,new,1)

old="if(isMuseumHost())setTimeout(()=>connectMuseumBridge(false),250);\nelse setTimeout(autoReconnectEsp32,450);"
new="if(isMuseumHost())setTimeout(()=>connectMuseumBridge(false),250);\nelse if(typeof DIRECT_SERIAL_MODE!=='undefined'&&DIRECT_SERIAL_MODE)setTimeout(autoReconnectEsp32,450);"
if old not in s:
    raise SystemExit('startup serial marker not found')
s=s.replace(old,new,1)

# On the ordinary public page, remove the hardware-connect button entirely.
marker="if(MUSEUM_WEB_MODE){\n  const originalToggleEsp32=window.toggleEsp32;\n  window.toggleEsp32=function(){connectMuseumLan(true)};\n  setTimeout(()=>connectMuseumLan(false),900);\n}"
replacement=marker+"\nelse if(!DIRECT_SERIAL_MODE){\n  const b=$('serialBtn');if(b)b.style.display='none';\n  setSerialStatus('MUIS ACTIEF');\n}"
if marker not in s:
    raise SystemExit('museum web mode block not found')
s=s.replace(marker,replacement,1)

p.write_text(s,encoding='utf-8')
print('Disabled serial-port chooser on ordinary public Morse page')
