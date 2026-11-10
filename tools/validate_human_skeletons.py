"""Check vanilla anatomy, untouched skin UVs and actual rotated arm/head separation."""
from pathlib import Path
import base64,collections,itertools,json,hashlib,math
import numpy as np
from PIL import Image
from scipy.spatial.transform import Rotation
from build_human_skeletons import separation
ROOT=Path(__file__).resolve().parents[1]/'human_skeletons'
def obb(e):return np.array(e['origin']),np.array(e['to'])-e['from'],Rotation.from_euler('xyz',e['rotation'],degrees=True).as_matrix()
results=[]
for f in sorted((ROOT/'blockbench').glob('*.bbmodel')):
 m=json.loads(f.read_text());els=m['elements'];assert len(els)==10 and not m.get('animations')
 assert m['resolution']=={'width':64,'height':32}
 png=(ROOT/'textures/human_skeletons.png').read_bytes();assert base64.b64decode(m['textures'][0]['source'].split(',')[1])==png
 atlas=Image.open(ROOT/'textures/human_skeletons.png');assert atlas.size==(64,32)
 refs=[]
 def walk(nodes):
  for n in nodes:
   if isinstance(n,str):refs.append(n)
   else:walk(n['children'])
 walk(m['outliner']);assert collections.Counter(refs)==collections.Counter(e['uuid'] for e in els)
 assert len(set(e['uuid'] for e in els))==len(els)
 assert not ({e['uuid'] for e in els}&{g['uuid'] for g in m['outliner']}), 'Group and cube UUID collision'
 assert {g['name'] for g in m['outliner']}=={'skull','torso','arm_left','arm_right','leg_left','leg_right'}
 points=[]
 for e in els:
  assert all(math.isfinite(v) for k in ('from','to','origin','rotation') for v in e[k]);size=np.array(e['to'])-e['from'];assert (size>0).all()
  if e['name']=='cranium':assert np.allclose(size,[8,8,8])
  elif e['name']=='torso':assert np.allclose(size,[8,12,4])
  else:assert np.allclose(size[[0,2]],[2,2])
  assert set(e['faces'])=={'up','down','north','south','east','west'}
  for face in e['faces'].values():
   a,b,c,d=face['uv'];assert face['texture']==0 and 0<=a<c<=64 and 0<=b<d<=32
  centre,size,r=obb(e)
  for p in itertools.product(*zip(e['from'],e['to'])):points.append(r@(np.array(p)-centre)+centre)
 bounds=np.array(points);low=bounds.min(0);high=bounds.max(0);span=high-low
 head=obb(next(e for e in els if e['name']=='cranium'))
 landmarks=json.loads((ROOT/(f.stem+'_landmarks.json')).read_text())
 for side in ('left','right'):
  for kind in ('arm','leg'):
   joints=np.array(landmarks[side+'_'+kind+'_joints'])
   actual=[]
   for index,label in enumerate(('upper','lower')):
    e=next(e for e in els if e['name']==side+'_'+kind+'_'+label);centre,size,r=obb(e)
    ends=np.array([centre-r[:,1]*size[1]/2,centre+r[:,1]*size[1]/2])
    assert np.allclose(ends,joints[index:index+2],atol=2e-5),(f,e['name'],ends,joints[index:index+2])
    actual.append(ends)
   assert np.linalg.norm(actual[0][1]-actual[1][0])<2e-5
 gaps={e['name']:round(separation(obb(e),head),4) for e in els if '_arm_' in e['name']}
 assert all(gap>.20 for gap in gaps.values()),(f,gaps)
 if f.stem=='lying_skeleton':assert span[2]>29 and abs(low[1]-.08)<.001
 if f.stem=='sitting_skeleton':assert span[1]>19 and abs(low[1]-.08)<.001
 if f.stem=='hanging_skeleton':
  assert abs(high[1]-16)<.001 and low[1]>-26
  assert next(e for e in els if e['name']=='left_arm_lower')['origin'][1]>head[0][1]
 report=dict(model=f.stem,cuboids=len(els),vanilla_anatomy=True,euler_order='ZYX',limb_joints_connected=True,atlas_size=[64,32],skin_sha256=hashlib.sha256(png).hexdigest(),embedded_atlas_matches=True,arm_head_clearance_pixels=gaps,static=True,bounds_pixels={'min':low.round(4).tolist(),'max':high.round(4).tolist()},size_blocks=(span/16).round(3).tolist())
 results.append(report);print(json.dumps(report))
(ROOT/'validation.json').write_text(json.dumps(results,indent=2))
