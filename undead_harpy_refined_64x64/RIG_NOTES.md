# Undead Harpy — refinement of the attached source

This revision reads the uploaded `undead_harpy.bbmodel` as its baseline. It does not regenerate
the creature from a new design. All 70 original cuboid UUIDs and all 24 original bones remain.
The body, limbs, pose, original wing feathers, tail and chest wound keep their original geometry.
Only seven existing hair/beak cuboids change shape; 18 purposeful cuboids are added.

## Final budget

| Part | Cuboids |
|---|---:|
| Body, neck, skull and existing rib wound | 11 |
| Closed compact hooked beak | 4 |
| Scalp coverage and grouped uneven hair locks | 13 |
| Original wings plus attached sockets and supports | 28 |
| Arms and hand claws | 14 |
| Legs and talons | 16 |
| Tail | 2 |
| Total | 88 |

The model has 528 cuboid faces, 1056 triangles and approximately 2112 separate-face render
vertices. It uses one embedded 64×64 opaque atlas. Every UV stays within the atlas. There are
no animation clips, controllers or animation files. The existing rig is retained for later work.

## Requested fixes

**Wings.** The existing broad feathers keep their placement and UUIDs. Each side gains a solid
root socket inside the upper back and two broad feather-covered supports beneath the leading
ridge. These connect the back, ridge and feather roots without rebuilding the original wings.

**Hair.** Thin upper side shells cover the temples and full skull sides; the skull's side, back
and top UVs also use hair as backup coverage. Broad back panels stop at skull-base height.
Below them, separate front, middle and rear locks end at different lengths. The rear scalp root
fits inside the crown footprint. No hair part extends above the crown.

**Beak.** The three original cuboids are reshaped and one overlapping bridge is added. The four
short horn volumes form a continuously seated, closed raptor hook. The original head and jaw
proportions are preserved.

**Claws.** Four small central hooks are added to the existing fingers/toes. All original hand
and foot cuboids keep their placement. Palms and foot scales use a distinct material from the
darker claw tips.

**Wound.** The original missing-flesh recess and both actual rib cuboids are preserved. The new
atlas supplies a darker cavity and restrained dried-blood cut edges. Wound UVs are cropped
coherently across the original torso pieces, rather than stamped repeatedly on every cube.

## Structural and provenance checks

`source-preservation-audit.json` records all original UUIDs and per-cube geometry comparisons.
All 61 protected body/limb/wound/wing cuboids are geometrically unchanged; 63 of the 70 original
cuboids are unchanged overall. All original bone transforms, hierarchy and cube ownership are
unchanged. No original cubes are removed, orphaned or multiply owned.

`connection-validation.json` uses exact 15-axis separating-axis tests on actual world-space
oriented boxes, including both bone and cube rotations. It verifies:

- every wing cuboid has a contact path to the torso;
- the upper 20% root volume of each of the 12 broad feathers directly intersects a supporting
  cover, socket or leading ridge;
- all four feather tips intersect their original parent feathers;
- all four beak parts connect to the skull;
- all four added hooks directly intersect their own source finger or toe;
- every hair piece has a physical contact path to the crown;
- all 196 sampled side, back and crown skull points are geometrically covered by hair.

`hair-root-bounds.json` confirms the crown top is at head-local Y=37.05, while the highest other
hair vertex is Y=36.3169. The rear scalp root ends at Z=1.9 inside crown Z=2.1. Lower rear-lock
roots end below Y=30.6276. The apparent projection in a full profile was background wing
geometry; isolated head views confirm no hair horn.

The parent's independent Blockbench validation additionally loads and round-trips the model,
checks the live mesh contact graph and exports the official geometry file. No Java or game
mechanics are introduced by this source package.
