"""Hierarchy Specification Language: general guardrail hierarchies as checked DAGs.

A hierarchy is an acyclic graph of three stage types. A *gate* passes or denies,
and passing establishes a goal and provides facts for later stages: unconditionally
if the gate is deterministic, or under its layer's obligations if it is a veto stage.
A *guard* consults a layer, whose verdict accepts (ending the decision on that
node's route), blocks, or escalates to its successor; it provides nothing. A *switch*
routes on a trusted condition. Leaving the graph denies, so there is no accepting
terminal: every acceptance is a guard's.

`check` decides the composition condition of the paper and returns witnesses. A
componentwise must-analysis decides hierarchies without provided facts exactly and
in near-linear time. With provided facts it is only sound, so a rejection is
refined by exact exploration of the reachable (goals, facts) states; the problem is
coNP-complete, and that exploration is exponential in the worst case.
"""
from __future__ import annotations
from dataclasses import dataclass, field, replace
import json
from typing import Any

KINDS = ('checked', 'construction', 'assumed')
VIEWS = ('metadata', 'raw', 'structured')


class SpecError(ValueError):
    pass


@dataclass(frozen=True)
class Obligation:
    name: str
    kind: str
    view: str | None = None  # if set, only a layer with this view can be given it


@dataclass(frozen=True)
class Layer:
    name: str
    scope: frozenset[str]     # goals this layer's contract covers on acceptance
    requires: frozenset[str]  # its assumption O_l: obligation names
    view: str


@dataclass(frozen=True)
class Gate:
    id: str
    rule: str
    establishes: str | None                  # None: the gate only provides facts
    next: str | None
    layer: str | None = None                 # a veto stage's contract; None if deterministic
    evidence: frozenset[str] = frozenset()   # Omega on the edge into this stage
    provides: frozenset[str] = frozenset()   # D: obligations that hold on every later invocation


@dataclass(frozen=True)
class Guard:
    id: str
    layer: str
    evidence: frozenset[str]  # Omega: scoped to this one invocation
    next: str | None


@dataclass(frozen=True)
class Switch:
    id: str
    condition: str
    then: str | None
    otherwise: str | None


Node = Gate | Guard | Switch


def successors(node: Node) -> tuple[str, ...]:
    pair = (node.then, node.otherwise) if isinstance(node, Switch) else (node.next,)
    return tuple(x for x in pair if x is not None)


@dataclass(frozen=True)
class Hierarchy:
    goals: frozenset[str]
    obligations: dict[str, Obligation]
    layers: dict[str, Layer]
    nodes: dict[str, Node]
    entry: str | None


def _keys(value: Any, required: set[str], optional: set[str] = frozenset()) -> None:
    if not isinstance(value, dict) or not required <= set(value) <= required | optional:
        raise SpecError('unknown or missing fields: ' + str(value)[:80])


def _names(value: Any) -> frozenset[str]:
    if not isinstance(value, list) or not all(isinstance(x, str) and x for x in value) or len(set(value)) != len(value):
        raise SpecError('expected a list of unique non-empty names')
    return frozenset(value)


def _name(value: Any) -> str:
    if not isinstance(value, str) or not value:
        raise SpecError('expected a non-empty name')
    return value


def _ref(value: Any) -> str | None:
    return None if value is None else _name(value)


def _unique(pairs: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise SpecError('duplicate JSON field: ' + key)
        result[key] = value
    return result


def parse(text: str) -> Hierarchy:
    """Closed-schema parser. Structural validity only; `check` decides composition."""
    try:
        data = json.loads(text, object_pairs_hook=_unique)
    except json.JSONDecodeError as exc:
        raise SpecError('invalid JSON') from exc
    _keys(data, {'version', 'goals', 'obligations', 'layers', 'nodes', 'entry'})
    if data['version'] != 'hsl-1':
        raise SpecError('unsupported version')
    obligations: dict[str, Obligation] = {}
    for row in data['obligations']:
        _keys(row, {'name', 'kind'}, {'view'})
        if row['kind'] not in KINDS or row.get('view') not in (None, *VIEWS):
            raise SpecError('invalid obligation kind or view')
        name = _name(row['name'])
        if name in obligations:
            raise SpecError('duplicate obligation: ' + name)
        obligations[name] = Obligation(name, row['kind'], row.get('view'))
    layers: dict[str, Layer] = {}
    for row in data['layers']:
        _keys(row, {'name', 'scope', 'requires', 'view'})
        if row['view'] not in VIEWS:
            raise SpecError('invalid view')
        name = _name(row['name'])
        if name in layers:
            raise SpecError('duplicate layer: ' + name)
        layers[name] = Layer(name, _names(row['scope']), _names(row['requires']), row['view'])
    nodes: dict[str, Node] = {}
    for row in data['nodes']:
        if not isinstance(row, dict) or 'type' not in row:
            raise SpecError('node without type')
        kind = row['type']
        if kind == 'gate':
            _keys(row, {'type', 'id', 'rule', 'establishes', 'next'}, {'layer', 'evidence', 'provides'})
            node: Node = Gate(_name(row['id']), _name(row['rule']), _ref(row['establishes']), _ref(row['next']),
                              _ref(row.get('layer')), _names(row.get('evidence', [])), _names(row.get('provides', [])))
        elif kind == 'guard':
            _keys(row, {'type', 'id', 'layer', 'evidence', 'next'})
            node = Guard(_name(row['id']), _name(row['layer']), _names(row['evidence']), _ref(row['next']))
        elif kind == 'switch':
            _keys(row, {'type', 'id', 'condition', 'then', 'otherwise'})
            node = Switch(_name(row['id']), _name(row['condition']), _ref(row['then']), _ref(row['otherwise']))
        else:
            raise SpecError('unknown node type')
        if node.id in nodes:
            raise SpecError('duplicate node: ' + node.id)
        nodes[node.id] = node
    return Hierarchy(_names(data['goals']), obligations, layers, nodes, _ref(data['entry']))


@dataclass(frozen=True)
class Finding:
    code: str      # dangling | cycle | undeclared | view | obligation | coverage
    node: str
    detail: str    # the missing name, where one applies
    path: tuple[str, ...] = ()  # a witness path from the entry to the node
    goal: str = ''              # for obligation and coverage: the goal left open on that path


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)
    warnings: list[Finding] = field(default_factory=list)  # evidence dropped because its view does not match
    exact_states: int = 0                              # (node, goals, facts) states explored by refinement
    routes: tuple[str, ...] = ()                       # reachable guard nodes
    residual: tuple[tuple[str, str], ...] = ()         # (node, assumed obligation)
    claims: tuple[tuple[str, str], ...] = ()           # (deterministic gate, goal or fact it is trusted to establish)
    checked: tuple[tuple[str, str], ...] = ()          # (node, checked obligation)
    construction: tuple[tuple[str, str], ...] = ()     # (node, obligation by construction)
    order: tuple[str, ...] = ()                        # topological order of reachable nodes

    @property
    def ok(self) -> bool:
        return not self.findings


def _order(h: Hierarchy) -> tuple[list[str], str | None]:
    """Reachable nodes in topological order (iterative DFS); also a cycle witness."""
    if h.entry is None:
        return [], None
    state: dict[str, int] = {}
    postorder: list[str] = []
    stack: list[tuple[str, int]] = [(h.entry, 0)]
    state[h.entry] = 1
    while stack:
        name, index = stack.pop()
        following = successors(h.nodes[name])
        if index < len(following):
            stack.append((name, index + 1))
            child = following[index]
            if state.get(child) == 1:
                return [], child
            if child not in state:
                state[child] = 1
                stack.append((child, 0))
        else:
            state[name] = 2
            postorder.append(name)
    return postorder[::-1], None


def usable(h: Hierarchy, name: str, layer: str | None) -> frozenset[str]:
    """Omega at a stage, less evidence tied to a view this layer does not have."""
    node = h.nodes[name]
    if layer is None:
        return node.evidence
    view = h.layers[layer].view
    return frozenset(x for x in node.evidence if x in h.obligations and h.obligations[x].view in (None, view))


def credited(h: Hierarchy, node: Gate, facts: frozenset[str] = frozenset()) -> bool:
    """A gate establishes its goal only if its layer's obligations are supplied or provided here."""
    return node.layer is None or h.layers[node.layer].requires <= usable(h, node.id, node.layer) | facts


def _structure(h: Hierarchy, report: Report) -> None:
    names = set(h.nodes)
    for node in h.nodes.values():
        for child in successors(node):
            if child not in names:
                report.findings.append(Finding('dangling', node.id, child))
        if (isinstance(node, Guard) or isinstance(node, Gate) and node.layer is not None) and node.layer not in h.layers:
            report.findings.append(Finding('undeclared', node.id, node.layer))
        if isinstance(node, Gate):
            if node.establishes is not None and node.establishes not in h.goals:
                report.findings.append(Finding('undeclared', node.id, node.establishes))
            for item in sorted(node.provides):
                # A checked fact would claim a runtime predicate that nothing runs.
                if item not in h.obligations or h.obligations[item].view is not None or h.obligations[item].kind == 'checked':
                    report.findings.append(Finding('undeclared', node.id, item))
            if node.layer is None:
                for item in sorted(node.evidence - set(h.obligations)):
                    report.findings.append(Finding('undeclared', node.id, item))
    for layer in h.layers.values():
        for item in sorted((layer.scope - h.goals) | (layer.requires - set(h.obligations))):
            report.findings.append(Finding('undeclared', layer.name, item))
    if h.entry is not None and h.entry not in names:
        report.findings.append(Finding('dangling', '<entry>', h.entry))


def _mask(names, rank: dict[str, int]) -> int:
    """A set as an integer, in time linear in its size plus the words of the universe."""
    buffer = bytearray((len(rank) + 7) // 8)
    for name in names:
        if name in rank:
            i = rank[name]
            buffer[i >> 3] |= 1 << (i & 7)
    return int.from_bytes(buffer, 'little')


def _bits(mask: int, ranked: list[str]):
    """Names of the set bits, one scan of the bytes, so a dense mask stays linear."""
    for index, byte in enumerate(mask.to_bytes((mask.bit_length() + 7) // 8, 'little')):
        for bit in range(8):
            if byte >> bit & 1:
                yield ranked[index * 8 + bit]


def check(h: Hierarchy, witnesses: bool = True) -> Report:
    """Decide whether every implementation of `h`'s contracts is safe.

    Forward must-analysis over the DAG: for each node, the goals and facts every path
    to it has established. A pass in topological order with meet = intersection computes
    the meet over all paths when nothing is provided, because the transfer functions are
    then gen-only and independent. Goal sets are integers, so a set operation costs
    O(|goals|/w). Decision: O((|V|+|E|)*(|goals|+|obligations|)/w + S log S) for a
    specification of size S; `witnesses` adds up to |V| per finding.

    With provided facts the analysis is sound but can reject a safe hierarchy, since
    goals and facts are correlated across paths. A rejection is then settled exactly
    by `_refine`, over the reachable (goals, facts) pairs.
    """
    report = Report()
    _structure(h, report)
    if report.findings:
        return report
    order, cycle = _order(h)
    if cycle is not None:
        report.findings.append(Finding('cycle', cycle, cycle))
        return report
    ranked = sorted(h.goals)
    goal_rank = {g: i for i, g in enumerate(ranked)}
    obligations = sorted(h.obligations)
    fact_rank = {o: i for i, o in enumerate(obligations)}
    all_goals = (1 << len(ranked)) - 1
    # Per layer once, so that a guard pays for words of goals, not for each goal.
    outside = {name: all_goals & ~_mask(layer.scope, goal_rank) for name, layer in h.layers.items()}
    needs = {name: _mask(layer.requires, fact_rank) for name, layer in h.layers.items()}
    supplied: dict[str, int] = {}
    for name in order:
        node = h.nodes[name]
        if not isinstance(node, Switch):
            supplied[name] = _mask(usable(h, name, node.layer), fact_rank)
    flow = any(isinstance(h.nodes[n], Gate) and h.nodes[n].provides for n in order)
    available: dict[str, int] = {}
    facts: dict[str, int] = {}
    generated: dict[str, int] = {}
    parent: dict[str, str] = {}
    predecessors: dict[str, list[str]] = {name: [] for name in order}
    for name in order:
        node = h.nodes[name]
        here = available.setdefault(name, 0)
        known = facts.setdefault(name, 0)
        made = gained = 0
        if isinstance(node, Gate) and (node.layer is None or not needs[node.layer] & ~(supplied[name] | known)):
            made = 0 if node.establishes is None else 1 << goal_rank[node.establishes]
            gained = _mask(node.provides, fact_rank) if node.provides else 0
        generated[name] = made
        out, out_facts = here | made, known | gained
        for child in successors(node):
            predecessors[child].append(name)
            if child in available:
                available[child] &= out
                facts[child] &= out_facts
            else:
                available[child], facts[child] = out, out_facts
                parent[child] = name
    def path_to(name: str) -> tuple[str, ...]:
        trail = [name]
        while trail[-1] in parent:
            trail.append(parent[trail[-1]])
        return tuple(reversed(trail))
    lacking: dict[tuple[str, int], str | None] = {}
    def gap_path(name: str, goal: str) -> tuple[str, ...]:
        # goal is unavailable at name, so some predecessor's output lacks it. The first such
        # predecessor is remembered, so each (node, goal) scans its predecessors only once.
        index, trail = goal_rank[goal], [name]
        while True:
            key = (trail[-1], index)
            if key not in lacking:
                lacking[key] = next((p for p in predecessors[trail[-1]] if not ((available[p] | generated[p]) >> index) & 1), None)
            step = lacking[key]
            if step is None:
                return tuple(reversed(trail))
            trail.append(step)
    routes: list[str] = []
    evidence_by_kind: dict[str, list] = {'assumed': [], 'checked': [], 'construction': []}
    for name in order:
        node = h.nodes[name]
        if isinstance(node, Switch) or (isinstance(node, Gate) and node.layer is None):
            continue
        layer = h.layers[node.layer]
        for item in sorted(node.evidence):
            obligation = h.obligations.get(item)
            if obligation is None:
                report.findings.append(Finding('undeclared', name, item, path_to(name) if witnesses else ()))
            elif obligation.view is not None and obligation.view != layer.view:
                report.warnings.append(Finding('view', name, item, path_to(name) if witnesses else ()))
        have = supplied[name] | facts[name]
        if isinstance(node, Gate):
            # A contract-bearing gate matters if its goal is still open here, or it provides a fact.
            relevant = bool(node.provides) or (node.establishes is not None and not (available[name] >> goal_rank[node.establishes]) & 1)
        else:
            routes.append(name)
            # Only goals still open here depend on this guard. When gates have
            # established every goal, acceptance is safe whatever the guard does,
            # so demanding its obligations would be a false alarm.
            missing = all_goals & ~available[name]
            relevant = missing != 0
            if relevant:
                goal = ranked[(missing & -missing).bit_length() - 1]
                for item in _bits(needs[node.layer] & ~have, obligations):
                    report.findings.append(Finding('obligation', name, item, gap_path(name, goal) if witnesses else (), goal))
                for g in _bits(missing & outside[node.layer], ranked):
                    report.findings.append(Finding('coverage', name, g, gap_path(name, g) if witnesses else (), g))
        if relevant:
            for item in sorted(layer.requires & usable(h, name, node.layer)):
                if item in h.obligations:
                    evidence_by_kind[h.obligations[item].kind].append((name, item))
    report.routes = tuple(routes)
    report.residual = tuple(evidence_by_kind['assumed'])
    report.checked = tuple(evidence_by_kind['checked'])
    report.construction = tuple(evidence_by_kind['construction'])
    report.order = tuple(order)
    report.claims = tuple((name, x) for name in order if isinstance(h.nodes[name], Gate) and h.nodes[name].layer is None
                          for x in sorted(({h.nodes[name].establishes} - {None}) | h.nodes[name].provides))
    if flow and (witnesses or any(f.code in ('obligation', 'coverage') for f in report.findings)):
        kept = [f for f in report.findings if f.code not in ('obligation', 'coverage')]
        refined, report.exact_states, open_at = _refine(h, order, ranked, goal_rank, obligations, fact_rank, supplied, needs, outside, all_goals, witnesses)
        report.findings = kept + refined
        # With facts, what depends on a stage is read from the exact states, not from the meets.
        evidence_by_kind = {'assumed': [], 'checked': [], 'construction': []}
        for name in order:
            node = h.nodes[name]
            if isinstance(node, Switch) or (isinstance(node, Gate) and node.layer is None):
                continue
            if isinstance(node, Gate):
                relevant = bool(node.provides) or (node.establishes is not None and (open_at[name] >> goal_rank[node.establishes]) & 1)
            else:
                relevant = open_at[name] != 0
            if relevant:
                for item in sorted(h.layers[node.layer].requires & usable(h, name, node.layer)):
                    if item in h.obligations:
                        evidence_by_kind[h.obligations[item].kind].append((name, item))
        report.residual = tuple(evidence_by_kind['assumed'])
        report.checked = tuple(evidence_by_kind['checked'])
        report.construction = tuple(evidence_by_kind['construction'])
    return report


def _refine(h, order, ranked, goal_rank, obligations, fact_rank, supplied, needs, outside, all_goals, witnesses) -> tuple[list[Finding], int, dict[str, int]]:
    """Exact check: explore every reachable (goals, facts) pair at each node, with one way to reach it.

    Also returns, per node, the goals open on some path to it.
    """
    states: dict[str, dict[tuple[int, int], tuple]] = {name: {} for name in order}
    states[order[0]][(0, 0)] = (None, None)
    findings: dict[tuple, Finding] = {}
    def trail(name: str, state: tuple[int, int]) -> tuple[str, ...]:
        path = [name]
        before = states[name][state]
        while before[0] is not None:
            path.append(before[0])
            before = states[before[0]][before[1]]
        return tuple(reversed(path))
    count = 0
    open_at = dict.fromkeys(order, 0)
    for name in order:
        node = h.nodes[name]
        for state in list(states[name]):
            count += 1
            goals, known = state
            open_at[name] |= all_goals & ~goals
            after = state
            if isinstance(node, Gate) and (node.layer is None or not needs[node.layer] & ~(supplied[name] | known)):
                after = (goals | (0 if node.establishes is None else 1 << goal_rank[node.establishes]),
                         known | (_mask(node.provides, fact_rank) if node.provides else 0))
            elif isinstance(node, Guard):
                missing = all_goals & ~goals
                if missing:
                    goal = ranked[(missing & -missing).bit_length() - 1]
                    for item in _bits(needs[node.layer] & ~(supplied[name] | known), obligations):
                        findings.setdefault(('obligation', name, item), Finding('obligation', name, item, trail(name, state) if witnesses else (), goal))
                    for g in _bits(missing & outside[node.layer], ranked):
                        findings.setdefault(('coverage', name, g), Finding('coverage', name, g, trail(name, state) if witnesses else (), g))
            for child in successors(node):
                states[child].setdefault(after, (name, state))
    return list(findings.values()), count, open_at


def necessary(h: Hierarchy) -> tuple[tuple[str, str], ...]:
    """The residual entries whose removal alone makes the hierarchy unsafe.

    Tested one at a time, so two entries that can stand in for each other are both
    reported as not necessary, although removing both would make it unsafe.
    """
    result = []
    for name, item in check(h).residual:
        node = h.nodes[name]
        thinner = dict(h.nodes)
        thinner[name] = replace(node, evidence=node.evidence - {item})
        if not check(replace(h, nodes=thinner), witnesses=False).ok:
            result.append((name, item))
    return tuple(result)


def gated(h: Hierarchy, order: tuple[str, ...], goals: frozenset[str]) -> dict[str, frozenset[str]]:
    """For each node, those of `goals` that a deterministic gate establishes on every path to it."""
    available: dict[str, frozenset[str]] = {}
    for name in order:
        node = h.nodes[name]
        out = available.setdefault(name, frozenset())
        if isinstance(node, Gate) and node.layer is None and node.establishes is not None and node.establishes in goals:
            out = out | {node.establishes}
        for child in successors(node):
            available[child] = available[child] & out if child in available else out
    return available


def ancestors(h: Hierarchy, order: tuple[str, ...]) -> dict[str, tuple[str, ...]]:
    """Immediate predecessors of each reachable node, in deterministic order."""
    result: dict[str, list[str]] = {name: [] for name in order}
    for name in order:
        for child in successors(h.nodes[name]):
            if name not in result[child]:
                result[child].append(name)
    return {k: tuple(sorted(v)) for k, v in result.items()}


def witness_model(h: Hierarchy, finding: Finding) -> dict:
    """Turn a finding into a complete model: a run that respects every contract and is unsafe.

    Gates on the path pass, earlier guards escalate, switches follow the path, and the
    final guard accepts. This is the proof of completeness, as a procedure. All obligations
    hold everywhere, except one that fails at each gate the path does not credit, and,
    for an obligation finding, the named one at the final guard, whose contract then
    promises nothing. The proposal satisfies every goal but the one reported.
    """
    if finding.code not in ('obligation', 'coverage'):
        raise ValueError('structural findings have no behavioural witness')
    everything = frozenset(h.obligations)
    passes, verdict, branch, holds = {}, {}, {}, {}
    known: frozenset[str] = frozenset()
    for here, following in zip(finding.path, finding.path[1:]):
        node = h.nodes[here]
        holds[here] = everything
        if isinstance(node, Gate):
            passes[here] = True
            if credited(h, node, known):
                known = known | node.provides
            else:
                absent = h.layers[node.layer].requires - usable(h, here, node.layer) - known
                holds[here] = everything - {min(absent)}
        elif isinstance(node, Guard):
            verdict[here] = 'esc'
        else:
            branch[here] = node.then == following
    verdict[finding.node] = 'acc'
    holds[finding.node] = everything - ({finding.detail} if finding.code == 'obligation' else frozenset())
    return {'passes': passes, 'verdict': verdict, 'branch': branch, 'holds': holds, 'safe': h.goals - {finding.goal},
            'violated': finding.goal, 'failing_obligation': finding.detail if finding.code == 'obligation' else None}
