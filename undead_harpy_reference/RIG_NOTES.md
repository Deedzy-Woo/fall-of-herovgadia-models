# Undead Harpy — rig and source notes

Editable source: `undead_harpy.bbmodel` in the final package (`bare.bbmodel` in geometry staging), native Blockbench Bedrock Entity format.
The atlas is128×64, with a dedicated8×8 front-face island atUV `[0,0,8,8]`.
The source model currently embeds the finished atlas supplied by the parent task.

## Coordinate convention and rest size

Y is up; the face and claws point toward-Z. Sixteen model units equal one Minecraft block.
All pivots are absolute rest-space coordinates; parent-child transforms preserve the pose.
The official Blockbench Bedrock exporter converts the X handedness on geometry output.

Calculated rest bounds, including the raised spread wings:

- X: −42.168 to42.168 units, total84.335 units /5.271 blocks.
- Y:0.310 to44.700 units, total44.390 units /2.774 blocks.
- Z: −8.888 to9.228 units, total18.116 units /1.132 blocks.

The humanoid head-to-talon body is about37 units high; wings extend above the head.
These are visual bounds, not proposed entity collision dimensions.

## Hierarchy

`root` → `body` → `chest` → `neck` → `head` → `hair` / `beak`.

The upper-back wings are separate from the grasping arms:

- `wing_left` → `wing_fore_left`
- `wing_right` → `wing_fore_right`

The two wing sections provide shoulder flapping and elbow/outer-fan flexing.
Each wing contains seven three-stage primary feathers, four secondary feathers and three
pale leading-edge bone segments. Feather UV length follows V from top to bottom.

Arms:

- `arm_left` → `forearm_left` → `hand_left`
- `arm_right` → `forearm_right` → `hand_right`

Legs:

- `thigh_left` → `shin_left` → `foot_left`
- `thigh_right` → `shin_right` → `foot_right`

`tail` hangs from `body`. `hair` is independently movable from `head`.
Hand and foot hooks are edited as cuboids inside their hand/foot bone; individual phalange
bones were deliberately omitted to retain a moderate, easy-to-animate rig.

## Cuboid budget

| Part | Cuboids |
|---|---:|
| Torso, neck, skull and jaw |6|
| Closed hooked beak |4|
| Grouped long hair |8|
| Two feather wings, including pale leading ridges |56|
| Arms, palms and hooked finger claws |18|
| Legs, feet and front/rear talons |22|
| Short feather tail |3|
| Total |117|

The model has24 bones,702 cuboid faces,1404 triangles, and approximately2808 render vertices
when each cuboid face has separate UV/normal vertices. This excludes possible renderer-side
merging or double-sided material processing.

## Animation clips

| Clip | Duration | Playback | Purpose |
|---|---:|---|---|
| `animation.undead_harpy.wing_flap` |1.2s|Loop|Shoulder stroke with delayed outer-wing flex.|
| `animation.undead_harpy.hover` |2.4s|Loop|Gentle body bob, head movement, tail and hair drift.|
| `animation.undead_harpy.dive` |1.1s|Once|Pitch down, sweep wings back, reach with arms and tuck/clutch talons.|
| `animation.undead_harpy.grab` |1.0s|Once|Forward grasp with wrists plus staggered leg/foot clutch.|

`hover` and `wing_flap` affect separate sets of bones and may be layered later.
Animations are editable visual clips; no attack, grabbing, collision, AI, damage, or flight
mechanics are implemented by these files. The final package should use the official
Blockbench geometry and animation exports captured by the validation task.

## Validation

`geometry-validation.json` checks every cube belongs to exactly one bone, every cuboid has
positive finite dimensions, all24 bone names agree between the source and geometry export,
and exported/source cuboid counts agree. No orphaned or multiply-owned cubes exist.
The parent validation task additionally tests actual opening, texture loading, animation
motion, model round-trip, official export agreement, and final renders in Blockbench.
