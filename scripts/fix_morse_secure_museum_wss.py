from pathlib import Path

p = Path('morse.html')
s = p.read_text(encoding='utf-8')
backup = Path('morse_BACKUP_2026-08-23_1254.html')
if not backup.exists():
    backup.write_text(s, encoding='utf-8')

old = "const MUSEUM_BRIDGE_URL = new URLSearchParams(location.search).get('bridge') || 'ws://192.168.0.68:8765/ws';"
new = "const MUSEUM_BRIDGE_URL = new URLSearchParams(location.search).get('bridge') || 'wss://192.168.0.68:8765/ws';"
if old not in s:
    raise SystemExit('museum bridge URL marker not found')
s = s.replace(old, new, 1)

s = s.replace("setMuseumLanStatus('STA LOKAAL NETWERK TOE IN CHROME','bad');", "setMuseumLanStatus('BEVEILIGDE MUSEUMBRUG NIET BEREIKBAAR','bad');")

p.write_text(s, encoding='utf-8')
print('Switched museum bridge to secure WSS')
