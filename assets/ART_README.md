# Original tactical pixel art

All pixel artwork was drawn from original geometric source code in `tools/generate_art.py` using Pillow. No third-party artwork, traced images, or extracted game sprites are included.

- `terrain/*.png`: 32 × 32 pixels. Includes palisades (`wall`, `wall_vertical`), tents (`village`, `tent`), storehouse, plus grass variations and an optional village house.
- `units/*.png`: 48 × 48 pixels with transparent backgrounds. Cao Cao and Guan Yu are mounted. All other figures are infantry. Blue allied soldier included.
- `units/*_sheet.png`: 144 × 48 pixels, three 48-pixel frames: idle, idle glint, hit flash.
- `portraits/*.png`: 128 × 128 pixels, authored at 64 × 64 and enlarged with nearest-neighbour sampling.
- `terrain_atlas.png`, `unit_atlas.png`, `portrait_atlas.png`: horizontal atlases. Exact cell order in `art_manifest.json`.
- `previews/contact_sheet.png`: full pack visual inspection sheet.

Use nearest-neighbour texture filtering to retain crisp edges. Unit sprite foot/shadow baseline is approximately y = 42 of the 48-pixel canvas.

To regenerate: `python tools/generate_art.py` (requires Pillow). Preview labels use the system's Noto Sans CJK font; game artwork has no font dependency.
