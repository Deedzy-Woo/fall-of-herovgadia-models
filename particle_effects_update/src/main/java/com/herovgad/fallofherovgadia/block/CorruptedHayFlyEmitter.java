package com.herovgad.fallofherovgadia.block;

import com.herovgad.fallofherovgadia.ModParticles;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.WeakHashMap;

/** Runs from client animateTick only. No client classes are referenced by this common hook. */
public final class CorruptedHayFlyEmitter {
    public static final int MIN_INTERVAL_TICKS = 9;
    public static final int MAX_INTERVAL_TICKS = 19;
    public static final int CELL_COOLDOWN_TICKS = 7;
    private static final int MAX_ENTRIES = 2048;
    private static final Direction[] SURFACES = {Direction.UP, Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST};
    private static final Map<Level, Schedule> SCHEDULES = new WeakHashMap<>();

    private CorruptedHayFlyEmitter() {}

    public static void animateTick(Level level, BlockPos pos, RandomSource random) {
        if (!level.isClientSide || level.getNearestPlayer(pos.getX() + 0.5, pos.getY() + 0.5,
                pos.getZ() + 0.5, 18.0, false) == null) return;
        Schedule schedule = SCHEDULES.computeIfAbsent(level, ignored -> new Schedule());
        long now = level.getGameTime(), key = pos.asLong();
        Long due = schedule.blocks.get(key);
        if (due == null) {
            schedule.blocks.put(key, now + random.nextInt(12));
            return;
        }
        if (now < due) return;
        schedule.blocks.put(key, now + interval(random));
        long cell = BlockPos.asLong(Math.floorDiv(pos.getX(), 4), Math.floorDiv(pos.getY(), 4), Math.floorDiv(pos.getZ(), 4));
        if (now < schedule.cells.getOrDefault(cell, Long.MIN_VALUE)) return;
        int first = random.nextInt(SURFACES.length);
        for (int i = 0; i < SURFACES.length; i++) {
            Direction face = SURFACES[(first + i) % SURFACES.length];
            BlockPos neighbor = pos.relative(face);
            if (!level.getFluidState(neighbor).isEmpty()
                    || !level.getBlockState(neighbor).getCollisionShape(level, neighbor).isEmpty()) continue;
            double x = pos.getX() + 0.5, y = pos.getY() + 0.5, z = pos.getZ() + 0.5;
            if (face.getAxis() == Direction.Axis.Y) { x += jitter(random); z += jitter(random); }
            else if (face.getAxis() == Direction.Axis.X) { y += jitter(random); z += jitter(random); }
            else { x += jitter(random); y += jitter(random); }
            x += face.getStepX() * 0.64; y += face.getStepY() * 0.64; z += face.getStepZ() * 0.64;
            schedule.cells.put(cell, now + CELL_COOLDOWN_TICKS);
            // Ordinary particle path respects quality, distance and the provider's global group cap.
            level.addParticle(ModParticles.CORRUPTED_HAY_FLY.get(), x, y, z, 0, 0, 0);
            return;
        }
    }

    private static double jitter(RandomSource random) { return (random.nextDouble() - 0.5) * 0.72; }
    private static int interval(RandomSource random) { return MIN_INTERVAL_TICKS + random.nextInt(MAX_INTERVAL_TICKS - MIN_INTERVAL_TICKS + 1); }
    private static Map<Long, Long> boundedMap() {
        return new LinkedHashMap<>() {
            @Override protected boolean removeEldestEntry(Map.Entry<Long, Long> eldest) { return size() > MAX_ENTRIES; }
        };
    }
    private static final class Schedule {
        final Map<Long, Long> blocks = boundedMap();
        final Map<Long, Long> cells = boundedMap();
    }
}
