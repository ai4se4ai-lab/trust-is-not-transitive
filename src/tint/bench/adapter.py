"""Map benchmark tool calls to typed actions. The agent never supplies labels or approvals."""
from __future__ import annotations
from dataclasses import dataclass
from ..model import Action, ActionKind, Label, Observation, ProvenanceStore


@dataclass(frozen=True)
class ToolRule:
    kind: ActionKind
    target_arg: str | None = None
    fixed_target: str = ""


class ToolAdapter:
    def __init__(self, rules: dict[str, ToolRule], store: ProvenanceStore,
                 trusted_hosts: tuple[str, ...] = (), environment: str = "sandbox") -> None:
        self.rules, self.store = dict(rules), store
        self.trusted_hosts, self.environment = frozenset(trusted_hosts), environment
        self._context: list[str] = []

    def observe(self, identifier: str, text: str, *, untrusted: bool = False, secret: bool = False) -> None:
        label = (Label.UNTRUSTED if untrusted else Label.TRUSTED) | (Label.SECRET if secret else Label.TRUSTED)
        self.store.add(Observation(identifier, text, label))  # raises on a duplicate identifier
        self._context.append(identifier)

    def to_action(self, tool: str, args: dict) -> Action:
        rule = self.rules.get(tool)
        if rule is None:
            raise ValueError(f"tool {tool!r} has no typed mapping")
        target = rule.fixed_target
        if rule.target_arg is not None:
            target = str(args.get(rule.target_arg, ""))
        if rule.kind == ActionKind.HTTP and target in self.trusted_hosts:
            target = "local-mock"
        return Action(rule.kind, target, tuple(self._context), self.environment)
