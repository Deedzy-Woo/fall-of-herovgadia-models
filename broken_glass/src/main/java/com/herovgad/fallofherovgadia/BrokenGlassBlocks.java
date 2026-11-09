package com.herovgad.fallofherovgadia;

import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.IronBarsBlock;
import net.minecraft.world.level.block.TransparentBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.event.BuildCreativeModeTabContentsEvent;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredRegister;

/** Decorative broken glass; missing shards do not change vanilla collision. */
public final class BrokenGlassBlocks {
    public static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(FallOfHerovgadia.MODID);
    public static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(FallOfHerovgadia.MODID);
    public static final DeferredBlock<TransparentBlock> BROKEN_GLASS = BLOCKS.register("broken_glass",
            () -> new TransparentBlock(BlockBehaviour.Properties.ofFullCopy(Blocks.GLASS)));
    public static final DeferredBlock<IronBarsBlock> BROKEN_GLASS_PANE = BLOCKS.register("broken_glass_pane",
            () -> new IronBarsBlock(BlockBehaviour.Properties.ofFullCopy(Blocks.GLASS_PANE)));
    static {
        ITEMS.registerSimpleBlockItem(BROKEN_GLASS);
        ITEMS.registerSimpleBlockItem(BROKEN_GLASS_PANE);
    }
    public static void register(IEventBus bus) {
        BLOCKS.register(bus);
        ITEMS.register(bus);
        bus.addListener(BrokenGlassBlocks::addCreativeItems);
    }
    private static void addCreativeItems(BuildCreativeModeTabContentsEvent event) {
        if (event.getTabKey() == CreativeModeTabs.COLORED_BLOCKS) {
            event.accept(BROKEN_GLASS.get());
            event.accept(BROKEN_GLASS_PANE.get());
        }
    }
    private BrokenGlassBlocks() {}
}
