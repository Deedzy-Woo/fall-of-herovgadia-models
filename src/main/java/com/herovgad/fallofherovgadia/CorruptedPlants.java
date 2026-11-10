package com.herovgad.fallofherovgadia;

import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.PushReaction;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.event.BuildCreativeModeTabContentsEvent;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredRegister;

/** Call register(modEventBus) once from the existing mod constructor. */
public final class CorruptedPlants {
    public static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(FallOfHerovgadia.MODID);
    public static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(FallOfHerovgadia.MODID);

    public static final DeferredBlock<CorruptedPlantBlock> SMALL = plant("corrupted_plant_small", 6, 5);
    public static final DeferredBlock<CorruptedPlantBlock> MEDIUM = plant("corrupted_plant_medium", 10, 11);
    public static final DeferredBlock<CorruptedPlantBlock> TALL = plant("corrupted_plant_tall", 6, 15);
    public static final DeferredBlock<CorruptedPlantBlock> WITHERED_BUSH = plant("corrupted_plant_withered_bush", 15, 11);

    private static DeferredBlock<CorruptedPlantBlock> plant(String name, int width, int height) {
        DeferredBlock<CorruptedPlantBlock> block = BLOCKS.register(name, () -> new CorruptedPlantBlock(width, height,
                BlockBehaviour.Properties.ofFullCopy(Blocks.DEAD_BUSH)
                        .noCollission().noOcclusion().instabreak().replaceable()
                        .sound(SoundType.GRASS).offsetType(BlockBehaviour.OffsetType.XZ)
                        .pushReaction(PushReaction.DESTROY)));
        ITEMS.registerSimpleBlockItem(block);
        return block;
    }

    public static void register(IEventBus bus) {
        BLOCKS.register(bus);
        ITEMS.register(bus);
        bus.addListener(CorruptedPlants::addCreativeItems);
    }

    private static void addCreativeItems(BuildCreativeModeTabContentsEvent event) {
        if (event.getTabKey() == CreativeModeTabs.NATURAL_BLOCKS) {
            event.accept(SMALL.get());
            event.accept(MEDIUM.get());
            event.accept(TALL.get());
            event.accept(WITHERED_BUSH.get());
        }
    }

    private CorruptedPlants() {}
}
