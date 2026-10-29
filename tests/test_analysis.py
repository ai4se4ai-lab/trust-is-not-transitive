"""Independent artifact mutation checks for retained LP evidence."""
from copy import deepcopy
import pytest
from scripts.process_results import verify_mixture_record


def record():
    return {'risks':[.05,.15],'costs':[10.,1.],'mixture_weights':[0.,.5,.5],
            'mixture_risk':.1,'mixture_cost':5.5}


def test_lp_evidence_independently_verified():
    verify_mixture_record(record())


@pytest.mark.parametrize('mutation',['normalization','risk','objective'])
def test_lp_evidence_tampering_rejected(mutation):
    row=deepcopy(record())
    if mutation=='normalization':row['mixture_weights'][0]+=.2
    if mutation=='risk':row['mixture_risk']+=.01
    if mutation=='objective':row['mixture_cost']+=.1
    with pytest.raises(AssertionError):verify_mixture_record(row)
