"""Separate expected CRC, split-conformal quantiles and high-confidence certification."""
from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np
from scipy.stats import beta


def _probability(value: float, name: str) -> None:
    if not math.isfinite(value) or not 0<value<1:
        raise ValueError(name+' must be strictly between zero and one')


def binomial_upper(misses: int, n: int, delta: float=0.05) -> float:
    _probability(delta,'delta')
    if type(n) is not int or type(misses) is not int or n<=0 or not 0<=misses<=n:
        raise ValueError('invalid binomial counts')
    return 1.0 if misses==n else float(beta.ppf(1-delta,misses+1,n-misses))


def split_quantile(scores: np.ndarray, alpha: float) -> float:
    _probability(alpha,'alpha')
    values=np.asarray(scores,dtype=float)
    if values.ndim!=1 or len(values)==0 or not np.isfinite(values).all():
        raise ValueError('invalid nonconformity scores')
    rank=math.ceil((len(values)+1)*(1-alpha))
    return math.inf if rank>len(values) else float(np.sort(values)[rank-1])


def conformal_risk_control(losses: np.ndarray, alpha: float) -> int | None:
    """Rows are samples; columns are fixed increasingly conservative policies.

    Returns a column or None for an externally guaranteed zero-loss block-all
    fallback. Promise: marginal expected risk under exchangeability and nested
    bounded loss. It is not a conditional high-probability certificate.
    """
    _probability(alpha,'alpha')
    values=np.asarray(losses,dtype=float)
    if values.ndim!=2 or values.shape[0]==0 or values.shape[1]==0 or not np.isfinite(values).all() or np.any((values<0)|(values>1)):
        raise ValueError('invalid bounded loss matrix')
    if np.any(np.diff(values,axis=1)>0):
        raise ValueError('CRC requires pointwise nested decreasing loss')
    feasible=np.flatnonzero((values.sum(axis=0)+1)/(len(values)+1)<=alpha)
    return int(feasible[0]) if len(feasible) else None


def certify_family(losses: np.ndarray, delta: float) -> np.ndarray:
    _probability(delta,'delta')
    values=np.asarray(losses)
    if values.ndim!=2 or 0 in values.shape or not np.isin(values,[0,1]).all():
        raise ValueError('expected binary fixed-policy losses')
    return np.array([binomial_upper(int(column.sum()),len(column),delta/values.shape[1]) for column in values.T])


def correlation(misses: np.ndarray) -> np.ndarray:
    values=np.asarray(misses,dtype=float)
    if values.ndim!=2 or values.shape[0]<2 or values.shape[1]<2 or not np.isin(values,[0,1]).all():
        raise ValueError('expected binary miss matrix')
    # Constant guards have undefined correlation, represented as NaN explicitly.
    with np.errstate(invalid='ignore',divide='ignore'):
        return np.corrcoef(values,rowvar=False)


def veto_bound(miss_rates: list[float], prevalence: float=1.0, common_shock: float | None=None) -> float:
    if not miss_rates or not all(math.isfinite(v) and 0<=v<=1 for v in miss_rates) or not 0<=prevalence<=1:
        raise ValueError('invalid miss rates/prevalence')
    if common_shock is None:
        return prevalence*min(miss_rates)
    if not math.isfinite(common_shock) or not 0<=common_shock<=1:
        raise ValueError('invalid mixture weight')
    return prevalence*((1-common_shock)*math.prod(miss_rates)+common_shock*min(miss_rates))


@dataclass(frozen=True)
class Certificate:
    policy_id: str
    context_id: str
    view_version: str
    upper_risk: float
    delta: float
    sample_count: int

    def applies(self, policy_id: str, context_id: str, view_version: str, epsilon: float, max_delta: float=0.05) -> bool:
        return (self.policy_id==policy_id and self.context_id==context_id and self.view_version==view_version
                and math.isfinite(self.upper_risk) and 0<=self.upper_risk<=epsilon<=1
                and 0<self.delta<=max_delta<1 and type(self.sample_count) is int and self.sample_count>0)
