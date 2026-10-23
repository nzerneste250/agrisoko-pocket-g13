"""Package reviewed repository files and the existing APK; never claim completion."""
from pathlib import Path
import hashlib
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'COMBO_A3_G13/'
SKIP = {'.git', '.venv', 'venv', 'env', 'node_modules', '.expo', 'dist', '__pycache__', '.pytest_cache', '.npm-cache', '.mypy_cache', '.ruff_cache', '.cache', '.tox', 'secrets', '.idea', '.vscode', 'android', 'ios'}
REQUIRED = ('README.md', 'mobile/package-lock.json', 'ai-api/requirements.txt', 'build/AgriSokoPocket_G13.apk', 'docs/SUBMISSION_MANIFEST.md', 'docs/COMBO_A3_G13_REPORT.pdf', 'evidence/CONTRIBUTIONS.pdf', 'evidence/TEST_LOG.pdf', 'evidence/FEEDBACK.pdf', 'evidence/AI_USE.md')

def permitted(path):
    parts = path.parts
    name = path.name.lower()
    if any(part.lower() in SKIP or part.startswith('.pytest-tmp') for part in parts):
        return False
    if parts[:3] == ('ai-api', 'data', 'index') or parts[:2] == ('ai-api', 'evaluation'):
        return False
    if name.startswith(('tmp_', 'tmp-')) or (name.startswith('.env') and name != '.env.example'):
        return False
    return not (name.endswith(('.log', '.pyc', '.zip', '.pem', '.key', '.p12', '.jks', '.keystore'))
                or 'secret' in name or 'credential' in name or name == 'config.local.json')

def main():
    target = ROOT / 'COMBO_A3_G13.zip'
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    candidates = {Path(p) for p in tracked if p}
    candidates.update(Path(p) for p in ('build/AgriSokoPocket_G13.apk', 'docs/FINALIZATION_STATUS.md', 'docs/FINALIZATION_VALIDATION.json'))
    paths = sorted(p for p in candidates if permitted(p) and (ROOT / p).is_file())
    for required in REQUIRED:
        assert Path(required) in paths, required
    apk = ROOT / 'build/AgriSokoPocket_G13.apk'
    digest = hashlib.sha256(apk.read_bytes()).hexdigest()
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
        for relative in paths:
            archive.write(ROOT / relative, PREFIX + relative.as_posix())
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        names = archive.namelist()
        assert all(n.startswith(PREFIX) for n in names)
        for required in REQUIRED:
            assert PREFIX + required in names, required
        for folder in ('mobile', 'ai-api', 'build', 'docs', 'evidence'):
            assert any(n.startswith(PREFIX + folder + '/') for n in names)
        assert hashlib.sha256(archive.read(PREFIX + 'build/AgriSokoPocket_G13.apk')).hexdigest() == digest
    print(f'INCOMPLETE submission archive: {target}; {target.stat().st_size} bytes; {len(paths)} files')
    print('Missing demonstration: evidence/COMBO_A3_G13_DEMO.mp4')

if __name__ == '__main__':
    main()
