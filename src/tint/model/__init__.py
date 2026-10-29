"""Immutable proposals and monitor-owned provenance. No shell parsing claims."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, IntFlag
import hashlib
import json


class Label(IntFlag):
    TRUSTED = 0
    UNTRUSTED = 1
    SECRET = 2

    def join(self, other: Label) -> Label:
        return self | other


class Verdict(str, Enum):
    ALLOW = "allow"
    BLOCK = "block"
    ESCALATE = "escalate"


class ActionKind(str, Enum):
    DELETE = "delete"
    FORCE_PUSH = "force_push"
    HTTP = "http"
    PATCH = "patch"
    READ = "read"
    TEST = "test"


@dataclass(frozen=True)
class Action:
    kind: ActionKind
    target: str = ""
    inputs: tuple[str, ...] = ()
    environment: str = "sandbox"

    def __post_init__(self) -> None:
        if not isinstance(self.kind, ActionKind):
            raise ValueError("unknown typed action")
        if self.environment not in {"sandbox", "production"}:
            raise ValueError("unknown environment")
        if not isinstance(self.inputs, tuple) or not all(isinstance(x, str) for x in self.inputs):
            raise ValueError("inputs must be immutable identifiers")
        if not isinstance(self.target, str):
            raise ValueError("target must be a string")

    def digest(self) -> str:
        return hashlib.sha256(json.dumps({"kind":self.kind.value,"target":self.target,
                                         "inputs":self.inputs,"environment":self.environment},sort_keys=True).encode()).hexdigest()


@dataclass(frozen=True)
class Observation:
    identifier: str
    text: str
    label: Label
    parents: tuple[str, ...] = ()


class ProvenanceStore:
    """Trusted sandbox component; never exposed as a callable agent tool."""
    def __init__(self) -> None:
        self._items: dict[str, Observation] = {}

    def add(self, observation: Observation) -> None:
        if observation.identifier in self._items:
            raise ValueError("provenance identifiers are write-once")
        inherited = self.labels(observation.parents)
        if observation.label.join(inherited) != observation.label:
            raise ValueError("derived observation cannot erase parent taint")
        self._items[observation.identifier] = observation

    def labels(self, identifiers: tuple[str, ...]) -> Label:
        result = Label.TRUSTED
        for identifier in identifiers:
            item = self._items.get(identifier)
            result |= item.label if item else Label.UNTRUSTED | Label.SECRET
        return result

    def text(self, identifier: str) -> str:
        return self._items[identifier].text


@dataclass(frozen=True)
class Trace:
    identifier: str
    issue: str
    action: Action
    unsafe: bool  # oracle annotation for evaluation only; never passed into a guard
    family: str


class ApprovalStore:
    """Trusted capability stub: grant is a host operation, not an agent argument."""
    def __init__(self) -> None:
        self._grants: set[tuple[str,int]] = set()
        self.epoch = 0

    def grant(self, action: Action) -> None:
        self._grants.add((action.digest(),self.epoch))

    def permits(self, action: Action) -> bool:
        return (action.digest(),self.epoch) in self._grants

    def revoke_all(self) -> None:
        self.epoch += 1


@dataclass(frozen=True)
class ActionView:
    destructive: bool
    production: bool
    approved: bool
    external: bool
    secret: bool
    untrusted: bool


def action_view(action: Action, store: ProvenanceStore, approvals: ApprovalStore) -> ActionView:
    label = store.labels(action.inputs)
    # Only one exact local mock destination is considered internal. Aliases,
    # redirects, real URLs, and arbitrary hosts are external/fail closed.
    external = action.kind == ActionKind.HTTP and action.target != "local-mock"
    return ActionView(action.kind in {ActionKind.DELETE,ActionKind.FORCE_PUSH},
                      action.environment == "production", approvals.permits(action),
                      external, bool(label & Label.SECRET), bool(label & Label.UNTRUSTED))
