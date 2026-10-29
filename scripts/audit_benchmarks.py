"""Read public repository/license metadata; no benchmark execution or redistribution."""
import base64
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
REPOS={'AgentDojo':'ethz-spylab/agentdojo','ASB':'agiresearch/ASB',
       'RedCode':'AI-secure/RedCode','ToolEmu':'ryoungj/ToolEmu',
       'R-Judge':'Lordog/R-Judge','WildGuard':'allenai/wildguard',
       'AgentHarm':'UKGovernmentBEIS/inspect_evals'}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'TINT-research-audit'}),timeout=30) as response:
        return json.load(response)


def main():
    records=[]
    for name,repo in REPOS.items():
        row={'name':name,'repo':repo,'checked':'2026-10-29','executed':False}
        try:
            head=get('https://api.github.com/repos/'+repo+'/commits?per_page=1')[0]['sha']
            row['commit']=head
            if name=='AgentHarm':
                data=get(f'https://api.github.com/repos/{repo}/contents/src/inspect_evals/agentharm/LICENSE?ref={head}')
                row['spdx']='custom MIT plus safety-use restriction; inspect text'
            else:
                data=get(f'https://api.github.com/repos/{repo}/license?ref={head}')
                row['spdx']=data.get('license',{}).get('spdx_id','unclassified')
            text=base64.b64decode(data['content']).decode()
            row.update(license_url=data['html_url'],license_text=text,sha256=hashlib.sha256(text.encode()).hexdigest(),availability='source and license opened')
        except Exception as exc:
            row.update(availability='not verified',error=str(exc),spdx='unknown')
        records.append(row)
        print(name,row['availability'],row['spdx'],flush=True)
    out=ROOT/'experiments/benchmark_audit.json'
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(records,indent=2)+'\n')


if __name__=='__main__':main()
