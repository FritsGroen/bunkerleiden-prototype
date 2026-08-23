(function(){
  'use strict';

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

    const badge=card.querySelector('.badge');
    card.insertBefore(video,badge||null);
  }

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',wireSloopVideo);
  else wireSloopVideo();
})();
