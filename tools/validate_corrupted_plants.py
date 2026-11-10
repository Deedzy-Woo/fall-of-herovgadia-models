"""Static, meaningful resource/texture validation; not a Minecraft runtime test."""
from pathlib import Path
import json,base64,hashlib,subprocess
from PIL import Image
from build_corrupted_plants import PLANTS
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'corrupted_plants';RES=ROOT/'src/main/resources'
results=[];hashes=set()
for variant,width,height,ru,en in PLANTS:
 name='corrupted_plant_'+variant;png=(OUT/'textures'/f'{name}.png').read_bytes();im=Image.open(OUT/'textures'/f'{name}.png').convert('RGBA');assert im.size==(16,16)
 alpha=list(im.getchannel('A').get_flattened_data());assert set(alpha)=={0,255}
 box=im.getbbox();assert box and box[3]==16 and 16-box[1]<=height
 mask=bytes(1 if v else 0 for v in alpha);h=hashlib.sha256(mask).hexdigest();assert h not in hashes;hashes.add(h)
 visible={(x,y) for y in range(16) for x in range(16) if im.getpixel((x,y))[3]}
 # All main stems must connect to the ground; report stray pixels explicitly.
 grounded=set(p for p in visible if p[1]==15);pending=list(grounded)
 while pending:
  x,y=pending.pop()
  for dx in (-1,0,1):
   for dy in (-1,0,1):
    q=(x+dx,y+dy)
    if q in visible and q not in grounded:grounded.add(q);pending.append(q)
 stray=len(visible-grounded)
 assert stray<=2,(name,'disconnected art pixels',stray)
 model=json.loads((RES/f'assets/fallofherovgadia/models/block/{name}.json').read_text());assert model['parent']=='minecraft:block/cross' and model['render_type']=='minecraft:cutout' and 'tintindex' not in model
 assert model['textures']['cross']==f'fallofherovgadia:block/{name}'
 item=json.loads((RES/f'assets/fallofherovgadia/models/item/{name}.json').read_text());assert item['parent']=='minecraft:item/generated' and item['textures']['layer0']==model['textures']['cross']
 states=json.loads((RES/f'assets/fallofherovgadia/blockstates/{name}.json').read_text());assert {s['y'] for s in states['variants']['']}=={0,90,180,270}
 loot=json.loads((RES/f'data/fallofherovgadia/loot_table/blocks/{name}.json').read_text());assert loot['pools'][0]['rolls']==1 and loot['pools'][0]['entries']==[{'type':'minecraft:item','name':f'fallofherovgadia:{name}'}]
 bb=json.loads((OUT/'blockbench'/f'{name}.bbmodel').read_text());assert len(bb['elements'])==2 and not bb['animations'];assert base64.b64decode(bb['textures'][0]['source'].split(',')[1])==png
 for base in (RES,OUT/'src/main/resources'):assert (base/f'assets/fallofherovgadia/textures/block/{name}.png').read_bytes()==png
 for lang,label in (('ru_ru',ru),('en_us',en)):
  labels=json.loads((RES/f'assets/fallofherovgadia/lang/{lang}.json').read_text());assert labels['block.fallofherovgadia.'+name]==label
 result=dict(id='fallofherovgadia:'+name,size=[16,16],visible_bounds=list(box),opaque_texels=len(visible),ground_connected_texels=len(grounded),stray_pixels=stray,binary_alpha=True,unique_silhouette=True,block_item_and_loot_references_valid=True,embedded_texture_matches=True);results.append(result);print(result)
for lang in ('ru_ru','en_us'):
 path=f'src/main/resources/assets/fallofherovgadia/lang/{lang}.json';before=json.loads(subprocess.check_output(['git','show','HEAD:'+path],cwd=ROOT));after=json.loads((ROOT/path).read_text());assert all(after[k]==v for k,v in before.items())
tag=json.loads((RES/'data/fallofherovgadia/tags/block/corrupted_plant_soils.json').read_text());assert tag['replace'] is False and '#minecraft:dirt' in tag['values'] and {'id':'fallofherovgadia:corrupted_soil','required':False} in tag['values']
for name in ('CorruptedPlantBlock.java','CorruptedPlants.java'):
 src=ROOT/'src/main/java/com/herovgad/fallofherovgadia'/name;copy=OUT/'src/main/java/com/herovgad/fallofherovgadia'/name;assert src.read_bytes()==copy.read_bytes()
# Verify the standalone kit and active resource tree have identical artifacts.
for f in (OUT/'src/main/resources').rglob('*'):
 if f.is_file():assert f.read_bytes()==(RES/f.relative_to(OUT/'src/main/resources')).read_bytes()
(OUT/'validation.json').write_text(json.dumps(dict(resource_checks=results,existing_language_entries_preserved=True,custom_soil_tag_valid=True,java_compiled=False,minecraft_runtime_tested=False),indent=2))
