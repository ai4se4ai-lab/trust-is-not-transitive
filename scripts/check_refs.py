"""Check citation membership and retained primary-source verification evidence."""
import csv
import hashlib
import json
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]


def main():
    bib=(ROOT/'paper/references.bib').read_text(encoding='utf-8')
    keys=re.findall(r'@\w+\{([^,]+),',bib)
    assert len(keys)==len(set(keys))
    rows=list(csv.DictReader((ROOT/'paper/refs_verification.csv').open(encoding='utf-8')))
    verified={r['key']:r for r in rows}
    records=json.loads((ROOT/'docs/literature/metadata.json').read_text(encoding='utf-8'))
    by_key={r['key']:r for r in records}
    for key in keys:
        assert verified[key]['verified']=='yes'
        assert verified[key]['URL']==by_key[key]['url']
        assert verified[key]['evidence_sha256']==by_key[key]['evidence_sha256']
        local=ROOT/'docs/literature/evidence'/(verified[key]['URL'].rsplit('/',1)[-1]+'.html')
        if local.exists():assert hashlib.sha256(local.read_text(encoding='utf-8').encode()).hexdigest()==verified[key]['evidence_sha256']
    main=ROOT/'paper/main.tex'
    if main.exists():
        citations=set(k for group in re.findall(r'\\cite\{([^}]+)\}',main.read_text(encoding='utf-8')) for k in group.split(','))
        assert citations<=set(keys),citations-set(keys)
    assert len(keys)>=60
    print(len(keys),'bibliographic entries have matching opened-primary-source verification records.')
    print('Checks authenticate retained records, not correctness of all source claims; refresh is a separate network step.')


if __name__=='__main__':main()
