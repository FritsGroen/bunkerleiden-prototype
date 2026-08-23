/* R616 3D room pilot — 01 Schakelruimte — plan/top-view aligned — 2026-08-23 */
(function(){
  'use strict';

  const GOLD=0xe4b719;
  const GOLD2=0xffd84b;

  /* Afgeleid uit de 2D-plattegrond + het 3D-bovenaanzicht in dezelfde oriëntatie.
     Straatzijde = onderkant van het plan. Alleen ruimte 01 is nu actief. */
  const ROOM={
    cxN:0.61,
    czN:0.41,
    sxN:0.29,
    szN:0.25,
    cyN:0.31,
    syN:0.42
  };

  let detectBox=null,glowBox=null,glowEdges=null,marker=null,roomAnchor=null,raf=0,pointerWired=false;
  const state={roomHover:false,markerHover:false,cardHover:false,selected:false};

  function isActive(){return !!(state.selected||state.roomHover||state.markerHover||state.cardHover)}

  function addStyles(){
    if(document.getElementById('room-hotspot-style'))return;
    const s=document.createElement('style');
    s.id='room-hotspot-style';
    s.textContent=`
      .room3d-marker{position:absolute;z-index:18;transform:translate(-50%,-100%);display:none;min-width:146px;padding:8px 10px;border:1px solid rgba(228,183,25,.85);border-left:3px solid #e4b719;border-radius:6px;background:rgba(7,10,7,.94);color:#eee7d4;font:800 9px/1.3 monospace;letter-spacing:.04em;text-align:left;cursor:pointer;box-shadow:0 10px 24px #000a;user-select:none;touch-action:manipulation}
      .room3d-marker b{display:block;color:#ffd84b;font-size:10px}.room3d-marker span{display:block;margin-top:2px;color:#aaa28e;font-weight:500}.room3d-marker:after{content:'';position:absolute;left:50%;bottom:-16px;width:1px;height:16px;background:#e4b719}.room3d-marker.hot,.room3d-marker.selected{background:rgba(52,43,8,.96);border-color:#ffd84b;box-shadow:0 0 28px rgba(228,183,25,.35)}
      #three .hotspot.room01-linked{transition:.16s;border-color:rgba(228,183,25,.55)}#three .hotspot.room01-linked.hot,#three .hotspot.room01-linked.selected{border-color:#e4b719;background:rgba(228,183,25,.10);box-shadow:inset 3px 0 0 #e4b719}
      .room-tech-intro{margin:18px 0 24px;padding:15px 16px;border:1px solid rgba(228,183,25,.38);border-left:3px solid #e4b719;border-radius:8px;background:linear-gradient(180deg,#111511,#0a0e0a)}.room-tech-intro h3{margin:3px 0 8px;color:#ffd84b}.room-tech-intro .room-tech-links{display:flex;gap:8px;flex-wrap:wrap;margin-top:11px}.room-tech-intro button{border:1px solid rgba(228,183,25,.45);background:#0b0f0b;color:#ffd84b;padding:9px 10px;border-radius:5px;font:800 9px monospace;cursor:pointer}
      @media(max-width:850px){.room3d-marker{min-width:124px;padding:7px 8px;font-size:8px}.room3d-marker b{font-size:9px}.room-tech-intro{margin-top:14px}}
    `;
    document.head.appendChild(s);
  }

  function linkedCard(){
    return [...document.querySelectorAll('#three .hotspot')].find(el=>/^\s*01\s*·\s*SCHAKELRUIMTE/i.test(el.textContent||''));
  }

  function updateVisualState(){
    const active=isActive();
    if(glowBox)glowBox.visible=active;
    if(glowEdges)glowEdges.visible=active;
    if(marker){
      marker.classList.toggle('hot',active&&!state.selected);
      marker.classList.toggle('selected',!!state.selected);
    }
    const card=linkedCard();
    if(card){
      card.classList.toggle('hot',active&&!state.selected);
      card.classList.toggle('selected',!!state.selected);
    }
  }

  function openRoomTech(){
    if(typeof go==='function')go('techniek');
    setTimeout(()=>{
      const target=document.getElementById('tech-sch-room');
      if(!target)return;
      target.scrollIntoView({behavior:'smooth',block:'start'});
      try{target.animate([{boxShadow:'0 0 0 rgba(228,183,25,0)'},{boxShadow:'0 0 0 1px rgba(228,183,25,.95), 0 0 24px rgba(228,183,25,.25)'},{boxShadow:'0 0 0 rgba(228,183,25,0)'}],{duration:1200})}catch(_){ }
    },90);
  }

  function addTechRoom(){
    if(document.getElementById('tech-sch-room'))return;
    const tech=document.getElementById('techniek');
    if(!tech)return;
    const p=tech.querySelector(':scope > p.copy');
    const box=document.createElement('section');
    box.id='tech-sch-room';box.className='room-tech-intro';
    box.innerHTML=`<div class="k">RUIMTE 01 · 3D BUNKER</div><h3>SCHAKELRUIMTE</h3><p class="copy">Technische kernruimte van de R616. Hier komen kabelinvoer en verdeling, ventilatie/overdruk, elektrische installatie en telefonie samen.</p><div class="room-tech-links"><button type="button" data-room-action="kev">KEV · KABELINVOER</button><button type="button" data-room-action="hes">HES 1.2 · VENTILATIE</button><button type="button" data-room-action="elektra">AEG · ELEKTRA</button></div>`;
    (p||tech.querySelector('h2')).insertAdjacentElement('afterend',box);
    box.addEventListener('click',e=>{
      const b=e.target.closest('[data-room-action]');if(!b)return;
      const fn=window[b.dataset.roomAction];if(typeof fn==='function')fn();
    });
  }

  function wireCard(){
    const card=linkedCard();
    if(!card||card.dataset.room01Wired)return;
    card.dataset.room01Wired='1';card.classList.add('room01-linked');card.removeAttribute('onclick');
    card.title='Hover/tap: toon Schakelruimte · dubbelklik: Techniek';
    card.addEventListener('mouseenter',()=>{state.cardHover=true;updateVisualState()});
    card.addEventListener('mouseleave',()=>{state.cardHover=false;updateVisualState()});
    card.addEventListener('click',()=>{state.selected=!state.selected;updateVisualState()});
    card.addEventListener('dblclick',e=>{e.preventDefault();openRoomTech()});
  }

  function addMarker(wrap){
    if(marker)return;
    marker=document.createElement('button');marker.type='button';marker.className='room3d-marker';marker.setAttribute('aria-label','01 Schakelruimte');
    marker.innerHTML='<b>01 · SCHAKELRUIMTE</b><span>klik = vasthouden · dubbelklik = techniek</span>';
    wrap.appendChild(marker);
    marker.addEventListener('mouseenter',()=>{state.markerHover=true;updateVisualState()});
    marker.addEventListener('mouseleave',()=>{state.markerHover=false;updateVisualState()});
    marker.addEventListener('click',e=>{e.stopPropagation();state.selected=!state.selected;updateVisualState()});
    marker.addEventListener('dblclick',e=>{e.preventDefault();e.stopPropagation();openRoomTech()});
  }

  function buildRoom(){
    if(detectBox||typeof mesh3==='undefined'||!mesh3||!mesh3.geometry||typeof scene3==='undefined'||!scene3)return false;
    const g=mesh3.geometry;if(!g.boundingBox)g.computeBoundingBox();
    const bb=g.boundingBox,size=new THREE.Vector3();bb.getSize(size);

    const cx=bb.min.x+size.x*ROOM.cxN;
    const cz=bb.min.z+size.z*ROOM.czN;
    const cy=bb.min.y+size.y*ROOM.cyN;
    const sx=size.x*ROOM.sxN,sy=size.y*ROOM.syN,sz=size.z*ROOM.szN;

    detectBox=new THREE.Mesh(new THREE.BoxGeometry(sx,sy,sz),new THREE.MeshBasicMaterial({transparent:true,opacity:0,depthWrite:false,depthTest:false}));
    detectBox.position.set(cx,cy,cz);detectBox.renderOrder=60;scene3.add(detectBox);

    glowBox=new THREE.Mesh(new THREE.BoxGeometry(sx,sy,sz),new THREE.MeshBasicMaterial({color:GOLD,transparent:true,opacity:.20,side:THREE.DoubleSide,depthWrite:false,depthTest:false}));
    glowBox.position.copy(detectBox.position);glowBox.visible=false;glowBox.renderOrder=80;scene3.add(glowBox);

    glowEdges=new THREE.LineSegments(new THREE.EdgesGeometry(glowBox.geometry),new THREE.LineBasicMaterial({color:GOLD2,transparent:true,opacity:.95,depthTest:false,depthWrite:false}));
    glowEdges.position.copy(glowBox.position);glowEdges.visible=false;glowEdges.renderOrder=81;scene3.add(glowEdges);

    roomAnchor=new THREE.Vector3(cx,cy+sy*.72,cz);
    return true;
  }

  function updateMarker(){
    raf=requestAnimationFrame(updateMarker);
    if(!marker||!roomAnchor||typeof camera3==='undefined'||!camera3||typeof renderer3==='undefined'||!renderer3)return;
    const wrap=document.getElementById('modelwrap');if(!wrap)return;
    const p=roomAnchor.clone().project(camera3),onscreen=p.z>-1&&p.z<1,show=isActive()&&onscreen;
    marker.style.display=show?'block':'none';
    if(!show)return;
    marker.style.left=((p.x*.5+.5)*wrap.clientWidth)+'px';
    marker.style.top=((-p.y*.5+.5)*wrap.clientHeight)+'px';
  }

  function wirePointer(){
    if(pointerWired||typeof renderer3==='undefined'||!renderer3||typeof camera3==='undefined'||!camera3||!detectBox)return;
    const canvas=renderer3.domElement,raycaster=new THREE.Raycaster(),pointer=new THREE.Vector2();
    const hitFromEvent=e=>{
      const r=canvas.getBoundingClientRect();
      pointer.x=((e.clientX-r.left)/r.width)*2-1;pointer.y=-((e.clientY-r.top)/r.height)*2+1;
      raycaster.setFromCamera(pointer,camera3);
      return raycaster.intersectObject(detectBox,false).length>0;
    };
    canvas.addEventListener('pointermove',e=>{state.roomHover=hitFromEvent(e);updateVisualState()});
    canvas.addEventListener('pointerleave',()=>{state.roomHover=false;updateVisualState()});
    canvas.addEventListener('click',e=>{
      if(hitFromEvent(e))state.selected=!state.selected;
      else if(!state.markerHover&&!state.cardHover)state.selected=false;
      updateVisualState();
    });
    canvas.addEventListener('dblclick',e=>{if(hitFromEvent(e)){e.preventDefault();openRoomTech()}});
    pointerWired=true;
  }

  function init(){
    addStyles();addTechRoom();wireCard();
    const wrap=document.getElementById('modelwrap');if(!wrap)return;
    addMarker(wrap);
    if(buildRoom()){
      wirePointer();
      if(!raf)updateMarker();
    }
  }

  let tries=0;
  const timer=setInterval(()=>{
    addTechRoom();wireCard();init();
    const ready=!!detectBox&&typeof renderer3!=='undefined'&&!!renderer3&&typeof camera3!=='undefined'&&!!camera3;
    if(ready||++tries>100)clearInterval(timer);
  },180);

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
