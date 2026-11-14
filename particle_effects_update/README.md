# Corrupted block particle effects update

[Download ZIP](../downloads/corrupted_block_particles_update.zip) · [In-game overview](preview-overview.png) · [Parameters and installation](README_RU.md) · [Changed files](CREATED_FILES.txt)

Denser five-shape swamp vapor, tiny dark pixel flies, bounded emission and local/global particle limits. Source/resource update for the existing particle systems; no block registration or block asset changes. The original Blockbench ZIPs are preserved unchanged in originals/.

Client tests: single/3x3/10x10/20x20 soil, day/night with soul lantern; 1/3/18 hay bales; Minimal/Decreased/covered. Dedicated server started successfully. Soil used a development-only fixture because its production block is not registered in the available main branch. No fixture is included in src.

This is an integration package, not a standalone mod JAR. See README_RU.md for the existing hay implementation dependency and source registration requirements.
