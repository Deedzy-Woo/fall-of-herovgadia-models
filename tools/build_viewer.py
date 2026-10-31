"""Bundle a self-contained inspection viewer. Requires a local Three.js r129 tree."""
import argparse
import json
from pathlib import Path

parser=argparse.ArgumentParser()
parser.add_argument('--three-dir',type=Path,required=True)
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
out=root/'dead_harpy'
model=json.loads((out/'dead_harpy.bbmodel').read_text())
payload=json.dumps(dict(geometry=json.loads((out/'render_geometry.json').read_text()),
                        rig=json.loads((out/'rig_points.json').read_text()),
                        texture=model['textures'][0]['source']),separators=(',',':'))
three=(args.three_dir/'build/three.min.js').read_text()
orbit=(args.three_dir/'examples/js/controls/OrbitControls.js').read_text()
html='''<!doctype html>
<html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Мёртвая гарпия · Fall of Herovgadia</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#11191d;color:#e7e2d7;font:14px/1.5 system-ui,sans-serif;overflow:hidden}
#stage{position:absolute;inset:0;background:radial-gradient(ellipse at 53% 47%,#2c3c43 0,#1c282f 45%,#10171c 90%)}
canvas{display:block;width:100%;height:100%;touch-action:none}header{position:absolute;top:34px;left:40px;pointer-events:none}
.eyebrow{color:#b09a76;font-size:10px;letter-spacing:3px;font-weight:650}h1{font-size:28px;font-weight:450;letter-spacing:-.8px;margin:7px 0 4px}p{color:#96a4aa;margin:0;font-size:12px}
.status{position:absolute;top:35px;right:40px;display:flex;gap:18px;font-size:11px;color:#a4b0b4}.status b{display:block;color:#e0dbd0;font-weight:500;font-size:16px}
nav{position:absolute;bottom:36px;left:50%;transform:translateX(-50%);padding:7px;background:#10191ed9;border:1px solid #5f6d713b;border-radius:10px;display:flex;gap:3px;max-width:95vw}
button{cursor:pointer;border:0;background:transparent;color:#b8c2c4;padding:9px 13px;border-radius:5px;font:12px system-ui;white-space:nowrap}button:hover,button[aria-pressed=true]{background:#354247;color:#f5ecdc}button:focus-visible{outline:2px solid #b09a76}button.sep{margin-left:9px;border-left:1px solid #5f6d7144;border-radius:0 5px 5px 0}
footer{position:absolute;bottom:101px;left:50%;transform:translateX(-50%);font-size:10px;color:#7f919a;letter-spacing:.2px;white-space:nowrap}
#notice{position:absolute;bottom:15px;left:40px;color:#6e818b;font-size:9px}
@media(max-width:720px){header{left:20px;top:20px}h1{font-size:22px}.status{display:none}nav{bottom:22px;flex-wrap:wrap;justify-content:center;width:95%}button{padding:8px 9px}footer{bottom:126px;font-size:9px}#notice{left:20px;font-size:8px}}
</style>
<div id="stage" aria-label="Интерактивная 3D-модель мёртвой гарпии"></div>
<header><div class="eyebrow">FALL OF HEROVGADIA</div><h1>Мёртвая гарпия</h1><p>Кубическая модель по концепт-арту</p></header>
<div class="status"><span><b>__CUBES__</b>кубоидов</span><span><b>__BONES__</b>групп / суставов</span><span><b>__TEXSIZE__²</b>единая текстура</span></div>
<footer>Вращение — левая кнопка · Масштаб — колесо · Смещение — правая кнопка</footer>
<nav aria-label="Просмотр модели"><button data-view="hero">Ракурс ¾</button><button data-view="front">Спереди</button><button data-view="back">Сзади</button><button data-view="side">Сбоку</button><button id="wire" class="sep" aria-pressed="false">Каркас</button><button id="bones" aria-pressed="false">Суставы</button><button id="reset">Сброс</button></nav>
<div id="notice">Модель без анимаций · автономный просмотр · исходник: dead_harpy.bbmodel</div>
<script>__THREE__</script><script>__ORBIT__</script>
<script>
const DATA=__DATA__;
const host=document.querySelector('#stage'),scene=new THREE.Scene();
const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true,preserveDrawingBuffer:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.outputEncoding=THREE.sRGBEncoding;
renderer.toneMapping=THREE.NoToneMapping;host.appendChild(renderer.domElement);
const camera=new THREE.OrthographicCamera(-50,50,40,-40,.1,1000);
const controls=new THREE.OrbitControls(camera,renderer.domElement);controls.target.set(0,22,0);controls.enableDamping=false;controls.minZoom=.4;controls.maxZoom=8;
scene.add(new THREE.HemisphereLight(0xe4e7e9,0x77716c,.85));
function light(color,power,p){const l=new THREE.DirectionalLight(color,power);l.position.set(...p);scene.add(l)}
light(0xfff0db,.45,[40,70,-70]);light(0xb5c5d2,.15,[-70,30,-20]);light(0xcbd5df,.25,[0,50,50]);
const texture=new THREE.TextureLoader().load(DATA.texture,draw);texture.magFilter=THREE.NearestFilter;texture.minFilter=THREE.NearestFilter;texture.generateMipmaps=false;texture.encoding=THREE.sRGBEncoding;
const material=new THREE.MeshLambertMaterial({map:texture});
const model=new THREE.Group(),wire=new THREE.Group();scene.add(model,wire);wire.visible=false;
for(const c of DATA.geometry){const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(c.position,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(c.uv,2));g.setIndex(c.index);g.computeVertexNormals();const mesh=new THREE.Mesh(g,material);mesh.name=c.name;mesh.matrix.fromArray(c.matrix);mesh.matrixAutoUpdate=false;model.add(mesh);const edges=new THREE.LineSegments(new THREE.EdgesGeometry(g,20),new THREE.LineBasicMaterial({color:0xc3aa80,transparent:true,opacity:.48}));edges.matrix.copy(mesh.matrix);edges.matrixAutoUpdate=false;wire.add(edges)}
const rig=new THREE.Group();scene.add(rig);rig.visible=false;
const byName=Object.fromEntries(DATA.rig.map(g=>[g.name,g]));const line=[];
const joints=[];for(const b of DATA.rig){if(b.name==='root')continue;joints.push(...b.point);const p=byName[b.parent];if(p&&p.name!=='root'){line.push(...p.point,...b.point)}}
const lg=new THREE.BufferGeometry();lg.setAttribute('position',new THREE.Float32BufferAttribute(line,3));rig.add(new THREE.LineSegments(lg,new THREE.LineBasicMaterial({color:0xf4b75f,depthTest:false,transparent:true,opacity:.85})));
const pg=new THREE.BufferGeometry();pg.setAttribute('position',new THREE.Float32BufferAttribute(joints,3));rig.add(new THREE.Points(pg,new THREE.PointsMaterial({color:0xffdaa0,size:4,sizeAttenuation:false,depthTest:false})));rig.renderOrder=20;
const views={hero:[80,53,-140],front:[0,32,-150],back:[0,36,150],side:[150,34,-1]};
function draw(){renderer.render(scene,camera)}
function view(name){camera.position.set(...views[name]);camera.zoom=name==='side'?1.36:1;controls.target.set(0,22,0);camera.updateProjectionMatrix();controls.update();draw();document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===name)))}
function resize(){const w=host.clientWidth,h=host.clientHeight,half=Math.max(32,47*h/w);camera.left=-half*w/h;camera.right=half*w/h;camera.top=half;camera.bottom=-half;camera.updateProjectionMatrix();renderer.setSize(w,h);draw()}
controls.addEventListener('change',draw);window.addEventListener('resize',resize);
document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>view(b.dataset.view));
document.querySelector('#wire').onclick=function(){wire.visible=!wire.visible;this.setAttribute('aria-pressed',wire.visible);draw()};
document.querySelector('#bones').onclick=function(){rig.visible=!rig.visible;this.setAttribute('aria-pressed',rig.visible);draw()};
document.querySelector('#reset').onclick=()=>{wire.visible=rig.visible=false;document.querySelector('#wire').setAttribute('aria-pressed','false');document.querySelector('#bones').setAttribute('aria-pressed','false');view('hero')};
view('hero');resize();window.HarpyViewer={scene,model,wire,rig,camera,controls,renderer,draw,view};
</script></html>'''
stats=json.loads((out/'build_stats.json').read_text())
html=html.replace('__CUBES__',str(stats['cuboids'])).replace('__BONES__',str(stats['bones'])).replace('__TEXSIZE__',str(model['resolution']['width']))
html=html.replace('__THREE__',three).replace('__ORBIT__',orbit).replace('__DATA__',payload)
(out/'dead_harpy_viewer.html').write_text(html)
(out/'THIRD_PARTY_LICENSE.txt').write_text('The standalone viewer includes Three.js r129 and OrbitControls.\n\n'+(args.three_dir/'LICENSE').read_text())
print(out/'dead_harpy_viewer.html')
