"""Assemble the user-facing asset kit and verify its ZIP integrity."""
from pathlib import Path
import hashlib
import shutil
import zipfile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dead_harpy'
EXPORT=ROOT.parent/'exports'
STAGE=EXPORT/'dead_harpy'
STAGE.mkdir(parents=True,exist_ok=True)
files=['dead_harpy.bbmodel','dead_harpy.geo.json','dead_harpy.png',
       'dead_harpy_viewer.html','README_RU.md','QA.md','THIRD_PARTY_LICENSE.txt']
for name in files:
 shutil.copy2(OUT/name,STAGE/name)
frames=['hero.png','front.png','back.png','side.png','face_detail.png',
        'beak_profile.png','wing_claw_detail.png','hair_back_detail.png',
        'uv_layout.png','blockbench_open.png','interactive_viewer.png']
(STAGE/'previews').mkdir(exist_ok=True)
for name in frames:
 p=OUT/'previews'/name
 if name in ['hero.png','front.png','back.png','side.png','face_detail.png','beak_profile.png','wing_claw_detail.png','hair_back_detail.png']:
  assert p.stat().st_mtime>(OUT/'render_geometry.json').stat().st_mtime, f'Stale render: {name}'
 shutil.copy2(p,STAGE/'previews'/name)
manifest=[]
for path in sorted(STAGE.rglob('*')):
 if path.is_file() and path.name!='SHA256SUMS.txt':
  manifest.append(hashlib.sha256(path.read_bytes()).hexdigest()+'  '+path.relative_to(STAGE).as_posix())
(STAGE/'SHA256SUMS.txt').write_text('\n'.join(manifest)+'\n')
archive=EXPORT/'fall_of_herovgadia_dead_harpy.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for path in sorted(STAGE.rglob('*')):
  if path.is_file(): z.write(path,path.relative_to(EXPORT))
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 print(f'Archive: {archive}\nFiles: {len(z.namelist())}\nBytes: {archive.stat().st_size}')
