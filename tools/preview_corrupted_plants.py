"""Render cutout cross models at native size on three ground textures, offline."""
from pathlib import Path
import re,json,base64,asyncio
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'corrupted_plants'
def uri(path):return 'data:image/png;base64,'+base64.b64encode(path.read_bytes()).decode()
source=(ROOT/'dead_harpy/dead_harpy_viewer.html').read_text();libs=re.findall(r'<script[^>]*>(.*?)</script>',source,re.S)[:2]
plants=[dict(id='corrupted_plant_'+v,label=label,image=uri(OUT/'textures'/f'corrupted_plant_{v}.png')) for v,label in [('small','Сухой пучок'),('medium','Сорняк'),('tall','Высокий стебель'),('withered_bush','Мёртвый куст')]]
grounds=[dict(name='Обычная земля',image=uri(Path('/workspace/plants-work/dirt.png'))),dict(name='Грубая земля',image=uri(Path('/workspace/plants-work/coarse_dirt.png'))),dict(name='Осквернённая земля',image=uri(ROOT/'src/main/resources/assets/fallofherovgadia/textures/block/corrupted_soil_top.png'))]
JS=r'''
const scene=new THREE.Scene();scene.background=new THREE.Color(0x242a27);const renderer=new THREE.WebGLRenderer({antialias:false,preserveDrawingBuffer:true});renderer.setPixelRatio(devicePixelRatio);renderer.setSize(innerWidth,innerHeight);document.body.appendChild(renderer.domElement);
const camera=new THREE.PerspectiveCamera(35,innerWidth/innerHeight,.1,500);const controls=new THREE.OrbitControls(camera,renderer.domElement);controls.enableDamping=false;scene.add(new THREE.AmbientLight(0xffffff,.9));const sun=new THREE.DirectionalLight(0xfff7e8,.35);sun.position.set(-25,65,-20);scene.add(sun);
const textures=[];function texture(src){const t=new THREE.TextureLoader().load(src,draw);t.magFilter=THREE.NearestFilter;t.minFilter=THREE.NearestFilter;textures.push(t);return t;}
const groundTextures=DATA.grounds.map(g=>texture(g.image));const plantTextures=DATA.plants.map(p=>texture(p.image));const collection=new THREE.Group();scene.add(collection);const models=[];
for(let row=0;row<3;row++)for(let col=0;col<4;col++){const cell=new THREE.Group();cell.position.set(col*24,0,row*24);collection.add(cell);const earth=new THREE.Mesh(new THREE.BoxGeometry(16,5,16),new THREE.MeshLambertMaterial({map:groundTextures[row]}));earth.position.set(8,-2.5,8);cell.add(earth);const plant=new THREE.Group();cell.add(plant);const mat=new THREE.MeshLambertMaterial({map:plantTextures[col],alphaTest:.5,side:THREE.DoubleSide});for(const angle of [-Math.PI/4,Math.PI/4]){const mesh=new THREE.Mesh(new THREE.PlaneGeometry(14.4*Math.SQRT2,16),mat);mesh.position.set(8,8,8);mesh.rotation.y=angle;plant.add(mesh);}models.push({row,col,cell,plant});}
function draw(){renderer.render(scene,camera)}
function show(plant=-1,row=-1){for(const m of models)m.cell.visible=(plant<0||m.col===plant)&&(row<0||m.row===row);const subset=models.filter(m=>m.cell.visible);const centre=new THREE.Vector3();for(const m of subset)centre.add(m.cell.position.clone().add(new THREE.Vector3(8,6,8)));centre.divideScalar(subset.length);controls.target.copy(centre);camera.position.copy(centre).add(plant<0?new THREE.Vector3(-68,75,-100):new THREE.Vector3(-30,24,-40));camera.lookAt(centre);controls.update();draw();}
controls.addEventListener('change',draw);show();window.PlantsViewer={renderer,models,textures,show,draw,controls,camera};
document.querySelector('#all').onclick=()=>show();document.querySelectorAll('[data-plant]').forEach(b=>b.onclick=()=>show(+b.dataset.plant,1));addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);draw()});window.previewReady=false;setTimeout(()=>{draw();window.previewReady=textures.every(t=>t.image&&t.image.complete)},500);
'''
def build():
 cards=''.join(f'<button data-plant="{i}"><img src="{p["image"]}"><span>{p["label"]}</span></button>' for i,p in enumerate(plants))
 html='''<!doctype html><html lang="ru"><meta charset="utf-8"><title>Осквернённые растения</title><style>body{margin:0;overflow:hidden;color:#e0dccb;font:14px system-ui}header{position:absolute;left:24px;top:20px;z-index:2}h1{font-size:25px;margin:0 0 6px}small{color:#acb7a2}aside{position:absolute;top:100px;left:24px;background:#253029dd;padding:12px;line-height:1.8}nav{position:absolute;bottom:18px;left:24px;display:flex;gap:10px;z-index:2}button{border:1px solid #61715c;border-radius:4px;background:#303a30;color:#ddd9c3;padding:10px 15px;cursor:pointer;display:flex;align-items:center;gap:9px}button img{width:64px;height:64px;image-rendering:pixelated}button span{max-width:80px}canvas{display:block}</style><header><h1>Осквернённые растения · Fall of Herovgadia</h1><small>4 варианта · 16×16 · прозрачные cross-модели · офлайн-превью, не игровой скриншот</small></header><aside>Ряды спереди назад:<br>Обычная земля<br>Грубая земля<br>Осквернённая земля<br><br>Значки внизу — предметные спрайты.<br>Мышь: вращение / масштаб.</aside><nav><button id="all">Все растения</button>'''+cards+'</nav><script>'+libs[0]+'</script><script>'+libs[1]+'</script><script>const DATA='+json.dumps(dict(plants=plants,grounds=grounds))+';'+JS+'</script></html>'
 (OUT/'corrupted_plants_viewer.html').write_text(html)
async def capture():
 async with async_playwright() as p:
  browser=await p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']);page=await browser.new_page(viewport={'width':1600,'height':1150});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  await page.route('https://**/*',lambda r:r.abort());await page.route('http://**/*',lambda r:r.abort());await page.set_content((OUT/'corrupted_plants_viewer.html').read_text(),wait_until='load');await page.wait_for_function('window.previewReady===true')
  await page.screenshot(path=str(OUT/'previews/plants_on_three_soils.png'))
  for i,plant in enumerate(plants):
   await page.locator(f'[data-plant="{i}"]').click();assert await page.evaluate('PlantsViewer.models.filter(m=>m.cell.visible).length')==1
   await page.screenshot(path=str(OUT/'previews'/f'{plant["id"]}.png'))
  await page.locator('#all').click();assert await page.evaluate('PlantsViewer.models.filter(m=>m.cell.visible).length')==12
  assert not errors,errors
  result=await page.evaluate('({cells:PlantsViewer.models.length,planes:PlantsViewer.models.reduce((n,m)=>n+m.plant.children.length,0),textures:PlantsViewer.textures.map(t=>[t.image.naturalWidth,t.image.naturalHeight]),triangles:PlantsViewer.renderer.info.render.triangles})');result.update(errors=errors,all_four_controls=True,offline=True,ingame=False);(OUT/'viewer_validation.json').write_text(json.dumps(result,indent=2));print(result);await browser.close()
if __name__=='__main__':build();asyncio.run(capture())
