"""Deterministic gate rules. Each is a total predicate on monitor-owned facts."""
from __future__ import annotations
from dataclasses import dataclass
import posixpath
from .engine import Ledger, Proposal
from ..model import ActionKind, ActionView


def production_approval(facts: ActionView, proposal: Proposal, ledger: Ledger) -> bool:
    return not (facts.destructive and facts.production) or facts.approved


def secret_egress(facts: ActionView, proposal: Proposal, ledger: Ledger) -> bool:
    return not (facts.external and facts.secret)


def no_untrusted_input(facts: ActionView, proposal: Proposal, ledger: Ledger) -> bool:
    return not facts.untrusted


@dataclass(frozen=True)
class PathConfinement:
    """File actions stay inside `root`; `..`, absolute escapes and aliases deny."""
    root: str = 'workspace'
    version = 'path-confinement-1'

    @property
    def config(self) -> str:
        return self.root

    def __call__(self, facts: ActionView, proposal: Proposal, ledger: Ledger) -> bool:
        if proposal.action.kind not in {ActionKind.PATCH, ActionKind.READ, ActionKind.DELETE}:
            return True
        target = proposal.action.target
        if '\\' in target or '\x00' in target or target.startswith('/'):
            return False
        normal = posixpath.normpath(target)
        return normal == self.root or normal.startswith(self.root + '/')


@dataclass(frozen=True)
class CumulativeBudget:
    """Stateful gate: accepted actions never spend more than `limit` in total."""
    limit: float
    version = 'cumulative-budget-1'
    stateful = True

    @property
    def config(self) -> str:
        return repr(self.limit)

    def __call__(self, facts: ActionView, proposal: Proposal, ledger: Ledger) -> bool:
        return proposal.cost >= 0 and ledger.spent + proposal.cost <= self.limit
