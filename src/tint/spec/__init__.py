"""Closed JSON DSL: direct trust edges with explicit assumption discharge."""
from __future__ import annotations
from dataclasses import dataclass
import json
from typing import Any


class SpecError(ValueError):
    pass


@dataclass(frozen=True)
class Contract:
    name: str
    scope: frozenset[str]
    requires: frozenset[str]
    provides: frozenset[str]
    view: str


@dataclass(frozen=True)
class TrustEdge:
    caller: str
    callee: str
    property: str
    evidence: frozenset[str]


@dataclass(frozen=True)
class Specification:
    layers: tuple[Contract, ...]
    edges: tuple[TrustEdge, ...]
    mandatory: frozenset[str]
    rules: tuple[str, ...]


def _keys(value: Any, expected: set[str]) -> None:
    if not isinstance(value, dict) or set(value) != expected:
        raise SpecError("unknown or missing fields")


def _strings(value: Any) -> frozenset[str]:
    if not isinstance(value,list) or not all(isinstance(x,str) and x for x in value) or len(set(value))!=len(value):
        raise SpecError("expected unique nonempty string list")
    return frozenset(value)


def parse(text: str) -> Specification:
    def unique(pairs):
        result={}
        for k,v in pairs:
            if k in result:
                raise SpecError("duplicate JSON field")
            result[k]=v
        return result
    try:
        data=json.loads(text,object_pairs_hook=unique)
    except json.JSONDecodeError as exc:
        raise SpecError("invalid JSON") from exc
    _keys(data,{"layers","trust","mandatory","rules"})
    if not isinstance(data['layers'],list) or not isinstance(data['trust'],list):
        raise SpecError("layers/trust must be lists")
    layers=[]
    for row in data['layers']:
        _keys(row,{"name","scope","requires","provides","view"})
        if not isinstance(row['name'],str) or not row['name'] or row['view'] not in {'metadata','raw','structured-v1'}:
            raise SpecError("invalid layer identity/view")
        layers.append(Contract(row['name'],_strings(row['scope']),_strings(row['requires']),_strings(row['provides']),row['view']))
    edges=[]
    for row in data['trust']:
        _keys(row,{"caller","callee","property","evidence"})
        if not all(isinstance(row[k],str) for k in ['caller','callee','property']):
            raise SpecError("invalid edge identifiers")
        edges.append(TrustEdge(row['caller'],row['callee'],row['property'],_strings(row['evidence'])))
    spec=Specification(tuple(layers),tuple(edges),_strings(data['mandatory']),tuple(sorted(_strings(data['rules']))))
    check(spec)
    return spec


def check(spec: Specification) -> None:
    by_name={x.name:x for x in spec.layers}
    if len(by_name)!=len(spec.layers) or not by_name:
        raise SpecError("duplicate or empty layers")
    if spec.mandatory!={'production_approval','secret_egress'}:
        raise SpecError("unknown or missing mandatory sink invariant")
    if set(spec.rules)!={'production_approval','secret_egress'}:
        raise SpecError("unsupported predicate; only typed deterministic fragment is implemented")
    seen=set()
    for edge in spec.edges:
        if edge.caller not in by_name or edge.callee not in by_name:
            raise SpecError("unknown direct trust endpoint; transitive authority is never inferred")
        pair=(edge.caller,edge.callee,edge.property)
        if pair in seen:
            raise SpecError("duplicate trust edge")
        seen.add(pair)
        caller,callee=by_name[edge.caller],by_name[edge.callee]
        if edge.property not in caller.scope & callee.scope:
            raise SpecError("property scope mismatch")
        if not edge.evidence <= caller.provides or not callee.requires <= edge.evidence:
            raise SpecError("undischarged assumptions (possibly unjustified transitive trust)")
        if callee.view=='raw' and 'quarantine' in callee.requires:
            raise SpecError("raw judge cannot satisfy quarantine interface")
    # Directed acyclic escalation graph; iterative DFS handles large specs.
    graph={name:set() for name in by_name}
    indegree={name:0 for name in by_name}
    for edge in spec.edges:
        if edge.callee not in graph[edge.caller]:
            graph[edge.caller].add(edge.callee)
            indegree[edge.callee]+=1
    queue=[name for name,degree in indegree.items() if degree==0]
    visited=0
    while queue:
        node=queue.pop()
        visited+=1
        for child in graph[node]:
            indegree[child]-=1
            if indegree[child]==0:
                queue.append(child)
    if visited!=len(by_name):
        raise SpecError("cyclic escalation")
