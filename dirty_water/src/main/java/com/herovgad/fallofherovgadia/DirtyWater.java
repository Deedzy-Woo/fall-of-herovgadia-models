package com.herovgad.fallofherovgadia;

import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.*;
import net.minecraft.world.level.material.*;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.common.SoundActions;
import net.neoforged.neoforge.event.BuildCreativeModeTabContentsEvent;
import net.neoforged.neoforge.fluids.FluidType;
import net.neoforged.neoforge.registries.*;

/** A separate water family with vanilla flow and bucket logic; visual prototype only. */
public final class DirtyWater {
    public static final DeferredRegister<FluidType> TYPES = DeferredRegister.create(NeoForgeRegistries.Keys.FLUID_TYPES, FallOfHerovgadia.MODID);
    public static final DeferredRegister<Fluid> FLUIDS = DeferredRegister.create(Registries.FLUID, FallOfHerovgadia.MODID);
    public static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(FallOfHerovgadia.MODID);
    public static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(FallOfHerovgadia.MODID);
    public static final DeferredHolder<FluidType, FluidType> TYPE = TYPES.register("dirty_water", () -> new FluidType(FluidType.Properties.create()
            .descriptionId("fluid_type.fallofherovgadia.dirty_water")
            .density(1000).viscosity(1000).temperature(300).lightLevel(0)
            .motionScale(0.014).fallDistanceModifier(0).canSwim(true).canDrown(true)
            .canExtinguish(true).supportsBoating(true).canConvertToSource(true).canHydrate(true)
            .sound(SoundActions.BUCKET_FILL, SoundEvents.BUCKET_FILL)
            .sound(SoundActions.BUCKET_EMPTY, SoundEvents.BUCKET_EMPTY)
            .sound(SoundActions.FLUID_VAPORIZE, SoundEvents.FIRE_EXTINGUISH)) {
        @Override public boolean canConvertToSource(FluidState state, LevelReader reader, BlockPos pos) {
            return reader instanceof Level level ? level.getGameRules().getBoolean(GameRules.RULE_WATER_SOURCE_CONVERSION)
                    : super.canConvertToSource(state, reader, pos);
        }
    });
    public static final DeferredHolder<Fluid, Source> SOURCE = FLUIDS.register("dirty_water", Source::new);
    public static final DeferredHolder<Fluid, Flowing> FLOWING = FLUIDS.register("flowing_dirty_water", Flowing::new);
    public static final DeferredBlock<LiquidBlock> BLOCK = BLOCKS.register("dirty_water",
            () -> new LiquidBlock(SOURCE.get(), BlockBehaviour.Properties.ofFullCopy(Blocks.WATER).noLootTable()));
    public static final DeferredItem<BucketItem> BUCKET = ITEMS.register("dirty_water_bucket",
            () -> new BucketItem(SOURCE.get(), new Item.Properties().craftRemainder(Items.BUCKET).stacksTo(1)));

    public static void register(IEventBus bus) {
        TYPES.register(bus); FLUIDS.register(bus); BLOCKS.register(bus); ITEMS.register(bus);
        bus.addListener(DirtyWater::creative);
    }
    private static void creative(BuildCreativeModeTabContentsEvent event) {
        if (event.getTabKey() == CreativeModeTabs.TOOLS_AND_UTILITIES) event.accept(BUCKET);
    }
    public abstract static class FluidBase extends WaterFluid {
        @Override public FluidType getFluidType() { return TYPE.get(); }
        @Override public Fluid getSource() { return SOURCE.get(); }
        @Override public Fluid getFlowing() { return FLOWING.get(); }
        @Override public Item getBucket() { return BUCKET.get(); }
        @Override public boolean isSame(Fluid fluid) { return fluid == SOURCE.get() || fluid == FLOWING.get(); }
        @Override public net.minecraft.world.level.block.state.BlockState createLegacyBlock(FluidState state) {
            return BLOCK.get().defaultBlockState().setValue(LiquidBlock.LEVEL, getLegacyLevel(state));
        }
    }
    public static final class Source extends FluidBase {
        @Override public int getAmount(FluidState state) { return 8; }
        @Override public boolean isSource(FluidState state) { return true; }
    }
    public static final class Flowing extends FluidBase {
        @Override protected void createFluidStateDefinition(StateDefinition.Builder<Fluid, FluidState> builder) {
            super.createFluidStateDefinition(builder); builder.add(LEVEL);
        }
        @Override public int getAmount(FluidState state) { return state.getValue(LEVEL); }
        @Override public boolean isSource(FluidState state) { return false; }
    }
    private DirtyWater() {}
}
