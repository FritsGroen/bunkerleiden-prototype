/* R616 3D room pilot — 01 Schakelruimte — 2026-08-23 */
(function(){
  'use strict';
  const GOLD=0xe4b719;
  let roomBox=null, roomEdges=null, marker=null, selected=false, raf=0;
  let roomAnchor=null;

  function addStyles(){
    if(document.getElementById('room-hotspot-style')) return;
    const s=document.createElement('style');
    s.id='room-hotspot-style';
    s.textContent=`
      .room3d-marker{position:absolute;z-index:8;transform:translate(-50%,-100%);display:none;min-width:132px;padding:8px 10px;border:1px solid rgba(228,183,25,.78);border-left:3px solid #e4b719;border-radius:5px;background:rgba(5,7,5,.92);color:#eee7d4;font:800 9px/1.3 monospace;letter-spacing:.04em;text-align:left;cursor:pointer;box-shadow:0 8px 24px #0009;user-select:none;touch-action:manipulation}
      .room3d-marker b{display:block;color:#ffd84b;font-size:10px}.room3d-marker span{display:block;margin-top:2px;color:#aaa28e;font-weight:500}.room3d-marker:after{content:'';position:absolute;left:50%;bottom:-14px;width:1px;height:14px;background:#e4b719}.room3d-marker.hot,.room3d-marker.selected{background:rgba(52,43,8,.95);border-color:#ffd84b;box-shadow:0 0 26px rgba(228,183,25,.32)}
      #three .hotspot.room01-linked{transition:.16s;border-color:rgba(228,183,25,.55)}#three .hotspot.room01-linked.hot,#three .hotspot.room01-linked.selected{border-color:#e4b719;background:rgba(228,183,25,.10);box-shadow:inset 3px 0 0 #e4b719}
      .room-tech-intro{margin:18px 0 24px;padding:15px 16px;border:1px solid rgba(228,183,25,.38);border-left:3px solid #e4b719;border-radius:8px;background:linear-gradient(180deg,#111511,#0a0e0a)}.room-tech-intro h3{margin:3px 0 8px;color:#ffd84b}.room-tech-intro .room-tech-links{display:flex;gap:8px;flex-wrap:wrap;margin-top:11px}.room-tech-intro button{border:1px solid rgba(228,183,25,.45);background:#0b0f0b;color:#ffd84b;padding:9px 10px;border-radius:5px;font:800 9px monospace;cursor:pointer}
      @media(max-width:850px){.room3d-marker{min-width:118px;padding:7px 8px;font-size:8px}.room3d-marker b{font-size:9px}.room-tech-intro{margin-top:14px}}
    `;
    document.head.appendChild(s);
  }

  function linkedCard(){
    return [...document.querySelectorAll('#three .hotspot')].find(el=>/^\s*01\s*·\s*SCHAKELRUIMTE/i.test(el.textContent||''));
  }

  function setHot(on){
    if(roomBox) roomBox.visible=!!on;
    if(roomEdges) roomEdges.visible=!!on;
    if(marker) marker.classList.toggle('hot',!!on);
    const card=linkedCard(); if(card) card.classList.toggle('hot',!!on);
  }
  function setSelected(on){
    selected=!!on;
    if(marker) marker.classList.toggle('selected',selected);
    const card=linkedCard(); if(card) card.classList.toggle('selected',selected);
    setHot(selected);
  }

  function openRoomTech(){
    if(typeof go==='function') go('techniek');
    setTimeout(()=>{
      const target=document.getElementById('tech-sch-room');
      if(target){target.scrollIntoView({behavior:'smooth',block:'start'});target.animate([{outline:'1px solid rgba(228,183,25,0)'},{outline:'1px solid #e4b719'},{outline:'1px solid rgba(228,183,25,0)'}],{duration:1200});}
    },80);
  }

  function addTechRoom(){
    if(document.getElementById('tech-sch-room')) return;
    const tech=document.getElementById('techniek');
    if(!tech) return;
    const p=tech.querySelector(':scope > p.copy');
    const box=document.createElement('section');
    box.id='tech-sch-room';box.className='room-tech-intro';
    box.innerHTML=`<div class="k">RUIMTE 01 · 3D BUNKER</div><h3>SCHAKELRUIMTE</h3><p class="copy">Technische kernruimte van de R616. Hier komen de kabelinvoer en verdeling, ventilatie/overdruk, elektrische installatie en telefonie samen.</p><div class="room-tech-links"><button type="button" data-room-action="kev">KEV · KABELINVOER</button><button type="button" data-room-action="hes">HES 1.2 · VENTILATIE</button><button type="button" data-room-action="elektra">AEG · ELEKTRA</button></div>`;
    (p||tech.querySelector('h2')).insertAdjacentElement('afterend',box);
    box.addEventListener('click',e=>{
      const b=e.target.closest('[data-room-action]'); if(!b) return;
      const fn=window[b.dataset.roomAction]; if(typeof fn==='function') fn();
    });
  }

  function wireCard(){
    const card=linkedCard();
    if(!card||card.dataset.room01Wired) return;
    card.dataset.room01Wired='1';card.classList.add('room01-linked');
    card.removeAttribute('onclick');
    card.title='Hover/tap: toon Schakelruimte · dubbelklik: Techniek';
    card.addEventListener('mouseenter',()=>setHot(true));
    card.addEventListener('mouseleave',()=>{if(!selected)setHot(false)});
    card.addEventListener('click',()=>setSelected(!selected));
    card.addEventListener('dblclick',e=>{e.preventDefault();openRoomTech()});
  }

  function addMarker(wrap){
    if(marker) return;
    marker=document.createElement('button');marker.type='button';marker.className='room3d-marker';marker.setAttribute('aria-label','01 Schakelruimte');
    marker.innerHTML='<b>01 · SCHAKELRUIMTE</b><span>hover/tap = highlight · dubbelklik = techniek</span>';
    wrap.appendChild(marker);
    marker.addEventListener('mouseenter',()=>setHot(true));
    marker.addEventListener('mouseleave',()=>{if(!selected)setHot(false)});
    marker.addEventListener('click',e=>{e.stopPropagation();setSelected(!selected)});
    marker.addEventListener('dblclick',e=>{e.preventDefault();e.stopPropagation();openRoomTech()});
  }

  function buildRoom(){
    if(roomBox || typeof mesh3==='undefined' || !mesh3 || !mesh3.geometry || typeof scene3==='undefined' || !scene3) return false;
    const g=mesh3.geometry;
    if(!g.boundingBox) g.computeBoundingBox();
    const bb=g.boundingBox, size=new THREE.Vector3();bb.getSize(size);

    /* Pilotpositie: genormaliseerd binnen het STL-bounding-box. Hierdoor blijft de hotspot
       bruikbaar als het model later opnieuw wordt geëxporteerd met dezelfde oriëntatie. */
    const cx=bb.min.x + size.x*0.43;
    const cy=bb.min.y + size.y*0.35;
    const cz=bb.min.z + size.z*0.52;
    const sx=size.x*0.27, sy=size.y*0.48, sz=size.z*0.30;

    const mat=new THREE.MeshBasicMaterial({color:GOLD,transparent:true,opacity:.16,depthWrite:false,side:THREE.DoubleSide});
    roomBox=new THREE.Mesh(new THREE.BoxGeometry(sx,sy,sz),mat);roomBox.position.set(cx,cy,cz);roomBox.visible=false;roomBox.renderOrder=4;scene3.add(roomBox);
    const edgeGeo=new THREE.EdgesGeometry(roomBox.geometry);
    roomEdges=new THREE.LineSegments(edgeGeo,new THREE.LineBasicMaterial({color:0xffd84b,transparent:true,opacity:.85}));roomEdges.position.copy(roomBox.position);roomEdges.visible=false;roomEdges.renderOrder=5;scene3.add(roomEdges);
    roomAnchor=new THREE.Vector3(cx,cy+sy*.72,cz);
    return true;
  }

  function updateMarker(){
    raf=requestAnimationFrame(updateMarker);
    if(!marker||!roomAnchor||typeof camera3==='undefined'||typeof renderer3==='undefined'||!camera3||!renderer3) return;
    const p=roomAnchor.clone().project(camera3);
    const wrap=document.getElementById('modelwrap'); if(!wrap) return;
    const visible=p.z>-1&&p.z<1;
    marker.style.display=visible?'block':'none';
    if(!visible) return;
    marker.style.left=((p.x*.5+.5)*wrap.clientWidth)+'px';
    marker.style.top=((-p.y*.5+.5)*wrap.clientHeight)+'px';
  }

  function init(){
    addStyles();addTechRoom();wireCard();
    const wrap=document.getElementById('modelwrap');if(!wrap) return;
    addMarker(wrap);
    if(buildRoom()&&!raf) updateMarker();
  }

  let tries=0;
  const timer=setInterval(()=>{
    addTechRoom();wireCard();init();
    if(roomBox||++tries>80) clearInterval(timer);
  },200);
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init); else init();
})();
