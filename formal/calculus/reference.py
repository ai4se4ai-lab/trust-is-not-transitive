"""Reference semantics: the definitions of core.py, as a plain tree interpreter.

Written from the equations of core.py, not from src/tint/hsl. It works on the tree of
paths of a DAG, so it is exponential in the worst case and is used only as an oracle.
`adequacy` in experiments/v2/run.py confirms it computes the definitions the proofs
are about, for check, eval and wf.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Mapping

Term = tuple


def unfold(nodes: Mapping, entry: str | None, types: tuple, usable=lambda name, node: frozenset(node.evidence)) -> Term:
    """nodes: id -> stage object from tint.hsl. Shared subterms stay shared in memory.

    `usable` gives Omega after dropping evidence whose view does not match the layer,
    a normalization that precedes the calculus.
    """
    Gate, Guard, Switch = types
    memo: dict = {None: ('deny',)}
    def go(name):
        if name in memo:
            return memo[name]
        node = nodes[name]
        if isinstance(node, Gate):
            term = ('gate', name, node.establishes, node.layer, usable(name, node), frozenset(node.provides), go(node.next))
        elif isinstance(node, Guard):
            term = ('guard', name, node.layer, usable(name, node), go(node.next))
        else:
            term = ('switch', name, go(node.then), go(node.otherwise))
        memo[name] = term
        return term
    return go(entry)


def locally_ok(goals: frozenset, req: frozenset, scope: frozenset, evidence: frozenset, available: frozenset) -> bool:
    return goals <= available or (req <= evidence and goals <= (available | scope))


def check(term: Term, available: frozenset, goals: frozenset, req: Mapping, scope: Mapping, facts: frozenset = frozenset()) -> bool:
    """The check equations. Memoized on (subterm, available, facts) for shared subterms."""
    memo: dict = {}
    def go(t, a, b):
        key = (id(t), a, b)
        if key in memo:
            return memo[key]
        if t[0] == 'deny':
            result = True
        elif t[0] == 'gate':
            if t[3] is None or req[t[3]] <= t[4] | b:
                result = go(t[6], a | {t[2]}, b | t[5])
            else:
                result = go(t[6], a, b)
        elif t[0] == 'guard':
            result = locally_ok(goals, req[t[2]], scope[t[2]], t[3] | b, a) and go(t[4], a, b)
        else:
            result = go(t[2], a, b) and go(t[3], a, b)
        memo[key] = result
        return result
    return go(term, available, facts)


def evaluate(term: Term, passes: Mapping, verdict: Mapping, branch: Mapping) -> tuple:
    """The eval equations. Models are keyed by node id. Returns ('accepted', id) or ('denied',)."""
    t = term
    while True:
        if t[0] == 'deny':
            return ('denied',)
        if t[0] == 'gate':
            if not passes[t[1]]:
                return ('denied',)
            t = t[6]
        elif t[0] == 'guard':
            v = verdict[t[1]]
            if v == 'acc':
                return ('accepted', t[1])
            if v != 'esc':
                return ('denied',)
            t = t[4]
        else:
            t = t[2] if branch[t[1]] else t[3]


def wf(term: Term, passes, verdict, branch, holds, safe: frozenset, req: Mapping, scope: Mapping, facts: frozenset = frozenset()) -> bool:
    """The wf equations: contract and realization premises on the reached invocations."""
    t = term
    while True:
        if t[0] == 'deny':
            return True
        if t[0] == 'gate':
            if not passes[t[1]]:
                return True
            here = holds[t[1]]
            if not (t[4] <= here and facts <= here):
                return False
            if t[3] is None or req[t[3]] <= here:
                if t[2] is not None and t[2] not in safe:
                    return False
                facts = facts | t[5]
            t = t[6]
        elif t[0] == 'guard':
            g, layer, omega, k = t[1], t[2], t[3], t[4]
            here = holds[g]
            if not (omega <= here and facts <= here):
                return False
            if verdict[g] == 'acc' and req[layer] <= here and not scope[layer] <= safe:
                return False
            if verdict[g] != 'esc':
                return True
            t = k
        else:
            t = t[2] if branch[t[1]] else t[3]


def residual(term: Term, goals: frozenset, req: Mapping, kinds: Mapping) -> frozenset:
    """(stage, assumed obligation) pairs supplied where some path leaves a goal open, or a veto stage provides."""
    found: set = set()
    seen: set = set()
    def go(t, a, b):
        key = (id(t), a, b)
        if t[0] == 'deny' or key in seen:
            return
        seen.add(key)
        if t[0] == 'gate':
            if t[3] is not None and (t[5] or (t[2] is not None and t[2] not in a)):
                found.update((t[1], x) for x in req[t[3]] & t[4])
            if t[3] is None or req[t[3]] <= t[4] | b:
                go(t[6], a | ({t[2]} if t[2] is not None else frozenset()), b | t[5])
            else:
                go(t[6], a, b)
        elif t[0] == 'guard':
            if not goals <= a:
                found.update((t[1], x) for x in req[t[2]] & t[3])
            go(t[4], a, b)
        else:
            go(t[2], a, b); go(t[3], a, b)
    go(term, frozenset(), frozenset())
    return frozenset(x for x in found if kinds[x[1]] == 'assumed')


def nodes_of(term: Term) -> dict:
    """The distinct stages of a term, by id."""
    found: dict = {}
    def go(t):
        if t[0] == 'deny' or t[1] in found:
            return
        found[t[1]] = t
        if t[0] == 'gate':
            go(t[6])
        elif t[0] == 'guard':
            go(t[4])
        else:
            go(t[2]); go(t[3])
    go(term)
    return found


def violating_model_exists(term: Term, goals: frozenset, req: Mapping, scope: Mapping, obligations: frozenset) -> bool:
    """Model search that shares nothing with the checker: enumerate models, apply wf and evaluate.

    For one safe set S, a verdict, pass or branch for every stage is enumerated by walking
    the decision: at each stage every behaviour is tried, and every subset of obligations
    is tried as E(n). Only stages the proposal reaches can matter, by the frame lemma's
    meaning, so a search over runs is a search over all models. Each complete run is then
    judged by `wf` and `evaluate`, the executable definitions of Figure 1.
    """
    goal_list, obligation_list = sorted(goals), sorted(obligations)
    subsets = lambda items: [frozenset(x for i, x in enumerate(items) if mask >> i & 1) for mask in range(1 << len(items))]
    held = subsets(obligation_list)
    for safe in subsets(goal_list):
        if goals <= safe:
            continue
        def walk(t, passes, verdict, branch, holds):
            if t[0] == 'deny':
                return False
            if t[0] == 'switch':
                return any(walk(t[2 if value else 3], passes, verdict, {**branch, t[1]: value}, holds) for value in (True, False))
            for here in held:
                chosen = {**holds, t[1]: here}
                if t[0] == 'gate':
                    if walk(t[6], {**passes, t[1]: True}, verdict, branch, chosen):
                        return True
                else:
                    accepted = {**verdict, t[1]: 'acc'}
                    if evaluate(term, passes, accepted, branch)[0] == 'accepted' and wf(term, passes, accepted, branch, chosen, safe, req, scope):
                        return True
                    if walk(t[4], passes, {**verdict, t[1]: 'esc'}, branch, chosen):
                        return True
            return False
        if walk(term, {}, {}, {}, {}):
            return True
    return False
