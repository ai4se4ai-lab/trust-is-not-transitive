"""Executable inventory of DSL support; no claim about a real policy corpus."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from tint.spec import parse,SpecError


def main():
    text=(ROOT/'experiments/configs/devagent.json').read_text()
    base=json.loads(text)
    rows=[]
    for name,rule in [('production approval','production_approval'),('secret egress','secret_egress'),
                      ('semantic injection','semantic_injection'),('filesystem confinement','path_confinement'),
                      ('cumulative spending','cumulative_budget')]:
        data=json.loads(text)
        if rule not in data['rules']:data['rules'].append(rule)
        accepted=True
        try:parse(json.dumps(data))
        except SpecError:accepted=False
        rows.append({'policy_class':name,'requested_rule':rule,'dsl_fully_supported':accepted,
                     'semantic_proxy_only':rule=='semantic_injection'})
    out=ROOT/'results/raw/policy_inventory.json'
    out.write_text(json.dumps({'policies':rows,'authored_spec_lines':len(text.splitlines()),
                               'authoring_time_measured':False,'participants':0},indent=2)+'\n')
    print(rows)


if __name__=='__main__':main()
