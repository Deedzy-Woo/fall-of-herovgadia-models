package com.herovgad.fallofherovgadia.client.particle;

import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.particle.*;
import net.minecraft.core.particles.*;
import java.util.Optional;

public final class CorruptedHayFlyParticle extends TextureSheetParticle {
    public static final int GLOBAL_LIMIT=CorruptedParticleBudget.FLY_LIMIT;
    private static final ParticleGroup GROUP=new ParticleGroup(GLOBAL_LIMIT);
    private final double anchorX,anchorY,anchorZ;
    private double targetX,targetY,targetZ;
    private int retarget,hover,stuck;
    private CorruptedHayFlyParticle(ClientLevel level,double x,double y,double z,SpriteSet sprites){
        super(level,x,y,z);anchorX=x;anchorY=y;anchorZ=z;
        lifetime=70+random.nextInt(51);quadSize=0.018F+random.nextFloat()*0.008F;
        gravity=0;friction=0.72F;hasPhysics=true;setSize(0.02F,0.02F);
        pickSprite(sprites);chooseTarget();
    }
    private void chooseTarget(){
        targetX=anchorX+(random.nextDouble()-0.5)*0.95;
        targetY=anchorY+(random.nextDouble()-0.5)*0.65;
        targetZ=anchorZ+(random.nextDouble()-0.5)*0.95;
        retarget=4+random.nextInt(10);hover=random.nextInt(4)==0?3+random.nextInt(6):0;
    }
    @Override public void tick(){
        if(--retarget<=0)chooseTarget();
        if(hover-->0){xd*=0.45;yd*=0.45;zd*=0.45;}
        else {
            xd=Math.clamp(xd+(targetX-x)*0.09,-0.055,0.055);
            yd=Math.clamp(yd+(targetY-y)*0.08,-0.04,0.04);
            zd=Math.clamp(zd+(targetZ-z)*0.09,-0.055,0.055);
        }
        super.tick();if(!isAlive())return;
        if(x==xo&&y==yo&&z==zo){if(++stuck>8){remove();return;}}else stuck=0;
        if(Math.abs(x-anchorX)>0.7||Math.abs(z-anchorZ)>0.7||Math.abs(y-anchorY)>0.5){remove();return;}
        alpha=Math.min(1,Math.min(age/3F,(lifetime-age)/7F));
    }
    @Override public ParticleRenderType getRenderType(){return ParticleRenderType.PARTICLE_SHEET_TRANSLUCENT;}
    @Override public Optional<ParticleGroup> getParticleGroup(){return Optional.of(GROUP);}
    public static final class Provider implements ParticleProvider<SimpleParticleType>{
        private final SpriteSet sprites;public Provider(SpriteSet sprites){this.sprites=sprites;}
        @Override public Particle createParticle(SimpleParticleType t,ClientLevel l,double x,double y,double z,double dx,double dy,double dz){
            if(!CorruptedParticleBudget.allow(l,x,y,z,true))return null;
            var p=new CorruptedHayFlyParticle(l,x,y,z,sprites);CorruptedParticleBudget.track(l,p,true);return p;
        }
    }
}
