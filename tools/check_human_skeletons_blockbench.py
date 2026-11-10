"""Import actual .bbmodel exports in a built official Blockbench web editor.
Usage: python3 tools/check_human_skeletons_blockbench.py --blockbench-dir PATH
Verify all world vertices and joint endpoints against authored coordinates;
this catches mismatched Euler conventions that a custom viewer can conceal.
"""
import argparse,asyncio,json,itertools,threading
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit
import numpy as np
from scipy.spatial.transform import Rotation
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1]/'human_skeletons'
parser=argparse.ArgumentParser();parser.add_argument('--blockbench-dir',type=Path,required=True);args=parser.parse_args()
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(args.blockbench_dir)));threading.Thread(target=server.serve_forever,daemon=True).start()
origin=f'http://127.0.0.1:{server.server_port}'
async def main():
 results=[]
 async with async_playwright() as p:
  browser=await p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader'])
  page=await browser.new_page(viewport={'width':1600,'height':1100});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  async def route(r):
   u=urlsplit(r.request.url)
   if u.hostname=='web.blockbench.net' and u.path=='/content/news.json':await r.fulfill(status=200,content_type='application/json',body=(args.blockbench_dir/'content/news.json').read_text())
   elif r.request.url.startswith((origin,'data:','blob:')):await r.continue_()
   else:await r.abort()
  await page.route('**/*',route);await page.goto(origin);await page.wait_for_function('window.Blockbench && Blockbench.setup_successful',timeout=60000)
  for path in sorted((ROOT/'blockbench').glob('*.bbmodel')):
   model=json.loads(path.read_text());landmarks=json.loads((ROOT/(path.stem+'_landmarks.json')).read_text())
   await page.evaluate('(m)=>Codecs.project.load(m,{path:m.name+".bbmodel",no_file:true})',model)
   await page.wait_for_function('Texture.all[0] && Texture.all[0].img.complete && Texture.all[0].img.naturalWidth===64')
   data=await page.evaluate('''()=>{Canvas.updateAll();Project.model_3d.updateMatrixWorld(true);return {version:Blockbench.version,order:Format.euler_order,cubes:Cube.all.map(c=>{c.mesh.geometry.computeBoundingBox();const box=c.mesh.geometry.boundingBox;const vertices=[];for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z])vertices.push(Project.model_3d.worldToLocal(c.mesh.localToWorld(new THREE.Vector3(x,y,z))).toArray());const mid=box.getCenter(new THREE.Vector3());const ends=[box.min.y,box.max.y].map(y=>Project.model_3d.worldToLocal(c.mesh.localToWorld(new THREE.Vector3(mid.x,y,mid.z))).toArray());return {name:c.name,vertices,ends,order:c.mesh.rotation.order}})}}''')
   assert data['order']=='ZYX'
   max_error=0.;max_joint_error=0.
   for actual,e in zip(data['cubes'],model['elements']):
    assert actual['name']==e['name'];r=Rotation.from_euler('xyz',e['rotation'],degrees=True).as_matrix();o=np.array(e['origin'])
    expected=np.array([r@(np.array(v)-o)+o for v in itertools.product(*zip(e['from'],e['to']))]);v=np.array(actual['vertices']);dist=np.linalg.norm(v[:,None,:]-expected[None,:,:],axis=2);error=max(dist.min(axis=0).max(),dist.min(axis=1).max());max_error=max(max_error,float(error))
    if error>3e-5:print('vertex mismatch',e['name'],error,actual['vertices'],expected.tolist(),flush=True)
    if '_arm_' in e['name'] or '_leg_' in e['name']:
     side,kind,part=e['name'].split('_');idx=0 if part=='upper' else 1;joints=np.array(landmarks[side+'_'+kind+'_joints']);max_joint_error=max(max_joint_error,float(np.max(np.linalg.norm(np.array(actual['ends'])-joints[idx:idx+2],axis=1))))
   assert max_error<3e-5 and max_joint_error<3e-5,(path,max_error,max_joint_error)
   # Actual editor screenshots, after import, without proxy-rendered geometry.
   await page.evaluate('''()=>{if(Dialog.open)Dialog.open.hide();const box=new THREE.Box3().setFromObject(Project.model_3d),c=box.getCenter(new THREE.Vector3()),s=box.getSize(new THREE.Vector3());const preview=Preview.selected;preview.camera.position.copy(c).add(new THREE.Vector3(-1,.65,-1.6).normalize().multiplyScalar(Math.max(s.x,s.y,s.z)*2.5));preview.controls.target.copy(c);preview.controls.update();Canvas.updateAll()}''')
   await page.screenshot(path=str(ROOT/'previews'/f'{path.stem}_blockbench.png'))
   result=dict(model=path.stem,blockbench=data['version'],euler_order=data['order'],cuboids=len(data['cubes']),max_vertex_error_pixels=max_error,max_joint_error_pixels=max_joint_error,passed=True);results.append(result);print(result,flush=True)
  (ROOT/'blockbench_validation.json').write_text(json.dumps({'models':results,'page_errors':errors},indent=2));await browser.close()
try:asyncio.run(main())
finally:server.shutdown();server.server_close()
