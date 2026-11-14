package com.herovgad.fallofherovgadia.client.particle;

import net.minecraft.client.Minecraft;
import net.minecraft.client.ParticleStatus;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.particle.Particle;
import java.lang.ref.WeakReference;
import java.util.*;

/** Shared admission limits, not a second emitter. Only existing providers call this. */
final class CorruptedParticleBudget {
    static final int VAPOR_LIMIT = 64, FLY_LIMIT = 24;
    private record Live(WeakReference<Particle> particle, boolean fly) {}
    private static final Map<ClientLevel, List<Live>> LIVE = new WeakHashMap<>();
    static boolean allow(ClientLevel level, double x, double y, double z, boolean fly) {
        var mc = Minecraft.getInstance();
        if (mc.options.particles().get() == ParticleStatus.MINIMAL) return false;
        var camera = mc.gameRenderer.getMainCamera().getPosition();
        if (camera.distanceToSqr(x,y,z) > (fly ? 18*18 : 24*24)) return false;
        var live = LIVE.computeIfAbsent(level, l -> new ArrayList<>());
        live.removeIf(e -> { var p=e.particle.get(); return p==null || !p.isAlive(); });
        int total=0, near=0, cluster=0;
        for (var e : live) {
            var p=e.particle.get(); if(p==null || e.fly!=fly) continue;
            total++; double d=p.getPos().distanceToSqr(x,y,z);
            if(d < (fly ? 2.1*2.1 : 1.3*1.3)) near++;
            if(d < 4*4) cluster++;
        }
        int limit=fly ? FLY_LIMIT : VAPOR_LIMIT;
        if(mc.options.particles().get()==ParticleStatus.DECREASED) limit/=2;
        return total<limit && near<(fly?5:4) && cluster<(fly?10:9);
    }
    static void track(ClientLevel level, Particle p, boolean fly) {
        LIVE.computeIfAbsent(level,l->new ArrayList<>()).add(new Live(new WeakReference<>(p),fly));
    }
    private CorruptedParticleBudget() {}
}
