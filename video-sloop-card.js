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

  function init(){
    wireSloopVideo();
    protectAllVideos();

    new MutationObserver(mutations=>{
      mutations.forEach(m=>m.addedNodes.forEach(node=>{
        if(node.nodeType===1)protectAllVideos(node);
      }));
    }).observe(document.body,{childList:true,subtree:true});
  }

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);
  else init();
})();
