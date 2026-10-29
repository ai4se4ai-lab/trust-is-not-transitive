"""Randomized probability checks (sanity tests, not substitutes for proofs)."""
import itertools
import json
from pathlib import Path
import random


def run():
    rng=random.Random(20261029)
    for _ in range(10000):
        weights=[rng.random() for _ in range(8)]
        total=sum(weights)
        weights=[w/total for w in weights]
        states=list(itertools.product([0,1],repeat=3))
        marginal=[sum(w for s,w in zip(states,weights) if s[i]) for i in range(3)]
        joint=weights[-1]
        assert joint<=min(marginal)+1e-12
        assert joint>=max(0,sum(marginal)-2)-1e-12
        # disjoint early acceptance has a sum, and may exceed any route's loss
        route=[rng.random()/3 for _ in range(3)]
        assert sum(route)<=1
        m=[rng.random() for _ in range(3)]
        rho=rng.random()
        mixture=(1-rho)*m[0]*m[1]*m[2]+rho*min(m)
        assert m[0]*m[1]*m[2]-1e-12<=mixture<=min(m)+1e-12
    return {'seed':20261029,'instances':10000,'status':'passed',
            'scope':'arbitrary three-Bernoulli laws; Frechet inequalities; common-shock interpolation'}


if __name__=='__main__':
    p=Path(__file__).resolve().parents[1]/'results/raw/formal_sanity.json'
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(run(),indent=2)+'\n')
    print(p.read_text())
