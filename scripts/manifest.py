"""Hash raw observations and the source/configuration used to analyze them."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]


TEXT={'.py','.md','.tex','.bib','.toml','.lock','.pm','.pctl','.sh','.txt'}


def digest(path):
    # Source files are hashed with LF line endings so that Windows (autocrlf)
    # and Linux checkouts agree; recorded data/JSON bytes are hashed as stored.
    data=path.read_bytes()
    if path.suffix in TEXT or path.name in {'requirements.lock','requirements-paper.lock'}:
        data=data.replace(b'\r\n',b'\n')
    return hashlib.sha256(data).hexdigest()


def files():
    paths=[]
    for directory in ['src','formal','experiments','scripts','results/raw','results/processed']:
        paths.extend(p for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in {'.pyc'})
    paths.extend(ROOT/p for p in ['requirements.lock','requirements-paper.lock','pyproject.toml'])
    return {p.relative_to(ROOT).as_posix():digest(p) for p in sorted(set(paths))}


if __name__=='__main__':
    path=ROOT/'results/manifest.json'
    actual=files()
    if '--verify' in sys.argv:
        recorded=json.loads(path.read_text())['files']
        assert recorded==actual,'manifest differs; inspect changed source/data before explicitly refreshing'
        print(len(actual),'source/config/raw/processed hashes match manifest.')
    else:
        path.write_text(json.dumps({'algorithm':'sha256','analysis_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                                    'raw_execution_commits':'recorded separately in each raw environment.json',
                                    'files':actual},indent=2,sort_keys=True)+'\n')
        print('Wrote manifest for',len(actual),'files.')
