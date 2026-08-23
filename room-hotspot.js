/* R616 3D room pilot — 01 Schakelruimte — automatic wall/room detection — 2026-08-23 */
(function(){
  'use strict';

  const GOLD=0xe4b719, GOLD2=0xffd84b;
  const GRID=230;
  const TARGET={xFromLeft:.62,zFromTop:.35};
  const state={roomHover:false,markerHover:false,cardHover:false,selected:false};

  let detectMesh=null,glowMesh=null,marker=null,roomAnchor=null,raf=0,pointerWired=false;

  function active(){return !!(state.roomHover||state.markerHover||state.cardHover||state.selected)}

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

  function linkedCard(){return [...document.querySelectorAll('#three .hotspot')].find(el=>/^\s*01\s*·\s*SCHAKELRUIMTE/i.test(el.textContent||''))}

  function updateVisual(){
    const on=active();
    if(glowMesh)glowMesh.visible=on;
    if(marker){marker.classList.toggle('hot',on&&!state.selected);marker.classList.toggle('selected',state.selected)}
    const card=linkedCard();
    if(card){card.classList.toggle('hot',on&&!state.selected);card.classList.toggle('selected',state.selected)}
  }

  function openRoomTech(){
    if(typeof go==='function')go('techniek');
    setTimeout(()=>{
      const t=document.getElementById('tech-sch-room');
      if(!t)return;
      t.scrollIntoView({behavior:'smooth',block:'start'});
      try{t.animate([{outline:'1px solid transparent'},{outline:'1px solid #e4b719'},{outline:'1px solid transparent'}],{duration:1200})}catch(_){ }
    },90);
  }

  function addTechRoom(){
    if(document.getElementById('tech-sch-room'))return;
    const tech=document.getElementById('techniek');if(!tech)return;
    const p=tech.querySelector(':scope > p.copy');
    const box=document.createElement('section');
    box.id='tech-sch-room';box.className='room-tech-intro';
    box.innerHTML=`<div class="k">RUIMTE 01 · 3D BUNKER</div><h3>SCHAKELRUIMTE</h3><p class="copy">Technische kernruimte van de R616. Hier komen kabelinvoer en verdeling, ventilatie/overdruk, elektrische installatie en telefonie samen.</p><div class="room-tech-links"><button type="button" data-room-action="kev">KEV · KABELINVOER</button><button type="button" data-room-action="hes">HES 1.2 · VENTILATIE</button><button type="button" data-room-action="elektra">AEG · ELEKTRA</button></div>`;
    (p||tech.querySelector('h2')).insertAdjacentElement('afterend',box);
    box.addEventListener('click',e=>{const b=e.target.closest('[data-room-action]');if(!b)return;const fn=window[b.dataset.roomAction]||globalThis[b.dataset.roomAction];if(typeof fn==='function')fn()});
  }

  function wireCard(){
    const card=linkedCard();if(!card||card.dataset.room01Wired)return;
    card.dataset.room01Wired='1';card.classList.add('room01-linked');card.removeAttribute('onclick');
    card.title='Hover/tap: toon Schakelruimte · dubbelklik: Techniek';
    card.addEventListener('mouseenter',()=>{state.cardHover=true;updateVisual()});
    card.addEventListener('mouseleave',()=>{state.cardHover=false;updateVisual()});
    card.addEventListener('click',()=>{state.selected=!state.selected;updateVisual()});
    card.addEventListener('dblclick',e=>{e.preventDefault();openRoomTech()});
  }

  function addMarker(wrap){
    if(marker)return;
    marker=document.createElement('button');marker.type='button';marker.className='room3d-marker';marker.setAttribute('aria-label','01 Schakelruimte');
    marker.innerHTML='<b>01 · SCHAKELRUIMTE</b><span>klik = vasthouden · dubbelklik = techniek</span>';
    wrap.appendChild(marker);
    marker.addEventListener('mouseenter',()=>{state.markerHover=true;updateVisual()});
    marker.addEventListener('mouseleave',()=>{state.markerHover=false;updateVisual()});
    marker.addEventListener('click',e=>{e.stopPropagation();state.selected=!state.selected;updateVisual()});
    marker.addEventListener('dblclick',e=>{e.preventDefault();e.stopPropagation();openRoomTech()});
  }

  function rasterLine(blocked,x0,z0,x1,z1,r){
    const dx=x1-x0,dz=z1-z0,steps=Math.max(1,Math.ceil(Math.max(Math.abs(dx),Math.abs(dz))*1.6));
    for(let s=0;s<=steps;s++){
      const t=s/steps,x=Math.round(x0+dx*t),z=Math.round(z0+dz*t);
      for(let yy=-r;yy<=r;yy++)for(let xx=-r;xx<=r;xx++){
        if(xx*xx+yy*yy>r*r)continue;
        const gx=x+xx,gz=z+yy;if(gx>=0&&gx<GRID&&gz>=0&&gz<GRID)blocked[gz*GRID+gx]=1;
      }
    }
  }

  function sliceWalls(g,bb,size){
    const pos=g.getAttribute('position');
    const ys=[.30,.46,.60].map(n=>bb.min.y+size.y*n);
    const blocked=new Uint8Array(GRID*GRID);
    const toGX=x=>(x-bb.min.x)/size.x*(GRID-1);
    const toGZ=z=>(bb.max.z-z)/size.z*(GRID-1);
    const eps=size.y*1e-6;

    function cross(ax,ay,az,bx,by,bz,y,out){
      const da=ay-y,db=by-y;
      if(Math.abs(da)<eps&&Math.abs(db)<eps)return;
      if(!((da<0&&db>0)||(da>0&&db<0)))return;
      const t=da/(da-db);out.push([ax+(bx-ax)*t,az+(bz-az)*t]);
    }

    for(let i=0;i<pos.count;i+=3){
      const ax=pos.getX(i),ay=pos.getY(i),az=pos.getZ(i),bx=pos.getX(i+1),by=pos.getY(i+1),bz=pos.getZ(i+1),cx=pos.getX(i+2),cy=pos.getY(i+2),cz=pos.getZ(i+2);
      const minY=Math.min(ay,by,cy),maxY=Math.max(ay,by,cy);
      for(const y of ys){
        if(y<=minY||y>=maxY)continue;
        const pts=[];cross(ax,ay,az,bx,by,bz,y,pts);cross(bx,by,bz,cx,cy,cz,y,pts);cross(cx,cy,cz,ax,ay,az,y,pts);
        if(pts.length===2)rasterLine(blocked,toGX(pts[0][0]),toGZ(pts[0][1]),toGX(pts[1][0]),toGZ(pts[1][1]),2);
      }
    }
    /* Seal narrow wall openings (mainly doorways) in the analysis raster only.
       This does not change the STL; it lets the flood-fill recover complete rooms. */
    const MAX_GAP=Math.round(GRID*.060);
    for(let z=0;z<GRID;z++){
      let last=-1;
      for(let x=0;x<GRID;x++){
        if(!blocked[z*GRID+x])continue;
        if(last>=0&&x-last>1&&x-last-1<=MAX_GAP){
          for(let q=last+1;q<x;q++)blocked[z*GRID+q]=1;
        }
        last=x;
      }
    }
    for(let x=0;x<GRID;x++){
      let last=-1;
      for(let z=0;z<GRID;z++){
        if(!blocked[z*GRID+x])continue;
        if(last>=0&&z-last>1&&z-last-1<=MAX_GAP){
          for(let q=last+1;q<z;q++)blocked[q*GRID+x]=1;
        }
        last=z;
      }
    }
    return blocked;
  }

  function collectComponents(blocked){
    const seen=new Uint8Array(blocked.length),comps=[];
    const qx=new Int16Array(blocked.length),qz=new Int16Array(blocked.length);
    const dirs=[[1,0],[-1,0],[0,1],[0,-1]];

    function flood(sx,sz,store){
      let h=0,t=0;qx[t]=sx;qz[t++]=sz;seen[sz*GRID+sx]=1;
      const cells=[];let sumX=0,sumZ=0,minX=GRID,minZ=GRID,maxX=0,maxZ=0,touches=false;
      while(h<t){
        const x=qx[h],z=qz[h++];
        if(store){const idx=z*GRID+x;cells.push(idx);sumX+=x;sumZ+=z;minX=Math.min(minX,x);minZ=Math.min(minZ,z);maxX=Math.max(maxX,x);maxZ=Math.max(maxZ,z)}
        if(x===0||z===0||x===GRID-1||z===GRID-1)touches=true;
        for(const d of dirs){const nx=x+d[0],nz=z+d[1];if(nx<0||nz<0||nx>=GRID||nz>=GRID)continue;const ni=nz*GRID+nx;if(blocked[ni]||seen[ni])continue;seen[ni]=1;qx[t]=nx;qz[t++]=nz}
      }
      return store?{cells,area:cells.length,cx:sumX/cells.length,cz:sumZ/cells.length,minX,minZ,maxX,maxZ,touches}:null;
    }

    for(let x=0;x<GRID;x++){if(!blocked[x]&&!seen[x])flood(x,0,false);const b=(GRID-1)*GRID+x;if(!blocked[b]&&!seen[b])flood(x,GRID-1,false)}
    for(let z=0;z<GRID;z++){const l=z*GRID;if(!blocked[l]&&!seen[l])flood(0,z,false);const r=z*GRID+GRID-1;if(!blocked[r]&&!seen[r])flood(GRID-1,z,false)}

    for(let z=1;z<GRID-1;z++)for(let x=1;x<GRID-1;x++){
      const idx=z*GRID+x;if(blocked[idx]||seen[idx])continue;const c=flood(x,z,true);if(c.area>90)comps.push(c);
    }
    return comps;
  }

  function chooseRoom(comps){
    if(!comps.length)return null;
    const tx=TARGET.xFromLeft*(GRID-1),tz=TARGET.zFromTop*(GRID-1);
    const targetArea=GRID*GRID*.050;
    const candidates=[];
    for(const c of comps){
      const w=c.maxX-c.minX+1,h=c.maxZ-c.minZ+1;
      const short=Math.max(1,Math.min(w,h)),long=Math.max(w,h);
      const aspect=long/short,compact=c.area/(w*h);
      const areaFrac=c.area/(GRID*GRID);
      /* Schakelruimte is een flinke rechthoekige kamer; reject shafts/corridors. */
      if(areaFrac<.012||areaFrac>.14)continue;
      if(aspect>3.15||short<GRID*.055)continue;
      const dist=Math.hypot(c.cx-tx,c.cz-tz);
      const aspectPenalty=Math.abs(Math.log(aspect/1.72))*17;
      const areaPenalty=Math.abs(Math.log(c.area/targetArea))*8;
      const compactPenalty=Math.max(0,.48-compact)*18;
      const score=dist*.72+aspectPenalty+areaPenalty+compactPenalty;
      candidates.push({c,score,aspect,areaFrac,compact});
    }
    candidates.sort((a,b)=>a.score-b.score);
    console.info('R616 kamer-kandidaten',candidates.slice(0,8).map(v=>({score:+v.score.toFixed(1),aspect:+v.aspect.toFixed(2),area:+v.areaFrac.toFixed(3),cx:+(v.c.cx/(GRID-1)).toFixed(2),cz:+(v.c.cz/(GRID-1)).toFixed(2)})));
    if(candidates.length)return candidates[0].c;
    /* Conservative fallback: least corridor-like component near target. */
    return comps.slice().sort((a,b)=>{
      const aw=a.maxX-a.minX+1,ah=a.maxZ-a.minZ+1,bw=b.maxX-b.minX+1,bh=b.maxZ-b.minZ+1;
      const aa=Math.max(aw,ah)/Math.max(1,Math.min(aw,ah)),ba=Math.max(bw,bh)/Math.max(1,Math.min(bw,bh));
      return (Math.hypot(a.cx-tx,a.cz-tz)+aa*12)-(Math.hypot(b.cx-tx,b.cz-tz)+ba*12);
    })[0];
  }

  function contourFromComponent(comp){
    const member=new Uint8Array(GRID*GRID);for(const idx of comp.cells)member[idx]=1;
    const edges=[];
    function add(ax,az,bx,bz){edges.push([[ax,az],[bx,bz]])}
    for(const idx of comp.cells){
      const z=Math.floor(idx/GRID),x=idx-z*GRID;
      if(z===0||!member[(z-1)*GRID+x])add(x,z,x+1,z);
      if(x===GRID-1||!member[z*GRID+x+1])add(x+1,z,x+1,z+1);
      if(z===GRID-1||!member[(z+1)*GRID+x])add(x+1,z+1,x,z+1);
      if(x===0||!member[z*GRID+x-1])add(x,z+1,x,z);
    }
    const byStart=new Map();
    const key=p=>p[0]+','+p[1];
    edges.forEach((e,i)=>{const k=key(e[0]);if(!byStart.has(k))byStart.set(k,[]);byStart.get(k).push(i)});
    const used=new Uint8Array(edges.length),loops=[];
    for(let i=0;i<edges.length;i++){
      if(used[i])continue;const loop=[];let ei=i,start=edges[ei][0],cur=start,guard=0;
      while(ei!=null&&!used[ei]&&guard++<edges.length+10){used[ei]=1;const e=edges[ei];loop.push(e[0]);cur=e[1];if(cur[0]===start[0]&&cur[1]===start[1])break;const cand=(byStart.get(key(cur))||[]).find(j=>!used[j]);ei=cand==null?null:cand}
      if(loop.length>8)loops.push(loop);
    }
    if(!loops.length)return null;
    function area(poly){let a=0;for(let i=0,j=poly.length-1;i<poly.length;j=i++)a+=poly[j][0]*poly[i][1]-poly[i][0]*poly[j][1];return a/2}
    let poly=loops.sort((a,b)=>Math.abs(area(b))-Math.abs(area(a)))[0];
    const simple=[];
    for(let i=0;i<poly.length;i++){
      const p0=poly[(i-1+poly.length)%poly.length],p1=poly[i],p2=poly[(i+1)%poly.length];
      if((p0[0]===p1[0]&&p1[0]===p2[0])||(p0[1]===p1[1]&&p1[1]===p2[1]))continue;simple.push(p1);
    }
    return simple;
  }

  function buildPrism(poly,bb,size){
    const shape=new THREE.Shape();
    const modelPts=poly.map(p=>new THREE.Vector2(bb.min.x+(p[0]/GRID)*size.x,bb.max.z-(p[1]/GRID)*size.z));
    if(modelPts.length<3)return false;
    shape.moveTo(modelPts[0].x,modelPts[0].y);for(let i=1;i<modelPts.length;i++)shape.lineTo(modelPts[i].x,modelPts[i].y);shape.closePath();

    const yLow=bb.min.y+size.y*.08,yHigh=bb.min.y+size.y*.61,depth=yHigh-yLow;
    const geo=new THREE.ExtrudeGeometry(shape,{depth,bevelEnabled:false,curveSegments:1,steps:1});
    const p=geo.getAttribute('position');
    for(let i=0;i<p.count;i++){const x=p.getX(i),z=p.getY(i),dy=p.getZ(i);p.setXYZ(i,x,yLow+dy,z)}
    p.needsUpdate=true;geo.computeBoundingBox();geo.computeBoundingSphere();

    detectMesh=new THREE.Mesh(geo,new THREE.MeshBasicMaterial({transparent:true,opacity:0,depthWrite:false,depthTest:false,colorWrite:false,side:THREE.DoubleSide}));
    detectMesh.renderOrder=90;scene3.add(detectMesh);
    glowMesh=new THREE.Mesh(geo.clone(),new THREE.MeshBasicMaterial({color:GOLD,transparent:true,opacity:.18,depthWrite:false,depthTest:false,side:THREE.DoubleSide}));
    glowMesh.visible=false;glowMesh.renderOrder=100;scene3.add(glowMesh);
    const eg=new THREE.EdgesGeometry(geo,20);
    const lines=new THREE.LineSegments(eg,new THREE.LineBasicMaterial({color:GOLD2,transparent:true,opacity:.88,depthWrite:false,depthTest:false}));
    lines.renderOrder=101;glowMesh.add(lines);

    let sx=0,sz=0;for(const q of modelPts){sx+=q.x;sz+=q.y}roomAnchor=new THREE.Vector3(sx/modelPts.length,yHigh+size.y*.03,sz/modelPts.length);
    console.info('R616 room detector: Schakelruimte contourpunten',poly.length);
    return true;
  }

  function buildDetectedRoom(){
    if(detectMesh||typeof mesh3==='undefined'||!mesh3||!mesh3.geometry||typeof scene3==='undefined'||!scene3)return false;
    const g=mesh3.geometry;if(!g.boundingBox)g.computeBoundingBox();const bb=g.boundingBox,size=new THREE.Vector3();bb.getSize(size);
    try{
      const blocked=sliceWalls(g,bb,size),comps=collectComponents(blocked),room=chooseRoom(comps);
      if(!room)throw new Error('geen afgesloten ruimte gevonden');
      const poly=contourFromComponent(room);if(!poly)throw new Error('geen kamercontour gevonden');
      return buildPrism(poly,bb,size);
    }catch(err){console.warn('R616 room detector mislukt',err);return false}
  }

  function wirePointer(){
    if(pointerWired||!detectMesh||typeof renderer3==='undefined'||!renderer3||typeof camera3==='undefined'||!camera3)return;
    const canvas=renderer3.domElement,ray=new THREE.Raycaster(),pt=new THREE.Vector2();let downX=0,downY=0,moved=false;
    function hit(e){const r=canvas.getBoundingClientRect();pt.x=((e.clientX-r.left)/r.width)*2-1;pt.y=-((e.clientY-r.top)/r.height)*2+1;ray.setFromCamera(pt,camera3);return ray.intersectObject(detectMesh,false).length>0}
    canvas.addEventListener('pointerdown',e=>{downX=e.clientX;downY=e.clientY;moved=false});
    canvas.addEventListener('pointermove',e=>{if(Math.hypot(e.clientX-downX,e.clientY-downY)>6)moved=true;state.roomHover=hit(e);updateVisual()});
    canvas.addEventListener('pointerleave',()=>{state.roomHover=false;updateVisual()});
    canvas.addEventListener('click',e=>{if(moved)return;if(hit(e))state.selected=!state.selected;else if(!state.markerHover&&!state.cardHover)state.selected=false;updateVisual()});
    canvas.addEventListener('dblclick',e=>{if(hit(e)){e.preventDefault();openRoomTech()}});
    pointerWired=true;
  }

  function updateMarker(){
    raf=requestAnimationFrame(updateMarker);
    if(!marker||!roomAnchor||typeof camera3==='undefined'||!camera3)return;
    const wrap=document.getElementById('modelwrap');if(!wrap)return;const p=roomAnchor.clone().project(camera3),onscreen=p.z>-1&&p.z<1,show=active()&&onscreen;
    marker.style.display=show?'block':'none';if(!show)return;marker.style.left=((p.x*.5+.5)*wrap.clientWidth)+'px';marker.style.top=((-p.y*.5+.5)*wrap.clientHeight)+'px';
  }

  function init(){
    addStyles();addTechRoom();wireCard();const wrap=document.getElementById('modelwrap');if(!wrap)return;addMarker(wrap);
    if(buildDetectedRoom()){wirePointer();if(!raf)updateMarker();updateVisual()}
  }

  let tries=0;const timer=setInterval(()=>{addTechRoom();wireCard();init();if(detectMesh||++tries>100)clearInterval(timer)},180);
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
