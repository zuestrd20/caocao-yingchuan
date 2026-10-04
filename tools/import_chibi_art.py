#!/usr/bin/env python3
"""Rebuild game-ready assets mechanically from the supplied image-generated sheet.
Only component extraction, alpha-bbox trimming, uniform resize and packing occur.
This is not an art generator. Original alpha and aspect ratios are preserved.
"""
from pathlib import Path
import argparse, json
import numpy as np
from scipy import ndimage
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
A = ROOT / 'assets'
SOURCE = A / 'sources' / 'chibi'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--check', action='store_true', help='Check pixels without changing any file.')
args = parser.parse_args()
layout = json.loads((SOURCE / 'layout.json').read_text())
manifest = json.loads((A / 'art_manifest.json').read_text())
order = manifest['unit_order']
outputs = {}
images = {}
# Components isolate touching atlas rows without clipping crowns, feet or weapons.
src = Image.open(SOURCE / 'characters.png').convert('RGBA')
rgba = np.array(src)
raw, count = ndimage.label(rgba[:,:,3] > 127)
counts = np.bincount(raw.ravel())
ids = [i for i in range(1,count+1) if counts[i] > 1000]
assert len(ids) == 16, f'Expected 16 substantial illustrations, found {len(ids)}'
core = np.zeros(raw.shape, dtype=np.int16)
for component, raw_id in enumerate(ids,1):core[raw==raw_id]=component
distance, nearest = ndimage.distance_transform_edt(core==0, return_indices=True)
owners = core[nearest[0],nearest[1]]
components = {}
for component in range(1,17):
    pixels = rgba.copy()
    pixels[:,:,3] = np.where((owners==component) & (distance<=3), rgba[:,:,3], 0)
    cut = Image.fromarray(pixels)
    components[component] = cut.crop(cut.getchannel('A').getbbox())
for group, size in [('units', 48), ('portraits', 128)]:
    images[group] = {}
    for key in order:
        item = layout['items'][group][key]
        cut = components[item['component']]
        fitted = cut.copy()
        fitted.thumbnail((size-4, size-4), Image.Resampling.LANCZOS)
        target = Image.new('RGBA', (size, size))
        # Bottom-align feet/shoulders, centre horizontally; no stretching.
        target.alpha_composite(fitted, ((size-fitted.width)//2, size-2-fitted.height))
        images[group][key] = target
        outputs[A/group/f'{key}.png'] = target
        assert target.getchannel('A').getextrema() == (0,255)
        assert not any(target.getchannel('A').crop(box).getbbox() for box in [(0,0,size,1),(0,size-1,size,size),(0,0,1,size),(size-1,0,size,size)])
    atlas = Image.new('RGBA', (size*len(order),size))
    for i,key in enumerate(order):atlas.alpha_composite(images[group][key],(i*size,0))
    outputs[A/('unit_atlas.png' if group=='units' else 'portrait_atlas.png')] = atlas
for key in order:
    strip = Image.new('RGBA',(144,48))
    # Reserved legacy three-frame contract. The runtime uses idle PNG plus UI
    # animation/effects; do not manufacture alternative character drawings.
    for frame in range(3):strip.alpha_composite(images['units'][key],(48*frame,0))
    outputs[A/'units'/f'{key}_sheet.png'] = strip
# Contact preview packs delivered art only, with no procedural art substitutes.
preview=Image.new('RGBA',(8*144,208),(25,41,37,255))
for i,key in enumerate(order):
    preview.alpha_composite(images['portraits'][key],(i*144+8,8))
    preview.alpha_composite(images['units'][key],(i*144+48,152))
outputs[A/'previews'/'chibi_contact_sheet.png']=preview
for path, expected in outputs.items():
    if args.check:
        actual=Image.open(path).convert('RGBA')
        assert actual.size==expected.size and actual.tobytes()==expected.tobytes(),f'Stale asset {path}'
    else:
        path.parent.mkdir(parents=True,exist_ok=True);expected.save(path)
if not args.check:
    manifest.update(style='chibi',character_source='sources/chibi/characters.png',character_layout='sources/chibi/layout.json',character_pipeline='python3 tools/import_chibi_art.py',unit_sheet_frames=['idle','idle_reserved','idle_reserved'],character_generation='OpenAI built-in image_gen; deterministic component extraction, alpha trim, uniform downsample, and atlas packing only')
    manifest['license']='Newly generated character illustrations and original code-drawn terrain. No extracted original-game artwork.'
    manifest['units']['caocao']['mounted']=False
    manifest['units']['guanyu']['mounted']=False
    (A/'art_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(('CHECKED' if args.check else 'BUILT')+f' {len(outputs)} character images, sheets, atlases and preview; all alpha/aspect checks passed')
