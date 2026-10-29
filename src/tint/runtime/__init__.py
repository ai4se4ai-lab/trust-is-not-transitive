"""Final-sink middleware. Certificates are supplied only by trusted host code."""
from __future__ import annotations
from dataclasses import asdict, dataclass
import json
import hashlib
import math
from pathlib import Path
import time
from typing import Callable
from ..calibration import Certificate
from ..layers import LexicalScorer, StructuredJudge, checked_score, deterministic, quarantine, safe_judge_call
from ..model import Action, ActionKind, ApprovalStore, ProvenanceStore, Verdict, action_view
from ..spec import Specification, check


@dataclass(frozen=True)
class GuardDecision:
    action_digest: str
    verdict: Verdict
    route: str
    reason: str
    layers: tuple[str,...]
    elapsed_ns: int
    score: float | None
    certificate_id: str | None

    def as_dict(self) -> dict:
        return asdict(self)


class GuardRuntime:
    def __init__(self, spec: Specification, store: ProvenanceStore, approvals: ApprovalStore,
                 certificate: Certificate | None=None, context_id: str='local-fixtures-v1',
                 policy_id: str | None=None, epsilon: float=0.05, threshold: float=0.2,
                 scorer: Callable | None=None, judge: Callable | None=None, log_path: Path | None=None,
                 deployment_environment: str='sandbox') -> None:
        check(spec)
        if not 0<=threshold<=1 or not 0<=epsilon<=1:
            raise ValueError('invalid runtime threshold/budget')
        self.spec,self.store,self.approvals=spec,store,approvals
        if deployment_environment not in {'sandbox','production'}:
            raise ValueError('invalid trusted deployment environment')
        self.certificate,self.context_id=certificate,context_id
        self.deployment_environment=deployment_environment
        self.epsilon,self.threshold=epsilon,threshold
        self.scorer,self.judge=scorer or LexicalScorer(),judge or StructuredJudge()
        self.policy_id=policy_fingerprint(spec,threshold,getattr(self.scorer,'version','custom-unversioned'),
                                          getattr(self.judge,'version','custom-unversioned'),deployment_environment)
        if policy_id is not None and policy_id!=self.policy_id:
            raise ValueError('policy id does not match actual configuration')
        self.log_path=log_path

    def evaluate(self, action: Action, issue: str) -> GuardDecision:
        start=time.perf_counter_ns()
        view=action_view(action,self.store,self.approvals)
        verdict,reason=deterministic(view)
        if action.environment!=self.deployment_environment:
            verdict,reason=Verdict.BLOCK,'agent environment differs from trusted dispatcher environment'
        layers=['L1']
        route='deterministic'
        score=None
        certificate_id=None
        if verdict!=Verdict.BLOCK:
            actual_id=policy_fingerprint(self.spec,self.threshold,getattr(self.scorer,'version','custom-unversioned'),
                                         getattr(self.judge,'version','custom-unversioned'),self.deployment_environment)
            if actual_id!=self.policy_id or self.certificate is None or not self.certificate.applies(actual_id,self.context_id,'structured-v1',self.epsilon):
                verdict,reason,route=Verdict.BLOCK,'missing or inapplicable whole-policy certificate','contract'
            else:
                certificate_id=self.certificate.policy_id
                layers.append('L2')
                try:
                    score=checked_score(self.scorer,issue)
                    if score<self.threshold:
                        verdict,reason,route=Verdict.ALLOW,'certified cheap route','L2'
                    else:
                        layers.append('L3')
                        verdict=safe_judge_call(self.judge,quarantine(view,score))
                        if verdict==Verdict.ESCALATE:
                            layers.append('L4')
                            verdict=Verdict.BLOCK
                        reason,route='structured judge / fail-closed fallback','L3'
                except Exception:
                    verdict,reason,route=Verdict.BLOCK,'guard error; fail closed','error'
        decision=GuardDecision(action.digest(),verdict,route,reason,tuple(layers),time.perf_counter_ns()-start,score,certificate_id)
        if self.log_path:
            self.log_path.parent.mkdir(parents=True,exist_ok=True)
            with self.log_path.open('a',encoding='utf-8') as stream:
                stream.write(json.dumps(decision.as_dict(),sort_keys=True)+'\n')
        return decision


def policy_fingerprint(spec: Specification, threshold: float, scorer_version: str='lexical-v2',
                       judge_version: str='structured-surrogate-v1', environment: str='sandbox') -> str:
    # Trusted plugin versions must identify immutable implementations; a malicious
    # host/plugin can lie about this identity and is outside the threat model.
    payload={'spec':asdict(spec),'threshold':threshold,'scorer':scorer_version,'judge':judge_version,
             'view':'structured-v1','environment':environment}
    return hashlib.sha256(json.dumps(payload,sort_keys=True,default=lambda x:sorted(x)).encode()).hexdigest()


def parse_tool_call(arguments: str) -> Action:
    """OpenAI-compatible function argument object; intentionally narrow tool grammar.

    No approval, provenance labels, code, commands or shell expansion can be
    supplied through this tool. Tool-call context must come from the host.
    """
    def unique(pairs):
        result={}
        for k,v in pairs:
            if k in result:
                raise ValueError('duplicate tool field')
            result[k]=v
        return result
    data=json.loads(arguments,object_pairs_hook=unique)
    if not isinstance(data,dict) or set(data)!={'kind','target','inputs','environment'}:
        raise ValueError('unsupported tool fields')
    if not isinstance(data['inputs'],list) or not all(isinstance(x,str) for x in data['inputs']):
        raise ValueError('input references must be strings')
    return Action(ActionKind(data['kind']),data['target'],tuple(data['inputs']),data['environment'])
