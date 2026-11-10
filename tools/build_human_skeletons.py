"""Build three static, textured Blockbench skeleton decorations (pixel units).
Uses the committed 32x32 atlas; never modifies bone_piles or mod source.
"""
from pathlib import Path
import json,base64,uuid,math
import numpy as np
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parents[1]/'human_skeletons'
ATLAS=ROOT/'textures/human_skeletons.png'
def rx(a):return Rotation.from_euler('x',a,degrees=True).as_matrix()
def ry(a):return Rotation.from_euler('y',a,degrees=True).as_matrix()
def rz(a):return Rotation.from_euler('z',a,degrees=True).as_matrix()
SIDES=('east','west','up','down','south','north')
class Model:
 def __init__(self,name):self.name=name;self.elements=[];self.groups={};self.landmarks={}
 def cube(self,name,center,size,mat=0,R=None,group='body',head=False):
  R=np.eye(3) if R is None else R;c=np.array(center,dtype=float);size=np.array(size,dtype=float)
  uv={}
  for side in SIDES:
   if head:
    region={'north':[8,8,16,16],'south':[24,8,32,16],'west':[0,8,8,16],'east':[16,8,24,16],'up':[8,0,16,8],'down':[8,0,16,8]}[side]
   elif mat=='metal':region=[10,14,11,15]
   else:
    u=(mat%4)*8;v=24 if side in ('up','down') else 16
    a,b=(size[0],size[2]) if side in ('up','down') else ((size[2],size[1]) if side in ('east','west') else (size[0],size[1]))
    a=max(1,min(8,round(a)));b=max(1,min(8,round(b)));u+=(8-a)//2;v+=(8-b)//2;region=[u,v,u+a,v+b]
   uv[side]={'uv':region,'texture':0,'rotation':0}
  uid=str(uuid.uuid5(uuid.NAMESPACE_URL,self.name+'/'+group+'/'+name+'/'+str(len(self.elements))))
  element={'name':name,'type':'cube','uuid':uid,'from':(c-size/2).round(6).tolist(),'to':(c+size/2).round(6).tolist(),'origin':c.round(6).tolist(),'rotation':Rotation.from_matrix(R).as_euler('XYZ',degrees=True).round(6).tolist(),'faces':uv,'rescale':False,'shade':True,'visibility':True,'export':True,'autouv':0,'color':mat if isinstance(mat,int) else 7}
  self.elements.append(element);self.groups.setdefault(group,[]).append(uid)
 def bone(self,name,a,b,width=.95,shade=0,group=None,paired=False):
  a=np.array(a,float);b=np.array(b,float);v=b-a;L=np.linalg.norm(v);y=v/L
  x=np.cross(y,[0,0,1] if abs(y[2])<.92 else [1,0,0]);x/=np.linalg.norm(x);z=np.cross(x,y);R=np.column_stack((x,y,z));group=group or name
  if paired:
   for j,side in enumerate((-1,1)):
    self.cube(name+('_radius' if j==0 else '_ulna'),(a+b)/2+x*side*width*.32,[width*.49,L*.82,width*.65],shade,R,group)
  else:self.cube(name+'_shaft',(a+b)/2,[width,L*.83,width*.9],shade,R,group)
  for label,p in (('proximal',a),('distal',b)):
   self.cube(name+'_'+label,p,[width*1.35,width*.8,width*1.18],shade,R,group)
 def hand(self,name,wrist,direction,shade=0):
  w=np.array(wrist,float);v=np.array(direction,float);v/=np.linalg.norm(v)
  y=v;x=np.cross(y,[0,0,1] if abs(y[2])<.9 else [1,0,0]);x/=np.linalg.norm(x);z=np.cross(x,y);R=np.column_stack((x,y,z))
  self.cube(name+'_palm',w+v*.42,[1.2,.8,.52],shade,R,name)
  for i in range(3):self.cube(name+f'_finger_{i+1}',w+v*1.03+x*(i-1)*.36,[.26,.65,.34],shade,R,name)
  self.cube(name+'_thumb',w+v*.46+x*.81,[.3,.65,.35],shade,R@rz(-25),name)
 def foot(self,name,ankle,forward,shade=0):
  a=np.array(ankle,float);v=np.array(forward,float);v/=np.linalg.norm(v);x=np.cross([0,1,0],v);x/=np.linalg.norm(x);R=np.column_stack((x,[0,1,0],v))
  if np.linalg.det(R)<0:R[:,0]*=-1
  self.cube(name+'_heel',a,[1.6,.8,1.2],shade,R,name)
  for i in range(3):self.cube(name+f'_metatarsal_{i+1}',a+v*1.1+x*(i-1)*.5,[.4,.52,1.65],shade,R,name)
  self.cube(name+'_toes',a+v*1.95,[1.75,.48,.55],shade,R,name)
 def save(self):
  data={'meta':{'format_version':'4.10','model_format':'free','box_uv':False},'name':self.name,'resolution':{'width':32,'height':32},'elements':self.elements,'outliner':[{'name':g,'uuid':str(uuid.uuid5(uuid.NAMESPACE_URL,self.name+'/'+g)),'origin':[0,0,0],'rotation':[0,0,0],'export':True,'visibility':True,'isOpen':False,'children':children} for g,children in self.groups.items()], 'textures':[{'path':'../textures/human_skeletons.png','name':'human_skeletons.png','id':'0','uuid':str(uuid.uuid5(uuid.NAMESPACE_URL,'herovgadia/human_skeletons_atlas')),'width':32,'height':32,'uv_width':32,'uv_height':32,'render_mode':'default','render_sides':'auto','visible':True,'source':'data:image/png;base64,'+base64.b64encode(ATLAS.read_bytes()).decode()}], 'animations':[], 'display':{'gui':{'rotation':[25,35,0],'translation':[0,0,0],'scale':[.5,.5,.5]}},'variable_placeholders':''}
  (ROOT/'blockbench'/f'{self.name}.bbmodel').write_text(json.dumps(data,ensure_ascii=False,indent=2))
  (ROOT/f'{self.name}_landmarks.json').write_text(json.dumps(self.landmarks,indent=2))
  print(self.name,len(self.elements),'cuboids')
def build(name):
 m=Model(name)
 if name=='lying_skeleton':
  R=rx(90);origin=np.array([8,2.45,.25]);scale=.975
  def P(p):return origin+R@np.array(p)*scale
  headR=R@ry(16)@rz(-5);headC=P([0,28,0]);headC[1]=4.05
 elif name=='sitting_skeleton':
  R=rx(8);origin=np.array([8,2,8.0])-R@np.array([0,14,0])
  def P(p):return origin+R@np.array(p)
  headR=rx(-13)@ry(-11)@rz(9);headC=P([0,28,-.3])
 else:
  R=rz(-3);origin=np.array([8,-20,8])
  def P(p):return origin+R@np.array(p)
  headR=rx(-16)@ry(7)@rz(-6);headC=P([0,28,-.35])
 def C(n,c,s,shade=0,group='torso',Q=None):m.cube(n,P(c),s,shade,R if Q is None else R@Q,group)
 # Continuous spine, individual vertebrae, visible open rib cage.
 for i,y in enumerate(np.arange(14.8,24.1,1.28)):
  C(f'vertebra_{i+1}',[0,y,1.65],[1.22,.9,1.12],2,'spine')
  if i>0:C(f'spinous_process_{i+1}',[0,y,2.35],[.55,.48,.8],2,'spine')
 C('lumbar_connection',[0,14.3,1.25],[1.25,1.45,1.1],2,'spine')
 C('sternum',[0,19.7,-2.05],[.85,5.5,.65],0,'ribcage')
 for j,y in enumerate((16.5,18.05,19.6,21.15)):
  half=3.65 if j<3 else 3.35
  for side,sgn in (('left',-1),('right',1)):
   shade=(j+(sgn>0))%4
   C(f'{side}_rib_{j+1}_back',[sgn*half*.55,y+.15,1.72],[half*.95,.62,.66],shade,'ribcage',ry(sgn*8))
   C(f'{side}_rib_{j+1}_side',[sgn*half,y,.05],[.65,.66,3.7],shade,'ribcage')
   C(f'{side}_rib_{j+1}_front',[sgn*half*.55,y-.3,-1.93],[half*.98,.65,.68],shade,'ribcage',rz(sgn*7))
 for sgn,side in ((-1,'left'),(1,'right')):
  C(side+'_clavicle',[sgn*2.5,22.65,-.7],[4.35,.7,.85],0,'shoulders',rz(-sgn*5))
  C(side+'_scapula',[sgn*2.35,21.8,1.8],[2.2,2.45,.6],2,'shoulders',rz(sgn*12))
  C(side+'_ilium',[sgn*2.45,13.8,.55],[1.35,2.4,2.15],1,'pelvis',rz(-sgn*18))
  C(side+'_ischium',[sgn*1.8,12.65,-.05],[.95,1.35,2.4],1,'pelvis',rz(sgn*12))
 C('sacrum',[0,13.9,1.1],[1.4,2.35,1.2],2,'pelvis')
 C('pubic_arch',[0,12.5,-.95],[3.65,.75,.7],1,'pelvis')
 # Head is a full Steve-scale 8px skull with a thin U-shaped jaw, not a pedestal.
 m.cube('cranium',headC,[8,7,8],0,headR,'skull',head=True)
 for sgn in (-1,1):m.cube('jaw_ramus_'+str(sgn),headC+headR@np.array([sgn*3.0,-3.5,-.3]),[.9,1.7,5.1],2,headR,'skull')
 m.cube('mandible',headC+headR@np.array([0,-4.1,-3.0]),[6.7,.75,1],2,headR,'skull')
 neck=P([0,24,1.2]);m.bone('neck',P([0,23.35,1.6]),headC+headR@np.array([0,-3,1.2]),1.05,2,'neck')
 if name=='lying_skeleton':
  arms=[('left',[-5.4,21.8,0],[-6.4,16.2,-.7],[-7.0,10.8,-1.3]),('right',[5.4,21.8,0],[6.0,16.7,-.8],[2.8,12.5,-1.5])]
  legs=[('left',[-1.9,12.2,0],[-2.65,6.55,-1.15],[-3.55,.85,-1.0]),('right',[1.9,12.2,0],[2.8,6.7,-.9],[4.0,1.0,-1.3])]
  arms=[(s,*[P(v) for v in (a,b,c)]) for s,a,b,c in arms];legs=[(s,*[P(v) for v in (a,b,c)]) for s,a,b,c in legs]
  for side,shoulder,elbow,wrist in arms:elbow[1]=.95;wrist[1]=.75
  for side,hip,knee,ankle in legs:knee[1]=1.1;ankle[1]=.72
 elif name=='sitting_skeleton':
  arms=[('left',P([-5.2,22.2,0]),np.array([2.0,5.5,5.7]),np.array([3.1,2.2,1.4])),('right',P([5.2,22.2,0]),np.array([14,6.2,5]),np.array([13.5,2.2,.8]))]
  legs=[('left',np.array([6.0,2.4,7.8]),np.array([5.15,2.1,1.8]),np.array([4.0,1.0,-4.15])),('right',np.array([10,2.4,7.8]),np.array([11.1,2.65,2]),np.array([12,1.0,-3.6]))]
 else:
  arms=[('left',P([-5.1,22.5,0]),np.array([4.7,8.7,8]),np.array([7.35,14.5,8])),('right',P([5.1,22.5,0]),np.array([11.6,8.9,8.25]),np.array([8.65,14.5,8]))]
  legs=[('left',P([-1.9,12.2,0]),np.array([6.4,-13.9,8.05]),np.array([5.95,-19.55,8.45])),('right',P([1.9,12.2,0]),np.array([10.9,-13.65,9.1]),np.array([10.1,-19.1,9.9]))]
 for i,(side,shoulder,elbow,wrist) in enumerate(arms):
  m.bone(side+'_humerus',shoulder,elbow,1.05,i,'arm_'+side)
  m.bone(side+'_forearm',elbow,wrist,.98,i,'arm_'+side,paired=True)
  m.hand(side+'_hand',wrist,np.array(wrist)-elbow,i)
  m.landmarks[side+'_wrist']=np.array(wrist).round(5).tolist()
 for i,(side,hip,knee,ankle) in enumerate(legs):
  m.bone(side+'_femur',hip,knee,1.25,1+i,'leg_'+side)
  m.cube(side+'_patella',np.array(knee)+[0,0,-.47],[1.1,.85,.65],1+i,group='leg_'+side)
  m.bone(side+'_shin',knee,ankle,1.0,1+i,'leg_'+side,paired=True)
  forward=[0,0,-1] if name!='lying_skeleton' else [0,0,-1]
  m.foot(side+'_foot',ankle,forward,1+i)
 if name=='hanging_skeleton':
  for side,x in (('left',7.35),('right',8.65)):
   # Small cuff rings only. No chain or rope is included in the model.
   for z in (7.32,8.68):m.cube(side+'_cuff_edge_'+str(z),[x,15.12,z],[1.45,.48,.28],'metal',group='wrist_cuffs')
   for dx in (-.62,.62):m.cube(side+'_cuff_side_'+str(dx),[x+dx,15.12,8],[.24,.48,1.1],'metal',group='wrist_cuffs')
  m.landmarks['chain_connection']=[8,16,8]
  m.landmarks['placement_note']='Manual vanilla chain is centred above x=8,z=8; bottom of chain meets raised hands at y=16. No chain is part of this model.'
 # Ground the two floor poses by the actual transformed vertices.
 points=[]
 for e in m.elements:
  Rr=Rotation.from_euler('XYZ',e['rotation'],degrees=True).as_matrix();c=np.array(e['origin'])
  for corner in __import__('itertools').product(*zip(e['from'],e['to'])):points.append(Rr@(np.array(corner)-c)+c)
 bounds=np.array(points);low=bounds.min(0);high=bounds.max(0)
 if name!='hanging_skeleton':
  dy=.08-low[1]
  for e in m.elements:
   for key in ('from','to','origin'):e[key][1]=round(e[key][1]+dy,6)
  low[1]+=dy;high[1]+=dy
 m.landmarks['bounds_pixels']={'min':low.round(4).tolist(),'max':high.round(4).tolist()}
 m.landmarks['notes']='Static asset only; no animations, entities, block registration or multiblock implementation.'
 m.save()
if __name__=='__main__':
 for name in ('lying_skeleton','sitting_skeleton','hanging_skeleton'):build(name)
