# Q-version character artwork and original terrain

Eight identities each have a portrait and a transparent battlefield figure: Cao Cao, Liu Bei, Guan Yu, Zhang Fei, Zhang Liang, Zhang Bao, blue allied soldier, and Yellow Turban soldier. The character art was newly created with OpenAI's built-in image generation tool, using this project's previous original sprites as identity references. No artwork was extracted from the original commercial game. The terrain is unchanged original geometric artwork from `tools/generate_art.py`.

## Authoritative source and layout

- `sources/chibi/characters.png`: unmodified 1254 × 1254 RGBA image-generation output, with genuine transparency.
- `sources/chibi/generation_prompt.txt`: generation specification, reference roles and returned layout.
- `sources/chibi/layout.json`: exact mapping from each image's alpha component to the eight identities.
- `tools/import_chibi_art.py`: deterministic extraction/build/check pipeline.

The generated sheet's approximate rows overlap in their bounding boxes. The importer identifies the 16 substantial connected alpha components instead of slicing through crowns, feet or weapons. It keeps the original RGBA within a three-pixel nearest-component edge band, uniformly downsizes each illustration with Lanczos, and places it on a transparent square with two-pixel padding. It never stretches faces, redraws figures, recolors characters or synthesizes new poses.

## Runtime assets

- `units/*.png`: 48 × 48 transparent figures, bottom aligned at y = 46.
- `portraits/*.png`: 128 × 128 transparent portraits. Runtime UI displays these at 112 × 112 and 144 × 144.
- `units/*_sheet.png`: 144 × 48 compatibility strips. Three copies of the generated idle figure are reserved for the old three-frame interface; these are not three separately generated animations. The actual game loads the individual PNGs and still uses its existing movement, damage text, health bars, faction rings and casting presentation.
- `unit_atlas.png`, `portrait_atlas.png`: convenience horizontal atlases, ordered by `art_manifest.json`.
- `previews/chibi_contact_sheet.png`: current character pack at native asset resolution.
- `terrain/*.png`, `terrain_atlas.png`: unchanged pixel terrain; 32 × 32 cells.

Cao Cao and Guan Yu now use standing Q-version figures. This is a visual redesign only; movement and battle rules are unchanged. The runtime retains nearest-neighbour filtering and existing layout. Sources and previews are excluded from executable exports but retained in the editable source ZIP.

## Rebuilding

Install `tools/requirements-art.txt`, then run `python3 tools/import_chibi_art.py`. Use `--check` to compare every output pixel with a fresh mechanical extraction without writing files. The pipeline checks nonempty alpha, clear outer borders, equal aspect ratio scaling, all eight identities, every compatibility strip and both atlases.

`python3 tools/generate_art.py` refuses to overwrite the character pack. To reproduce the legacy art separately, pass `--output-dir /tmp/yingchuan-legacy`; it must not point at this assets directory. Original terrain generation is preserved in that source. `tools/build_release.sh` checks and packages the current assets without invoking the old generator.

See the project's README for tests and full export commands. No code license is added by this art update.
