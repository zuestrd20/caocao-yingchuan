#!/usr/bin/env bash
# Build from the checked-in generated art. Never call the legacy art generator here.
set -euo pipefail
cd "$(dirname "$0")/.."
GODOT="${GODOT:-godot}"
OUT="${1:-../caocao_deliverables}"
mkdir -p "$OUT" builds/{windows,linux,web}
OUT="$(cd "$OUT" && pwd)"
python3 tools/import_chibi_art.py --check
"$GODOT" --headless --path . --editor --import --quit
: > tests/results.txt
for test in test_battle test_restart test_wind_ui test_paths test_character_assets; do
  "$GODOT" --headless --path . --script "tests/$test.gd" 2>&1 | tee -a tests/results.txt
done
for pair in 'Windows:windows/Yingchuan.exe' 'Linux:linux/Yingchuan.x86_64' 'Web:web/index.html'; do
  "$GODOT" --headless --path . --export-release "${pair%%:*}" "builds/${pair#*:}"
done
python3 - "$OUT" <<'PY'
from pathlib import Path
import sys, zipfile, hashlib
root=Path.cwd(); out=Path(sys.argv[1])
for platform in ('windows','linux','web'):
    with zipfile.ZipFile(out/f'Yingchuan-{platform}.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted((root/'builds'/platform).rglob('*')):
            if p.is_file(): z.write(p,p.relative_to(root/'builds'/platform))
with zipfile.ZipFile(out/'Yingchuan-Godot-Source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(root.rglob('*')):
        rel=p.relative_to(root)
        if p.is_file() and not any(x in ('.godot','builds','__pycache__','.git') for x in rel.parts) and p.suffix not in ('.zip','.pyc'):
            z.write(p,Path('caocao_first_battle')/rel)
(out/'SHA256SUMS.txt').write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n' for p in sorted(out.glob('*.zip'))))
PY
