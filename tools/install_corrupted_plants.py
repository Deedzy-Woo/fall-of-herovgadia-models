"""Copy the additive integration kit into a real mod checkout; merge locales safely."""
from pathlib import Path
import argparse,json,shutil
base=Path(__file__).resolve().parents[1];kit=base/'corrupted_plants' if (base/'corrupted_plants/src').exists() else base
p=argparse.ArgumentParser();p.add_argument('--mod-dir',required=True,type=Path);p.add_argument('--dry-run',action='store_true');args=p.parse_args();dest=args.mod_dir.resolve()
if not dest.is_dir():p.error('--mod-dir must be an existing mod checkout')
plan=[]
for src in sorted((kit/'src').rglob('*')):
 if not src.is_file():continue
 target=dest/'src'/src.relative_to(kit/'src')
 if target.exists() and target.read_bytes()!=src.read_bytes():raise SystemExit(f'Refusing to overwrite a different file: {target}')
 plan.append((src,target))
locales=[]
for src in sorted((kit/'lang_additions').glob('*.json')):
 target=dest/'src/main/resources/assets/fallofherovgadia/lang'/src.name;add=json.loads(src.read_text());current=json.loads(target.read_text()) if target.exists() else {}
 for key,value in add.items():
  if key in current and current[key]!=value:raise SystemExit(f'Conflicting existing translation: {target}: {key}')
 current.update(add);locales.append((target,current))
if args.dry_run:print(f'Plan: {len(plan)} source/resource files, {len(locales)} additive locale merges. No files written.')
else:
 for src,target in plan:target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,target)
 for target,data in locales:target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 print(f'Installed {len(plan)} source/resource files and merged {len(locales)} locales. Now call CorruptedPlants.register(modEventBus) once from the existing mod constructor.')
