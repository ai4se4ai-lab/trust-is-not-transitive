"""Fail-closed interpreter for checked hierarchies and route-level certificates.

The engine has one decision path, used for both deployment and calibration, so
the certified function is the deployed function. A statistical route opens only
while a certificate for its exact prefix fingerprint is present; a stale route
closes alone, and the others keep their guarantees.
"""
from __future__ import annotations
from dataclasses import dataclass
import dataclasses
import functools
import hashlib
import inspect
import json
import math
import numbers
from typing import Any, Callable, Iterable, Mapping
from . import Gate, Guard, Hierarchy, Layer, SpecError, Switch, ancestors, check, gated
from ..calibration import binomial_upper
from ..model import Action, ActionView, ApprovalStore, ProvenanceStore, Verdict, action_view


@dataclass(frozen=True)
class Proposal:
    action: Action
    text: str = ''
    cost: float = 0.0


@dataclass(frozen=True)
class Outcome:
    accepted: bool
    route: str | None      # the accepting guard node, if any
    node: str              # node at which the decision ended
    reason: str
    path: tuple[str, ...]  # stages visited, in order


def _instance_state(value: Any) -> dict[str, Any]:
    """An object's attributes, from its `__dict__` and from the slots of every class.

    Slots are read from their descriptors, which already have private names mangled
    and exist however `__slots__` was spelled.
    """
    state = dict(getattr(value, '__dict__', {}))
    for cls in type(value).__mro__:
        for name, member in vars(cls).items():
            if inspect.ismemberdescriptor(member) and hasattr(value, name):
                state[name] = getattr(value, name)
    return state


def _value_digest(value: Any, seen: set[int]) -> str:
    if isinstance(value, (str, bytes, int, float, bool, type(None))):
        return repr(value)
    if id(value) in seen:
        return '<cycle>'
    seen = seen | {id(value)}
    if callable(value):
        return component_digest(value, seen)
    if hasattr(value, 'tobytes') and hasattr(value, 'shape'):
        return type(value).__qualname__ + repr(value.shape) + hashlib.sha256(value.tobytes()).hexdigest()
    if isinstance(value, Mapping):
        return repr(sorted((repr(k), _value_digest(v, seen)) for k, v in value.items()))
    if isinstance(value, (list, tuple, set, frozenset)):
        items = [_value_digest(v, seen) for v in value]
        return repr(sorted(items) if isinstance(value, (set, frozenset)) else items)
    shown = repr(value) if type(value).__repr__ is not object.__repr__ else ''
    return type(value).__qualname__ + shown + _value_digest(_instance_state(value), seen)


def component_digest(component: Any, seen: set[int] | None = None) -> str:
    """Identify a callable by what can be read from it, not by a version string alone.

    Covers direct source, closure values, defaults, partial arguments, instance state
    and any declared `version` and `config`. Code reached only through calls, and files
    such as model weights, are outside it; a deployer must declare those in `config`.
    A callable with no readable identity is refused rather than hashed by its type.
    """
    seen = set() if seen is None else seen
    if isinstance(component, functools.partial):
        parts: list = ['partial', component_digest(component.func, seen), _value_digest(component.args, seen), _value_digest(component.keywords, seen)]
    elif inspect.ismethod(component):
        parts = ['method', component_digest(component.__func__, seen), _value_digest(component.__self__, seen)]
    elif inspect.isfunction(component):
        cells = [c.cell_contents for c in component.__closure__ or ()]
        try:
            source = inspect.getsource(component)
        except (OSError, TypeError):
            source = repr((component.__code__.co_code, component.__code__.co_consts))
        parts = ['function', source, _value_digest(cells, seen), _value_digest(component.__defaults__, seen), _value_digest(component.__kwdefaults__, seen)]
    elif inspect.isbuiltin(component) or inspect.isclass(component):
        parts = ['named', getattr(component, '__module__', ''), component.__qualname__]
    else:
        try:
            source = inspect.getsource(type(component))
        except (OSError, TypeError) as exc:
            raise SpecError('component has no readable identity: ' + repr(type(component))) from exc
        parts = ['instance', source, _value_digest(_instance_state(component), seen)]
    parts += [str(getattr(component, 'version', '')), str(getattr(component, 'config', ''))]
    return hashlib.sha256(json.dumps(parts).encode()).hexdigest()


def prefix_fingerprints(h: Hierarchy, order: tuple[str, ...], identity: Mapping[str, str], world: str = '') -> dict[str, str]:
    """Merkle hash over each node's ancestor sub-DAG.

    A node's fingerprint covers its own stage, its components, the fingerprints of
    all predecessors, and `world`: the goals, statistical goals and labelling oracle
    that give a measured loss its meaning. One pass, linear.
    """
    predecessors = ancestors(h, order)
    result: dict[str, str] = {}
    for name in order:
        node = h.nodes[name]
        if isinstance(node, Gate):
            contract = h.layers.get(node.layer)
            own: list = ['gate', node.rule, node.establishes, node.layer, sorted(node.evidence), sorted(node.provides),
                         contract and [sorted(contract.requires), contract.view]]
        elif isinstance(node, Guard):
            layer = h.layers[node.layer]
            own = ['guard', node.layer, sorted(node.evidence), sorted(layer.scope), sorted(layer.requires), layer.view]
        else:
            # A switch's two outgoing branches route differently, so successors
            # are part of a switch's identity below through their edge label.
            own = ['switch', node.condition]
        kinds = sorted((x, h.obligations[x].kind) for x in getattr(node, 'evidence', ()) if x in h.obligations)
        labelled = []
        for p in predecessors[name]:
            parent = h.nodes[p]
            edge = ('then' if parent.then == name else '') + ('else' if parent.otherwise == name else '') if isinstance(parent, Switch) else 'next'
            labelled.append([edge, result[p]])
        payload = json.dumps([world, name, own, kinds, identity.get(name, ''), labelled, name == order[0]], sort_keys=True)
        result[name] = hashlib.sha256(payload.encode()).hexdigest()
    return result


@dataclass(frozen=True)
class RouteCertificate:
    route: str
    fingerprint: str
    context: str
    upper: float      # upper bound on Pr[unsafe and accepted on this route]
    delta: float      # this certificate's share of the confidence budget
    samples: int

    def valid(self) -> bool:
        return (math.isfinite(self.upper) and 0 <= self.upper <= 1 and 0 < self.delta < 1
                and type(self.samples) is int and self.samples > 0)


def _probability(value: Any, name: str) -> None:
    """Refuse what is not a probability, before NaN can make a later comparison false."""
    if isinstance(value, bool) or not isinstance(value, numbers.Real) or not 0 <= value <= 1:
        raise SpecError(f'{name} must be a probability: {value!r}')


Rule = Callable[[ActionView, Proposal, 'Ledger'], bool]


@dataclass
class Ledger:
    """Trusted mutable state of stateful gates; changed only on acceptance."""
    spent: float = 0.0


class Engine:
    """Fingerprints are computed once, at construction, and acceptance does not recompute
    them. Components must stay fixed for an engine's lifetime; after a change, build a new
    engine, whose fingerprints then decide which certificates still apply.
    """

    def __init__(self, h: Hierarchy, store: ProvenanceStore, approvals: ApprovalStore, rules: Mapping[str, Rule],
                 guards: Mapping[str, Callable], conditions: Mapping[str, Callable] | None = None,
                 checks: Mapping[str, Callable] | None = None, certificates: Iterable[RouteCertificate] = (),
                 context: str = '', statistical: frozenset[str] = frozenset(), budget: float = 1.0,
                 delta: float = 0.05, label: str = '', shares: Mapping[str, float] | None = None) -> None:
        _probability(delta, 'confidence budget')
        _probability(budget, 'risk budget')
        for route, share in (shares or {}).items():
            _probability(share, f'confidence share of {route}')
        report = check(h)
        if not report.ok:
            raise SpecError('specification rejected: ' + repr(report.findings[:3]))
        self.h, self.report, self.store, self.approvals = h, report, store, approvals
        self.rules, self.guards = dict(rules), dict(guards)
        self.conditions, self.checks = dict(conditions or {}), dict(checks or {})
        self.context, self.statistical, self.ledger = context, statistical, Ledger()
        for name in report.order:
            node = h.nodes[name]
            if isinstance(node, Gate) and node.rule not in self.rules:
                raise SpecError('no implementation for rule ' + node.rule)
            if isinstance(node, Guard) and node.layer not in self.guards:
                raise SpecError('no implementation for layer ' + node.layer)
            if isinstance(node, Switch) and node.condition not in self.conditions:
                raise SpecError('no implementation for condition ' + node.condition)
            for item in getattr(node, 'evidence', ()):
                if h.obligations[item].kind == 'checked' and item not in self.checks:
                    raise SpecError('no runtime predicate for checked obligation ' + item)
        world = json.dumps([sorted(h.goals), sorted(statistical), label])
        self.fingerprints = prefix_fingerprints(h, report.order, self._identities(), world)
        # A statistical goal is hard only where a deterministic gate establishes it on every
        # path. Elsewhere it rests on a guard or a veto stage, so the route needs evidence.
        hard = gated(h, report.order, statistical)
        self.needs_certificate = {r: bool(statistical - hard[r]) for r in report.routes}
        # Confidence is allocated to routes before any calibration, over all statistical routes,
        # so that which certificates happen to open cannot affect the union bound.
        statistical_routes = [r for r in report.routes if self.needs_certificate[r]]
        self.shares = dict(shares) if shares is not None else {r: delta / len(statistical_routes) for r in statistical_routes}
        if sum(self.shares.get(r, 0) for r in statistical_routes) > delta * (1 + 1e-12):
            raise SpecError('allocated confidence shares exceed the confidence budget')
        self.open: dict[str, RouteCertificate] = {}
        for certificate in certificates:
            if (certificate.valid() and certificate.route in self.fingerprints and certificate.context == context
                    and certificate.fingerprint == self.fingerprints[certificate.route]):
                if certificate.route in self.open:
                    raise SpecError('two certificates for route ' + certificate.route)
                if certificate.delta > self.shares.get(certificate.route, 0) * (1 + 1e-12):
                    raise SpecError('certificate exceeds its route\'s confidence share: ' + certificate.route)
                self.open[certificate.route] = certificate
        if sum(c.upper for c in self.open.values()) > budget:
            raise SpecError('certified route bounds exceed the risk budget')

    def _identities(self) -> dict[str, str]:
        result = {}
        for name in self.report.order:
            node = self.h.nodes[name]
            if isinstance(node, Gate):
                digest = component_digest(self.rules[node.rule])
            elif isinstance(node, Guard):
                digest = component_digest(self.guards[node.layer])
            else:
                digest = component_digest(self.conditions[node.condition])
            predicates = sorted(x for x in getattr(node, 'evidence', ()) if self.h.obligations[x].kind == 'checked')
            result[name] = json.dumps([digest, [(x, component_digest(self.checks[x])) for x in predicates]])
        return result

    def view_for(self, layer: Layer, facts: ActionView, proposal: Proposal, score: float | None) -> Any:
        """The only construction of a guard's input; `structured` carries no free text."""
        if layer.view == 'raw':
            return proposal.text
        record = {'destructive': facts.destructive, 'production': facts.production, 'approved': facts.approved,
                  'external': facts.external, 'secret': facts.secret, 'untrusted': facts.untrusted}
        if layer.view == 'structured':
            record['score'] = score
        return record

    def _run(self, proposal: Proposal, certified: bool) -> Outcome:
        facts = action_view(proposal.action, self.store, self.approvals)
        name, path, score = self.h.entry, [], None
        while name is not None:
            node = self.h.nodes[name]
            path.append(name)
            if isinstance(node, Gate):
                failed = self._unestablished(node, name, facts, proposal)
                if failed is not None:
                    return Outcome(False, None, name, 'obligation:' + failed, tuple(path))
                # A veto stage sees what its layer's view allows; a deterministic gate reads typed facts.
                shown = proposal if node.layer is None or self.h.layers[node.layer].view == 'raw' else dataclasses.replace(proposal, text='')
                if not self._holds(self.rules[node.rule], facts, shown):
                    return Outcome(False, None, name, 'gate:' + node.rule, tuple(path))
                name = node.next
            elif isinstance(node, Switch):
                taken = self._condition(node, facts, proposal)
                if taken is None:
                    return Outcome(False, None, name, 'condition:' + node.condition, tuple(path))
                name = node.then if taken else node.otherwise
            else:
                failed = self._unestablished(node, name, facts, proposal)
                if failed is not None:
                    return Outcome(False, None, name, 'obligation:' + failed, tuple(path))
                layer = self.h.layers[node.layer]
                verdict, value = self._consult(layer, facts, proposal, score)
                if value is not None:
                    score = value
                if verdict == Verdict.ALLOW:
                    if certified and self.needs_certificate[name] and name not in self.open:
                        return Outcome(False, None, name, 'route not certified', tuple(path))
                    return Outcome(True, name, name, 'accepted', tuple(path))
                if verdict == Verdict.BLOCK:
                    return Outcome(False, None, name, 'blocked:' + node.layer, tuple(path))
                name = node.next
        return Outcome(False, None, path[-1] if path else '<entry>', 'default deny', tuple(path))

    def _unestablished(self, node, name: str, facts: ActionView, proposal: Proposal) -> str | None:
        for item in sorted(node.evidence):
            if self.h.obligations[item].kind == 'checked' and not self._established(item, name, facts, proposal):
                return item
        return None

    def _holds(self, rule: Rule, facts: ActionView, proposal: Proposal) -> bool:
        try:
            return rule(facts, proposal, self.ledger) is True
        except Exception:
            return False

    def _condition(self, node: Switch, facts: ActionView, proposal: Proposal) -> bool | None:
        """The branch taken, or None if the condition failed, which denies."""
        try:
            return self.conditions[node.condition](facts, proposal) is True
        except Exception:
            return None

    def _established(self, item: str, node: str, facts: ActionView, proposal: Proposal) -> bool:
        try:
            return self.checks[item](node, facts, proposal) is True
        except Exception:
            return False

    def _consult(self, layer: Layer, facts: ActionView, proposal: Proposal, score: float | None) -> tuple[Verdict, float | None]:
        """A guard returns a Verdict or (Verdict, score). Anything else blocks."""
        try:
            answer = self.guards[layer.name](self.view_for(layer, facts, proposal, score))
            verdict, value = answer if isinstance(answer, tuple) else (answer, None)
            if value is not None and (not isinstance(value, (int, float)) or not math.isfinite(value)):
                return Verdict.BLOCK, None
            return Verdict(verdict), value
        except Exception:
            return Verdict.BLOCK, None

    def evaluate(self, proposal: Proposal) -> Outcome:
        if not (math.isfinite(proposal.cost) and proposal.cost >= 0):
            return Outcome(False, None, '<entry>', 'invalid cost', ())
        outcome = self._run(proposal, True)
        # Only a budget gate on the run accounts for the cost. That every route passes one
        # is a premise of the budget theorem, not something the engine can assume.
        if outcome.accepted and any(getattr(self.rules.get(getattr(self.h.nodes[x], 'rule', None)), 'stateful', False) for x in outcome.path):
            self.ledger.spent += proposal.cost
        return outcome

    def shadow(self, proposal: Proposal) -> Outcome:
        """The same decision path with route certificates ignored, for calibration."""
        return self._run(proposal, False)


def certify(engine: Engine, calibration: Iterable[tuple[Proposal, bool]], delta: float,
            routes: Iterable[str] | None = None, context: str | None = None, share: float | None = None) -> list[RouteCertificate]:
    """Bound Pr[unsafe and accepted on route r] for each route, on i.i.d. calibration data.

    Calibration runs the deployed decision function. Each route receives `share`, by
    default delta/q, q being the number of routes that need a certificate here, so all
    bounds hold together with probability at least 1-delta (union bound). The engine
    refuses a set of open certificates whose shares exceed its delta, so a deployer who
    expects new routes should reserve shares in advance.
    """
    needing = [r for r in engine.report.routes if engine.needs_certificate[r]]
    wanted = set(needing if routes is None else routes)
    losses, samples = dict.fromkeys(needing, 0), 0
    for proposal, unsafe in calibration:
        samples += 1
        outcome = engine.shadow(proposal)
        if unsafe and outcome.accepted and outcome.route in losses:
            losses[outcome.route] += 1
    share = delta / max(len(needing), 1) if share is None else share
    return [RouteCertificate(r, engine.fingerprints[r], engine.context if context is None else context,
                             binomial_upper(losses[r], samples, share), share, samples)
            for r in needing if r in wanted]


def affected_routes(old: Engine, new: Engine) -> tuple[str, ...]:
    """Routes of `new` whose prefix changed, so whose certificates no longer apply."""
    return tuple(r for r in new.report.routes
                 if new.needs_certificate[r] and old.fingerprints.get(r) != new.fingerprints[r])
