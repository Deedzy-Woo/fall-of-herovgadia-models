"""Generate four decorative cross models, vanilla resources and integration kit.
16x16 texture inputs live in corrupted_plants/textures. Existing unrelated
resources are untouched; language maps are merged by key, never replaced.
"""
from pathlib import Path
import json,base64,uuid,shutil
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'corrupted_plants';RES=ROOT/'src/main/resources'
PLANTS=[('small',6,5,'Осквернённый сухой пучок','Corrupted Dry Tuft'),('medium',10,11,'Осквернённый сорняк','Corrupted Weed'),('tall',6,15,'Высокий осквернённый стебель','Tall Corrupted Stalk'),('withered_bush',15,11,'Осквернённый мёртвый куст','Corrupted Withered Bush')]
def write(path,data):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def resource(path,data):
 write(RES/path,data);write(OUT/'src/main/resources'/path,data)
def build():
 langs={'ru_ru':{},'en_us':{}}
 for variant,width,height,ru,en in PLANTS:
  name='corrupted_plant_'+variant;tex=OUT/'textures'/f'{name}.png'
  target=Path('assets/fallofherovgadia/textures/block')/tex.name
  for base in (RES,OUT/'src/main/resources'):
   (base/target).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(tex,base/target)
  resource(Path(f'assets/fallofherovgadia/models/block/{name}.json'),{'parent':'minecraft:block/cross','render_type':'minecraft:cutout','textures':{'cross':f'fallofherovgadia:block/{name}'}})
  resource(Path(f'assets/fallofherovgadia/models/item/{name}.json'),{'parent':'minecraft:item/generated','textures':{'layer0':f'fallofherovgadia:block/{name}'}})
  resource(Path(f'assets/fallofherovgadia/blockstates/{name}.json'),{'variants':{'':[{'model':f'fallofherovgadia:block/{name}','y':angle} for angle in (0,90,180,270)]}})
  resource(Path(f'data/fallofherovgadia/loot_table/blocks/{name}.json'),{'type':'minecraft:block','pools':[{'rolls':1,'entries':[{'type':'minecraft:item','name':f'fallofherovgadia:{name}'}],'conditions':[{'condition':'minecraft:survives_explosion'}]}]})
  for lang,label in (('ru_ru',ru),('en_us',en)):langs[lang]['block.fallofherovgadia.'+name]=label
  elements=[]
  for index,angle in enumerate((-45,45)):
   elements.append({'name':f'cross_plane_{index+1}','type':'cube','uuid':str(uuid.uuid5(uuid.NAMESPACE_URL,name+'/plane/'+str(index))),'from':[.8,0,8],'to':[15.2,16,8],'origin':[8,8,8],'rotation':[0,angle,0],'rescale':True,'shade':False,'faces':{side:{'uv':[0,0,16,16],'texture':0,'rotation':0} for side in ('north','south')}})
   elements[-1]['faces'].update({side:{'uv':[0,0,0,0],'texture':None,'rotation':0} for side in ('up','down','east','west')})
  model={'meta':{'format_version':'4.10','model_format':'java_block','box_uv':False},'name':name,'resolution':{'width':16,'height':16},'elements':elements,'outliner':[e['uuid'] for e in elements],'textures':[{'name':tex.name,'path':'../textures/'+tex.name,'id':'0','uuid':str(uuid.uuid5(uuid.NAMESPACE_URL,name+'/texture')),'width':16,'height':16,'uv_width':16,'uv_height':16,'render_mode':'default','render_sides':'double','source':'data:image/png;base64,'+base64.b64encode(tex.read_bytes()).decode()}],'animations':[]}
  write(OUT/'blockbench'/f'{name}.bbmodel',model)
 for lang,additions in langs.items():
  path=RES/f'assets/fallofherovgadia/lang/{lang}.json';current=json.loads(path.read_text()) if path.exists() else {};current.update(additions);write(path,current)
  write(OUT/f'lang_additions/{lang}.json',additions)
  # Do not ship a partial file at the live lang path: use merge helper below.
 resource(Path('data/fallofherovgadia/tags/block/corrupted_plant_soils.json'),{'replace':False,'values':['#minecraft:dirt',{'id':'fallofherovgadia:corrupted_soil','required':False}]})
 print('Built 4 Blockbench projects and block/item resources; merged language entries.')
if __name__=='__main__':build()
