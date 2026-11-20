# Undead Harpy — simplified static source

The new source has 70 editable cuboids and 24 bones. It uses exactly one literal 16×16 PNG atlas,
embedded in the Blockbench project. Every UV rectangle stays within 0..16. There are no
animation clips, controllers, or animation files. Bones remain available for future work.

## Geometry budget

| Part | Cuboids |
|---|---:|
| Torso, exposed ribs, neck, skull and jaw |11|
| Compact closed hooked beak |3|
| Long grouped hair |6|
| Two dense feather wings and pale leading ridges |22|
| Arms, palms and single claw forms |12|
| Legs, feet and single talon forms |14|
| Short feather tail |2|
| Total |70|

This is a reduction from 117 cuboids to 70. Approximate geometry cost is 420 cuboid faces,
840 triangles and 1680 separate-face render vertices, before renderer-specific processing.

## Dense wings

Each wing uses two leading-edge bone segments, one broad inner cover, six broad overlapping
feather shapes and two short tapered tip pieces. Feather spans overlap to create a full fan.
The shoulders and outer fans remain separate bones (`wing_left/right`, `wing_fore_left/right`).
The former long sparse feather strips and extra feather layering were removed.

## Missing flesh and visible skeleton

The front-left ribcage has a genuine geometric recess. Surviving upper and lower flesh border
an opening; the dark red back surface lies behind the intact front plane. Two pale cuboid ribs
sit inside the recess. This is not a wound painted over an unbroken torso box.

Elements: `chest_core`, `chest_left_back`, `chest_left_upper_flesh`,
`chest_left_lower_flesh`, `exposed_rib_lower`, `exposed_rib_upper`.
All belong to the `chest` bone. Torso UV crops match the corresponding area of the shared 8×8
wound tile, so the entire wound is not repeated on every flesh element.

## Rig and coordinates

Y is up; forward is-Z. Sixteen units equal one Minecraft block.
`root` → `body` → `chest` → `neck` → `head`, with separate `hair` and `beak` bones.
Arms use shoulder/forearm/hand bones; legs use thigh/shin/foot bones. Wings mount to the upper
back and remain separate from the arms. `tail` belongs to `body`.

Rest world bounds including spread wings:

- X: −36.698 to 36.698 units.
- Y:0.070 to 43.724 units.
- Z: −8.941 to 8.523 units.
- Total span:73.396×43.655×17.464 units, about 4.59×2.73×1.09 blocks.

These are visual bounds, not an entity collision-box proposal.

## Checks

Every cuboid has positive finite dimensions and exactly one bone owner. There are no orphaned
or multiply-owned cuboids. Source and geometry export have the same 24 bone names and 70 cubes.
The embedded PNG is 16×16, opaque, and is the only texture. No higher-resolution atlas is used.
The official Blockbench geometry export from the parent validation task should be used as the
final interchange file. No game integration or gameplay behavior is implemented here.
