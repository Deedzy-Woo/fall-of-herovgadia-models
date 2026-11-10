"""Import the four plant projects in the official built Blockbench web editor."""
import argparse,asyncio,json,threading
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlsplit
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1]/'corrupted_plants'
p=argparse.ArgumentParser();p.add_argument('--blockbench-dir',required=True,type=Path);args=p.parse_args()
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(args.blockbench_dir)));threading.Thread(target=server.serve_forever,daemon=True).start();origin=f'http://127.0.0.1:{server.server_port}'
async def run():
 async with async_playwright() as p:
  browser=await p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader','--use-angle=swiftshader']);page=await browser.new_page(viewport={'width':1400,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  async def route(r):
   u=urlsplit(r.request.url)
   if u.hostname=='web.blockbench.net' and u.path=='/content/news.json':await r.fulfill(status=200,content_type='application/json',body=(args.blockbench_dir/'content/news.json').read_text())
   elif r.request.url.startswith((origin,'data:','blob:')):await r.continue_()
   else:await r.abort()
  await page.route('**/*',route);await page.goto(origin);await page.wait_for_function('window.Blockbench && Blockbench.setup_successful',timeout=60000);results=[]
  for f in sorted((ROOT/'blockbench').glob('*.bbmodel')):
   m=json.loads(f.read_text());await page.evaluate('(m)=>Codecs.project.load(m,{path:m.name+".bbmodel",no_file:true})',m);await page.wait_for_function('Texture.all[0]&&Texture.all[0].img.complete&&Texture.all[0].img.naturalWidth===16')
   r=await page.evaluate('''()=>{Canvas.updateAll();Project.model_3d.updateMatrixWorld(true);let bounds=new THREE.Box3();for(const c of Cube.all){const pos=c.mesh.geometry.attributes.position;for(let i=0;i<pos.count;i++){const p=new THREE.Vector3().fromBufferAttribute(pos,i).applyMatrix4(c.mesh.matrixWorld);bounds.expandByPoint(Project.model_3d.worldToLocal(p));}}return {version:Blockbench.version,cubes:Cube.all.length,texture:[Texture.all[0].width,Texture.all[0].height],rescale:Cube.all.every(c=>c.rescale),bounds:{min:bounds.min.toArray(),max:bounds.max.toArray()}}}''')
   assert r['cubes']==2 and r['texture']==[16,16] and r['rescale'],r
   assert all(abs(a-b)<.002 for a,b in zip(r['bounds']['min'],[.8,0,.8])) and all(abs(a-b)<.002 for a,b in zip(r['bounds']['max'],[15.2,16,15.2])),r
   await page.evaluate('''()=>{if(Dialog.open)Dialog.open.hide();const p=Preview.selected;p.camera.position.set(-22,18,-30);p.controls.target.set(0,6,0);p.controls.update();Canvas.updateAll()}''');await page.screenshot(path=str(ROOT/'previews'/f'{f.stem}_blockbench.png'));r.update(model=f.stem,passed=True);results.append(r);print(r,flush=True)
  assert not errors,errors
  (ROOT/'blockbench_validation.json').write_text(json.dumps(dict(models=results,page_errors=errors),indent=2));await browser.close()
try:asyncio.run(run())
finally:server.shutdown();server.server_close()
