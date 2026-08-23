/* R616 3D interactive rooms + POI configuration — contour volumes + dossier routing — 2026-08-23 */
(function(){
  'use strict';

  const GOLD=0xe4b719, GOLD2=0xffd84b;

  const ROOMS=[
    {id:'01',name:'SCHAKELRUIMTE',h:.47,poly:[
      [.4895,.2192],[.8040,.2192],[.8040,.4629],[.4895,.4629]
    ]},
    {id:'03',name:'GASSLUIS',h:.44,poly:[
      [.6699,.4764],[.7402,.4782],[.7402,.5101],[.8040,.5101],[.8040,.5930],
      [.7342,.5930],[.7342,.6280],[.6843,.6280],[.6843,.5930],[.6699,.5930]
    ]},
    {id:'04',name:'NOODUITGANG',h:.44,poly:[
      [.4366,.4052],[.4871,.4052],[.4871,.4438],[.4366,.4438]
    ]},
    {id:'05',name:'NAHKAMPFRAUM',h:.44,poly:[
      [.6735,.6280],[.7402,.6280],[.7402,.6605],[.8010,.6605],[.8040,.7735],
      [.7114,.7735],[.6729,.6802]
    ]},
    {id:'06',name:'ONDERHOUDSCORRIDOR',h:.44,poly:[
      [.3620,.2192],[.4366,.2192],[.4366,.7262],[.3620,.7262]
    ]},
    {id:'07',name:'TOEGANG NAAR TOBRUK',h:.44,poly:[
      [.0746,.6262],[.1419,.6274],[.1401,.6661],[.1155,.6661],[.1155,.7170],[.0746,.7170]
    ]},
    {id:'10',name:'HOOFDINGANG',h:.44,poly:[
      [.4883,.5187],[.6362,.5218],[.6356,.5924],[.5947,.5924],[.5767,.6065],
      [.5767,.7262],[.5262,.7262],[.5262,.5899],[.4883,.5899]
    ]}
  ];

  const POIS=[
    {id:'02',name:'HES',x:.652,z:.450,parent:'01'},
    {id:'08',name:'WT80K',x:.786,z:.450,parent:'01'},
    {id:'09',name:'KEV · VERBINDINGEN',x:.517,z:.243,parent:'01'}
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
      #three .hotspot.r616-linked{transition:.16s;cursor:pointer}#three .hotspot.r616-linked:hover{border-color:#e4b719!important}#three .hotspot.r616-linked.hot,#three .hotspot.r616-linked.selected{border-color:#e4b719!important;background:rgba(228,183,25,.10)!important;box-shadow:inset 3px 0 0 #e4b719}.r616-poi-card:before{content:'●';color:#ffd84b;text-shadow:0 0 8px #ffd84b;margin-right:6px}
      .r616-dossier-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}.r616-dossier-actions button{border:1px solid rgba(228,183,25,.55);background:#0b0f0b;color:#ffd84b;padding:9px 11px;border-radius:5px;font:800 9px monospace;cursor:pointer}.r616-dossier-actions button:hover{background:#e4b71912}
      @media(max-width:850px){.r616-label{min-width:124px;max-width:190px;padding:7px 8px;font-size:8px}.r616-label b{font-size:9px}}
    `;
    document.head.appendChild(s);
  }

  function worldXZ(x,z){
    return {x:bbox.min.x+size.x*z,z:bbox.max.z-size.z*x};
  }

  function polygonCentroid(poly){
    let a=0,cx=0,cz=0;
    for(let i=0;i<poly.length;i++){
      const p=poly[i],q=poly[(i+1)%poly.length];
      const cross=p[0]*q[1]-q[0]*p[1];
      a+=cross;cx+=(p[0]+q[0])*cross;cz+=(p[1]+q[1])*cross;
    }
    if(Math.abs(a)<1e-8){
      return {x:poly.reduce((s,p)=>s+p[0],0)/poly.length,z:poly.reduce((s,p)=>s+p[1],0)/poly.length};
    }
    a*=.5;
    return {x:cx/(6*a),z:cz/(6*a)};
  }

  function roomY(room){
    const sy=size.y*room.h;
    const yLow=bbox.min.y+size.y*.085;
    return {sy,yLow,cy:yLow+sy*.5,yTop:yLow+sy};
  }

  function makeRoomGeometry(room,yy){
    const shape=new THREE.Shape();
    room.poly.forEach((pt,i)=>{
      const w=worldXZ(pt[0],pt[1]);
      if(i===0)shape.moveTo(w.x,-w.z);else shape.lineTo(w.x,-w.z);
    });
    shape.closePath();
    const geo=new THREE.ExtrudeGeometry(shape,{depth:yy.sy,steps:1,bevelEnabled:false,curveSegments:1});
    geo.rotateX(-Math.PI/2);
    geo.translate(0,yy.yLow,0);
    geo.computeBoundingBox();
    geo.computeBoundingSphere();
    return geo;
  }

  function callGlobal(name){
    const fn=window[name];
    if(typeof fn==='function'){fn();return true}
    return false;
  }

  function showModal(html){
    if(typeof window.modal==='function'){window.modal(html,true);return true}
    return false;
  }

  function openHotspotRoute(id){
    id=String(id).padStart(2,'0');
    switch(id){
      case '01':
        return showModal(`<div class='k'>RUIMTEDOSSIER · R616</div><h2>01 · SCHAKELRUIMTE</h2><div class='techdetail'><img src="interieur-schakelruimte.jpg" alt="Schakelruimte"><div><p class='copy'>De centrale technische ruimte van de R616. Vanuit deze ruimte zijn de belangrijkste installaties voor kabelverbindingen, ventilatie, verwarming, elektra en telefonie te bekijken.</p><div class='r616-dossier-actions'><button onclick="r616HotspotOpen('09')">KEV & VERBINDINGEN</button><button onclick="r616HotspotOpen('02')">HES 1.2</button><button onclick="r616HotspotOpen('08')">WT80K</button><button onclick="elektra()">AEG / ELEKTRA</button><button onclick="ff33()">FF33</button></div></div></div>`) || false;
      case '02':
        return callGlobal('hes');
      case '03':
        return showModal(`<div class='k'>RUIMTEDOSSIER · BESCHERMDE TOEGANG</div><h2>03 · GASSLUIS</h2><div class='techdetail'><img src="gasssluis.jpg" alt="Gassluis"><div><p class='copy'>Gasdichte overgang tussen buitenwereld en het beschermde bunkerinterieur.</p><div class='techfacts'><div>FUNCTIE</div><div>beschermde overgang</div><div>LOCATIE</div><div>tussen hoofdtoegang en bunkerinterieur</div></div></div></div>`);
      case '04':
        return callGlobal('nooduitgang');
      case '05':
        return showModal(`<div class='k'>RUIMTEDOSSIER · R616</div><h2>05 · NAHKAMPFRAUM</h2><p class='copy'>De Nahkampfraum is de afzonderlijke ruimte voor de nabijverdediging van de bunker. In het 3D-model is de ruimte als eigen contour opgenomen.</p><div class='techfacts'><div>FUNCTIE</div><div>nabijverdediging</div><div>TYPE</div><div>afzonderlijke bunkerzone</div></div>`);
      case '06':
        return showModal(`<div class='k'>RUIMTEDOSSIER · TECHNISCHE ROUTE</div><h2>06 · ONDERHOUDSCORRIDOR</h2><div class='techdetail'><img src="huidige%20toegangsdeur%20onderhoudscorridor.jpg" alt="Toegangsdeur onderhoudscorridor"><div><p class='copy'>De onderhoudscorridor vormt de technische toegang en onderhoudsroute langs de installaties en nevenruimten van de bunker.</p><div class='techfacts'><div>FUNCTIE</div><div>technische toegang / onderhoud</div><div>WEERGAVE</div><div>lange smalle zone in het 3D-model</div></div></div></div>`);
      case '07':
        return showModal(`<div class='k'>RUIMTEDOSSIER · R616</div><h2>07 · TOEGANG NAAR TOBRUK</h2><p class='copy'>Deze zone vormt de toegang vanuit de bunker naar de aangebouwde Tobruk-positie.</p><div class='techfacts'><div>FUNCTIE</div><div>verbinding met Tobruk</div><div>LOCATIE</div><div>westelijke bunkerzijde</div></div>`);
      case '08':
        return showModal(`<div class='k'>TECHNISCH DOSSIER · VERWARMING</div><h2>08 · WT80K</h2><div class='techdetail'><img src="WT80K%20oven%20kachel.jpg" alt="WT80K bunkeroven"><div><p class='copy'>De WT80K is de bunkeroven / kachel voor verwarming van de ruimte.</p><div class='techfacts'><div>TYPE</div><div>WT80K</div><div>FUNCTIE</div><div>verwarming</div><div>LOCATIE R616</div><div>schakelruimte</div></div></div></div>`);
      case '09':
        return showModal(`<div class='k'>TECHNISCH DOSSIER · KABELS & VERBINDINGEN</div><h2>09 · KEV & VERBINDINGEN</h2><div class='techdetail'><img src="binnenzijde%20naar%20KEV%20kasten.jpg" alt="Interieur richting KEV-kasten"><div><p class='copy'>Hier komen de kabelinvoer, verdeling en interne communicatie samen. Vanuit dit dossier kun je direct door naar de afzonderlijke technische onderdelen.</p><div class='r616-dossier-actions'><button onclick="kev()">KEV · KABELENDVERSCHLUSS</button><button onclick="ff33()">FF33 · TELEFONIE</button><button onclick="sprachrohr()">SPRACHROHR</button></div></div></div>`);
      case '10':
        return showModal(`<div class='k'>RUIMTEDOSSIER · TOEGANG</div><h2>10 · HOOFDINGANG</h2><div class='techdetail'><img src="gevelaanszicht%20straatzijde.jpg" alt="Straatzijde R616"><div><p class='copy'>De hoofdtoegang vanaf de straatzijde naar het bunkerinterieur. Vanuit deze zone wordt de route door de gassluis naar de beschermde ruimten gevolgd.</p><div class='techfacts'><div>FUNCTIE</div><div>hoofdtoegang</div><div>VERVOLGROUTE</div><div>gassluis → bunkerinterieur</div></div><div class='r616-dossier-actions'><button onclick="r616HotspotOpen('03')">OPEN GASSLUIS →</button></div></div></div>`);
      default:
        if(typeof window.go==='function')window.go('techniek');
        return false;
    }
  }
  window.r616HotspotOpen=openHotspotRoute;

  function makeLabel(entry,type,wrap){
    const el=document.createElement('button');
    el.type='button';
    el.className='r616-label'+(type==='poi'?' poi':'');
    el.dataset.key=type+entry.id;
    el.innerHTML=`<b>${entry.id} · ${entry.name}</b><span>${type==='poi'?'point of interest · klik = dossier':'hover = ruimte tonen · klik = dossier'}</span>`;
    wrap.appendChild(el);
    el.addEventListener('mouseenter',()=>setHover(type+entry.id,true,'label'));
    el.addEventListener('mouseleave',()=>setHover(type+entry.id,false,'label'));
    el.addEventListener('click',e=>{e.preventDefault();e.stopPropagation();openHotspotRoute(entry.id)});
    return el;
  }

  function makeRoom(room,wrap){
    const yy=roomY(room),geo=makeRoomGeometry(room,yy);
    const detect=new THREE.Mesh(geo,new THREE.MeshBasicMaterial({transparent:true,opacity:0,depthWrite:false,depthTest:false,colorWrite:false,side:THREE.DoubleSide}));
    detect.userData.r616Key='room'+room.id;detect.renderOrder=80;scene3.add(detect);

    const glow=new THREE.Mesh(geo.clone(),new THREE.MeshBasicMaterial({color:GOLD,transparent:true,opacity:.17,depthWrite:false,depthTest:false,side:THREE.DoubleSide}));
    glow.visible=false;glow.renderOrder=100;scene3.add(glow);
    const edges=new THREE.LineSegments(new THREE.EdgesGeometry(glow.geometry,20),new THREE.LineBasicMaterial({color:GOLD2,transparent:true,opacity:.90,depthWrite:false,depthTest:false}));
    edges.renderOrder=101;glow.add(edges);

    const c=polygonCentroid(room.poly),p=worldXZ(c.x,c.z);
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
      card.title='Hover markeert in 3D · klik opent dossier';
      card.addEventListener('mouseenter',()=>setHover(key,true,'card'));
      card.addEventListener('mouseleave',()=>setHover(key,false,'card'));
      card.addEventListener('click',e=>{e.preventDefault();openHotspotRoute(data.id)});
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

  function wirePointer(){
    if(pointerWired||typeof renderer3==='undefined'||!renderer3||typeof camera3==='undefined'||!camera3)return;
    rendererCanvas=renderer3.domElement;
    const ray=new THREE.Raycaster(),pt=new THREE.Vector2();
    let downX=0,downY=0,moved=false,currentHover=null;

    function hit(e){
      const r=rendererCanvas.getBoundingClientRect();
      pt.x=((e.clientX-r.left)/r.width)*2-1;pt.y=-((e.clientY-r.top)/r.height)*2+1;ray.setFromCamera(pt,camera3);
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
    rendererCanvas.addEventListener('dblclick',e=>{const key=hit(e);if(key){e.preventDefault();const it=items.get(key);if(it)openHotspotRoute(it.data.id)}});
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
    console.info('R616 hotspots:',ROOMS.length,'ruimtes +',POIS.length,'POIs · dossier routing actief');return true;
  }

  function init(){addStyles();wireCards();build()}
  let tries=0;const timer=setInterval(()=>{init();if(items.size||++tries>100)clearInterval(timer)},180);
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
  new MutationObserver(()=>wireCards()).observe(document.body,{childList:true,subtree:true});
})();
