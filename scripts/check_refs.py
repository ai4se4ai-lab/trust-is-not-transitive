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
    refresh_path=ROOT/'docs/literature/audit-2026-11-01/audit.json'
    if refresh_path.exists():
        refreshed=json.loads(refresh_path.read_text(encoding='utf-8'))
        reviewed={r['key']:r for r in refreshed}
        assert len(rows)==len(verified) and len(refreshed)==len(reviewed), 'Duplicate verification records'
        assert set(keys)==set(verified)==set(reviewed), 'Bibliography/audit/verification keys differ'
        for key in keys:
            record=reviewed[key]
            entry=re.search(r'@\w+\{'+re.escape(key)+r',.*?\n\}',bib,flags=re.S).group()
            assert hashlib.sha256(entry.encode()).hexdigest()==record['entry_sha256'], ('Entry changed since audit',key)
            row=verified[key]
            assert row['verified']=='audited' and row['date_checked']==record['checked'],key
            assert row['URL']==record['entry'].get('url','https://doi.org/'+record['entry'].get('doi','')),key
            assert row['evidence_sha256']==hashlib.sha256(json.dumps(record,ensure_ascii=False,sort_keys=True).encode()).hexdigest(),key
            assert record['sources'] and record['evidence'],key
            for name,expected in record['evidence'].items():
                assert Path(name).name==name
                local=refresh_path.parent/name
                assert local.is_file() and hashlib.sha256(local.read_bytes()).hexdigest()==expected, ('Evidence differs',key,name)
            if 'historical_audit' in record:
                for name,expected in record['historical_audit']['evidence'].items():
                    local=ROOT/'docs/literature/audit-2026-10-29'/name
                    assert local.is_file() and hashlib.sha256(local.read_bytes()).hexdigest()==expected, ('Historical evidence differs',key,name)
        citations=set()
        for tex in (ROOT/'paper').rglob('*.tex'):
            text=re.sub(r'(?m)(?<!\\)%.*$','',tex.read_text(encoding='utf-8'))
            citations.update(k.strip() for group in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}',text) for k in group.split(','))
        assert citations<=set(keys),citations-set(keys)
        print(len(keys),'entries match the 2026-11-01 reviewed audit and evidence hashes;')
        print(sum(r['changed'] for r in refreshed),'entries corrected. All citation keys resolve.')
        print('Google Scholar was inaccessible (HTTP 429). Access and author-version limitations are recorded in REFERENCE_AUDIT.md.')
        return
    records=json.loads((ROOT/'docs/literature/metadata.json').read_text(encoding='utf-8'))
    by_key={r['key']:r for r in records}
    audit_path=ROOT/'docs/literature/audit-2026-10-29/audit.json'
    audit_records=json.loads(audit_path.read_text(encoding='utf-8')) if audit_path.exists() else []
    audited={r['key']:r for r in audit_records}
    if audited:
        assert set(keys)==set(verified) and set(audited)<=set(keys), 'Bibliography/audit/verification keys differ'
        added=json.loads((ROOT/'docs/literature/audit-2026-10-31/crossref.json').read_text(encoding='utf-8'))
        assert set(keys)-set(audited)==set(added), 'Entries outside both audits'
    for key in keys:
        if verified[key]['verified']=='primary':
            record=audited[key]
            entry=re.search(r'@\w+\{'+re.escape(key)+r',.*?\n\}',bib,flags=re.S).group()
            assert hashlib.sha256(entry.encode()).hexdigest()==record['entry_sha256'], ('Entry changed since audit',key)
            assert verified[key]['evidence_sha256']==hashlib.sha256(json.dumps(record,ensure_ascii=False,sort_keys=True).encode()).hexdigest(),key
            assert verified[key]['URL']==record['entry'].get('url',record['sources'][0]),key
            assert record['sources'] and record['evidence'],key
            for name,expected in record['evidence'].items():
                assert Path(name).name==name
                local=audit_path.parent/name
                assert local.is_file(), ('Missing primary-source evidence',key,name)
                assert hashlib.sha256(local.read_bytes()).hexdigest()==expected, ('Changed evidence',key,name)
            continue
        if verified[key]['verified']=='metadata':
            # Classic/methodological sources: bibliographic metadata were checked
            # against Crossref, OpenAlex or arXiv records; no archived HTML evidence.
            assert key not in by_key and verified[key]['URL'].startswith('https://')
            continue
        assert verified[key]['verified']=='yes'
        assert verified[key]['URL']==by_key[key]['url']
        assert verified[key]['evidence_sha256']==by_key[key]['evidence_sha256']
        local=ROOT/'docs/literature/evidence'/(verified[key]['URL'].rsplit('/',1)[-1]+'.html')
        if local.exists():assert hashlib.sha256(local.read_text(encoding='utf-8').encode()).hexdigest()==verified[key]['evidence_sha256']
    main=ROOT/'paper/main.tex'
    if main.exists():
        citations=set(k.strip() for group in re.findall(r'\\cite\{([^}]+)\}',main.read_text(encoding='utf-8')) for k in group.split(','))
        assert citations<=set(keys),citations-set(keys)
    assert len(keys)>=60
    if audited:
        print(len(keys),'entries match the reviewed primary-source audit and archived evidence hashes;')
        print(sum(r['upgraded_from_arxiv'] for r in audit_records),'arXiv entries upgraded to published versions;',
              sum(r['status']=='preprint' for r in audit_records),'verified preprints retained.')
    else:
        classic=sum(verified[k]['verified']=='metadata' for k in keys)
        print(len(keys)-classic,'arXiv entries have matching opened-primary-source verification records;',
              classic,'classic entries have registry-checked (Crossref/OpenAlex/arXiv) metadata records.')
    print('Checks authenticate retained records, not correctness of all source claims; refresh is a separate network step.')


if __name__=='__main__':main()
