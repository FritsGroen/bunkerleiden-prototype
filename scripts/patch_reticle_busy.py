from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = 'RETICLE-BUSY-SIGNAL-PATCH-20260818'
if marker in s:
    print('Patch already present')
    raise SystemExit(0)

block = r'''
<!-- RETICLE-BUSY-SIGNAL-PATCH-20260818 -->
<script>
(function(){
  const busySignal = new Audio('busy-signal.mp3');
  busySignal.loop = true;
  busySignal.volume = .38;
  let audioUnlocked = false;

  function stopBusySignal(){
    try{
      busySignal.pause();
      busySignal.currentTime = 0;
    }catch(_){ }
  }

  function startBusySignal(){
    try{
      busySignal.currentTime = 0;
      busySignal.play().then(()=>{audioUnlocked=true}).catch(()=>{});
    }catch(_){ }
  }

  // Browsers can block hover-only audio until the visitor has interacted once.
  function unlockAudio(){
    if(audioUnlocked) return;
    try{
      busySignal.muted = true;
      const p = busySignal.play();
      if(p && p.then) p.then(()=>{
        busySignal.pause();
        busySignal.currentTime = 0;
        busySignal.muted = false;
        audioUnlocked = true;
      }).catch(()=>{busySignal.muted=false});
    }catch(_){busySignal.muted=false}
  }
  document.addEventListener('pointerdown', unlockAudio, {once:true, capture:true});
  document.addEventListener('keydown', unlockAudio, {once:true, capture:true});

  document.querySelectorAll('.reticle').forEach(reticle=>{
    reticle.addEventListener('mouseenter', startBusySignal);
    reticle.addEventListener('mouseleave', stopBusySignal);
    reticle.addEventListener('blur', stopBusySignal);
    reticle.addEventListener('click', stopBusySignal, true);
  });

  window.addEventListener('blur', stopBusySignal);
  document.addEventListener('visibilitychange', ()=>{if(document.hidden) stopBusySignal()});
})();
</script>
'''

if '</body>' not in s:
    raise SystemExit('No </body> found')

s = s.replace('</body>', block + '\n</body>', 1)
p.write_text(s, encoding='utf-8')
print('Patched reticle busy-signal hover')
