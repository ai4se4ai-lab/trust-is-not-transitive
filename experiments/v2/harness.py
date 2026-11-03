"""Generators and differential oracles shared by the v2 experiments."""
from __future__ import annotations
from dataclasses import replace
import itertools
from pathlib import Path
import random
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'formal/calculus')]
import reference
from tint.agents import fixture_store
import tint.hsl
from tint.hsl import Gate, Guard, Hierarchy, Layer, Obligation, Switch, check, witness_model
import tint.hsl.engine as engine_module
from tint.hsl.engine import Engine, Proposal
from tint.model import Action, ActionKind, ApprovalStore, Verdict

TYPES = (Gate, Guard, Switch)


def term_of(h: Hierarchy):
    return reference.unfold(h.nodes, h.entry, TYPES, lambda name, node: tint.hsl.usable(h, name, node.layer))


def tables(h: Hierarchy):
    return {k: v.requires for k, v in h.layers.items()}, {k: v.scope for k, v in h.layers.items()}


def random_hierarchy(rng: random.Random, n: int | None = None, goals: int | None = None, obligations: int | None = None) -> Hierarchy:
    """A random spec. Each layer belongs to several stages sometimes; facts and views are in play."""
    n = rng.randint(2, 16) if n is None else n
    goal_names = [f'g{i}' for i in range(rng.randint(1, 3) if goals is None else goals)]
    names = [f'o{i}' for i in range(rng.randint(1, 3) if obligations is None else obligations)]
    declared = {x: Obligation(x, rng.choice(tint.hsl.KINDS), rng.choice(tint.hsl.VIEWS) if rng.random() < .15 else None) for x in names}
    plain = [x for x in names if declared[x].view is None and declared[x].kind != 'checked']
    subset = lambda items, p: frozenset(x for x in items if rng.random() < p)
    layers, nodes = {}, {}
    ids = [f'n{i}' for i in range(n)]
    for i, name in enumerate(ids):
        later = ids[i + 1:] + [None]
        step = lambda: later[0] if rng.random() < .75 else rng.choice(later)
        kind = rng.random()
        provides = subset(plain, .35) if rng.random() < .4 else frozenset()
        goal = rng.choice(goal_names) if rng.random() < .9 else None
        if kind < .25:
            nodes[name] = Gate(name, 'r_' + name, goal, step(), None, frozenset(), provides)
        elif kind < .4:
            layer = 'V_' + name
            layers[layer] = Layer(layer, frozenset(), subset(names, .4), rng.choice(tint.hsl.VIEWS))
            evidence = frozenset(layers[layer].requires) if rng.random() < .7 else subset(names, .4)
            nodes[name] = Gate(name, 'r_' + name, goal, step(), layer, evidence, provides)
        elif kind < .8:
            layer = 'L_' + name
            layers[layer] = Layer(layer, subset(goal_names, .7), subset(names, .4), rng.choice(tint.hsl.VIEWS))
            evidence = frozenset(layers[layer].requires) if rng.random() < .8 else subset(names, .4)
            nodes[name] = Guard(name, layer, evidence, step())
        else:
            nodes[name] = Switch(name, 'c_' + name, step(), step())
    return Hierarchy(frozenset(goal_names), declared, layers, nodes, ids[0])


class Scripted:
    """A callable stage whose behaviour is read from the current model table."""
    version = 'scripted'

    def __init__(self, table: dict, key: str, kind: str) -> None:
        self.table, self.key, self.kind = table, key, kind

    def __call__(self, *args):
        value = self.table[self.key]
        return {'acc': Verdict.ALLOW, 'esc': Verdict.ESCALATE, 'blk': Verdict.BLOCK}[value] if self.kind == 'guard' else value


class ScriptedCheck:
    """A checked obligation's runtime predicate, read from the model table; it may fail."""
    version = 'scripted'

    def __init__(self, table: dict, item: str) -> None:
        self.table, self.item = table, item

    def __call__(self, node, facts, proposal):
        return self.table.get(('check', node, self.item), True)


def wiring(h: Hierarchy, table: dict) -> tuple[dict, dict, dict, dict]:
    rules, guards, conditions, checks = {}, {}, {}, {}
    for name, node in h.nodes.items():
        for item in getattr(node, 'evidence', ()):
            checks[item] = ScriptedCheck(table, item)
        if isinstance(node, Gate):
            rules[node.rule] = Scripted(table, name, 'gate')
        elif isinstance(node, Guard):
            guards[node.layer] = Scripted(table, name, 'guard')
        else:
            conditions[node.condition] = Scripted(table, name, 'switch')
    return rules, guards, conditions, checks


def wired_engine(h: Hierarchy, table: dict, unchecked: bool = False) -> Engine:
    rules, guards, conditions, checks = wiring(h, table)
    if not unchecked:
        return Engine(h, fixture_store(), ApprovalStore(), rules, guards, conditions, checks)
    original = engine_module.check
    def permissive(spec):
        report = original(spec)
        report.findings.clear()
        return report
    engine_module.check = permissive
    try:
        return Engine(h, fixture_store(), ApprovalStore(), rules, guards, conditions, checks)
    finally:
        engine_module.check = original


PROPOSAL = Proposal(Action(ActionKind.TEST))


def random_model(rng: random.Random, h: Hierarchy) -> dict:
    table = {}
    for name, node in h.nodes.items():
        table[name] = rng.choice(['acc', 'esc', 'esc', 'blk']) if isinstance(node, Guard) else rng.random() < .8
        for item in getattr(node, 'evidence', ()):
            if item in h.obligations and h.obligations[item].kind == 'checked':
                table['check', name, item] = rng.random() < .9
    return table


def split_model(h: Hierarchy, table: dict) -> tuple[dict, dict, dict]:
    """The model the engine should realize: a failed checked obligation denies at its stage."""
    passes, verdict, branch = {}, {}, {}
    for name, node in h.nodes.items():
        failed = any(table.get(('check', name, x), True) is False for x in sorted(getattr(node, 'evidence', ())))
        if isinstance(node, Gate):
            passes[name] = table[name] and not failed
        elif isinstance(node, Guard):
            verdict[name] = 'blk' if failed else table[name]
        else:
            branch[name] = table[name]
    return passes, verdict, branch


def small_alphabet():
    obligations = {x: Obligation(x, 'assumed') for x in 'op'}
    layers = {}
    for scope in [frozenset(x) for x in ([], ['a'], ['a', 'b'])]:
        for requires in [frozenset(x) for x in ([], ['o'], ['o', 'p'])]:
            name = 'S' + ''.join(sorted(scope)) + 'R' + ''.join(sorted(requires))
            layers[name] = Layer(name, scope, requires, 'raw')
    return obligations, layers


EVIDENCE = (frozenset(), frozenset({'o'}), frozenset({'o', 'p'}))


def small_options(size: int, i: int) -> list:
    _, layers = small_alphabet()
    ids = [f'n{j}' for j in range(size)]
    name, later = ids[i], ids[i + 1:] + [None]
    result = [Gate(name, 'r', goal, s, None, frozenset(), d) for goal in ('a', 'b', None) for d in (frozenset(), frozenset({'o'})) for s in later]
    result += [Gate(name, 'r', 'a', s, 'SRo', om) for s in later for om in EVIDENCE[:2]]
    result += [Gate(name, 'r', None, s, 'SRo', om, frozenset({'p'})) for s in later for om in EVIDENCE[:2]]
    result += [Guard(name, l, om, s) for l in layers for om in EVIDENCE for s in later]
    result += [Switch(name, 'c', a, b) for a in later for b in later]
    return result


def enumerate_small(size: int, first: int | None = None):
    """All hierarchies of `size` nodes, all reachable, on the alphabet of the paper; goals {a} and {a,b}.

    `first` restricts to one choice for node 0, to partition the work. Conditions are
    free per node, as the calculus has them.
    """
    obligations, layers = small_alphabet()
    ids = [f'n{i}' for i in range(size)]
    choices = [small_options(size, i) for i in range(size)]
    if first is not None:
        choices[0] = [choices[0][first]]
    for combo in itertools.product(*choices):
        nodes = {n.id: n for n in combo}
        probe = Hierarchy(frozenset({'a', 'b'}), obligations, layers, nodes, ids[0])
        if len(tint.hsl._order(probe)[0]) != size:
            continue
        for goals in (frozenset({'a'}), frozenset({'a', 'b'})):
            yield Hierarchy(goals, obligations, {k: Layer(k, v.scope & goals, v.requires, v.view) for k, v in layers.items()},
                            {k: replace(v, establishes=None) if isinstance(v, Gate) and v.establishes not in (None, *goals) else v for k, v in nodes.items()}, ids[0])


def check_agreement(h: Hierarchy, semantic: bool = True) -> tuple[bool, bool, bool | None]:
    """(implementation, reference equations, absence of a violating model by search over `wf`)."""
    req, scope = tables(h)
    term = term_of(h)
    return (check(h, witnesses=False).ok, reference.check(term, frozenset(), h.goals, req, scope),
            (not reference.violating_model_exists(term, h.goals, req, scope, frozenset(h.obligations))) if semantic else None)


def sampled_violation(rng: random.Random, h: Hierarchy, term, req, scope, samples: int) -> tuple[int, int, int]:
    """Sampled contract-respecting runs, biased to reach acceptance: (runs, accepted ones, unsafe accepted ones)."""
    everything = sorted(h.obligations)
    goals = sorted(h.goals)
    respected = reached = unsafe = 0
    for _ in range(samples):
        table = random_model(rng, h)
        for name, node in h.nodes.items():
            if isinstance(node, Gate):
                table[name] = rng.random() < .97
            elif isinstance(node, Guard):
                table[name] = rng.choice(['acc', 'esc', 'esc', 'esc'])
        passes, verdict, branch = split_model(h, table)
        holds = {n: frozenset(x for x in everything if rng.random() < .85) for n in h.nodes}
        safe = frozenset(g for g in goals if rng.random() < .6)
        if reference.wf(term, passes, verdict, branch, holds, safe, req, scope):
            respected += 1
            accepted = reference.evaluate(term, passes, verdict, branch)[0] == 'accepted'
            reached += accepted
            unsafe += accepted and not h.goals <= safe
    return respected, reached, unsafe


def differential(seed: int, specs: int, models: int) -> dict:
    """The conformance oracle: checker vs. equations, engine vs. eval, witnesses vs. wf."""
    rng = random.Random(seed)
    result = dict(specs=0, accepted=0, rejected=0, check_disagreements=0, semantic_compared=0, semantic_disagreements=0, reachable_nodes=0,
                  decisions=0, engine_disagreements=0, route_disagreements=0, contract_runs=0, contract_accepting_runs=0, unsafe_accepted=0, contract_runs_rejected=0, unsafe_rejected=0, rejected_with_sampled_violation=0, residual_disagreements=0, witnesses=0, witness_failures=0, refined=0)
    for _ in range(specs):
        h = random_hierarchy(rng)
        report = check(h)
        reachable = len(report.order) or len(tint.hsl._order(h)[0])
        small = reachable <= 4
        implementation, equations, semantic = check_agreement(h, small)
        result['specs'] += 1
        result['reachable_nodes'] += reachable
        result['refined'] += report.exact_states > 0
        result['accepted' if implementation else 'rejected'] += 1
        result['check_disagreements'] += implementation != equations
        if small:
            result['semantic_compared'] += 1
            result['semantic_disagreements'] += implementation != semantic
        term = term_of(h)
        req, scope = tables(h)
        runs, reached, unsafe = sampled_violation(rng, h, term, req, scope, 40)
        result['contract_runs' if implementation else 'contract_runs_rejected'] += runs
        result['contract_accepting_runs'] += reached if implementation else 0
        result['unsafe_accepted' if implementation else 'unsafe_rejected'] += unsafe
        result['rejected_with_sampled_violation'] += not implementation and unsafe > 0
        if not any(f.code in ('undeclared', 'cycle', 'dangling') for f in report.findings):
            kinds = {k: v.kind for k, v in h.obligations.items()}
            result['residual_disagreements'] += frozenset(report.residual) != reference.residual(term, h.goals, req, kinds)
        table: dict = {}
        engine = wired_engine(h, table, unchecked=not implementation)
        for _ in range(models):
            table.clear()
            table.update(random_model(rng, h))
            expected = reference.evaluate(term, *split_model(h, table))
            outcome = engine.shadow(PROPOSAL)
            result['decisions'] += 1
            result['engine_disagreements'] += outcome.accepted != (expected[0] == 'accepted')
            result['route_disagreements'] += outcome.accepted and outcome.route != expected[1]
        for finding in report.findings:
            if finding.code not in ('obligation', 'coverage'):
                continue
            result['witnesses'] += 1
            model = witness_model(h, finding)
            table.clear()
            table.update({k: 'blk' if isinstance(v, Guard) else False for k, v in h.nodes.items()})
            table.update(model['passes']); table.update(model['verdict']); table.update(model['branch'])
            outcome = engine.shadow(PROPOSAL)
            passes, verdict, branch = split_model(h, table)
            good = (outcome.accepted and outcome.route == finding.node and finding.goal in h.goals and finding.goal not in model['safe']
                    and reference.evaluate(term, passes, verdict, branch) == ('accepted', finding.node)
                    and reference.wf(term, passes, verdict, branch, model['holds'], model['safe'], req, scope))
            result['witness_failures'] += not good
    return result
