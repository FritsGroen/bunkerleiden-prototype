from pathlib import Path
from datetime import datetime

p = Path('morse.html')
s = p.read_text(encoding='utf-8')

# Backup current working Morse page before the fix.
backup = Path('morse_BACKUP_2026-08-23_1050.html')
if not backup.exists():
    backup.write_text(s, encoding='utf-8')

old = "let scores=loadScores();\npurgeUnsafeL1Scores();\nlet unlocks=loadUnlocks();"
new = "let scores=loadScores();\nlet unlocks=loadUnlocks();"
if old not in s:
    raise SystemExit('early purge block not found')
s = s.replace(old, new, 1)

old2 = "function purgeUnsafeL1Scores(){\n  let changed=false;\n  for(const w of Object.keys(scores.l1||{})){if(!isCleanL1Word(w)){delete scores.l1[w];changed=true}}\n  for(const w of Object.keys(scores.l1Attempts||{})){if(!isCleanL1Word(w)){delete scores.l1Attempts[w];changed=true}}\n  if(changed)saveScores();\n}"
new2 = "function purgeUnsafeL1Scores(){\n  // Normalize older localStorage data first so museum kiosks upgraded from an\n  // earlier version cannot break the dashboard.\n  scores = scores && typeof scores==='object' ? scores : {};\n  scores.l1 = scores.l1 && typeof scores.l1==='object' ? scores.l1 : {};\n  scores.l1Attempts = scores.l1Attempts && typeof scores.l1Attempts==='object' ? scores.l1Attempts : {};\n  scores.l2 = Array.isArray(scores.l2) ? scores.l2 : [];\n  scores.l2Attempts = Number.isFinite(scores.l2Attempts) ? scores.l2Attempts : 0;\n  scores.l3 = scores.l3 && typeof scores.l3==='object' ? scores.l3 : {};\n  scores.l3Attempts = scores.l3Attempts && typeof scores.l3Attempts==='object' ? scores.l3Attempts : {};\n  let changed=false;\n  for(const w of Object.keys(scores.l1)){if(!isCleanL1Word(w)){delete scores.l1[w];changed=true}}\n  for(const w of Object.keys(scores.l1Attempts)){if(!isCleanL1Word(w)){delete scores.l1Attempts[w];changed=true}}\n  if(changed)saveScores();\n}\n// Run only after the filter constants/functions above have been initialized.\npurgeUnsafeL1Scores();"
if old2 not in s:
    raise SystemExit('purge function block not found')
s = s.replace(old2, new2, 1)

p.write_text(s, encoding='utf-8')
print('Morse Level 1 startup fixed')
