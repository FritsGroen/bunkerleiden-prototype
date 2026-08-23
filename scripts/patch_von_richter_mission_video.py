from pathlib import Path
import shutil

p = Path('index.html')
text = p.read_text(encoding='utf-8')
backup = Path('index_BACKUP_2026-08-23_1114.html')
if not backup.exists():
    shutil.copy2(p, backup)

old = '''<div class="card" onclick="playSound('telephone-ring-old-german-w48-.mp3',null)"><h3>02 · Inkomende oproep</h3><p>Neem een FF33-oproep aan en kies de juiste verbinding.</p><span class="badge">▶ LUISTER</span></div>'''
new = '''<div class="card" onclick="playSound('telephone-ring-old-german-w48-.mp3',null)" style="cursor:pointer" onmouseenter="var v=this.querySelector('video');if(v)v.play().catch(function(){})" onmouseleave="var v=this.querySelector('video');if(v){v.pause();v.currentTime=0}"><h3>02 · Inkomende oproep</h3><p>Neem een FF33-oproep aan en kies de juiste verbinding.</p><video src="bunker%20Von%20Richter.mp4" muted playsinline preload="metadata" style="display:block;width:100%;aspect-ratio:16/9;object-fit:cover;margin:12px 0;border:1px solid rgba(228,183,25,.35);border-radius:6px;background:#050705"></video><span class="badge">▶ LUISTER</span></div>'''

if old not in text:
    if 'bunker%20Von%20Richter.mp4' in text:
        print('Von Richter video already present')
    else:
        raise SystemExit('Target Inkomende oproep card not found')
else:
    p.write_text(text.replace(old, new, 1), encoding='utf-8')
    print('Patched Inkomende oproep with Von Richter video')
