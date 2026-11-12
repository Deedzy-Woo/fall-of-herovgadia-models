package com.herovgad.fallofherovgadia.client;

import com.herovgad.fallofherovgadia.DirtyWater;
import com.herovgad.fallofherovgadia.FallOfHerovgadia;
import net.minecraft.client.renderer.ItemBlockRenderTypes;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.fml.event.lifecycle.FMLClientSetupEvent;
import net.neoforged.neoforge.client.extensions.common.*;

@EventBusSubscriber(modid = FallOfHerovgadia.MODID, value = Dist.CLIENT, bus = EventBusSubscriber.Bus.MOD)
public final class DirtyWaterClient {
    @SubscribeEvent public static void extensions(RegisterClientExtensionsEvent event) {
        event.registerFluidType(new IClientFluidTypeExtensions() {
            @Override public ResourceLocation getStillTexture() { return texture("dirty_water_still"); }
            @Override public ResourceLocation getFlowingTexture() { return texture("dirty_water_flow"); }
            // Pigment and alpha are in the PNG; fixed tint prevents biome water turning it blue.
            @Override public int getTintColor() { return 0xFFFFFFFF; }
        }, DirtyWater.TYPE.get());
    }
    private static ResourceLocation texture(String name) {
        return ResourceLocation.fromNamespaceAndPath(FallOfHerovgadia.MODID, "block/" + name);
    }
    @SubscribeEvent public static void setup(FMLClientSetupEvent event) {
        event.enqueueWork(() -> {
            ItemBlockRenderTypes.setRenderLayer(DirtyWater.SOURCE.get(), RenderType.translucent());
            ItemBlockRenderTypes.setRenderLayer(DirtyWater.FLOWING.get(), RenderType.translucent());
        });
    }
    private DirtyWaterClient() {}
}
