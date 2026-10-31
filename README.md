# Fall of Herovgadia — creature models

Download the latest [complete asset kit](downloads/dead_harpy_latest.zip),
[Blockbench project](dead_harpy/dead_harpy.bbmodel), or
[pixel texture](dead_harpy/dead_harpy.png).

The first asset is the cuboid **Dead Harpy**, authored against the supplied concept and revised toward vanilla Minecraft proportions and pixel density (147 cuboids; layered matted hair, arms integrated into the wings, grasping digits at each carpal joint and a tapered hooked beak).

Open [`dead_harpy/dead_harpy.bbmodel`](dead_harpy/dead_harpy.bbmodel) in Blockbench.
The project embeds its single pixel atlas. The accompanying `.geo.json` is a
GeckoLib geometry resource for a Minecraft Java Edition 1.21.1 mod.

See [the Russian asset guide](dead_harpy/README_RU.md) for the rig, UVs and resource
paths. Open `dead_harpy/dead_harpy_viewer.html` for an offline inspection viewer.

## Rebuild

With Python 3.10+ and Pillow installed, run from this checkout:

```sh
python3 tools/build_dead_harpy.py
python3 tools/validate_dead_harpy.py
```

The generator is deterministic and writes the `.bbmodel`, `.geo.json`, PNG,
UV layout and descriptive manifests. It overwrites generated asset files; keep
manual Blockbench edits in a separate project before rebuilding.

`tools/check_in_blockbench.py --blockbench-dir /path/to/blockbench` verifies the
project in a locally built official Blockbench web editor and refreshes
`render_geometry.json` and `rig_points.json`. The checker requires Playwright
and Chromium. External startup news are read from the bundled official checkout.

`tools/render_dead_harpy.py` optionally runs in Blender 4.3+ and uses `render_geometry.json`,
which is read from the actual loaded Blockbench scene, including all transforms
and UV coordinates. It renders inspection images without smoothing the asset.
`tools/build_viewer.py --three-dir /path/to/three` bundles that same readback
with Three.js r129 into the standalone viewer. If the model changes, refresh the
Blockbench scene readback before rendering or rebuilding the viewer.

This repository holds model resources, not the mod's entity implementation.

`tools/capture_previews.py` tests the standalone viewer and captures the current
flat-shaded presentation without studio rendering.
