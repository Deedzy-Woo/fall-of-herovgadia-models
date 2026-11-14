package com.herovgad.fallofherovgadia.client.particle;

import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.particle.*;
import net.minecraft.core.particles.*;
import java.util.Optional;

public final class CorruptedSoilVaporParticle extends TextureSheetParticle {
    public static final float MIN_ALPHA=0.48F, MAX_ALPHA=0.60F;
    public static final double MIN_RISE_SPEED=0.007, MAX_RISE_SPEED=0.012;
    private static final ParticleGroup GROUP=new ParticleGroup(CorruptedParticleBudget.VAPOR_LIMIT);
    private final float initialAlpha, initialSize;
    private final double startY, rise, driftX, driftZ, phase;
    private CorruptedSoilVaporParticle(ClientLevel level,double x,double y,double z,double dx,double dy,double dz,SpriteSet sprites) {
        super(level,x,y,z);startY=y;lifetime=72+random.nextInt(37);
        gravity=0;friction=1;hasPhysics=true;setSize(0.06F,0.06F);
        driftX=Math.clamp(dx,-0.0025,0.0025);driftZ=Math.clamp(dz,-0.0025,0.0025);
        rise=Math.clamp(dy,MIN_RISE_SPEED,MAX_RISE_SPEED);phase=random.nextDouble()*Math.PI*2;
        initialSize=0.24F+random.nextFloat()*0.12F;quadSize=initialSize;
        initialAlpha=MIN_ALPHA+random.nextFloat()*(MAX_ALPHA-MIN_ALPHA);alpha=0;
        pickSprite(sprites); // one of five distinct silhouettes, stable for its whole life
    }
    @Override public void tick() {
        float progress=(float)age/lifetime;
        xd=driftX+Math.sin(phase+age*0.16)*0.0025;
        zd=driftZ+Math.cos(phase*1.3+age*0.13)*0.002;
        yd=rise*(0.88+0.12*Math.sin(phase+age*0.09))*(1-progress*0.2);
        super.tick();if(!isAlive())return;
        float fadeIn=Math.min(1,age/8F),fadeOut=Math.min(1,(lifetime-age)/26F);
        alpha=initialAlpha*fadeIn*fadeOut;
        quadSize=initialSize*(1+0.3F*progress);
        if(y-startY>1.4 || age>8 && y==yo)remove();
    }
    @Override public ParticleRenderType getRenderType(){return ParticleRenderType.PARTICLE_SHEET_TRANSLUCENT;}
    @Override public Optional<ParticleGroup> getParticleGroup(){return Optional.of(GROUP);}
    public static final class Provider implements ParticleProvider<SimpleParticleType> {
        private final SpriteSet sprites;
        public Provider(SpriteSet sprites){this.sprites=sprites;}
        @Override public Particle createParticle(SimpleParticleType t,ClientLevel l,double x,double y,double z,double dx,double dy,double dz){
            if(!CorruptedParticleBudget.allow(l,x,y,z,false))return null;
            var p=new CorruptedSoilVaporParticle(l,x,y,z,dx,dy,dz,sprites);CorruptedParticleBudget.track(l,p,false);return p;
        }
    }
}
