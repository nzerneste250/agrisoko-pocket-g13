"""Reviewed, one-way mobile-source synchronization. Default: plan only, no copy writes."""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

MAIN = Path(r'F:\COMBO_A3_G13')
BUILD_COPY = Path(r'F:\G13_EAS_CLEAN')
TOP_LEVEL = {'App.tsx', 'index.ts', 'app.json', 'app.config.js', 'eas.json', 'package.json', 'package-lock.json', 'tsconfig.json', '.env.example'}
SOURCE_DIRS = {'src', 'plugins', 'tests', 'assets'}

def digest(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None

def allowed(relative: str) -> bool:
    parts = Path(relative).parts
    return len(parts) >= 2 and parts[0] == 'mobile' and (
        len(parts) == 2 and parts[1] in TOP_LEVEL or
        len(parts) > 2 and parts[1] in SOURCE_DIRS and
        not any(p in ('node_modules', '.venv', '__pycache__', 'dist', 'build', '.expo') or p.startswith(('.pytest', '.env')) for p in parts[2:])
    )

def contained(root: Path, relative: str) -> Path:
    target = (root / relative).resolve()
    if not target.is_relative_to(root.resolve()) or not allowed(relative):
        raise ValueError(f'Unsafe or excluded source path: {relative}')
    return target

def make_plan(source: Path, destination: Path) -> dict:
    if source.resolve() == destination.resolve(): raise ValueError('Source and destination must differ')
    if not (destination / 'mobile').is_dir(): raise ValueError('Build copy must already contain mobile/')
    files = [p for p in (source / 'mobile').iterdir() if p.name in TOP_LEVEL and p.is_file()]
    for directory in SOURCE_DIRS:
        folder = source / 'mobile' / directory
        if folder.exists(): files.extend(p for p in folder.rglob('*') if p.is_file())
    rows = []
    for path in sorted(files):
        relative = path.relative_to(source).as_posix()
        if not allowed(relative): continue
        src = contained(source, relative); dst = contained(destination, relative)
        src_hash, dst_hash = digest(src), digest(dst)
        if src_hash == dst_hash: continue
        rows.append({'path': relative, 'sourceSha256': src_hash, 'destinationSha256': dst_hash,
                     'destinationNewer': dst.exists() and dst.stat().st_mtime > src.stat().st_mtime + 1})
    return {'source': str(source.resolve()), 'destination': str(destination.resolve()),
            'createdAt': datetime.now(timezone.utc).isoformat(), 'files': rows}

def apply_plan(plan: dict, source: Path, destination: Path) -> int:
    if plan['source'] != str(source.resolve()) or plan['destination'] != str(destination.resolve()):
        raise ValueError('Plan roots differ from the approved main/build-copy roots')
    # Validate EVERY file before writing any source. Changed/newer build-copy files require review.
    for row in plan['files']:
        src = contained(source, row['path']); dst = contained(destination, row['path'])
        if digest(src) != row['sourceSha256'] or digest(dst) != row['destinationSha256']:
            raise ValueError(f'File changed since plan; regenerate and review: {row["path"]}')
        if dst.exists() and dst.stat().st_mtime > src.stat().st_mtime + 1:
            raise ValueError(f'Newer differing build-copy file; reconcile in MAIN first: {row["path"]}')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    for row in plan['files']:
        src = contained(source, row['path']); dst = contained(destination, row['path'])
        if digest(src) != row['sourceSha256'] or digest(dst) != row['destinationSha256']:
            raise ValueError(f'File changed during sync; stop and review: {row["path"]}')
        if dst.exists():
            backup = (destination / '.g13-sync-backups' / stamp / row['path']).resolve()
            if not backup.is_relative_to(destination.resolve()): raise ValueError('Backup directory escapes build copy')
            backup.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(dst, backup)
        dst.parent.mkdir(parents=True, exist_ok=True)
        temp = dst.with_name(dst.name + '.g13-sync-tmp')
        if temp.exists(): raise ValueError(f'Temporary sync file already exists; review it: {temp}')
        shutil.copy2(src, temp); temp.replace(dst)
        if digest(dst) != row['sourceSha256']: raise ValueError(f'Copy verification failed: {dst}')
    return len(plan['files'])

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', type=Path, help='Apply a previously reviewed plan; otherwise only produce a plan')
    parser.add_argument('--plan', type=Path, default=MAIN / 'docs' / 'BUILD_SYNC_PLAN.json')
    args = parser.parse_args()
    if Path(__file__).resolve().parents[1] != MAIN.resolve(): raise SystemExit('Run this script from the MAIN project, not the build copy')
    if args.apply:
        print(f'Copied and hash-verified {apply_plan(json.loads(args.apply.read_text(encoding="utf-8")), MAIN, BUILD_COPY)} source files. Existing files were backed up. No deletes or builds performed.')
    else:
        plan = make_plan(MAIN, BUILD_COPY)
        args.plan.write_text(json.dumps(plan, indent=2) + '\n', encoding='utf-8')
        for row in plan['files']: print(('REVIEW NEWER' if row['destinationNewer'] else 'COPY CANDIDATE'), row['path'])
        print(f'Plan only: {len(plan["files"])} differing files. Review {args.plan}. No files copied to the build copy.')
if __name__ == '__main__': main()
