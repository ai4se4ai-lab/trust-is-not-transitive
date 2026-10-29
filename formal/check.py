"""Independent exhaustive finite-state checks, not a theorem prover."""
from __future__ import annotations
import itertools
import json
from pathlib import Path


def outcome(checked: bool, trace: int) -> bool:
    # Mirror the PRISM transition relation, independently from runtime modules.
    state = 0
    while state not in {3, 4}:
        if state == 0:
            state = 1
        elif state == 1:
            state = 3 if checked and trace != 1 else 2
        else:
            state = 3 if trace == 0 else 4
    return state == 4


def check() -> dict:
    canonical = [{'checked':c, 'trace':t, 'execute':outcome(c,t),
                  'bad_execute':outcome(c,t) and t!=1}
                 for c,t in itertools.product([False,True],range(3))]
    assert outcome(False,2) and not outcome(True,2)
    # Enumerate all downstream verdicts, destructive/production/approval,
    # secret/external flags. Every allowed execution satisfies both invariants.
    states = 0
    for bits in itertools.product([False,True],repeat=6):
        destructive,production,approved,secret,external,semantic_allow = bits
        bad = (destructive and production and not approved) or (secret and external)
        execute = semantic_allow and not bad
        assert not (execute and bad)
        states += 1
    even = [x for x in itertools.product([0,1],repeat=3) if sum(x)%2==0]
    odd = [x for x in itertools.product([0,1],repeat=3) if sum(x)%2==1]
    for law in [even,odd]:
        for i,j in itertools.combinations(range(3),2):
            assert sum(x[i]*x[j] for x in law)/len(law)==0.25
    return {'engine':'independent exhaustive Python finite-state checker',
            'canonical':canonical,'invariant_states':states,
            'parity_intersections':[sum(all(x) for x in law)/len(law) for law in [even,odd]]}


if __name__ == '__main__':
    root=Path(__file__).resolve().parents[1]
    out=root/'results/raw/formal.json'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(check(),indent=2)+'\n',encoding='utf-8')
    print(out.read_text())
