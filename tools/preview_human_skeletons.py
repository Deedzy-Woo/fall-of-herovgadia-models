"""Create offline Three.js inspection viewers and capture real rendered previews."""
from pathlib import Path
import re,json,asyncio
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'human_skeletons'
source=(ROOT/'dead_harpy/dead_harpy_viewer.html').read_text();scripts=re.findall(r'<script[^>]*>(.*?)</script>',source,re.S)
JS=r'''
const scene=new THREE.Scene();scene.background=new THREE.Color(0x242a29);
const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setPixelRatio(devicePixelRatio);renderer.setSize(innerWidth,innerHeight);document.body.appendChild(renderer.domElement);
const camera=new THREE.PerspectiveCamera(32,innerWidth/innerHeight,.1,500);const controls=new THREE.OrbitControls(camera,renderer.domElement);controls.enableDamping=false;
scene.add(new THREE.AmbientLight(0xffffff,.67));let sun=new THREE.DirectionalLight(0xffffff,.42);sun.position.set(-25,55,-35);scene.add(sun);let fill=new THREE.DirectionalLight(0xc8d8de,.18);fill.position.set(25,15,30);scene.add(fill);
const group=new THREE.Group();scene.add(group);const texture=new THREE.TextureLoader().load(M.textures[0].source,draw);texture.magFilter=THREE.NearestFilter;texture.minFilter=THREE.NearestFilter;
const faces=['east','west','up','down','south','north'];const materials=[];
for(const e of M.elements){const size=e.to.map((v,i)=>v-e.from[i]);const geo=new THREE.BoxGeometry(...size);for(let k=0;k<6;k++){let uv=e.faces[faces[k]].uv,arr=geo.attributes.uv;const a=[[uv[0]/32,1-uv[1]/32],[uv[2]/32,1-uv[1]/32],[uv[0]/32,1-uv[3]/32],[uv[2]/32,1-uv[3]/32]];for(let j=0;j<4;j++)arr.setXY(k*4+j,...a[j]);}const mat=new THREE.MeshLambertMaterial({map:texture});materials.push(mat);const mesh=new THREE.Mesh(geo,mat);mesh.position.set(...e.from.map((v,i)=>(v+e.to[i])/2-e.origin[i]));mesh.name=e.name;const pivot=new THREE.Group();pivot.position.set(...e.origin);pivot.rotation.set(...e.rotation.map(v=>v*Math.PI/180));pivot.add(mesh);group.add(pivot);}
const box=new THREE.Box3().setFromObject(group);const centre=box.getCenter(new THREE.Vector3());const span=box.getSize(new THREE.Vector3());const dist=Math.max(span.x,span.y,span.z)*2.65;
const context=new THREE.Group();scene.add(context);const floorY=M.name==='hanging_skeleton'?box.min.y-8:0;
const floor=new THREE.Mesh(new THREE.BoxGeometry(56,.8,56),new THREE.MeshLambertMaterial({color:0x414743}));floor.position.set(8,floorY-.45,8);context.add(floor);
const grid=new THREE.GridHelper(48,3,0x73796b,0x575d51);grid.position.set(8,floorY+.002,8);context.add(grid);
if(M.name==='sitting_skeleton'){const wall=new THREE.Mesh(new THREE.BoxGeometry(36,30,1),new THREE.MeshLambertMaterial({color:0x444a48}));wall.position.set(8,15,18);context.add(wall);}
// Reference chain is a viewer-only guide. It is deliberately absent from .bbmodel.
const chain=new THREE.Group();scene.add(chain);if(M.name==='hanging_skeleton'){
 const mat=new THREE.MeshLambertMaterial({color:0x43494b});for(let y=17;y<29;y+=2){const link=new THREE.Mesh(new THREE.TorusGeometry(.59,.16,4,4),mat);link.position.set(8,y,8);if(y%4===1)link.rotation.y=Math.PI/2;chain.add(link);}
 const beam=new THREE.Mesh(new THREE.BoxGeometry(24,2,4),new THREE.MeshLambertMaterial({color:0x494136}));beam.position.set(8,30,8);chain.add(beam);
}
function draw(){renderer.render(scene,camera)}
function view(which='hero'){
 controls.target.copy(centre);if(M.name==='lying_skeleton'){
 const dirs={hero:[-1,.95,-1.2],front:[0,.9,-1.3],back:[0,.9,1.3],side:[1,.65,0],top:[0,1,.001]};camera.position.copy(centre).add(new THREE.Vector3(...dirs[which]).normalize().multiplyScalar(dist));
 }else{const dirs={hero:[-1,.45,-1.7],front:[0,.12,-1.8],back:[0,.2,1.8],side:[1.8,.15,0],top:[0,1,.001]};camera.position.copy(centre).add(new THREE.Vector3(...dirs[which]).normalize().multiplyScalar(dist));}
 camera.lookAt(centre);controls.update();draw();}
controls.addEventListener('change',draw);view();
window.HumanSkeletonViewer={scene,group,camera,renderer,view,context,chain,materials,draw};
for(const b of document.querySelectorAll('[data-view]'))b.onclick=()=>view(b.dataset.view);
document.querySelector('#wire').onchange=e=>{materials.forEach(m=>m.wireframe=e.target.checked);draw()};document.querySelector('#context').onchange=e=>{context.visible=e.target.checked;draw()};document.querySelector('#chain').onchange=e=>{chain.visible=e.target.checked;draw()};
addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);draw()});
window.previewReady=false;setTimeout(()=>{draw();window.previewReady=texture.image&&texture.image.complete},500);
'''
def build():
 for path in sorted((OUT/'blockbench').glob('*.bbmodel')):
  model=json.loads(path.read_text());title={'lying_skeleton':'Лежащий скелет','sitting_skeleton':'Сидящий скелет','hanging_skeleton':'Подвешенный скелет'}[path.stem]
  head='''<!doctype html><html lang="ru"><meta charset="utf-8"><title>'''+title+'''</title><style>body{margin:0;overflow:hidden;font:14px system-ui;color:#e9e5d7}header{position:absolute;top:20px;left:24px;z-index:2}h1{font-size:21px;margin:0 0 5px}small{color:#b6b9ad}nav{position:absolute;bottom:20px;left:24px;z-index:2;display:flex;gap:8px;align-items:center;flex-wrap:wrap}button{background:#414943;color:#eee6d3;border:1px solid #687164;border-radius:5px;padding:8px 12px;cursor:pointer}label{padding:6px;background:#303833}canvas{display:block}</style><header><h1>'''+title+'''</h1><small>Fall of Herovgadia · 32×32 · статичная модель · офлайн-превью, не игровой скриншот</small></header><nav><button data-view="hero">Общий вид</button><button data-view="front">Спереди</button><button data-view="back">Сзади</button><button data-view="side">Сбоку</button><button data-view="top">Сверху</button><label><input type="checkbox" id="wire">Каркас</label><label><input type="checkbox" id="context" checked>Окружение</label><label><input type="checkbox" id="chain" checked>Ориентир цепи</label></nav>'''
  html=head+'<script>'+scripts[0]+'</script><script>'+scripts[1]+'</script><script>const M='+json.dumps(model)+';\n'+JS+'</script></html>'
  (OUT/f'{path.stem}_viewer.html').write_text(html)
async def capture():
 async with async_playwright() as p:
  browser=await p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader'])
  results=[]
  for path in sorted(OUT.glob('*_viewer.html')):
   page=await browser.new_page(viewport={'width':1200,'height':1050});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   await page.set_content(path.read_text(),wait_until="load");await page.wait_for_function('window.previewReady===true');await page.screenshot(path=str(OUT/'previews'/f'{path.stem[:-7]}.png'))
   for side in ('front','back','side','top'):
    await page.evaluate('(v)=>HumanSkeletonViewer.view(v)',side);await page.screenshot(path=str(OUT/'previews'/f'{path.stem[:-7]}_{side}.png'))
   await page.locator('#wire').check();assert await page.evaluate('HumanSkeletonViewer.materials.every(m=>m.wireframe)')
   await page.locator('#wire').uncheck();assert await page.evaluate('HumanSkeletonViewer.materials.every(m=>!m.wireframe)')
   assert not errors,errors
   result=await page.evaluate('({cuboids:HumanSkeletonViewer.group.children.length,triangles:HumanSkeletonViewer.renderer.info.render.triangles,texture:[HumanSkeletonViewer.materials[0].map.image.naturalWidth,HumanSkeletonViewer.materials[0].map.image.naturalHeight]})');result.update(model=path.stem,errors=errors,views=5,wireframe_controls=True);results.append(result);print(result)
   await page.close()
  await browser.close();(OUT/'viewer_validation.json').write_text(json.dumps(results,indent=2))
if __name__=='__main__':build();asyncio.run(capture())
