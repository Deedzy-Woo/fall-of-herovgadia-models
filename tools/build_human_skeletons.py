"""Static vanilla-proportioned skeletons, posed without a bow.
The unchanged Minecraft 1.21.1 skeleton texture is embedded (64x32).
Head 8x8x8; torso 8x12x4; limb cross section 2x2. Elbows/knees
split the vanilla 12-texel limb skin into two continuous six-row regions.
Blockbench free models use Euler ZYX: SciPy extrinsic xyz, NOT intrinsic XYZ.
"""
from pathlib import Path
import base64,json,uuid,itertools,math
import numpy as np
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parents[1]/'human_skeletons'
ATLAS=ROOT/'textures/human_skeletons.png'
def rx(a):return Rotation.from_euler('x',a,degrees=True).as_matrix()
def ry(a):return Rotation.from_euler('y',a,degrees=True).as_matrix()
def rz(a):return Rotation.from_euler('z',a,degrees=True).as_matrix()
def uvbox(u,v,w,h,d):
 return {'west':[u,v+d,u+d,v+d+h],'north':[u+d,v+d,u+d+w,v+d+h],'east':[u+d+w,v+d,u+2*d+w,v+d+h],'south':[u+2*d+w,v+d,u+2*d+2*w,v+d+h],'up':[u+d,v,u+d+w,v+d],'down':[u+d+w,v,u+d+2*w,v+d]}
def bone_frame(a,b):
 a=np.array(a,float);b=np.array(b,float);y=b-a;L=np.linalg.norm(y);y/=L
 x=np.cross(y,[0,0,1] if abs(y[2])<.92 else [1,0,0]);x/=np.linalg.norm(x);z=np.cross(x,y)
 return (a+b)/2,np.array([2,L,2]),np.column_stack((x,y,z))
def separation(A,B):
 """Separating-axis OBB distance; positive means genuinely disjoint boxes."""
 ca,sa,ra=A;cb,sb,rb=B;delta=cb-ca
 axes=[*ra.T,*rb.T,*[np.cross(a,b) for a in ra.T for b in rb.T]];gap=-1e9
 for axis in axes:
  length=np.linalg.norm(axis)
  if length<1e-8:continue
  axis=axis/length
  gap=max(gap,abs(delta@axis)-np.abs(axis@ra)@(sa/2)-np.abs(axis@rb)@(sb/2))
 return float(gap)
class Model:
 def __init__(self,name):self.name=name;self.elements=[];self.groups={};self.landmarks={}
 def cube(self,name,c,size,R,uv,group):
  c=np.array(c,float);size=np.array(size,float);uid=str(uuid.uuid5(uuid.NAMESPACE_URL,self.name+'/'+name))
  e={'name':name,'type':'cube','uuid':uid,'from':(c-size/2).round(6).tolist(),'to':(c+size/2).round(6).tolist(),'origin':c.round(6).tolist(),'rotation':Rotation.from_matrix(R).as_euler('xyz',degrees=True).round(6).tolist(),'faces':{side:{'uv':coords,'texture':0,'rotation':0} for side,coords in uv.items()},'rescale':False,'shade':True,'visibility':True,'export':True,'autouv':0}
  self.elements.append(e);self.groups.setdefault(group,[]).append(uid)
 def limb(self,side,kind,a,b,c):
  self.landmarks[side+'_'+kind+'_joints']=[np.array(p,dtype=float).tolist() for p in (a,b,c)]
  base=40 if kind=='arm' else 0
  for index,(start,end) in enumerate(((a,b),(b,c))):
   centre,size,R=bone_frame(start,end);uv=uvbox(base,16,2,12,2)
   for face in ('west','north','east','south'):
    u,v,uu,vv=uv[face];uv[face]=[u,v+6*index,uu,v+6*(index+1)]
   self.cube(side+'_'+kind+('_upper' if index==0 else '_lower'),centre,size,R,uv,kind+'_'+side)
 def save(self):
  data={'meta':{'format_version':'4.10','model_format':'free','box_uv':False},'name':self.name,'resolution':{'width':64,'height':32},'elements':self.elements,'outliner':[{'name':g,'uuid':str(uuid.uuid5(uuid.NAMESPACE_URL,self.name+'/group/'+g)),'origin':[0,0,0],'rotation':[0,0,0],'export':True,'visibility':True,'isOpen':False,'children':children} for g,children in self.groups.items()],'textures':[{'path':'../textures/human_skeletons.png','name':'human_skeletons.png','id':'0','uuid':str(uuid.uuid5(uuid.NAMESPACE_URL,'herovgadia/vanilla_skeleton_atlas')),'width':64,'height':32,'uv_width':64,'uv_height':32,'render_mode':'default','render_sides':'auto','visible':True,'source':'data:image/png;base64,'+base64.b64encode(ATLAS.read_bytes()).decode()}],'animations':[],'display':{'gui':{'rotation':[25,35,0],'translation':[0,0,0],'scale':[.5,.5,.5]}}}
  (ROOT/'blockbench'/f'{self.name}.bbmodel').write_text(json.dumps(data,ensure_ascii=False,indent=2));(ROOT/f'{self.name}_landmarks.json').write_text(json.dumps(self.landmarks,indent=2));print(self.name,len(self.elements),'cuboids',flush=True)
def build(name):
 m=Model(name)
 if name=='lying_skeleton':
  R=rx(90);origin=np.array([8,2.15,.25]);scale=.975
  def P(p):return origin+R@np.array(p)*scale
  headR=R@ry(16)@rz(-5);headC=P([0,28,0]);headC[1]=4.45
 elif name=='sitting_skeleton':
  R=rx(8);origin=np.array([8,2.5,8])-R@np.array([0,12,0])
  def P(p):return origin+R@np.array(p)
  headR=rx(-13)@ry(-11)@rz(9);headC=P([0,28,-.3])
 else:
  R=rz(-3);origin=np.array([8,-20,8])
  def P(p):return origin+R@np.array(p)
  headR=rx(-10)@ry(5)@rz(-4);headC=P([0,28,-2]);headC[1]+=.5
 m.cube('cranium',headC,[8,8,8],headR,uvbox(0,0,8,8,8),'skull')
 m.cube('torso',P([0,18,0]),[8,12,4],R,uvbox(16,16,8,12,4),'torso')
 if name=='lying_skeleton':
  arms=[('left',P([-5,23,0]),P([-6.4,17.2,-.7]),P([-7,11.4,-1.3])),('right',P([5,23,0]),P([6,17.5,-.8]),P([2.8,12.5,-1.5]))]
  legs=[('left',P([-2,12,0]),P([-2.65,6.2,-1.15]),P([-3.55,.35,-1])),('right',P([2,12,0]),P([2.8,6.3,-.9]),P([4,.4,-1.3]))]
  for _,_,elbow,wrist in arms:elbow[1]=1.15;wrist[1]=1.05
  for _,_,knee,ankle in legs:knee[1]=1.1;ankle[1]=1.05
 elif name=='sitting_skeleton':
  arms=[('left',P([-5,23,0]),np.array([2,7,5.5]),np.array([3,2.3,1.6])),('right',P([5,23,0]),np.array([14,7.2,5]),np.array([13.4,2.3,.9]))]
  legs=[('left',np.array([6,2.5,8]),np.array([5.15,2.1,2]),np.array([4,1.1,-3.9])),('right',np.array([10,2.5,8]),np.array([11.1,2.65,2.2]),np.array([12,1.1,-3.45]))]
 else:
  head=(headC,np.array([8,8,8]),headR)
  arms=[];clearances={}
  for side,sgn,wristx in (('left',-1,6.9),('right',1,9.1)):
   shoulder=P([sgn*5,23,0]);wrist=np.array([wristx,16.0,8.0]);best=None
   for offset,ey,ez in itertools.product((5.7,6.1,6.5,7.0,7.5),np.arange(10.5,14.01,.5),(7.0,8.0,9.0,10.0)):
    elbow=np.array([headC[0]+sgn*offset,ey,ez]);upper=bone_frame(shoulder,elbow);lower=bone_frame(elbow,wrist)
    gap=min(separation(upper,head),separation(lower,head))
    if gap<.25:continue
    length=np.linalg.norm(elbow-shoulder)+np.linalg.norm(wrist-elbow)
    score=(length-12)**2+.15*(offset-5.7)**2+.07*(ez-8)**2
    if best is None or score<best[0]:best=(score,elbow,gap,length)
   if best is None:raise RuntimeError('No collision-free raised arm found')
   _,elbow,gap,length=best;arms.append((side,shoulder,elbow,wrist));clearances[side]=round(gap,4)
   print(side,'raised-arm clearance',round(gap,3),'elbow',elbow.tolist(),flush=True)
  m.landmarks['arm_head_clearance_pixels']=clearances
  # Move the complete model after posing so wrists meet a chain at y=16.
  legs=[('left',P([-2,12,0]),np.array([6.4,-13.9,8.05]),np.array([5.95,-19.8,8.45])),('right',P([2,12,0]),np.array([10.9,-13.65,9.1]),np.array([10.1,-19.5,9.9]))]
 for side,a,b,c in arms:
  m.limb(side,'arm',a,b,c);m.landmarks[side+'_wrist']=np.array(c).round(5).tolist()
 for side,a,b,c in legs:m.limb(side,'leg',a,b,c)
 # Vanilla has a painted jaw and hands/feet in the limb skin, no added anatomy.
 points=[]
 for e in m.elements:
  r=Rotation.from_euler('xyz',e['rotation'],degrees=True).as_matrix();o=np.array(e['origin'])
  for p in itertools.product(*zip(e['from'],e['to'])):points.append(r@(np.array(p)-o)+o)
 bounds=np.array(points);low=bounds.min(0);high=bounds.max(0)
 dy=.08-low[1] if name!='hanging_skeleton' else 16-high[1]
 for e in m.elements:
  for k in ('from','to','origin'):e[k][1]=round(e[k][1]+dy,6)
 for key in ('left_wrist','right_wrist'):m.landmarks[key][1]=round(m.landmarks[key][1]+dy,5)
 for key,value in m.landmarks.items():
  if key.endswith('_joints'):
   for p in value:p[1]=round(p[1]+dy,6)
 low[1]+=dy;high[1]+=dy
 m.landmarks['bounds_pixels']={'min':low.round(4).tolist(),'max':high.round(4).tolist()}
 m.landmarks['anatomy']='Vanilla skeleton: 8x8x8 head, 8x12x4 torso, 2x2 arms/legs split at elbows and knees. No bow.'
 if name=='hanging_skeleton':m.landmarks['chain_connection']=[8,16,8]
 m.save()
if __name__=='__main__':
 for name in ('lying_skeleton','sitting_skeleton','hanging_skeleton'):build(name)
