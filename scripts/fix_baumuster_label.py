from pathlib import Path
p=Path('morse.html')
s=p.read_text(encoding='utf-8')
s=s.replace('BAUMEISTER T1 · VIRTUELE TASTER','BAUMUSTER T1 · VIRTUELE TASTER')
p.write_text(s,encoding='utf-8')
