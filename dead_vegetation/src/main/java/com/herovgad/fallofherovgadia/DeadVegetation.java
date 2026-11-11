package com.herovgad.fallofherovgadia;

import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.*;
import net.minecraft.world.phys.shapes.*;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.event.BuildCreativeModeTabContentsEvent;
import net.neoforged.neoforge.registries.*;
import java.util.*;

/** Inert decorations: no random ticks, growth, particles, damage or biome tint. */
public final class DeadVegetation {
    public static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(FallOfHerovgadia.MODID);
    public static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(FallOfHerovgadia.MODID);
    public static final TagKey<Block> SUBSTRATE = TagKey.create(Registries.BLOCK,
            ResourceLocation.fromNamespaceAndPath(FallOfHerovgadia.MODID, "dead_vegetation_substrate"));
    public static final List<DeferredBlock<? extends Block>> PLANTS = new ArrayList<>();
    static {
        for (String name : List.of("dead_short_grass", "dead_tall_grass", "withered_wildflower", "dead_fern",
                "dead_large_fern", "dead_savanna_grass", "dead_savanna_shrub", "dead_cactus",
                "frozen_dead_grass", "frozen_dead_shrub")) {
            DeferredBlock<? extends Block> block;
            if (name.equals("dead_cactus")) {
                block = BLOCKS.register(name, () -> new DryCactus(BlockBehaviour.Properties.of()
                        .strength(0.4F).sound(SoundType.WOOL).noOcclusion()));
            } else if (name.equals("dead_tall_grass") || name.equals("dead_large_fern")) {
                block = BLOCKS.register(name, () -> new TallPlant(plantProperties()));
            } else {
                block = BLOCKS.register(name, () -> new SmallPlant(plantProperties()));
            }
            PLANTS.add(block);
            ITEMS.registerSimpleBlockItem(block);
        }
    }
    private static BlockBehaviour.Properties plantProperties() {
        return BlockBehaviour.Properties.of().noCollission().instabreak().sound(SoundType.GRASS)
                .noOcclusion().pushReaction(net.minecraft.world.level.material.PushReaction.DESTROY);
    }
    public static void register(IEventBus bus) {
        BLOCKS.register(bus); ITEMS.register(bus);
        bus.addListener(DeadVegetation::creative);
    }
    private static void creative(BuildCreativeModeTabContentsEvent event) {
        if (event.getTabKey() == CreativeModeTabs.NATURAL_BLOCKS) PLANTS.forEach(b -> event.accept(b.get()));
    }
    public static final class SmallPlant extends BushBlock {
        public static final MapCodec<SmallPlant> CODEC = simpleCodec(SmallPlant::new);
        public SmallPlant(BlockBehaviour.Properties p) { super(p); }
        @Override protected MapCodec<SmallPlant> codec() { return CODEC; }
        @Override protected boolean mayPlaceOn(BlockState s, BlockGetter level, BlockPos pos) { return s.is(SUBSTRATE); }
    }
    public static final class TallPlant extends DoublePlantBlock {
        public static final MapCodec<TallPlant> CODEC = simpleCodec(TallPlant::new);
        public TallPlant(BlockBehaviour.Properties p) { super(p); }
        @Override public MapCodec<TallPlant> codec() { return CODEC; }
        @Override protected boolean mayPlaceOn(BlockState s, BlockGetter level, BlockPos pos) { return s.is(SUBSTRATE); }
    }
    public static final class DryCactus extends Block {
        public static final MapCodec<DryCactus> CODEC = simpleCodec(DryCactus::new);
        private static final VoxelShape SHAPE = Block.box(1, 0, 1, 15, 16, 15);
        public DryCactus(BlockBehaviour.Properties p) { super(p); }
        @Override protected MapCodec<DryCactus> codec() { return CODEC; }
        @Override protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return SHAPE; }
        @Override protected boolean canSurvive(BlockState s, LevelReader l, BlockPos p) {
            var below = l.getBlockState(p.below()); return below.is(SUBSTRATE) || below.is(this);
        }
        @Override protected BlockState updateShape(BlockState s, Direction d, BlockState n, LevelAccessor l, BlockPos p, BlockPos q) {
            return s.canSurvive(l,p) ? super.updateShape(s,d,n,l,p,q) : Blocks.AIR.defaultBlockState();
        }
    }
    private DeadVegetation() {}
}
