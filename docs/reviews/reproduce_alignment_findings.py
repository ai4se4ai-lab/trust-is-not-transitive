import sys,json,math
from pathlib import Path
ROOT=Path.cwd()
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'formal/calculus'),str(ROOT/'experiments/v2')]
from tint.hsl import *
from tint.hsl.engine import Engine,Proposal,RouteCertificate,component_digest
from tint.model import Action,ActionKind,ApprovalStore,Verdict
from tint.agents import fixture_store
Z=frozenset(); G=frozenset({'g'})
L=Layer('L',G,Z,'raw')
proposal=Proposal(Action(ActionKind.TEST))
def allow(view): return Verdict.ALLOW
def yes(*args): return True
def make_h(nodes,layers=(L,),obligations=()):
    return Hierarchy(G,{x.name:x for x in obligations},{x.name:x for x in layers},{x.id:x for x in nodes},nodes[0].id)
def engine(h,guard=allow,**kw):
    return Engine(h,fixture_store(),ApprovalStore(),{'rule':yes},{'L':guard},statistical=G,**kw)
h=make_h([Guard('a','L',Z,'b'),Guard('b','L',Z,None)])
base=engine(h)
cert=RouteCertificate('a',base.fingerprints['a'],'',.01,.4,100)
def attempt(label,**kw):
    try:
        e=engine(h,delta=.05,**kw)
        print(label,json.dumps({'open_delta':sum(c.delta for c in e.open.values()),'accepted':e.evaluate(proposal).accepted}))
    except SpecError as exc:
        print(label,'refused:',exc)
attempt('negative share:',shares={'a':.4,'b':-.35},certificates=[cert])
cert2=RouteCertificate('a',base.fingerprints['a'],'',.01,.8,100)
attempt('NaN share:',shares={'a':float('nan'),'b':0},certificates=[cert2])
class SlotGuard:
    __slots__=('accept',)
    def __init__(self,accept): self.accept=accept
    def __call__(self,view): return Verdict.ALLOW if self.accept else Verdict.BLOCK
b,a=SlotGuard(False),SlotGuard(True)
print('slotted callable identical digest:',component_digest(b)==component_digest(a),'different decisions:',b(None)!=a(None))
h1=make_h([Guard('a','L',Z,None)])
old=engine(h1,b)
oldcert=RouteCertificate('a',old.fingerprints['a'],'',.01,.05,100)
new=engine(h1,a,certificates=[oldcert])
print('slotted change:',json.dumps({'fingerprint_unchanged':old.fingerprints==new.fingerprints,'old_certificate_open':bool(new.open),'accepted':new.evaluate(proposal).accepted}))
class MutableGuard:
    def __init__(self): self.accept=False
    def __call__(self,view): return Verdict.ALLOW if self.accept else Verdict.BLOCK
m=MutableGuard(); old=engine(h1,m)
oldcert=RouteCertificate('a',old.fingerprints['a'],'',.01,.05,100)
live=engine(h1,m,certificates=[oldcert]);before=component_digest(m);m.accept=True
print('in-place mutation:',json.dumps({'digest_changed':before!=component_digest(m),'certificate_remains_open':bool(live.open),'accepted_after_mutation':live.evaluate(proposal).accepted}))
flow=make_h([Gate('v','rule','g','a',provides=frozenset({'o'})),Guard('a','L',Z,None)],obligations=(Obligation('o','assumed'),))
print('unneeded refinement:',json.dumps({'default_ok':check(flow).ok,'default_exact_states':check(flow).exact_states,'decision_exact_states':check(flow,witnesses=False).exact_states}))
# Validate the worked example without writing or rerunning experiment results.
import run,reference
from harness import term_of,tables
h=run.adversarial(parse((ROOT/'experiments/v2/cases/devagent.json').read_text()))
report=check(h)
bad=run.adversarial(parse((ROOT/'experiments/v2/cases/devagent_exposed_judge.json').read_text()))
rejected=check(bad);finding=rejected.findings[0];m=witness_model(bad,finding)
req,scope=tables(bad)
print('DevAgent:',json.dumps({'accepted':report.ok,'routes':report.routes,'residual':report.residual,'necessary':necessary(h),'exposed_finding':vars(finding),'witness_contract_respecting':reference.wf(term_of(bad),m['passes'],m['verdict'],m['branch'],m['holds'],m['safe'],req,scope),'witness_decision':reference.evaluate(term_of(bad),m['passes'],m['verdict'],m['branch'])}))
