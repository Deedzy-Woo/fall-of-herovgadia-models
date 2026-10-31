"""Independent structural, hierarchy and UV checks for the delivered assets."""
import base64
import collections
import io
import json
import math
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dead_harpy'
m=json.loads((OUT/'dead_harpy.bbmodel').read_text())
g=json.loads((OUT/'dead_harpy.geo.json').read_text())['minecraft:geometry'][0]
els=m['elements']
assert len(els)>0 and all(e['type']=='cube' for e in els)
assert len(m['textures'])==1 and not m.get('animations')
assert len({e['uuid'] for e in els})==len(els)
assert len({e['name'] for e in els})==len(els)
groups=[]; refs=[]; parents={}
def walk(nodes,parent=None):
 for node in nodes:
  if isinstance(node,str): refs.append(node)
  else:
   groups.append(node)
   parents[node['name']]=parent
   walk(node['children'],node['name'])
walk(m['outliner'])
assert len({x['name'] for x in groups})==len(groups)
assert collections.Counter(refs)==collections.Counter(e['uuid'] for e in els)
tex=Image.open(OUT/'dead_harpy.png').convert('RGBA')
embedded=Image.open(io.BytesIO(base64.b64decode(m['textures'][0]['source'].split(',')[1]))).convert('RGBA')
expected=(m['resolution']['width'],m['resolution']['height'])
assert tex.size==expected==embedded.size
assert tex.tobytes()==embedded.tobytes()
occupied=set()
for e in els:
 assert all(math.isfinite(v) for k in ('from','to','origin','rotation') for v in e[k])
 assert all(b>a for a,b in zip(e['from'],e['to']))
 assert set(e['faces'])=={'north','east','south','west','up','down'}
 for face in e['faces'].values():
  assert face['texture']==0
  a,b,c,d=face['uv']
  assert all(isinstance(v,int) for v in (a,b,c,d))
  assert 0<=a<c<=expected[0] and 0<=b<d<=expected[1]
  for y in range(b,d):
   for x in range(a,c):
    assert (x,y) not in occupied, ('overlapping UV',e['name'])
    assert tex.getpixel((x,y))[3]==255, ('transparent surface',e['name'])
    occupied.add((x,y))
assert {b['name'] for b in g['bones']}=={b['name'] for b in groups}
assert sum(len(b.get('cubes',[])) for b in g['bones'])==len(els)
for side in ('left','right'):
 names={b['name'] for b in groups}
 for suffix in ('wing','wing_upper','wing_forearm','wing_hand','wing_primaries','wing_coverts',
                'wing_thumb','thigh','shin','tarsus','foot','rear_toe'):
  assert f'{side}_{suffix}' in names
 for suffix in ('arm','forearm','hand','thumb'):
  assert f'{side}_{suffix}' not in names, 'Separate human arms must be absent'
 for suffix in ('upper_arm','forearm','palm'):
  assert f'{side}_{suffix}' not in {e['name'] for e in els}
 for i in (1,2):
  assert f'{side}_wing_finger_{i}_hook' in names
  assert parents[f'{side}_wing_finger_{i}']==f'{side}_wing_hand'
 assert parents[f'{side}_wing_thumb']==f'{side}_wing_hand'
 for i in (1,2,3):
  assert f'{side}_toe_{i}_hook' in names

# Compare against the official Blockbench exporter, ignoring insignificant floats
# and absent optional fields. The geometry must agree for every individual bone.
def normalize(o):
 if isinstance(o,list): return [normalize(v) for v in o]
 if isinstance(o,dict): return {k:normalize(v) for k,v in o.items() if v is not None}
 return o
def equal(a,b):
 if isinstance(a,(float,int)) and isinstance(b,(float,int)):
  return math.isclose(a,b,rel_tol=0,abs_tol=1e-5)
 if type(a) is not type(b): return False
 if isinstance(a,dict): return a.keys()==b.keys() and all(equal(a[k],b[k]) for k in a)
 if isinstance(a,list): return len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
 return a==b
official=OUT/'blockbench_export_check.json'
if official.exists():
 actual=json.loads(official.read_text())['minecraft:geometry'][0]
 assert equal(normalize(actual['bones']),normalize(g['bones'])), 'Official Blockbench export differs'
report=dict(cuboids=len(els), bones=len(groups), faces=len(els)*6, triangles=len(els)*12,
            single_texture=list(tex.size), embedded_texture_matches_png=True,
            all_elements_referenced_once=True, nondegenerate_cuboids=True,
            complete_six_face_uv=True, overlapping_uv_islands=0, transparent_surface_texels=0,
            all_uv_within_atlas=True, animations=0,
            separate_human_arms_present=False,grasping_digits_attached_to_wing_wrists=True,
            official_blockbench_export_matches=official.exists())
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
