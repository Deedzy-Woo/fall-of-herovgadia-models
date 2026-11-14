package com.herovgad.fallofherovgadia.client.particle;

import com.herovgad.fallofherovgadia.*;
import net.minecraft.client.Minecraft;
import net.minecraft.client.ParticleStatus;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import java.util.*;

/** Existing emitter, now usable without editing the common soil block class. */
@EventBusSubscriber(modid=FallOfHerovgadia.MODID,value=Dist.CLIENT)
public final class CorruptedSoilVapor {
    public static final int MIN_INTERVAL_TICKS=32,MAX_INTERVAL_TICKS=52,CELL_COOLDOWN_TICKS=16;
    public static final int DISCOVERY_CHECKS_PER_TICK=256;
    private static final int MAX_TRACKED_POSITIONS=1024;
    private static final ResourceLocation SOIL=ResourceLocation.fromNamespaceAndPath(FallOfHerovgadia.MODID,"corrupted_soil");
    private static final Map<ClientLevel,State> STATES=new WeakHashMap<>();
    private static final int[] D={-1,0,1};

    @SubscribeEvent public static void clientTick(ClientTickEvent.Post event){
        var mc=Minecraft.getInstance();var level=mc.level;
        if(level==null||mc.isPaused()||mc.options.particles().get()==ParticleStatus.MINIMAL)return;
        var soil=BuiltInRegistries.BLOCK.getOptional(SOIL).orElse(null);if(soil==null)return;
        var schedule=STATES.computeIfAbsent(level,l->new State());
        var camera=mc.gameRenderer.getMainCamera().getPosition();var center=BlockPos.containing(camera);
        // Fixed discovery work: never scan the complete field every frame or force chunk loads.
        for(int i=0;i<DISCOVERY_CHECKS_PER_TICK;i++){
            int n=schedule.cursor++%(41*41*13);if(schedule.cursor>=41*41*13)schedule.cursor=0;
            var p=center.offset(n%41-20,n/(41*41)-8,n/41%41-20);
            if(level.hasChunkAt(p)&&level.getBlockState(p).is(soil)){
                schedule.blocks.putIfAbsent(p.asLong(),level.getGameTime()+level.random.nextInt(18));
            }
        }
        for(long key:new ArrayList<>(schedule.blocks.keySet())){
            var pos=BlockPos.of(key);
            if(pos.distToCenterSqr(camera.x,camera.y,camera.z)>24*24||!level.hasChunkAt(pos)||!level.getBlockState(pos).is(soil)){schedule.blocks.remove(key);continue;}
            animateTick(level.getBlockState(pos),level,pos,level.random);
        }
    }
    public static void animateTick(BlockState state,ClientLevel level,BlockPos pos,RandomSource random){
        if(!SOIL.equals(BuiltInRegistries.BLOCK.getKey(state.getBlock())))return;
        var mc=Minecraft.getInstance();if(mc.options.particles().get()==ParticleStatus.MINIMAL)return;
        var camera=mc.gameRenderer.getMainCamera().getPosition();double distance=pos.distToCenterSqr(camera.x,camera.y,camera.z);if(distance>24*24)return;
        var above=pos.above();var cover=level.getBlockState(above);
        if(cover.isSolidRender(level,above)||!level.getFluidState(above).isEmpty())return;
        var schedule=STATES.computeIfAbsent(level,l->new State());long now=level.getGameTime(),key=pos.asLong();
        Long due=schedule.blocks.get(key);if(due==null){schedule.blocks.put(key,now+random.nextInt(18));return;}
        if(now<due)return;
        int neighbors=0;
        for(int dx:D)for(int dz:D)if((dx!=0||dz!=0)&&level.getBlockState(pos.offset(dx,0,dz)).is(state.getBlock()))neighbors++;
        int interval=MIN_INTERVAL_TICKS+random.nextInt(MAX_INTERVAL_TICKS-MIN_INTERVAL_TICKS+1);
        if(neighbors>1)interval*=2;if(distance>12*12)interval*=2;
        if(mc.options.particles().get()==ParticleStatus.DECREASED)interval*=2;
        schedule.blocks.put(key,now+interval);
        long cell=BlockPos.asLong(Math.floorDiv(pos.getX(),4),Math.floorDiv(pos.getY(),4),Math.floorDiv(pos.getZ(),4));
        if(now<schedule.cells.getOrDefault(cell,Long.MIN_VALUE))return;
        double x=pos.getX()+0.12+random.nextDouble()*0.76,y=pos.getY()+1.06,z=pos.getZ()+0.12+random.nextDouble()*0.76;
        if(cover.getCollisionShape(level,above).toAabbs().stream().anyMatch(b->b.inflate(0.04).contains(x-above.getX(),y-above.getY(),z-above.getZ())))return;
        schedule.cells.put(cell,now+CELL_COOLDOWN_TICKS*(distance>12*12?2:1));
        double rise=CorruptedSoilVaporParticle.MIN_RISE_SPEED+random.nextDouble()*(CorruptedSoilVaporParticle.MAX_RISE_SPEED-CorruptedSoilVaporParticle.MIN_RISE_SPEED);
        level.addParticle(ModParticles.CORRUPTED_SOIL_VAPOR.get(),x,y,z,(random.nextDouble()-0.5)*0.004,rise,(random.nextDouble()-0.5)*0.004);
    }
    private static Map<Long,Long> boundedMap(){return new LinkedHashMap<>(){
        @Override protected boolean removeEldestEntry(Map.Entry<Long,Long> e){return size()>MAX_TRACKED_POSITIONS;}
    };}
    private static final class State {int cursor;final Map<Long,Long> blocks=boundedMap(),cells=boundedMap();}
    private CorruptedSoilVapor(){}
}
