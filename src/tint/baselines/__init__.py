"""Controlled ablations and toy comparators, NOT named-system reimplementations."""
from __future__ import annotations
from ..layers import ExposedJudge, LexicalScorer, StructuredJudge, deterministic, quarantine
from ..model import ActionView, Verdict

NAMES=('rules_only','classifier_only','judge_only_scripted','naive_delegation',
       'naive_with_sink','checked_uncalibrated','checked_quarantine')


def decide(name: str, issue: str, view: ActionView, threshold: float=0.2) -> tuple[bool,tuple[str,...]]:
    if name not in NAMES:
        raise ValueError('unknown baseline')
    hard=deterministic(view)[0]==Verdict.ALLOW
    score=LexicalScorer()(issue)
    if name=='rules_only':
        return hard,('L1',)
    if name=='classifier_only':
        return score<threshold,('L2',)
    if name=='judge_only_scripted':
        return ExposedJudge()(issue,view,score)==Verdict.ALLOW,('L3',)
    if name=='naive_delegation':
        # Deliberately invalid T0: no mandatory sink. Not a competent SOTA baseline.
        return ExposedJudge()(issue,view,score)==Verdict.ALLOW,('L2','L3')
    if not hard:
        return False,('L1',)
    if score<threshold:
        return True,('L1','L2')
    judge=ExposedJudge()(issue,view,score) if name=='naive_with_sink' else StructuredJudge()(quarantine(view,score))
    return judge==Verdict.ALLOW,('L1','L2','L3')
