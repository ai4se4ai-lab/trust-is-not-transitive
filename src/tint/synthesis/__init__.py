"""Exact finite-family selection and two-action Lagrangian policies."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from scipy.optimize import linprog
from ..calibration import certify_family


@dataclass(frozen=True)
class Candidate:
    identifier: str
    threshold: float
    layers: int


def select(losses: np.ndarray, costs: np.ndarray, candidates: list[Candidate], epsilon: float,
           delta: float=0.05, late: np.ndarray | None=None, tail_budget: float=0.05) -> tuple[Candidate,float]:
    values=np.asarray(losses)
    costs=np.asarray(costs,dtype=float)
    if not 0<=epsilon<=1 or values.ndim!=2 or values.shape!=costs.shape or values.shape[1]!=len(candidates) or not np.isfinite(costs).all() or np.any(costs<0):
        raise ValueError('inconsistent candidate arrays/budget')
    bounds=certify_family(values,delta/2 if late is not None else delta)
    feasible=bounds<=epsilon
    if late is not None:
        if np.shape(late)!=values.shape or not 0<=tail_budget<=1:
            raise ValueError('invalid latency-tail array/budget')
        feasible &= certify_family(late,delta/2)<=tail_budget
    indices=np.flatnonzero(feasible)
    if len(indices)==0:
        raise ValueError('no certified feasible candidate; block or request a new calibration run')
    best=min(indices,key=lambda i:(float(costs[:,i].mean()),candidates[i].identifier))
    return candidates[best],float(bounds[best])


def lagrangian_escalate(r0: np.ndarray, r1: np.ndarray, cost: np.ndarray, multiplier: float) -> np.ndarray:
    a,b,c=map(lambda x:np.asarray(x,dtype=float),(r0,r1,cost))
    if a.shape!=b.shape or a.shape!=c.shape or not np.isfinite([*a.flat,*b.flat,*c.flat,multiplier]).all() or np.any((a<0)|(a>1)|(b<0)|(b>1)|(c<=0)) or multiplier<0:
        raise ValueError('invalid conditional risks/costs')
    return multiplier*(a-b)>c


def optimal_mixture(risks: np.ndarray, costs: np.ndarray, epsilon: float) -> np.ndarray:
    r,c=np.asarray(risks,dtype=float),np.asarray(costs,dtype=float)
    if r.ndim!=1 or r.shape!=c.shape or len(r)==0 or not np.isfinite(r).all() or not np.isfinite(c).all() or np.any((r<0)|(r>1)|(c<0)) or not 0<=epsilon<=1:
        raise ValueError('invalid finite-family LP')
    result=linprog(c,A_ub=r[None,:],b_ub=[epsilon],A_eq=np.ones((1,len(r))),b_eq=[1],bounds=(0,1),method='highs')
    if not result.success:
        raise ValueError('infeasible mixture')
    return result.x
