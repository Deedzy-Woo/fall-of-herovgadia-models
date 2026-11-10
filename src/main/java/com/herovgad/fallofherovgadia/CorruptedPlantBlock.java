package com.herovgad.fallofherovgadia;

import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.BushBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

/** Static decoration: ordinary plant support, no growth, effects or worldgen. */
public final class CorruptedPlantBlock extends BushBlock {
    public static final MapCodec<CorruptedPlantBlock> CODEC = RecordCodecBuilder.mapCodec(instance -> instance.group(
            Codec.intRange(1, 16).fieldOf("width").forGetter(block -> block.width),
            Codec.intRange(1, 16).fieldOf("height").forGetter(block -> block.height),
            propertiesCodec()
    ).apply(instance, CorruptedPlantBlock::new));

    public static final TagKey<Block> SOILS = TagKey.create(Registries.BLOCK,
            ResourceLocation.fromNamespaceAndPath(FallOfHerovgadia.MODID, "corrupted_plant_soils"));
    private final int width;
    private final int height;
    private final VoxelShape outline;

    public CorruptedPlantBlock(int width, int height, BlockBehaviour.Properties properties) {
        super(properties);
        this.width = width;
        this.height = height;
        this.outline = Block.box(8 - width / 2.0, 0, 8 - width / 2.0, 8 + width / 2.0, height, 8 + width / 2.0);
    }

    @Override
    public MapCodec<CorruptedPlantBlock> codec() { return CODEC; }

    @Override
    protected boolean mayPlaceOn(BlockState soil, BlockGetter level, BlockPos pos) {
        return soil.is(SOILS);
    }

    @Override
    public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        Vec3 offset = state.getOffset(level, pos);
        return outline.move(offset.x, offset.y, offset.z);
    }
}
