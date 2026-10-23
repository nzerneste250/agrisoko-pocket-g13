"""Package a reproducible source/evidence draft; never include dependencies or secrets."""
from pathlib import Path
import os
import zipfile
ROOT=Path(__file__).resolve().parents[1]
SKIP={'.git','.venv','venv','node_modules','.expo','dist','__pycache__','.pytest_cache','.npm-cache','android','ios'}

def main():
    target=ROOT/'COMBO_A3_G13.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as archive:
        for parent, dirs, files in os.walk(ROOT):
            dirs[:]=sorted(d for d in dirs if d not in SKIP and not d.startswith('.pytest-tmp'))
            for name in sorted(files):
                path=Path(parent)/name; relative=path.relative_to(ROOT)
                if path==target or name.endswith(('.log','.pyc','.secret')) or (name.startswith('.env') and name!='.env.example'): continue
                if relative.parts[:3]==('ai-api','data','index'): continue
                archive.write(path,relative.as_posix())
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        for required in ('docs/SUBMISSION_MANIFEST.md','mobile/package-lock.json','ai-api/requirements.txt','docs/COMBO_A3_G13_REPORT.pdf','evidence/AI_USE.md'):
            assert required in archive.namelist(),required
    print(f'DRAFT archive: {target}; {target.stat().st_size} bytes')
if __name__=='__main__':main()
