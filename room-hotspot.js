/* R616 3D interactive rooms + POI configuration — corrected plan mapping — 2026-08-23 */
(function(){
  'use strict';

  const GOLD=0xe4b719, GOLD2=0xffd84b;

  /* Coordinates are normalized to the FULL bunker footprint on the numbered historic plan.
     The STL local X/Z axes run opposite to that plan; worldXZ() handles that conversion. */
  const ROOMS=[
    {id:'01',name:'SCHAKELRUIMTE',        x:.647,z:.342,w:.315,d:.245,h:.47,tech:'SCHAKELRUIMTE'},
    {id:'03',name:'GASSLUIS',             x:.738,z:.544,w:.135,d:.115,h:.44,tech:'GASSLUIS'},
    {id:'04',name:'NOODUITGANG',          x:.469,z:.432,w:.055,d:.080,h:.44,tech:'NOODUITGANG'},
    {id:'05',name:'NAHKAMPFRAUM',         x:.764,z:.722,w:.095,d:.145,h:.44,tech:'NAHKAMPFRAUM'},
    {id:'06',name:'ONDERHOUDSCORRIDOR',   x:.424,z:.490,w:.128,d:.490,h:.44,tech:'ONDERHOUD'},
    {id:'07',name:'TOEGANG NAAR TOBRUK',  x:.105,z:.700,w:.070,d:.120,h:.44,tech:'TOBRUK'},
    {id:'10',name:'HOOFDINGANG',          x:.561,z:.550,w:.150,d:.100,h:.44,tech:'HOOFDINGANG'}
  ];

  const POIS=[
    {id:'02',name:'HES',                   x:.652,z:.450,parent:'01',tech:'HES'},
    {id:'08',name:'WT80K',                 x:.786,z:.450,parent:'01',tech:'WT80K'},
    {id:'09',name:'KEV · VERBINDINGEN',    x:.517,z:.243,parent:'01',tech:'KEV'}
  ];

  const items=new Map();
  let bbox=null,size=null,rendererCanvas=null,raf=0,pointerWired=false,selectedKey=null;

  function addStyles(){
    if(document.getElementById('r616-hotspot-style'))return;
    const s=document.createElement('style');
    s.id='r616-hotspot-style';
    s.textContent=`
      .r616-label{position:absolute;z-index:19;transform:translate(-50%,-100%);display:none;min-width:145px;max-width:235px;padding:8px 10px;border:1px solid rgba(228,183,25,.82);border-left:3px solid #e4b719;border-radius:6px;background:rgba(7,10,7,.94);color:#eee7d4;font:800 9px/1.3 monospace;letter-spacing:.035em;text-align:left;cursor:pointer;box-shadow:0 9px 26px #000a;user-select:none;touch-action:manipulation}
      .r616-label b{display:block;color:#ffd84b;font-size:10px}.r616-label span{display:block;margin-top:3px;color:#aaa28e;font-weight:500}.r616-label:after{content:'';position:absolute;left:50%;bottom:-15px;width:1px;height:15px;background:#e4b719}.r616-label.poi{border-color:rgba(255,216,75,.88);box-shadow:0 0 24px rgba(228,183,25,.28),0 9px 26px #0009}.r616-label.active{background:rgba(54,44,8,.96);border-color:#ffd84b}
      #three .hotspot.r616-linked{transition:.16s;cursor:pointer}#three .hotspot.r616-linked.hot,#three .hotspot.r616-linked.selected{border-color:#e4b719!important;background:rgba(228,183,25,.10)!important;box-shadow:inset 3px 0 0 #e4b719}.r616-poi-card:before{content:'●';color:#ffd84b;text-shadow:0 0 8px #ffd84b;margin-right:6px}
      @media(max-width:850px){.r616-label{min-width:124px;max-width:190px;padding:7px 8px;font-size:8px}.r616-label b{font-size:9px}}
    `;
    document.head.appendChild(s);
  }

  function worldXZ(x,z){
    /* Both STL horizontal axes are reversed relative to the supplied plan/top view. */
    return {x:bbox.max.x-size.x*x,z:bbox.min.z+size.z*z};
  }

  function roomY(room){
    const sy=size.y*room.h;
    const yLow=bbox.min.y+size.y*.085;
    return {sy,yLow,cy:yLow+sy*.5,yTop:yLow+sy};
  }

  function makeLabel(entry,type,wrap){
    const el=document.createElement('button');
    el.type='button';
    el.className='r616-label'+(type==='poi'?' poi':'');
    el.dataset.key=type+entry.id;
    el.innerHTML=`<b>${entry.id} · ${entry.name}</b><span>${type==='poi'?'point of interest · klik voor info':'hover = ruimte tonen · klik = vasthouden'}</span>`;
    wrap.appendChild(el);
    el.addEventListener('mouseenter',()=>setHover(type+entry.id,true,'label'));
    el.addEventListener('mouseleave',()=>setHover(type+entry.id,false,'label'));
    el.addEventListener('click',e=>{e.stopPropagation();toggleSelected(type+entry.id)});
    el.addEventListener('dblclick',e=>{e.preventDefault();e.stopPropagation();openTech(entry)});
    return el;
  }

  function makeRoom(room,wrap){
    const p=worldXZ(room.x,room.z),yy=roomY(room);
    const geo=new THREE.BoxGeometry(size.x*room.w,yy.sy,size.z*room.d);
    const detect=new THREE.Mesh(geo,new THREE.MeshBasicMaterial({transparent:true,opacity:0,depthWrite:false,depthTest:false,colorWrite:false,side:THREE.DoubleSide}));
    detect.position.set(p.x,yy.cy,p.z);detect.userData.r616Key='room'+room.id;detect.renderOrder=80;scene3.add(detect);

    const glow=new THREE.Mesh(geo.clone(),new THREE.MeshBasicMaterial({color:GOLD,transparent:true,opacity:.17,depthWrite:false,depthTest:false,side:THREE.DoubleSide}));
    glow.position.copy(detect.position);glow.visible=false;glow.renderOrder=100;scene3.add(glow);
    const edges=new THREE.LineSegments(new THREE.EdgesGeometry(glow.geometry),new THREE.LineBasicMaterial({color:GOLD2,transparent:true,opacity:.88,depthWrite:false,depthTest:false}));
    edges.renderOrder=101;glow.add(edges);

    const label=makeLabel(room,'room',wrap),key='room'+room.id;
    items.set(key,{key,type:'room',data:room,detect,glow,label,anchor:new THREE.Vector3(p.x,yy.yTop+size.y*.025,p.z),hover:false,labelHover:false,cardHover:false});
  }

  function makePoi(poi,wrap){
    const p=worldXZ(poi.x,poi.z);
    const parent=ROOMS.find(r=>r.id===poi.parent)||ROOMS[0];
    const yy=roomY(parent),y=yy.cy;
    const radius=Math.min(size.x,size.z)*.012;

    const core=new THREE.Mesh(new THREE.SphereGeometry(radius,18,12),new THREE.MeshBasicMaterial({color:GOLD2,transparent:true,opacity:.95,depthTest:false,depthWrite:false,blending:THREE.AdditiveBlending}));
    core.position.set(p.x,y,p.z);core.renderOrder=120;core.userData.r616Key='poi'+poi.id;scene3.add(core);

    const halo=new THREE.Mesh(new THREE.SphereGeometry(radius*2.7,18,12),new THREE.MeshBasicMaterial({color:GOLD,transparent:true,opacity:.18,depthTest:false,depthWrite:false,blending:THREE.AdditiveBlending}));
    halo.position.copy(core.position);halo.renderOrder=119;scene3.add(halo);

    /* Intentionally generous hit sphere: POIs must remain easy to target inside a room volume. */
    const hit=new THREE.Mesh(new THREE.SphereGeometry(radius*5.0,14,10),new THREE.MeshBasicMaterial({transparent:true,opacity:0,depthTest:false,depthWrite:false,colorWrite:false}));
    hit.position.copy(core.position);hit.userData.r616Key='poi'+poi.id;scene3.add(hit);

    const label=makeLabel(poi,'poi',wrap),key='poi'+poi.id;
    items.set(key,{key,type:'poi',data:poi,detect:hit,core,halo,label,anchor:new THREE.Vector3(p.x,y+radius*4.0,p.z),hover:false,labelHover:false,cardHover:false,phase:Math.random()*Math.PI*2});
  }

  function ownActive(it){return !!(it.hover||it.labelHover||it.cardHover||selectedKey===it.key)}
  function childPoiActive(roomItem){
    for(const child of items.values()){
      if(child.type==='poi'&&child.data.parent===roomItem.data.id&&ownActive(child))return true;
    }
    return false;
  }

  function refreshItem(it){
    const own=ownActive(it);
    const visual=(it.type==='room')?(own||childPoiActive(it)):own;
    if(it.type==='room'&&it.glow)it.glow.visible=visual;
    if(it.label)it.label.classList.toggle('active',own);
    const card=findCard(it.data.id);
    if(card){card.classList.toggle('hot',own&&selectedKey!==it.key);card.classList.toggle('selected',selectedKey===it.key)}
  }
  function refreshAll(){items.forEach(refreshItem)}

  function setHover(key,on,source){
    const it=items.get(key);if(!it)return;
    if(source==='label')it.labelHover=on;else if(source==='card')it.cardHover=on;else it.hover=on;
    refreshAll();
  }

  function toggleSelected(key){selectedKey=selectedKey===key?null:key;refreshAll()}

  function findCard(id){
    return [...document.querySelectorAll('#three .hotspot')].find(el=>new RegExp('^\\s*0?'+parseInt(id,10)+'\\s*·').test((el.textContent||'').trim()));
  }

  function wireCards(){
    const all=[...ROOMS.map(x=>({type:'room',data:x})),...POIS.map(x=>({type:'poi',data:x}))];
    all.forEach(({type,data})=>{
      const key=type+data.id,card=findCard(data.id);if(!card||card.dataset.r616Wired)return;
      card.dataset.r616Wired='1';card.classList.add('r616-linked');if(type==='poi')card.classList.add('r616-poi-card');card.removeAttribute('onclick');
      const heading=card.querySelector('b,strong,h1,h2,h3')||card.firstElementChild;if(heading)heading.textContent=data.id+' · '+data.name;
      card.title=type==='poi'?'Point of interest in de 3D-bunker':'Hover om deze ruimte in 3D te markeren';
      card.addEventListener('mouseenter',()=>setHover(key,true,'card'));
      card.addEventListener('mouseleave',()=>setHover(key,false,'card'));
      card.addEventListener('click',()=>toggleSelected(key));
      card.addEventListener('dblclick',e=>{e.preventDefault();openTech(data)});
    });

    if(!findCard('10')){
      const side=document.querySelector('#three .threed-right');
      const exemplar=side&&side.querySelector('.hotspot');
      if(side&&exemplar){
        const c=exemplar.cloneNode(true);c.removeAttribute('onclick');c.removeAttribute('data-r616-wired');
        const h=c.querySelector('b,strong,h1,h2,h3')||c.firstElementChild;if(h)h.textContent='10 · HOOFDINGANG';
        const p=c.querySelector('p');if(p)p.textContent='Hoofdtoegang vanaf de straatzijde naar het bunkerinterieur.';
        side.appendChild(c);setTimeout(wireCards,0);
      }
    }
  }

  function openTech(entry){
    if(typeof go==='function')go('techniek');
    setTimeout(()=>{
      const tech=document.getElementById('techniek');if(!tech)return;
      const needle=(entry.tech||entry.name).toUpperCase();
      const candidates=[...tech.querySelectorAll('h1,h2,h3,b,strong,.techpanel,.card')];
      const target=candidates.find(el=>(el.textContent||'').toUpperCase().includes(needle));
      (target||tech).scrollIntoView({behavior:'smooth',block:'start'});
      if(target){try{target.animate([{outline:'1px solid transparent'},{outline:'1px solid #e4b719'},{outline:'1px solid transparent'}],{duration:1200})}catch(_){}}
    },100);
  }

  function wirePointer(){
    if(pointerWired||typeof renderer3==='undefined'||!renderer3||typeof camera3==='undefined'||!camera3)return;
    rendererCanvas=renderer3.domElement;
    const ray=new THREE.Raycaster(),pt=new THREE.Vector2();
    let downX=0,downY=0,moved=false,currentHover=null;

    function hit(e){
      const r=rendererCanvas.getBoundingClientRect();
      pt.x=((e.clientX-r.left)/r.width)*2-1;pt.y=-((e.clientY-r.top)/r.height)*2+1;ray.setFromCamera(pt,camera3);

      /* POIs deliberately win over the larger room hit boxes they sit inside. */
      const poiTargets=[...items.values()].filter(i=>i.type==='poi').map(i=>i.detect).filter(Boolean);
      let hs=ray.intersectObjects(poiTargets,false);if(hs.length)return hs[0].object.userData.r616Key;
      const roomTargets=[...items.values()].filter(i=>i.type==='room').map(i=>i.detect).filter(Boolean);
      hs=ray.intersectObjects(roomTargets,false);return hs.length?hs[0].object.userData.r616Key:null;
    }

    rendererCanvas.addEventListener('pointerdown',e=>{downX=e.clientX;downY=e.clientY;moved=false});
    rendererCanvas.addEventListener('pointermove',e=>{
      if(Math.hypot(e.clientX-downX,e.clientY-downY)>6)moved=true;
      const key=hit(e);
      if(key!==currentHover){if(currentHover)setHover(currentHover,false,'scene');currentHover=key;if(currentHover)setHover(currentHover,true,'scene')}
    });
    rendererCanvas.addEventListener('pointerleave',()=>{if(currentHover)setHover(currentHover,false,'scene');currentHover=null});
    rendererCanvas.addEventListener('click',e=>{if(moved)return;const key=hit(e);if(key)toggleSelected(key);else{selectedKey=null;refreshAll()}});
    rendererCanvas.addEventListener('dblclick',e=>{const key=hit(e);if(key){e.preventDefault();const it=items.get(key);if(it)openTech(it.data)}});
    pointerWired=true;
  }

  function updateLabelsAndPulse(t){
    raf=requestAnimationFrame(updateLabelsAndPulse);
    if(typeof camera3==='undefined'||!camera3)return;
    const wrap=document.getElementById('modelwrap');if(!wrap)return;

    items.forEach(it=>{
      if(it.type==='poi'){
        const wave=(Math.sin(t*.0035+it.phase)+1)*.5;
        it.core.scale.setScalar(1+wave*.20);it.halo.scale.setScalar(.90+wave*.42);it.halo.material.opacity=.10+wave*.16;
      }
      /* A parent room may remain glowing for a child POI, but only the actively hovered item gets a label. */
      const show=ownActive(it);if(!it.label)return;
      const p=it.anchor.clone().project(camera3),onscreen=p.z>-1&&p.z<1;
      it.label.style.display=(show&&onscreen)?'block':'none';
      if(show&&onscreen){it.label.style.left=((p.x*.5+.5)*wrap.clientWidth)+'px';it.label.style.top=((-p.y*.5+.5)*wrap.clientHeight)+'px'}
    });
  }

  function build(){
    if(items.size||typeof mesh3==='undefined'||!mesh3||!mesh3.geometry||typeof scene3==='undefined'||!scene3)return false;
    const g=mesh3.geometry;if(!g.boundingBox)g.computeBoundingBox();bbox=g.boundingBox;size=new THREE.Vector3();bbox.getSize(size);
    const wrap=document.getElementById('modelwrap');if(!wrap)return false;
    ROOMS.forEach(r=>makeRoom(r,wrap));POIS.forEach(p=>makePoi(p,wrap));wireCards();wirePointer();
    if(!raf)raf=requestAnimationFrame(updateLabelsAndPulse);
    console.info('R616 hotspots:',ROOMS.length,'ruimtes +',POIS.length,'POIs');return true;
  }

  function init(){addStyles();wireCards();build()}
  let tries=0;const timer=setInterval(()=>{init();if(items.size||++tries>100)clearInterval(timer)},180);
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
  new MutationObserver(()=>wireCards()).observe(document.body,{childList:true,subtree:true});
})();
