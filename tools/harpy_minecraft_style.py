"""Cuboid harpy with wing arms, matted layered hair and restrained surface detail."""
import hashlib
import random
from PIL import Image, ImageDraw


def build_geometry(cube, beam, group, groups):
    root=group('root',(0,0,0))
    pelvis=group('pelvis',(0,18,1),root)
    abdomen=group('abdomen',(0,20,.5),pelvis)
    chest=group('chest',(0,24,0),abdomen)
    neck=group('neck',(0,29,-.5),chest)
    head=group('head',(0,31,-2),neck)
    beak=group('beak_lower',(0,31.65,-5.4),head)
    hair=group('hair',(0,37,-2),head)
    plumage=group('hip_plumage',(0,18,2),pelvis)
    tail=group('tail_feathers',(0,18,3),pelvis)

    def rag(name,a,b,width,mat,parent):
        mid=[a[k]+(b[k]-a[k])*.77 for k in range(3)]
        beam(name+'_broad',a,mid,width,1,mat,parent)
        start=[a[k]+(b[k]-a[k])*.755 for k in range(3)]
        # Only a few primaries receive a third torn step. Keep the broad fan.
        worn=any(name.endswith(f'primary_{i:02d}') for i in (1,3,5))
        if worn:
            end=[a[k]+(b[k]-a[k])*.925 for k in range(3)]
            beam(name+'_step',start,end,max(1,width-1),.8,mat,parent)
            end2=[a[k]+(b[k]-a[k])*.915 for k in range(3)]
            beam(name+'_torn_tip',end2,b,max(1,width-2.2),.65,mat,parent)
        else:
            beam(name+'_step',start,b,max(1,width-1),.8,mat,parent)

    def claw(name,a,b,c,parent,width=1):
        base=group(name,a,parent)
        hook=group(name+'_hook',b,base)
        beam(name+'_base',a,b,width,1,'claw',base)
        beam(name+'_hook_point',b,c,width*.72,.75,'claw',hook)

    # Minecraft-like body masses. Ribs, tendons, hollows and scales are painted.
    cube('pelvis_core',(0,18.5,1),(6,3,4),'skin',pelvis)
    cube('waist',(0,21,.5),(4,4,3),'skin',abdomen)
    cube('ribcage',(0,26,0),(6.5,8,4),'skin',chest)
    cube('clavicle',(0,29.5,-.5),(8,1,3),'bone',chest)
    beam('neck_tendon',(0,29,-.5),(0,32,-2),2,2,'skin',neck)
    for s,side in [(-1,'r'),(1,'l')]:
        beam('raised_rib_'+side,(s*.6,26.5,-2.15),(s*3,27.1,-1.9),.6,.55,'bone',chest)
        beam('lower_raised_rib_'+side,(s*.6,24.8,-2.15),(s*2.7,25.4,-1.9),.5,.5,'bone',chest)

    # A single readable block head; eyes/cheek hollows are pixel art, not tiny cubes.
    cube('skull',(0,34,-2.5),(7,7,6),'skin',head)
    for s,side in [(-1,'r'),(1,'l')]:
        cube('brow_'+side,(s*1.75,35.25,-5.65),(2,.5,.6),'bone',head,(0,0,s*6))
        cube('cheekbone_'+side,(s*2.45,32.45,-5.35),(1.1,.85,.8),'bone',head,(0,s*12,-s*10))
    cube('beak_cere',(0,32.65,-5.65),(1.85,1.6,1.3),'bone',head)
    # A pale projecting bridge, a steep descending hook and a narrow inward tip.
    # Each section is a rotated cuboid; the silhouette follows the first version.
    beam('beak_bridge',(0,33.05,-5.8),(0,32.0,-7.4),1.75,1.3,'bone',head)
    beam('beak_hook',(0,32.12,-7.4),(0,30.05,-8.05),1.3,1.1,'beak',head)
    beam('beak_point',(0,30.15,-8.05),(0,29.12,-7.35),.65,.7,'beak',head)
    beam('lower_beak',(0,31.55,-5.6),(0,30.85,-7.05),1.05,.65,'beak',beak)

    # Layered matted crown, temples and irregular long locks, as in the concept.
    # Volumes stay broad; these remain cuboids rather than many thin hair cards.
    cube('hair_cap',(0,37.25,-2.25),(7.6,1.35,6.8),'hair',hair)
    cube('hair_crown_l',(1.65,38,-2.1),(3.7,.85,6.2),'hair',hair,(8,0,-10))
    cube('hair_crown_r',(-1.9,37.85,-2.15),(3.45,.8,6.1),'hair',hair,(7,0,12))
    cube('hair_crown_part',(-.1,38.35,-2),(1.6,.6,5.7),'hair',hair,(9,0,-6))
    cube('hair_crown_back',(0,37.4,.8),(6.9,1,2.2),'hair',hair,(12,0,0))
    back=group('hair_back',(0,37.1,.6),hair)
    beam('hair_back',(0,37.1,.6),(0,26.5,4),6.9,1.5,'hair',back)
    beam('hair_back_torn_l',(-2,27,3.8),(-2.5,24,4.2),2,1.3,'hair',back)
    beam('hair_back_torn_r',(1.5,27,3.8),(1.8,25,4.2),3,1.3,'hair',back)
    for i,(x,endx,y,z,width) in enumerate([(-2.2,-2.5,24.3,4.9,1.6),(-.3,.2,23.5,5.3,1.55),(2,2.7,25,4.8,1.7)]):
        a=(x,35.5,1.85)
        mid=(x*.7+endx*.3,29,3.8)
        beam(f'hair_back_layer_{i}_upper',a,mid,width,1.1,'hair',back)
        beam(f'hair_back_layer_{i}_torn',mid,(endx,y,z),width*.72,.9,'hair',back)
    for s,side in [(-1,'r'),(1,'l')]:
        lock=group('hair_'+side,(s*3,36,-4),hair)
        beam('hair_front_'+side,(s*3,36,-4),(s*3.4,27+(s+1)*.5,-3),1.5,1.5,'hair',lock)
        beam('hair_loose_'+side,(s*3.3,33,-1),(s*3.75,25.5+(s+1)*.5,.5),.9,1,'hair',lock)
        beam('hair_temple_'+side,(s*3.5,36,-1.9),(s*3.75,29.2,-.3),1.5,2.2,'hair',lock)
    cube('hair_fringe',(-1.75,36.5,-5.25),(3.5,1.5,1),'hair',hair)
    cube('hair_fringe_r',(1.6,36.5,-5.3),(2.2,1.4,.9),'hair',hair,(0,0,-11))
    beam('hair_forelock',(-2.1,36.4,-5.6),(-2.6,31.9,-5.25),1,.8,'hair',hair)

    for s,side in [(-1,'right'),(1,'left')]:
        hp=(s*2,18,1);kn=(s*3,13,0);hk=(s*3.5,8,3);an=(s*3.5,4,0)
        thigh=group(side+'_thigh',hp,pelvis)
        shin=group(side+'_shin',kn,thigh)
        tarsus=group(side+'_tarsus',hk,shin)
        foot=group(side+'_foot',an,tarsus)
        beam(side+'_thigh',hp,kn,2,2.5,'skin',thigh)
        beam(side+'_shin',kn,hk,1.5,1.5,'skin',shin)
        beam(side+'_tarsus',hk,an,1.5,1.5,'bone',tarsus)
        cube(side+'_foot_pad',(s*3.5,3.5,-.75),(3,1.5,2.5),'claw',foot)
        for j in range(3):
            x=s*(2.5+j)
            spread=s*(j-1)*.5
            claw(f'{side}_toe_{j+1}',(x,3,-1.5),(x+spread,2,-3.5-(.5 if j==1 else 0)),
                 (x+spread,1,-3),foot)
        claw(side+'_rear_toe',(s*3.5,3,.25),(s*3.25,2,2),(s*3.25,1,1.5),foot)

        # The arms ARE the wings: shoulder, upper arm, forearm and carpal joint.
        # There are no separate human arms or hanging hands beneath the wings.
        wsh=(s*4,28.5,.5);wel=(s*9.5,34,2.5);wwr=(s*14.5,42,3)
        wtip=(s*35.5,38.5,3)
        wing=group(side+'_wing',wsh,chest)
        upper=group(side+'_wing_upper',wsh,wing)
        wfore=group(side+'_wing_forearm',wel,upper)
        whand=group(side+'_wing_hand',wwr,wfore)
        prim=group(side+'_wing_primaries',wwr,whand)
        cov=group(side+'_wing_coverts',wwr,whand)
        cube(side+'_wing_shoulder',wsh,(2,2.5,2.5),'bone',upper)
        beam(side+'_shoulder_feather',(s*5.5,30,2.3),(s*6.8,27.2,2.6),1.8,.6,'brown',upper)
        beam(side+'_wing_upper_bone',wsh,wel,2.25,2.25,'bone',upper)
        beam(side+'_wing_forearm_bone',wel,wwr,2,2,'bone',wfore)
        beam(side+'_wing_leading_edge',wwr,wtip,1.5,1.5,'bone',whand)
        cube(side+'_wing_wrist',(wwr[0],41.8,2.5),(3,2.2,2.5),'bone',whand)
        beam(side+'_wing_end',wtip,(s*38,38,3),1,1,'brown',whand)
        # Two grasping fingers and an opposing thumb emerge from the carpus.
        # Their hierarchy follows the wing when folding, flapping or grasping.
        for j,x in enumerate((13.7,15.2),start=1):
            claw(f'{side}_wing_finger_{j}',(s*x,41.5,1.5),
                 (s*(x+.1),39.6,-.15),(s*(x-.1),38.45,.6),whand,.95)
        claw(side+'_wing_thumb',(s*13.15,42.1,1.9),
             (s*11.9,40.8,.6),(s*12.25,39.7,1.1),whand,1)
        mats=['brown','umber','rust','brown','ash','brown']
        for j in range(6):
            u=j/5
            a=(s*(14.5+20.5*u),41.25-3.25*u,3.75)
            endy=17.5+14*u+[1,-1,1.5,-.5,1,-.5][j]
            if s<0:endy += [1,0,-1.5,.5,0,1][j]
            b=(s*(11.5+26*u),endy,4.25)
            rag(f'{side}_primary_{j+1:02d}',a,b,4.5,mats[j],prim)
        for j,(x,y) in enumerate([(17,40),(24,39),(31.5,38)]):
            beam(f'{side}_covert_panel_{j}',(s*x,y,3.1),
                 (s*(x+1),y-7+(j*.5),3.1),7.5,.9,'brown' if j!=1 else 'umber',cov)
        beam(side+'_covert_torn_accent',(s*22,35,2.75),(s*23.5,31,2.8),3,.7,'umber',cov)
        beam(side+'_covert_outer_accent',(s*31,34,2.75),(s*32.5,31,2.8),2,.7,'brown',cov)
        rag(side+'_secondary_inner',(s*6,30.5,3),(s*5.5,21.5,3.5),3.5,'brown',upper)
        rag(side+'_secondary_outer',(s*10.5,35,3),(s*9,18.5+(s+1)*.5,3.5),4,'umber',wfore)

    # A few significant torn remnants, with no ornamental micro-cubes.
    for s,side in [(-1,'r'),(1,'l')]:
        beam('hip_rag_'+side,(s*2.5,19,2),(s*4,14,3),2.5,1,'rust',plumage)
        beam('flank_rag_'+side,(s*3,19,-.5),(s*3.75,15,.5),2,1,'umber',plumage)
    for j in range(3):
        x=(j-1)*1.75
        beam(f'tail_{j}',(x,18,3),(x*1.5,12.5+abs(x)*.5,8),2.5,1,
             ['brown','rust','ash'][j],tail)

    chest['rotation']=[-13.5,0,0]
    for g in groups:
        n=g['name']
        if n in ('left_wing','right_wing'):g['rotation']=[13.5,0,0]
        if n in ('left_thigh','right_thigh'):g['rotation']=[22.5,0,0]
        if n in ('left_shin','right_shin'):g['rotation']=[-45,0,0]
        if n in ('left_tarsus','right_tarsus'):g['rotation']=[22.5,0,0]
    return root


def paint_face(w,h,mat,name,face,palettes):
    """Hand-placed pixel motifs with seeded weathering, at 1.5 texels per unit."""
    seed=int(hashlib.sha256(f'{name}/{face}'.encode()).hexdigest()[:16],16)
    rr=random.Random(seed)
    pal=palettes[mat]
    im=Image.new('RGBA',(w,h),pal[2]+(255,))
    d=ImageDraw.Draw(im)
    def rect(box,index):
        x0,y0,x1,y1=[int(v) for v in box]
        x0=max(0,min(w-1,x0));x1=max(x0,min(w-1,x1))
        y0=max(0,min(h-1,y0));y1=max(y0,min(h-1,y1))
        d.rectangle((x0,y0,x1,y1),fill=pal[index]+(255,))
    def motif(box,index,grid=(7,8)):
        x0,y0,x1,y1=box
        rect((x0*w/grid[0],y0*h/grid[1],(x1+1)*w/grid[0]-1,(y1+1)*h/grid[1]-1),index)
    if mat in ('skin','bone'):
        if w>=3 and h>=4:
            # Uneven pallor, dry skin and worn bone planes, in small clusters.
            for _ in range(min(6,max(1,w*h//30))):
                x=rr.randrange(w);y=rr.randrange(h)
                rect((x,y,x+rr.choice([0,1]),y+rr.choice([1,2])),rr.choice([1,3]))
            rect((0,h//2,0,min(h-1,h//2+2)),1)
            if mat=='bone':
                rect((w-1,1,w-1,h-2),3)
                if w>=4:rect((w-2,h//3,w-2,h//3+1),1)
            elif h>=8:
                # A thin crease and a muted dried mark on desiccated skin.
                x=rr.randrange(max(1,w-1));y=rr.randrange(2,h-2)
                rect((x,y,x,y+1),0)
                if rr.random()<.35:
                    d.point((min(w-1,x+1),y+1),fill=palettes['hollow'][3]+(255,))
        if name=='ribcage' and face=='north':
            for y in (2,4,6):
                motif((0,y,2,y),1);motif((4,y,6,y),1)
                motif((1,y-1,2,y-1),3);motif((4,y-1,5,y-1),3)
            motif((3,1,3,6),3)
            rect((w//2-1,h-2,w//2+1,h-1),1)
        if name=='ribcage' and face=='south':
            for y in range(1,h-1,3):rect((w//2,y,w//2,y+1),1)
            rect((1,2,1,h//2),3);rect((w-2,2,w-2,h//2),3)
        if name=='waist' and face=='north':
            rect((w//2-1,1,w//2,h-2),1)
            rect((w//2,h//2,w//2,h//2),0)
        if any(k in name for k in ('arm','thigh','shin')) and face in ('north','south') and h>=6:
            rect((max(0,w//2-1),1,max(0,w//2-1),h-2),3)
            rect((0,h-3,w-1,h-2),1)
        if 'tarsus' in name and h>=4:
            for y in range(1,h,3):
                rect((0,y,w-1,y),1)
                if y+1<h:rect((0,y+1,max(0,w-2),y+1),3)
    elif mat=='hair':
        if w>=2 and h>=3:
            # Broken streaks, short crossed fibres and a swept part on the crown.
            crown=('crown' in name or name=='hair_cap') and face=='up' and w>=4
            if crown:
                for x in range(0,w,3):
                    ex=max(0,min(w-1,x+(1 if x<w//2 else -1)))
                    d.line((x,0,ex,h-1),fill=pal[1]+(255,))
                    if x+1<w:
                        rect((x+1,1,x+1,min(h-1,rr.choice([2,3]))),3)
                for y in range(h):
                    px=min(w-1,w//2+(y//4)%2)
                    rect((px,y,px,y),0)
            else:
                for x in range(0,w,3):
                    rect((x,1,x,h-2),1)
                    for y in range(2+(x%3),h-1,5):
                        length=rr.choice([1,2,3])
                        rect((min(w-1,x+1),y,min(w-1,x+1),min(h-1,y+length)),3)
                        if x+2<w and y+1<h:
                            d.line((x+1,y,x+2,y+1),fill=pal[2]+(255,))
                rect((0,0,w-1,0),1)
                if h>6:rect((w-1,h//2,w-1,h-1),0)
    elif mat in ('brown','umber','rust','ash'):
        if h>=4 and w>=2:
            # Vane edge, intermittent shaft and short offset barbs.
            rect((0,0,0,h-1),1)
            shaft=w//2
            for y in range(h):
                if y%7!=6:rect((shaft,y,shaft,y),3 if y%4 else 2)
            if w>=4:
                for y in range(2,h-1,3):
                    rect((max(0,shaft-2),y,min(w-1,shaft-1),min(h-1,y+1)),1)
                    rect((min(w-1,shaft+1),max(0,y-1),min(w-1,shaft+2),y),1)
                # Subtle clumped pigment and rubbed, grey feather tips.
                for _ in range(max(1,w*h//45)):
                    x=rr.randrange(w);y=rr.randrange(h)
                    rect((x,y,min(w-1,x+1),min(h-1,y+2)),rr.choice([1,2,3]))
                if 'panel' in name or 'accent' in name:
                    accent=palettes['rust' if rr.random()<.6 else 'ash'][1]+(255,)
                    x=rr.randrange(max(1,w-2));y=rr.randrange(max(1,h-3))
                    d.rectangle((x,y,min(w-1,x+1),min(h-1,y+2)),fill=accent)
                if ('step' in name or 'tip' in name) and rr.random()<.65:
                    d.point((w-1,h-1),fill=palettes['ash'][2]+(255,))
            rect((0,0,w-1,0),1)
    elif mat=='claw':
        if w>=2:
            rect((w-1,0,w-1,h-1),3)
            if h>=4:rect((0,h//2,0,h//2+1),1)
            rect((w-1,h-1,w-1,h-1),2)
    elif mat=='beak':
        if w>=2:
            rect((0,0,0,h-1),1)
            rect((w-1,0,w-1,max(0,h-2)),3)
            rect((0,h-1,w-1,h-1),0)
    if name=='beak_cere' and face=='north' and w>=3:
        d.point((0,h//2),fill=palettes['hollow'][0]+(255,))
        d.point((w-1,h//2),fill=palettes['hollow'][0]+(255,))
    if name=='skull' and face=='north':
        # Preserve the Minecraft face, with deeper sockets and slight decay.
        def facebox(box,color):
            x0,y0,x1,y1=box
            a=int(x0*w/7);b=int(y0*h/7)
            c=max(a,int((x1+1)*w/7)-1);e=max(b,int((y1+1)*h/7)-1)
            d.rectangle((a,b,c,e),fill=color+(255,))
        dark=(29,25,25);rim=(100,88,73)
        facebox((1,2,2,3),dark);facebox((4,2,5,3),dark)
        facebox((0,1,2,1),rim);facebox((4,1,6,1),rim)
        facebox((1,4,1,4),rim);facebox((5,4,5,4),rim)
        facebox((2,5,4,6),pal[1])
        if w>=10:
            for u in (.29,.71):
                d.point((int(w*u),int(h*.43)),fill=palettes['eye_ember'][1]+(255,))
            d.point((1,h-3),fill=pal[3]+(255,))
            d.point((w-2,h-4),fill=palettes['hollow'][2]+(255,))
    return im
