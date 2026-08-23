(function(){
  'use strict';

  function protectVideo(video){
    if(!video||video.dataset.r616Protected==='1')return;
    video.dataset.r616Protected='1';

    /* Hide the browser's obvious save/download routes while keeping normal playback controls. */
    video.setAttribute('controlsList','nodownload noplaybackrate');
    video.controlsList && video.controlsList.add && video.controlsList.add('nodownload');
    video.disablePictureInPicture=true;
    video.setAttribute('disablepictureinpicture','');
    video.disableRemotePlayback=true;
    video.setAttribute('disableremoteplayback','');
    video.draggable=false;
    video.setAttribute('draggable','false');

    video.addEventListener('contextmenu',e=>e.preventDefault());
    video.addEventListener('dragstart',e=>e.preventDefault());
  }

  function protectAllVideos(root=document){
    if(root instanceof HTMLVideoElement)protectVideo(root);
    if(root.querySelectorAll)root.querySelectorAll('video').forEach(protectVideo);
  }

  function wireSloopVideo(){
    const card=[...document.querySelectorAll('#dossiers .card')].find(el=>{
      const h=el.querySelector('h3');
      return h&&h.textContent.trim()==='1984 · Poging tot sloop';
    });
    if(!card||card.querySelector('.sloop-card-video'))return;

    const video=document.createElement('video');
    video.className='sloop-card-video';
    video.src='poging%20tot%20sloop%203.mp4';
    video.controls=true;
    video.playsInline=true;
    video.preload='metadata';
    video.setAttribute('aria-label','Film over de poging tot sloop in 1984');
    video.style.cssText='display:block;width:100%;aspect-ratio:16/9;object-fit:cover;margin:12px 0;border:1px solid rgba(228,183,25,.35);border-radius:6px;background:#050705;';

    ['click','dblclick','pointerdown','pointerup'].forEach(type=>{
      video.addEventListener(type,e=>e.stopPropagation());
    });

    protectVideo(video);
    const badge=card.querySelector('.badge');
    card.insertBefore(video,badge||null);
  }

  function patchMainEntranceDossier(){
    if(typeof window.r616HotspotOpen!=='function'||window.r616HotspotOpen.datasetMainEntranceFixed)return false;

    const original=window.r616HotspotOpen;
    const patched=function(id){
      const key=String(id).padStart(2,'0');
      if(key!=='10')return original(id);

      if(typeof window.modal!=='function')return false;
      window.modal(`
        <div class='k'>RUIMTEDOSSIER · TOEGANG</div>
        <h2>10 · HOOFDINGANG</h2>
        <div style="display:grid;grid-template-columns:minmax(260px,.9fr) 1.1fr;gap:22px;align-items:start">
          <div style="min-height:300px;border:1px solid rgba(228,183,25,.28);border-radius:8px;background:linear-gradient(180deg,#0c100c,#080a08);display:grid;place-items:center;padding:28px;text-align:center">
            <div>
              <div class='k' style="margin-bottom:10px">BEELD WORDT VERVANGEN</div>
              <div style="font:800 15px/1.4 monospace;color:#ffd84b">FOTO VAN DE OORSPRONKELIJKE HOOFDINGANG VOLGT</div>
              <p class='copy' style="margin:12px 0 0">De eerder getoonde straatgevel is niet de hoofdingang en is daarom verwijderd.</p>
            </div>
          </div>
          <div>
            <p class='copy'>De oorspronkelijke hoofdingang bevindt zich aan de betonnen bunkerzijde en leidt via de beschermde toegang naar de gassluis en vervolgens het bunkerinterieur. Deze oorspronkelijke ingang is tegenwoordig dichtgemetseld.</p>
            <div class='techfacts'>
              <div>FUNCTIE</div><div>oorspronkelijke hoofdtoegang</div>
              <div>HUIDIGE STAAT</div><div>dichtgemetseld</div>
              <div>VERVOLGROUTE</div><div>gassluis → bunkerinterieur</div>
            </div>
            <div class='r616-dossier-actions'><button onclick="r616HotspotOpen('03')">OPEN GASSLUIS →</button></div>
          </div>
        </div>
        <style>@media(max-width:760px){#mb>div[style*='grid-template-columns']{grid-template-columns:1fr!important}}</style>
      `,true);
      return true;
    };
    patched.datasetMainEntranceFixed='1';
    window.r616HotspotOpen=patched;
    return true;
  }

  function init(){
    wireSloopVideo();
    protectAllVideos();
    if(!patchMainEntranceDossier()){
      let attempts=0;
      const timer=setInterval(()=>{
        if(patchMainEntranceDossier()||++attempts>30)clearInterval(timer);
      },150);
    }

    new MutationObserver(mutations=>{
      mutations.forEach(m=>m.addedNodes.forEach(node=>{
        if(node.nodeType===1)protectAllVideos(node);
      }));
    }).observe(document.body,{childList:true,subtree:true});
  }

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);
  else init();
})();
