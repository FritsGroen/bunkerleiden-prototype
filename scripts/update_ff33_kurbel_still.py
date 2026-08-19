from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
backup=Path('index_BACKUP_2026-08-19_1206.html')
if not backup.exists():
    backup.write_text(s, encoding='utf-8')

still='kurbel_kast_vloeiend%20%20still.gif'
old_initial="id='kurbelImg' src='ff33.png'"
new_initial=f"id='kurbelImg' src='{still}'"
old_stop="if(img)img.src='ff33.png';"
new_stop=f"if(img)img.src='{still}';"

changed=False
if old_initial in s:
    s=s.replace(old_initial,new_initial,1)
    changed=True
if old_stop in s:
    s=s.replace(old_stop,new_stop,1)
    changed=True

if not changed:
    print('Kurbel still already updated or anchors not found')
    raise SystemExit(0)

p.write_text(s,encoding='utf-8')
print('Kurbel resting image updated to side-view still')
