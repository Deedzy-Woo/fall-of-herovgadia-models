"""Validate exported static model geometry, atlas bindings, anatomy and chain point."""
from pathlib import Path
import base64,collections,itertools,json,math,io
import numpy as np
from PIL import Image
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parents[1]/'human_skeletons'
results=[]
for f in sorted((ROOT/'blockbench').glob('*.bbmodel')):
 m=json.loads(f.read_text());els=m['elements'];assert not m.get('animations');assert m['resolution']=={'width':32,'height':32}
 t=m['textures'][0];assert base64.b64decode(t['source'].split(',')[1])==(ROOT/'textures/human_skeletons.png').read_bytes()
 atlas=Image.open(ROOT/'textures/human_skeletons.png').convert('RGBA');assert atlas.size==(32,32)
 refs=[]
 def walk(nodes):
  for n in nodes:
   if isinstance(n,str):refs.append(n)
   else:walk(n['children'])
 walk(m['outliner']);assert collections.Counter(refs)==collections.Counter(e['uuid'] for e in els)
 assert len(set(e['uuid'] for e in els))==len(els)
 groups={g['name'] for g in m['outliner']};assert {'skull','spine','ribcage','pelvis','arm_left','arm_right','leg_left','leg_right','left_hand','right_hand','left_foot','right_foot'}<=groups
 points=[]
 for e in els:
  assert all(math.isfinite(v) for k in ('from','to','origin','rotation') for v in e[k])
  assert all(b>a for a,b in zip(e['from'],e['to']))
  assert set(e['faces'])=={'up','down','north','south','east','west'}
  for face in e['faces'].values():
   a,b,c,d=face['uv'];assert face['texture']==0;assert 0<=a<c<=32 and 0<=b<d<=32
   assert atlas.crop((a,b,c,d)).getextrema()[3]==(255,255), (f,e['name'],'transparent used UV')
  r=Rotation.from_euler('XYZ',e['rotation'],degrees=True).as_matrix();o=np.array(e['origin'])
  for p in itertools.product(*zip(e['from'],e['to'])):points.append(r@(np.array(p)-o)+o)
 bounds=np.array(points);low=bounds.min(0);high=bounds.max(0);size=high-low
 if f.stem=='lying_skeleton':assert size[2]>29 and size[1]<11 and abs(low[1]-.08)<.001
 if f.stem=='sitting_skeleton':assert size[1]>19 and abs(low[1]-.08)<.001
 if f.stem=='hanging_skeleton':
  hands=[e for e in els if e['name'].endswith('_palm')];head=next(e for e in els if e['name']=='cranium')
  assert len(hands)==2 and all(e['origin'][1]>head['to'][1] for e in hands)
  assert abs(hands[0]['origin'][0]-hands[1]['origin'][0])<2
  assert low[1]>-24 and size[1]>32
  landmark=json.loads((ROOT/'hanging_skeleton_landmarks.json').read_text());assert landmark['chain_connection']==[8,16,8]
 report=dict(model=f.stem,cuboids=len(els),bones_and_limbs_present=True,complete_opaque_uv=True,embedded_atlas_matches=True,static=True,bounds_pixels={'min':low.round(4).tolist(),'max':high.round(4).tolist()},size_blocks=(size/16).round(3).tolist())
 results.append(report);print(json.dumps(report))
(ROOT/'validation.json').write_text(json.dumps(results,indent=2))
