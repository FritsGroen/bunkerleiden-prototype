from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = 'PLAN-CURSOR-ZOOM-20260818'
if marker in s:
    print('cursor zoom patch already present')
    raise SystemExit(0)

old = """function fitPlan(){let st=planstage,c=plancanvas;ps=Math.min(st.clientWidth/c.width,st.clientHeight/c.height);px=(st.clientWidth-c.width*ps)/2;py=(st.clientHeight-c.height*ps)/2;prot=0;planApply()}function planZoom(f){ps=Math.max(.05,Math.min(8,ps*f));planApply()}function planRot(d){prot=(prot+d)%360;planApply()}function wirePlan(){planstage.addEventListener('wheel',e=>{e.preventDefault();planZoom(e.deltaY<0?1.15:.87)},{passive:false});planstage.addEventListener('pointerdown',e=>{pdrag=true;plx=e.clientX;ply=e.clientY;planstage.setPointerCapture(e.pointerId)});planstage.addEventListener('pointermove',e=>{if(!pdrag)return;px+=e.clientX-plx;py+=e.clientY-ply;plx=e.clientX;ply=e.clientY;planApply()});planstage.addEventListener('pointerup',()=>pdrag=false)}"""

new = """function fitPlan(){let st=planstage,c=plancanvas;ps=Math.min(st.clientWidth/c.width,st.clientHeight/c.height);px=(st.clientWidth-c.width*ps)/2;py=(st.clientHeight-c.height*ps)/2;prot=0;planApply()}
/* PLAN-CURSOR-ZOOM-20260818 */
function planZoomAt(f,cx,cy){
  const st=planstage,r=st.getBoundingClientRect();
  const sx=cx-r.left,sy=cy-r.top;
  const old=ps,next=Math.max(.05,Math.min(8,old*f));
  if(next===old)return;
  const ratio=next/old;
  px=sx-(sx-px)*ratio;
  py=sy-(sy-py)*ratio;
  ps=next;planApply();
}
function planZoom(f){const r=planstage.getBoundingClientRect();planZoomAt(f,r.left+r.width/2,r.top+r.height/2)}
function planRot(d){prot=(prot+d)%360;planApply()}
function wirePlan(){
  const st=planstage;
  st.addEventListener('wheel',e=>{e.preventDefault();planZoomAt(e.deltaY<0?1.15:.87,e.clientX,e.clientY)},{passive:false});
  const pts=new Map();let pinchDist=0,pinchCenter=null;
  st.addEventListener('pointerdown',e=>{pts.set(e.pointerId,{x:e.clientX,y:e.clientY});st.setPointerCapture(e.pointerId);if(pts.size===1){pdrag=true;plx=e.clientX;ply=e.clientY}else if(pts.size===2){pdrag=false;const a=[...pts.values()];pinchDist=Math.hypot(a[0].x-a[1].x,a[0].y-a[1].y);pinchCenter={x:(a[0].x+a[1].x)/2,y:(a[0].y+a[1].y)/2}}});
  st.addEventListener('pointermove',e=>{if(!pts.has(e.pointerId))return;pts.set(e.pointerId,{x:e.clientX,y:e.clientY});if(pts.size===2){const a=[...pts.values()],d=Math.hypot(a[0].x-a[1].x,a[0].y-a[1].y),c={x:(a[0].x+a[1].x)/2,y:(a[0].y+a[1].y)/2};if(pinchDist>0)planZoomAt(d/pinchDist,c.x,c.y);px+=c.x-(pinchCenter?pinchCenter.x:c.x);py+=c.y-(pinchCenter?pinchCenter.y:c.y);pinchDist=d;pinchCenter=c;planApply();return}if(pdrag){px+=e.clientX-plx;py+=e.clientY-ply;plx=e.clientX;ply=e.clientY;planApply()}});
  const end=e=>{pts.delete(e.pointerId);if(pts.size===0){pdrag=false;pinchDist=0;pinchCenter=null}else if(pts.size===1){const q=[...pts.values()][0];pdrag=true;plx=q.x;ply=q.y;pinchDist=0;pinchCenter=null}};
  st.addEventListener('pointerup',end);st.addEventListener('pointercancel',end);
}"""

if old not in s:
    raise SystemExit('Expected plan viewer code not found; index.html left unchanged')

s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')
print('Patched plan viewer cursor/pinch zoom')
