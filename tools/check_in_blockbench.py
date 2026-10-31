"""Open the asset in official Blockbench, exercise its rig and read back geometry.

Run after building Blockbench's web target. Requires Playwright and Chromium.
The temporary local HTTP server is shut down before this program exits.
"""
import argparse
import asyncio
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import json
from pathlib import Path
import threading
from urllib.parse import unquote, urlsplit
from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dead_harpy'
parser=argparse.ArgumentParser()
parser.add_argument('--blockbench-dir',type=Path,required=True)
args=parser.parse_args()

class Handler(SimpleHTTPRequestHandler):
    def translate_path(self,path):
        path=unquote(urlsplit(path).path)
        return str(args.blockbench_dir/path.lstrip('/'))
    def log_message(self,*args):pass

async def main(origin):
    model=json.loads((OUT/'dead_harpy.bbmodel').read_text())
    size=model['resolution']['width']
    async with async_playwright() as p:
        browser=await p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,
            args=['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader'])
        page=await browser.new_page(viewport={'width':1600,'height':1100})
        errors=[]
        failed=[]
        page.on('requestfailed',lambda r:failed.append({'host':urlsplit(r.url).hostname,'path':urlsplit(r.url).path,'failure':r.failure}))
        page.on('pageerror',lambda e:errors.append({'message':str(e),'stack':e.stack}))
        await page.add_init_script('''window.harpyRejections=[];addEventListener('unhandledrejection',e=>{try{window.harpyRejections.push({message:String(e.reason),keys:Object.keys(e.reason||{}),detail:JSON.stringify(e.reason)})}catch(_){}})''')
        async def route_request(r):
            url=urlsplit(r.request.url)
            if url.hostname=='web.blockbench.net' and url.path=='/content/news.json':
                # The editor's unhandled startup-news request is unrelated to
                # model loading. Use the same official news file bundled in the
                # checkout so this asset test can run entirely offline.
                await r.fulfill(status=200,content_type='application/json',body=(args.blockbench_dir/'content/news.json').read_text())
            elif r.request.url.startswith((origin,'data:','blob:')):
                await r.continue_()
            else:
                await r.abort()
        await page.route('**/*',route_request)
        await page.goto(origin)
        await page.wait_for_function('window.Blockbench && Blockbench.setup_successful',timeout=60000)
        await page.evaluate('(m)=>Codecs.project.load(m,{path:"dead_harpy.bbmodel",no_file:true})',model)
        await page.wait_for_function(f'Texture.all[0] && Texture.all[0].img.complete && Texture.all[0].img.naturalWidth==={size}')
        info=await page.evaluate('''()=>({version:Blockbench.version,format:Format.id,cubes:Cube.all.length,bones:Group.all.length,textures:Texture.all.length,animations:Animation.all.length,textureSize:[Texture.all[0].width,Texture.all[0].height],errors:window.ErrorLog})''')
        assert info['cubes']==len(model['elements']) and not info['errors']
        await page.evaluate('''()=>{if(Dialog.open)Dialog.open.hide();Preview.selected.camera.position.set(70,48,-120);Preview.selected.controls.target.set(0,23,0);Preview.selected.controls.update();Outliner.root[0].isOpen=true;Canvas.updateAll();}''')
        await page.screenshot(path=str(OUT/'previews/blockbench_open.png'))
        export=await page.evaluate('()=>Codecs.bedrock.compile({raw:true})')
        (OUT/'blockbench_export_check.json').write_text(json.dumps(export,indent=2))
        data=await page.evaluate('''()=>{Project.model_3d.updateMatrixWorld(true);return Cube.all.map(c=>{let m=c.mesh,g=m.geometry;return {name:c.name,position:Array.from(g.attributes.position.array),uv:Array.from(g.attributes.uv.array),index:Array.from(g.index.array),matrix:m.matrixWorld.toArray()}})}''')
        (OUT/'render_geometry.json').write_text(json.dumps(data))
        report=await page.evaluate('''()=>{
            function refresh(){Canvas.updateAll();Project.model_3d.updateMatrixWorld(true)}
            function corner(c){return new THREE.Vector3().fromBufferAttribute(c.mesh.geometry.attributes.position,0).applyMatrix4(c.mesh.matrixWorld).toArray()}
            refresh();const base=Object.fromEntries(Cube.all.map(c=>[c.uuid,corner(c)]));
            const rig=Group.all.map(g=>({name:g.name,parent:g.parent?.name,point:new THREE.Vector3().setFromMatrixPosition(g.mesh.matrixWorld).toArray()}));
            const tests=[];
            for(const [name,axis,delta] of [['left_wing',2,25],['left_wing_forearm',2,30],['left_wing_hand',1,-50],['right_wing_finger_2_hook',0,40],['right_wing_thumb',1,35],['left_thigh',0,35],['right_shin',0,-40]]){
                const g=Group.all.find(g=>g.name===name),subset=new Set();
                function walk(o){for(const c of o.children){if(c instanceof Cube)subset.add(c.uuid);else if(c.children)walk(c)}}walk(g);
                const old=g.rotation[axis];g.rotation[axis]+=delta;refresh();
                const moved=Cube.all.filter(c=>corner(c).some((v,i)=>Math.abs(v-base[c.uuid][i])>1e-5));
                const unrelated=moved.filter(c=>!subset.has(c.uuid));
                tests.push({bone:name,moved_cuboids:moved.length,unrelated_cuboids_moved:unrelated.length,pass:moved.length>0&&!unrelated.length});
                g.rotation[axis]=old;refresh();
            }
            const restored=Cube.all.every(c=>corner(c).every((v,i)=>Math.abs(v-base[c.uuid][i])<1e-5));
            function positions(){const a=[];refresh();for(const c of Cube.all){const v=c.mesh.geometry.attributes.position;for(let i=0;i<v.count;i++)a.push(new THREE.Vector3().fromBufferAttribute(v,i).applyMatrix4(c.mesh.matrixWorld).toArray().map(x=>Math.round(x*1e4)/1e4))}return a.sort((a,b)=>a[0]-b[0]||a[1]-b[1]||a[2]-b[2])}
            window.harpyBaselinePositions=positions();
            return {tests,rest_pose_restored:restored,rig,animations:Animation.all.length};
        }''')
        (OUT/'rig_points.json').write_text(json.dumps(report.pop('rig')))
        geo=json.loads((OUT/'dead_harpy.geo.json').read_text())
        await page.evaluate('(g)=>Codecs.bedrock.load(g,{path:"dead_harpy.geo.json",no_file:true})',geo)
        rt=await page.evaluate('''()=>{Canvas.updateAll();Project.model_3d.updateMatrixWorld(true);const a=[];for(const c of Cube.all){const v=c.mesh.geometry.attributes.position;for(let i=0;i<v.count;i++)a.push(new THREE.Vector3().fromBufferAttribute(v,i).applyMatrix4(c.mesh.matrixWorld).toArray().map(x=>Math.round(x*1e4)/1e4))}a.sort((a,b)=>a[0]-b[0]||a[1]-b[1]||a[2]-b[2]);const old=window.harpyBaselinePositions;let max=0;for(let i=0;i<a.length;i++)for(let k=0;k<3;k++)max=Math.max(max,Math.abs(a[i][k]-old[i][k]));return {cuboids:Cube.all.length,bones:Group.all.length,vertex_count:a.length,max_vertex_error_pixels:max}}''')
        report.update(blockbench=info['version'],geometry_reimport=rt)
        report['passed']=all(t['pass'] for t in report['tests']) and report['rest_pose_restored'] and rt['max_vertex_error_pixels']<.001
        info['page_errors']=errors
        info['unhandled_rejections']=await page.evaluate('window.harpyRejections')
        info['failed_requests']=failed
        info['startup_news_source']='official checkout/content/news.json (offline)'
        (OUT/'blockbench_validation.json').write_text(json.dumps(info,indent=2))
        (OUT/'rig_validation.json').write_text(json.dumps(report,indent=2))
        assert report['passed'] and not errors
        print(json.dumps(dict(blockbench=info,rig=report),indent=2))
        await browser.close()

server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
thread=threading.Thread(target=server.serve_forever,daemon=True)
thread.start()
try:
    asyncio.run(main(f'http://127.0.0.1:{server.server_port}/'))
finally:
    server.shutdown()
    server.server_close()
