"""Behaviours the random differential oracle cannot reach, found by reading E5 survivors.

Its generator produces only well-formed acyclic graphs of goal-establishing gates with
no views on obligations, and it never raises. These tests pin the checker's structural
findings, the residual lists and the engine's fail-closed paths.
"""
import pytest
from tint.agents import fixture_store
from tint.hsl import Gate, Guard, Hierarchy, Layer, Obligation, SpecError, Switch, check
from tint.hsl.engine import Engine, Proposal, RouteCertificate, certify
from tint.model import Action, ActionKind, ApprovalStore, Verdict

G = frozenset({'g'})
NONE = frozenset()
OPEN = Layer('open', G, NONE, 'structured')
PROPOSAL = Proposal(Action(next(iter(ActionKind))))


def hierarchy(nodes, layers=(OPEN,), obligations=(), goals=G, entry=None):
    return Hierarchy(goals, {o.name: o for o in obligations}, {x.name: x for x in layers}, {n.id: n for n in nodes},
                     nodes[0].id if entry is None else entry)


def codes(h):
    return [(f.code, f.node, f.detail) for f in check(h).findings]


def engine(h, guards=None, rules=None, checks=None, **kw):
    return Engine(h, fixture_store(), ApprovalStore(), rules or {}, guards or {}, {}, checks, **kw)


def test_dangling_entry_and_successor():
    assert codes(hierarchy([Guard('a', 'open', NONE, None)], entry='gone')) == [('dangling', '<entry>', 'gone')]
    assert codes(hierarchy([Guard('a', 'open', NONE, 'gone')])) == [('dangling', 'a', 'gone')]


def test_undeclared_layers_of_guard_and_veto_stage():
    assert codes(hierarchy([Guard('a', 'nope', NONE, None)])) == [('undeclared', 'a', 'nope')]
    assert codes(hierarchy([Gate('a', 'r', 'g', None, 'nope')])) == [('undeclared', 'a', 'nope')]


@pytest.mark.parametrize('nodes', [
    [Guard('a', 'open', NONE, 'a')],
    [Guard('a', 'open', NONE, 'b'), Guard('b', 'open', NONE, 'a')],
    [Guard('a', 'open', NONE, 'b'), Guard('b', 'open', NONE, 'c'), Guard('c', 'open', NONE, 'b')]])
def test_cycles_are_rejected(nodes):
    assert [f.code for f in check(hierarchy(nodes)).findings] == ['cycle']


def test_shared_successor_is_not_a_cycle():
    nodes = [Switch('s', 'c', 'x', 'y'), Gate('x', 'r', 'g', 'z'), Gate('y', 'r', 'g', 'z'), Guard('z', 'open', NONE, None)]
    report = check(hierarchy(nodes))
    assert report.ok and report.order[0] == 's' and report.order[-1] == 'z'


def test_evidence_of_another_view_counts_for_nothing_and_warns():
    view = Obligation('v', 'construction', 'structured')
    raw = Layer('raw', G, frozenset({'v'}), 'raw')
    nodes = [Gate('p', 'r', None, 'a'), Guard('a', 'raw', frozenset({'v'}), None)]
    report = check(hierarchy(nodes, (raw,), (view,)))
    assert [(f.code, f.detail, f.path) for f in report.warnings] == [('view', 'v', ('p', 'a'))]
    assert [(f.code, f.detail, f.path) for f in report.findings] == [('obligation', 'v', ('p', 'a'))]
    good = hierarchy(nodes, (Layer('raw', G, frozenset({'v'}), 'structured'),), (view,))
    assert check(good).ok and not check(good).warnings


def test_view_warning_alone_does_not_reject_when_gates_settle_every_goal():
    view = Obligation('v', 'construction', 'structured')
    closed = Layer('closed', NONE, NONE, 'raw')
    report = check(hierarchy([Gate('p', 'r', 'g', 'a'), Guard('a', 'closed', frozenset({'v'}), None)], (closed,), (view,)))
    assert report.ok and [f.code for f in report.warnings] == ['view']


def test_undeclared_names_are_findings():
    finding = check(hierarchy([Gate('p', 'r', None, 'a'), Guard('a', 'open', frozenset({'x'}), None)])).findings[0]
    assert (finding.code, finding.detail, finding.path) == ('undeclared', 'x', ('p', 'a'))
    assert codes(hierarchy([Gate('a', 'r', 'not_a_goal', None)])) == [('undeclared', 'a', 'not_a_goal')]
    assert codes(hierarchy([Gate('a', 'r', None, None, None, NONE, frozenset({'nope'}))])) == [('undeclared', 'a', 'nope')]
    assert codes(hierarchy([Guard('a', 'bad', NONE, None)], (Layer('bad', frozenset({'nope'}), NONE, 'raw'),))) == [('undeclared', 'bad', 'nope')]
    assert codes(hierarchy([Guard('a', 'bad', NONE, None)], (Layer('bad', NONE, frozenset({'nope'}), 'raw'),))) == [('undeclared', 'bad', 'nope')]


def test_evidence_of_a_veto_stage_is_filtered_by_view():
    view = Obligation('v', 'construction', 'structured')
    raw = Layer('raw', NONE, frozenset({'v'}), 'raw')
    nodes = [Gate('a', 'r', 'g', 'b', 'raw', frozenset({'v'})), Guard('b', 'closed', NONE, None)]
    report = check(hierarchy(nodes, (raw, Layer('closed', NONE, NONE, 'raw')), (view,)))
    assert [f.code for f in report.warnings] == ['view'] and [(f.code, f.detail) for f in report.findings] == [('coverage', 'g')]


def test_gate_without_a_goal_credits_nothing():
    closed = Layer('closed', NONE, NONE, 'structured')
    nodes = [Gate('a', 'r', None, 'b'), Guard('b', 'closed', NONE, None)]
    assert codes(hierarchy(nodes, (closed,))) == [('coverage', 'b', 'g')]


def test_residual_lists_only_obligations_a_decision_depends_on():
    assumed, checked, built = Obligation('o', 'assumed'), Obligation('c', 'checked'), Obligation('b', 'construction')
    veto = Layer('veto', NONE, frozenset({'o', 'c', 'b'}), 'structured')
    needs = Layer('needs', G, frozenset({'o'}), 'structured')
    all_three = frozenset({'o', 'c', 'b'})
    # The veto stage's goal is open, so its obligations count; extra evidence does not.
    report = check(hierarchy([Gate('v', 'r', 'g', 'n', 'veto', all_three), Guard('n', 'needs', frozenset({'o', 'c'}), None)],
                             (veto, needs), (assumed, checked, built)))
    assert report.ok and report.residual == (('v', 'o'),)
    assert report.checked == (('v', 'c'),) and report.construction == (('v', 'b'),)
    # Goal already established: the second stage's obligations are not relied on.
    report = check(hierarchy([Gate('d', 'r', 'g', 'v'), Gate('v', 'r', 'g', 'n', 'veto', all_three), Guard('n', 'needs', frozenset({'o'}), None)],
                             (veto, needs), (assumed, checked, built)))
    assert report.ok and report.residual == ()
    # A veto stage for something that is not a goal is not relied on either.
    report = check(hierarchy([Gate('v', 'r', None, 'n', 'veto', all_three), Guard('n', 'needs', frozenset({'o'}), None)],
                             (veto, needs), (assumed, checked, built)))
    assert report.ok and report.residual == (('n', 'o'),)
    # An open guard's obligations count.
    report = check(hierarchy([Guard('n', 'needs', frozenset({'o'}), None)], (needs,), (assumed,)))
    assert report.residual == (('n', 'o'),)
    # Evidence a layer does not require is not something the decision depends on.
    report = check(hierarchy([Guard('n', 'needs', frozenset({'o', 'x'}), None)], (needs,), (assumed, Obligation('x', 'assumed'))))
    assert report.residual == (('n', 'o'),)


def always(verdict):
    return lambda view: verdict


CHECKED = Obligation('c', 'checked')
NEEDS = Layer('needs', G, frozenset({'c'}), 'structured')
VETO = Layer('veto', NONE, frozenset({'c'}), 'structured')


@pytest.mark.parametrize('predicate', [lambda *a: False, lambda *a: 1 / 0, lambda *a: 1])
def test_failed_checked_obligation_denies_at_guard_and_veto_stage(predicate):
    h = hierarchy([Guard('n', 'needs', frozenset({'c'}), None)], (NEEDS,), (CHECKED,))
    outcome = engine(h, {'needs': always(Verdict.ALLOW)}, checks={'c': predicate}).evaluate(PROPOSAL)
    assert not outcome.accepted and outcome.reason == 'obligation:c'
    h = hierarchy([Gate('v', 'r', 'g', 'n', 'veto', frozenset({'c'})), Guard('n', 'open', NONE, None)], (VETO, OPEN), (CHECKED,))
    outcome = engine(h, {'open': always(Verdict.ALLOW)}, {'r': lambda *a: True}, {'c': predicate}).evaluate(PROPOSAL)
    assert not outcome.accepted and outcome.reason == 'obligation:c'


def test_passing_checked_obligation_lets_the_decision_continue():
    h = hierarchy([Guard('n', 'needs', frozenset({'c'}), None)], (NEEDS,), (CHECKED,))
    assert engine(h, {'needs': always(Verdict.ALLOW)}, checks={'c': lambda *a: True}).evaluate(PROPOSAL).accepted


def test_assumed_obligations_are_not_evaluated():
    assumed = Obligation('o', 'assumed')
    layer = Layer('needs', G, frozenset({'o'}), 'structured')
    h = hierarchy([Guard('n', 'needs', frozenset({'o'}), None)], (layer,), (assumed,))
    assert engine(h, {'needs': always(Verdict.ALLOW)}).evaluate(PROPOSAL).accepted


def test_raising_rule_denies():
    h = hierarchy([Gate('a', 'r', 'g', 'b'), Guard('b', 'open', NONE, None)])
    def rule(*a):
        raise RuntimeError
    outcome = engine(h, {'open': always(Verdict.ALLOW)}, {'r': rule}).evaluate(PROPOSAL)
    assert not outcome.accepted and outcome.reason == 'gate:r'


def test_rule_must_return_exactly_true():
    h = hierarchy([Gate('a', 'r', 'g', 'b'), Guard('b', 'open', NONE, None)])
    assert not engine(h, {'open': always(Verdict.ALLOW)}, {'r': lambda *a: 1}).evaluate(PROPOSAL).accepted


def test_uncertified_statistical_route_denies_and_a_valid_certificate_opens_it():
    h = hierarchy([Guard('n', 'open', NONE, None)])
    closed = engine(h, {'open': always(Verdict.ALLOW)}, statistical=G)
    outcome = closed.evaluate(PROPOSAL)
    assert not outcome.accepted and outcome.reason == 'route not certified' and closed.shadow(PROPOSAL).accepted
    certificates = certify(closed, [(PROPOSAL, False)] * 50, .05)
    opened = engine(h, {'open': always(Verdict.ALLOW)}, statistical=G, certificates=certificates)
    assert opened.evaluate(PROPOSAL).accepted
    stale = RouteCertificate('n', 'other', '', .1, .05, 50)
    assert not engine(h, {'open': always(Verdict.ALLOW)}, statistical=G, certificates=[stale]).evaluate(PROPOSAL).accepted


def test_score_flows_to_later_views_and_survives_a_plain_verdict():
    seen = []
    def plain(view):
        return Verdict.ESCALATE
    def last(view):
        seen.append(view['score'])
        return Verdict.ALLOW
    layers = tuple(Layer(x, G, NONE, 'structured') for x in ['s', 'p', 'j'])
    h = hierarchy([Guard('a', 's', NONE, 'b'), Guard('b', 'p', NONE, 'c'), Guard('c', 'j', NONE, None)], layers)
    engine(h, {'s': always((Verdict.ESCALATE, 0.25)), 'p': plain, 'j': last}).evaluate(PROPOSAL)
    assert seen == [0.25]


@pytest.mark.parametrize('score', [float('nan'), float('inf'), 'high', True and []])
def test_bad_score_blocks(score):
    h = hierarchy([Guard('a', 'open', NONE, None)])
    assert not engine(h, {'open': always((Verdict.ALLOW, score))}).evaluate(PROPOSAL).accepted


def test_valid_score_does_not_block():
    h = hierarchy([Guard('a', 'open', NONE, None)])
    assert engine(h, {'open': always((Verdict.ALLOW, 0.5))}).evaluate(PROPOSAL).accepted


def test_default_deny_names_the_last_stage():
    h = hierarchy([Guard('a', 'open', NONE, 'b'), Guard('b', 'open', NONE, None)])
    outcome = engine(h, {'open': always(Verdict.ESCALATE)}).evaluate(PROPOSAL)
    assert (outcome.accepted, outcome.node, outcome.reason, outcome.path) == (False, 'b', 'default deny', ('a', 'b'))
    empty = Hierarchy(G, {}, {}, {}, None)
    assert engine(empty).evaluate(PROPOSAL).node == '<entry>'


def test_rejected_specification_cannot_build_an_engine():
    with pytest.raises(SpecError):
        engine(hierarchy([Guard('a', 'nope', NONE, None)]))


OB = Obligation('o', 'assumed')
NEEDS_O = Layer('needs', G, frozenset({'o'}), 'structured')


def test_a_provided_fact_discharges_a_later_obligation():
    nodes = [Gate('p', 'r', None, 'n', None, NONE, frozenset({'o'})), Guard('n', 'needs', NONE, None)]
    report = check(hierarchy(nodes, (NEEDS_O,), (OB,)))
    assert report.ok and report.residual == ()


def test_a_guard_provides_nothing():
    nodes = [Guard('a', 'needs', frozenset({'o'}), 'b'), Guard('b', 'needs', NONE, None)]
    assert codes(hierarchy(nodes, (NEEDS_O,), (OB,))) == [('obligation', 'b', 'o')]


def test_an_uncredited_gate_provides_nothing():
    veto = Layer('veto', NONE, frozenset({'x'}), 'structured')
    nodes = [Gate('p', 'r', None, 'n', 'veto', NONE, frozenset({'o'})), Guard('n', 'needs', NONE, None)]
    report = check(hierarchy(nodes, (veto, NEEDS_O), (OB, Obligation('x', 'assumed'))))
    assert [(f.code, f.detail) for f in report.findings] == [('obligation', 'o')]


def test_fact_on_only_one_path_is_not_enough():
    nodes = [Switch('s', 'c', 'p', 'n'), Gate('p', 'r', None, 'n', None, NONE, frozenset({'o'})), Guard('n', 'needs', NONE, None)]
    finding = check(hierarchy(nodes, (NEEDS_O,), (OB,))).findings[0]
    assert (finding.code, finding.path) == ('obligation', ('s', 'n'))


def test_refinement_removes_the_false_alarm_of_componentwise_meets():
    # One arm establishes the goal, the other provides the fact. Each path is safe; the meet is not.
    closed = Layer('needs', G, frozenset({'o'}), 'structured')
    nodes = [Switch('s', 'c', 'x', 'y'), Gate('x', 'r', 'g', 'n'), Gate('y', 'r', None, 'n', None, NONE, frozenset({'o'})), Guard('n', 'needs', NONE, None)]
    report = check(hierarchy(nodes, (closed,), (OB,)))
    assert report.ok and report.exact_states > 0


def test_raising_condition_denies():
    h = hierarchy([Switch('s', 'c', 'a', None), Guard('a', 'open', NONE, None)])
    def condition(facts, proposal):
        raise RuntimeError
    outcome = Engine(h, fixture_store(), ApprovalStore(), {}, {'open': always(Verdict.ALLOW)}, {'c': condition}).evaluate(PROPOSAL)
    assert not outcome.accepted and outcome.reason == 'condition:c'


def test_veto_stage_with_structured_view_does_not_see_text():
    seen = []
    def rule(facts, proposal, ledger):
        seen.append(proposal.text)
        return True
    layer = Layer('veto', G, NONE, 'structured')
    h = hierarchy([Gate('v', 'r', 'g', 'n', 'veto'), Guard('n', 'open', NONE, None)], (layer, OPEN))
    engine(h, {'open': always(Verdict.ALLOW)}, {'r': rule}).evaluate(Proposal(PROPOSAL.action, 'attacker text'))
    assert seen == ['']


def test_cost_is_spent_only_through_a_budget_gate_and_cannot_be_negative():
    from tint.hsl.rules import CumulativeBudget
    gated_route = hierarchy([Gate('b', 'budget', 'g', 'n'), Guard('n', 'open', NONE, None)])
    e = engine(gated_route, {'open': always(Verdict.ALLOW)}, {'budget': CumulativeBudget(10)})
    assert e.evaluate(Proposal(PROPOSAL.action, cost=4)).accepted and e.ledger.spent == 4
    assert not e.evaluate(Proposal(PROPOSAL.action, cost=7)).accepted and e.ledger.spent == 4
    assert not e.evaluate(Proposal(PROPOSAL.action, cost=-1)).accepted
    free = engine(hierarchy([Guard('n', 'open', NONE, None)]), {'open': always(Verdict.ALLOW)})
    assert free.evaluate(Proposal(PROPOSAL.action, cost=100)).accepted and free.ledger.spent == 0


def constant(value):
    def predicate(*args):
        return value
    return predicate


def test_fingerprint_covers_predicates_labels_closures_and_partials():
    import functools
    from tint.hsl.engine import component_digest
    h = hierarchy([Guard('n', 'needs', frozenset({'c'}), None)], (NEEDS,), (CHECKED,))
    guards = {'needs': always(Verdict.ALLOW)}
    first = engine(h, guards, checks={'c': constant(True)}).fingerprints['n']
    assert first != engine(h, guards, checks={'c': constant(False)}).fingerprints['n']
    plain = hierarchy([Guard('n', 'open', NONE, None)])
    opened = {'open': always(Verdict.ALLOW)}
    assert engine(plain, opened, statistical=G).fingerprints['n'] != engine(plain, opened, label='v2', statistical=G).fingerprints['n']
    assert engine(plain, opened).fingerprints['n'] != engine(plain, opened, statistical=G).fingerprints['n']
    assert component_digest(functools.partial(print, 1)) != component_digest(functools.partial(len, 2))
    assert engine(plain, opened).fingerprints['n'] != engine(plain, {'open': always(Verdict.BLOCK)}).fingerprints['n']


def test_component_without_identity_is_refused():
    from tint.hsl.engine import component_digest
    opaque = type('Opaque', (), {'__call__': lambda self, *a: True})
    with pytest.raises(SpecError):
        component_digest(opaque())


def test_confidence_shares_are_enforced():
    h = hierarchy([Guard('a', 'open', NONE, 'b'), Guard('b', 'open', NONE, None)])
    base = engine(h, {'open': always(Verdict.ESCALATE)}, statistical=G)
    certificates = certify(base, [(PROPOSAL, False)] * 50, .05, share=.04)
    assert len(certificates) == 2
    with pytest.raises(SpecError):
        engine(h, {'open': always(Verdict.ESCALATE)}, statistical=G, certificates=certificates)


def test_gated_uses_every_path():
    nodes = [Switch('s', 'c', 'x', 'n'), Gate('x', 'r', 'g', 'n'), Guard('n', 'open', NONE, None)]
    h = hierarchy(nodes)
    e = Engine(h, fixture_store(), ApprovalStore(), {'r': lambda *a: True}, {'open': always(Verdict.ALLOW)}, {'c': lambda *a: True}, statistical=G)
    assert e.needs_certificate['n']


def test_branch_swap_changes_the_fingerprint():
    conditions = {'c': lambda *a: True}
    a = hierarchy([Switch('s', 'c', 'x', None), Guard('x', 'open', NONE, None)])
    b = hierarchy([Switch('s', 'c', None, 'x'), Guard('x', 'open', NONE, None)])
    make = lambda h: Engine(h, fixture_store(), ApprovalStore(), {}, {'open': always(Verdict.ALLOW)}, conditions)
    assert make(a).fingerprints['x'] != make(b).fingerprints['x']


def test_witness_failing_obligation_and_full_model():
    from tint.hsl import witness_model
    veto = Layer('veto', NONE, frozenset({'x'}), 'structured')
    nodes = [Gate('p', 'r', 'g', 'n', 'veto'), Guard('n', 'closed', NONE, None)]
    h = hierarchy(nodes, (veto, Layer('closed', NONE, NONE, 'raw')), (Obligation('x', 'assumed'),))
    model = witness_model(h, check(h).findings[0])
    assert 'x' not in model['holds']['p'] and model['safe'] == NONE and model['failing_obligation'] is None
    h = hierarchy([Guard('n', 'needs', NONE, None)], (NEEDS_O,), (OB,))
    model = witness_model(h, check(h).findings[0])
    assert model['failing_obligation'] == 'o' and 'o' not in model['holds']['n']


def test_necessary_separates_needed_assumptions_from_redundant_ones():
    from tint.hsl import necessary
    assumed = Obligation('o', 'assumed')
    veto = Layer('veto', NONE, frozenset({'o'}), 'structured')
    closed = Layer('closed', NONE, NONE, 'structured')
    needed = hierarchy([Guard('n', 'needs', frozenset({'o'}), None)], (NEEDS_O,), (assumed,))
    assert necessary(needed) == (('n', 'o'),)
    redundant = hierarchy([Gate('v', 'r', 'g', 'd', 'veto', frozenset({'o'})), Gate('d', 'r', 'g', 'n'), Guard('n', 'closed', NONE, None)], (veto, closed), (assumed,))
    assert check(redundant).residual == (('v', 'o'),) and necessary(redundant) == ()


def test_witness_path_follows_the_arm_that_lacks_the_goal():
    closed = Layer('closed', NONE, NONE, 'structured')
    nodes = [Switch('s', 'c', 'x', 'y'), Gate('x', 'r', 'g', 'n'), Gate('y', 'r', None, 'n'), Guard('n', 'closed', NONE, None)]
    assert check(hierarchy(nodes, (closed,))).findings[0].path == ('s', 'y', 'n')
    nodes = [Switch('s', 'c', 'x', 'y'), Gate('x', 'r', None, 'n'), Gate('y', 'r', 'g', 'n'), Guard('n', 'closed', NONE, None)]
    assert check(hierarchy(nodes, (closed,))).findings[0].path == ('s', 'x', 'n')


def test_certificate_counts_losses_exactly():
    from tint.calibration import binomial_upper
    h = hierarchy([Guard('n', 'open', NONE, None)])
    e = engine(h, {'open': always(Verdict.ALLOW)}, statistical=G)
    certificate = certify(e, [(PROPOSAL, False)] * 90 + [(PROPOSAL, True)] * 10, .05)[0]
    assert certificate.samples == 100 and certificate.delta == .05 and certificate.upper == binomial_upper(10, 100, .05)
    assert certify(e, [(PROPOSAL, False)] * 100, .05)[0].upper == binomial_upper(0, 100, .05)


def test_certify_with_no_statistical_route_returns_nothing():
    h = hierarchy([Guard('n', 'open', NONE, None)])
    assert certify(engine(h, {'open': always(Verdict.ALLOW)}), [(PROPOSAL, False)], .05) == []


def test_certificate_validity_boundaries():
    make = lambda upper, delta=.05, samples=10: RouteCertificate('n', 'f', '', upper, delta, samples).valid()
    assert make(0.0) and make(1.0) and not make(1.1) and not make(-.1) and not make(float('nan'))
    assert not make(.1, 0.0) and not make(.1, 1.0) and not make(.1, .05, 0)


def test_invalid_costs_deny_on_any_route():
    free = engine(hierarchy([Guard('n', 'open', NONE, None)]), {'open': always(Verdict.ALLOW)})
    for cost in (-1, float('nan'), float('inf')):
        assert not free.evaluate(Proposal(PROPOSAL.action, cost=cost)).accepted


def test_digest_sees_state_in_each_kind_of_container():
    from tint.hsl.engine import component_digest
    def closing(value):
        def stage(*args):
            return value
        return stage
    assert component_digest(closing([1, 2])) != component_digest(closing([2, 1]))
    assert component_digest(closing({1, 2})) == component_digest(closing({2, 1}))
    assert component_digest(closing({'a': 1})) != component_digest(closing({'a': 2}))
    assert component_digest(closing((1,))) != component_digest(closing((2,)))
    assert component_digest(closing(1)) != component_digest(closing(2))

    class Plain:
        def __init__(self, value):
            self.value = value

    class Shown:
        def __init__(self, value):
            self.value = value

        def __repr__(self):
            return f'Shown({self.value})'
    assert component_digest(closing(Plain(1))) != component_digest(closing(Plain(2)))
    assert component_digest(closing(Shown(1))) != component_digest(closing(Shown(2)))
    assert component_digest(closing(Shown(1))) == component_digest(closing(Shown(1)))
    cycle = []
    cycle.append(cycle)
    assert component_digest(closing(cycle))


def test_refinement_credits_no_fact_from_a_gate_that_provides_none():
    closed = Layer('needs', G, frozenset({'o'}), 'structured')
    nodes = [Switch('s', 'c', 'x', 'y'), Gate('x', 'r', None, 'n'), Gate('y', 'r', None, 'n', None, NONE, frozenset({'o'})), Guard('n', 'needs', NONE, None)]
    report = check(hierarchy(nodes, (closed,), (OB,)))
    assert [(f.code, f.detail, f.path) for f in report.findings] == [('obligation', 'o', ('s', 'x', 'n'))]


def test_one_sample_certificate_is_valid_and_kind_is_fingerprinted():
    assert RouteCertificate('n', 'f', '', .5, .05, 1).valid()
    layer = Layer('needs', G, frozenset({'o'}), 'structured')
    guards = {'needs': always(Verdict.ALLOW)}
    nodes = [Guard('n', 'needs', frozenset({'o'}), None)]
    assumed = engine(hierarchy(nodes, (layer,), (OB,)), guards).fingerprints['n']
    built = engine(hierarchy(nodes, (layer,), (Obligation('o', 'construction'),)), guards).fingerprints['n']
    assert assumed != built


def test_veto_stage_whose_value_is_a_fact_is_on_the_residual_list():
    from tint.hsl import necessary
    veto = Layer('veto', NONE, frozenset({'x'}), 'structured')
    nodes = [Gate('v', 'r', None, 'n', 'veto', frozenset({'x'}), frozenset({'o'})), Guard('n', 'needs', NONE, None)]
    h = hierarchy(nodes, (veto, NEEDS_O), (OB, Obligation('x', 'assumed')))
    report = check(h)
    assert report.ok and report.residual == (('v', 'x'),) and necessary(h) == (('v', 'x'),)


def test_deterministic_gate_claims_are_listed():
    nodes = [Gate('p', 'r', 'g', 'n', None, NONE, frozenset({'o'})), Guard('n', 'needs', NONE, None)]
    report = check(hierarchy(nodes, (NEEDS_O,), (OB,)))
    assert report.claims == (('p', 'g'), ('p', 'o'))


def test_a_checked_obligation_cannot_be_provided():
    nodes = [Gate('p', 'r', None, 'n', None, NONE, frozenset({'c'})), Guard('n', 'needs', NONE, None)]
    assert ('undeclared', 'p', 'c') in codes(hierarchy(nodes, (NEEDS,), (CHECKED,)))


def test_undeclared_evidence_at_a_deterministic_gate_is_a_finding():
    assert ('undeclared', 'p', 'x') in codes(hierarchy([Gate('p', 'r', 'g', None, None, frozenset({'x'}))]))


def test_fingerprint_covers_the_view_of_a_veto_stage():
    veto = lambda view: Layer('veto', NONE, NONE, view)
    nodes = [Gate('v', 'r', 'g', 'n', 'veto'), Guard('n', 'open', NONE, None)]
    make = lambda view: engine(hierarchy(nodes, (veto(view), OPEN)), {'open': always(Verdict.ALLOW)}, {'r': constant(True)}).fingerprints['n']
    assert make('raw') != make('structured')


def test_digest_sees_arrays_slots_and_state_behind_a_repr():
    import numpy as np
    from tint.hsl.engine import component_digest
    def closing(value):
        def stage(*args):
            return value
        return stage
    large = np.zeros(5000)
    other = large.copy()
    other[2500] = 1
    assert component_digest(closing(large)) != component_digest(closing(other))

    class Slotted:
        __slots__ = ('value',)

        def __init__(self, value):
            self.value = value

    class Hidden:
        def __init__(self, value):
            self.value = value

        def __repr__(self):
            return 'Hidden()'
    assert component_digest(closing(Slotted(1))) != component_digest(closing(Slotted(2)))
    assert component_digest(closing(Hidden(1))) != component_digest(closing(Hidden(2)))


def test_duplicate_certificates_and_oversized_shares_are_refused():
    h = hierarchy([Guard('a', 'open', NONE, 'b'), Guard('b', 'open', NONE, None)])
    base = engine(h, {'open': always(Verdict.ESCALATE)}, statistical=G)
    one = certify(base, [(PROPOSAL, False)] * 50, .05)[0]
    with pytest.raises(SpecError):
        engine(h, {'open': always(Verdict.ESCALATE)}, statistical=G, certificates=[one, one])
    reserved = engine(h, {'open': always(Verdict.ESCALATE)}, statistical=G, shares={'a': .04, 'b': .01})
    assert reserved.shares == {'a': .04, 'b': .01}
    with pytest.raises(SpecError):
        engine(h, {'open': always(Verdict.ESCALATE)}, statistical=G, shares={'a': .04, 'b': .04})


def test_appended_route_does_not_inherit_old_shares():
    two = hierarchy([Guard('a', 'open', NONE, 'b'), Guard('b', 'open', NONE, None)])
    old = certify(engine(two, {'open': always(Verdict.ESCALATE)}, statistical=G), [(PROPOSAL, False)] * 50, .05)
    three = hierarchy([Guard('a', 'open', NONE, 'b'), Guard('b', 'open', NONE, 'c'), Guard('c', 'open', NONE, None)])
    with pytest.raises(SpecError):
        engine(three, {'open': always(Verdict.ESCALATE)}, statistical=G, certificates=old)


def test_residual_with_facts_comes_from_exact_states():
    closed = Layer('needs', G, frozenset({'o'}), 'structured')
    nodes = [Switch('s', 'c', 'x', 'y'), Gate('x', 'r', 'g', 'n'), Gate('y', 'r', None, 'n', None, NONE, frozenset({'o'})), Guard('n', 'needs', NONE, None)]
    report = check(hierarchy(nodes, (closed,), (OB,)))
    assert report.ok and report.residual == ()


def test_dense_masks_stay_fast():
    import time
    names = frozenset(f'o{i}' for i in range(200000))
    layer = Layer('L', G, names, 'structured')
    h = hierarchy([Guard('n', 'L', NONE, None)], (layer,), tuple(Obligation(x, 'assumed') for x in names))
    start = time.perf_counter()
    assert len(check(h, witnesses=False).findings) == 200000
    assert time.perf_counter() - start < 10


def test_first_pass_meets_facts_in_decision_mode():
    nodes = [Switch('s', 'c', 'p', 'n'), Gate('p', 'r', None, 'n', None, NONE, frozenset({'o'})), Guard('n', 'needs', NONE, None)]
    assert not check(hierarchy(nodes, (NEEDS_O,), (OB,)), witnesses=False).ok


def test_decision_mode_refines_a_false_alarm_and_finds_real_rejections():
    both = [Switch('s', 'c', 'x', 'y'), Gate('x', 'r', 'g', 'n'), Gate('y', 'r', None, 'n', None, NONE, frozenset({'o'})), Guard('n', 'needs', NONE, None)]
    assert check(hierarchy(both, (NEEDS_O,), (OB,)), witnesses=False).ok
    goalless = [Switch('s', 'c', 'x', 'y'), Gate('x', 'r', None, 'n'), Gate('y', 'r', None, 'n', None, NONE, frozenset({'o'})), Guard('n', 'needs', NONE, None)]
    assert not check(hierarchy(goalless, (NEEDS_O,), (OB,)), witnesses=False).ok


def test_residual_with_facts_on_open_and_closed_goals():
    assumed = Obligation('x', 'assumed')
    needs = Layer('needs', G, frozenset({'x'}), 'structured')
    veto = Layer('veto', NONE, frozenset({'x'}), 'structured')
    provider = Gate('p', 'r', None, 'n', None, NONE, frozenset({'o'}))
    open_goal = check(hierarchy([provider, Guard('n', 'needs', frozenset({'x'}), None)], (needs,), (OB, assumed)))
    assert open_goal.residual == (('n', 'x'),)
    settled = check(hierarchy([Gate('p', 'r', 'g', 'n', None, NONE, frozenset({'o'})), Guard('n', 'needs', frozenset({'x'}), None)], (needs,), (OB, assumed)))
    assert settled.ok and settled.residual == ()
    two_goals = frozenset({'g', 'h'})
    wide = Layer('wide', two_goals, NONE, 'structured')
    gates = [Gate('p', 'r', None, 'v', None, NONE, frozenset({'o'})), Gate('v', 'r', 'g', 'n', 'veto', frozenset({'x'})), Guard('n', 'wide', NONE, None)]
    report = check(hierarchy(gates, (veto, wide), (OB, assumed), goals=two_goals))
    assert report.ok and report.residual == (('v', 'x'),)
    later = [Gate('p', 'r', 'h', 'd', None, NONE, frozenset({'o'})), Gate('d', 'r', 'g', 'v'), Gate('v', 'r', 'g', 'n', 'veto', frozenset({'x'})), Guard('n', 'wide', NONE, None)]
    assert check(hierarchy(later, (veto, wide), (OB, assumed), goals=two_goals)).residual == ()


def test_witness_threads_facts_through_credited_gates():
    from tint.hsl import witness_model
    closed = Layer('closed', NONE, NONE, 'structured')
    veto = Layer('veto', NONE, frozenset({'o'}), 'structured')
    nodes = [Gate('p', 'r', None, 'v', None, NONE, frozenset({'o'})), Gate('v', 'r', 'g', 'n', 'veto'), Guard('n', 'closed', NONE, None)]
    h = hierarchy(nodes, (veto, closed), (OB,), goals=frozenset({'g', 'h'}))
    model = witness_model(h, check(h).findings[0])
    assert model['violated'] == 'h' and 'o' in model['holds']['v']


def test_route_without_an_allocated_share_cannot_open():
    h = hierarchy([Guard('a', 'open', NONE, 'b'), Guard('b', 'open', NONE, None)])
    base = engine(h, {'open': always(Verdict.ESCALATE)}, statistical=G)
    certificates = certify(base, [(PROPOSAL, False)] * 50, .05, routes=['b'], share=.01)
    with pytest.raises(SpecError):
        engine(h, {'open': always(Verdict.ESCALATE)}, statistical=G, shares={'a': .01}, certificates=certificates)
