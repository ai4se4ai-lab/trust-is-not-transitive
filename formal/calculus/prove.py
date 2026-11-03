"""Discharge every proof obligation of the calculus with Z3 and, independently, cvc5.

Each obligation is valid iff its negation is unsatisfiable. Results, solver versions
and timing go to results/v2/proofs.json. Nothing here relies on bounded enumeration.
"""
from __future__ import annotations
import json
from pathlib import Path
import sys
import time
from z3 import (And, Array, BoolVal, Const, Consts, ForAll, Exists, If, Implies, Int, Ints, K, Not, Or, Select, Solver,
                Store, BoolSort, IntSort, Bool, unsat, get_version_string, Length, Function, Datatype, Real, Reals, RealSort,
                DeclareSort, ArraySort, sat, is_implies, is_quantifier)
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from core import *

OBLIGATIONS: list[tuple[str, str, object]] = []


def ob(theorem: str, case: str, formula) -> None:
    """The union axiom joins the premises, so that the vacuity check also covers it."""
    if is_implies(formula):
        formula = Implies(And(union_axiom(), formula.arg(0)), formula.arg(1))
    else:
        formula = Implies(union_axiom(), formula)
    OBLIGATIONS.append((theorem, case, formula))


# Fresh variables, shared by all obligations.
A, B, S, S2 = Consts('A B S S2', SetOb)
P, P2 = Consts('P P2', Pa)
V, V2 = Consts('V V2', Va)
W, W2 = Consts('W W2', Wa)
E, E2 = Consts('E E2', Ea)
k, k1, k2, K_ = Consts('k k1 k2 K_', H)
g, t, r = Ints('g t r')
phi, q, o = Consts('phi q o', Ob)
l = Const('l', Lay)
om = Const('om', SetOb)
# The full obligation set and the everywhere-full map, by their defining properties.
TOP = Const('TOP', SetOb)
ALLTOP = Const('ALLTOP', Ea)
ofull, ifull = Const('o!full', Ob), Int('i!full')
FULL = And(ForAll(ofull, Select(TOP, ofull)), ForAll(ifull, Select(ALLTOP, ifull) == TOP))

dd, F = Consts('dd F', SetOb)      # D of a gate; the provided-facts parameter of wf
D0 = H.deny
GATE = H.gate(g, phi, l, om, dd, k)
GUARD = H.guard(g, l, om, k)
SWITCH = H.switch(g, k1, k2)
ACCEPTED = lambda T: evalF(T, P, V, W) == Out.accepted(t)
EV = unionF(om, B)        # the evidence a stage has: supplied here, or provided on the path
AP, BP = Store(A, phi, True), unionF(B, dd)     # after a credited gate
FP = unionF(F, dd)

# ---- T1 soundness: every model satisfying the contracts on reached invocations is safe.
# Generalized over A, B and the facts F; each premise on k is an instance of the induction hypothesis.
def soundness(T, A_=A, B_=B, F_=F):
    return Implies(And(checkF(T, A_, B_), sub(A_, S), sub(B_, F_), wfF(T, P, V, W, E, S, F_), ACCEPTED(T)), sub(G, S))


ob('T1-soundness', 'deny', Implies(And(eval_def(D0, P, V, W)), soundness(D0)))
ob('T1-soundness', 'gate', Implies(And(check_def(GATE, A, B), eval_def(GATE, P, V, W), wf_def(GATE, P, V, W, E, S, F),
                                       soundness(k, AP, BP, FP), soundness(k, A, B, F), soundness(k, A, B, FP)),
                                   soundness(GATE)))
ob('T1-soundness', 'guard', Implies(And(check_def(GUARD, A, B), eval_def(GUARD, P, V, W), wf_def(GUARD, P, V, W, E, S, F), soundness(k)), soundness(GUARD)))
ob('T1-soundness', 'switch', Implies(And(check_def(SWITCH, A, B), eval_def(SWITCH, P, V, W), wf_def(SWITCH, P, V, W, E, S, F),
                                         soundness(k1), soundness(k2)), soundness(SWITCH)))

# ---- Frame lemmas: changing a model at an id outside a term changes neither eval nor wf.
# Stated for arbitrary base arrays and facts, so that they compose when a proof changes several.
c = Int('c')
b = Const('b', BoolSort())
v_ = Const('v_', Vd)
e_ = Const('e_', SetOb)


def frame(T, base, changed, idx=c, F_=F):
    """If idx is outside T, the two model tuples (P,V,W,E) agree on T."""
    (P0, V0, W0, E0), (P1, V1, W1, E1) = base, changed
    return Implies(Not(Select(idsF(T), idx)),
                   And(evalF(T, P1, V1, W1) == evalF(T, P0, V0, W0), wfF(T, P1, V1, W1, E1, S, F_) == wfF(T, P0, V0, W0, E0, S, F_)))


BASE = (P, V, W, E)
FRAMES = {'P': (Store(P, c, b), V, W, E), 'V': (P, Store(V, c, v_), W, E), 'W': (P, V, Store(W, c, b), E), 'E': (P, V, W, Store(E, c, e_))}


def defs(T, changed):
    P1, V1, W1, E1 = changed
    return And(eval_def(T, P1, V1, W1), eval_def(T, P, V, W), wf_def(T, P1, V1, W1, E1, S, F), wf_def(T, P, V, W, E, S, F), ids_def(T))


for label, changed in FRAMES.items():
    name = 'L1-frame-' + label
    ob(name, 'deny', Implies(defs(D0, changed), frame(D0, BASE, changed)))
    ob(name, 'gate', Implies(And(defs(GATE, changed), frame(k, BASE, changed), frame(k, BASE, changed, c, FP)), frame(GATE, BASE, changed)))
    ob(name, 'guard', Implies(And(defs(GUARD, changed), frame(k, BASE, changed)), frame(GUARD, BASE, changed)))
    ob(name, 'switch', Implies(And(defs(SWITCH, changed), frame(k1, BASE, changed), frame(k2, BASE, changed)), frame(SWITCH, BASE, changed)))

# ---- T2 completeness: a rejected term with no repeated id on a path has a model that satisfies
# every contract on the reached invocations and accepts a proposal violating a goal.
# The IH is the premise `witness(subterm, ...)` on a model obtained from the subterm's existential.
def witness(T, A_, B_, P1, V1, W1, E1, S1):
    return And(wfF(T, P1, V1, W1, E1, S1, B_), sub(A_, S1), evalF(T, P1, V1, W1) == Out.accepted(t), Not(sub(G, S1)))


ob('T2-completeness', 'deny', Implies(check_def(D0, A, B), checkF(D0, A, B)))
ob('T2-completeness', 'gate-reduction', Implies(And(check_def(GATE, A, B), uniq_def(GATE), uniqF(GATE), Not(checkF(GATE, A, B))),
                                                And(uniqF(k), If(sub(req(l), EV), Not(checkF(k, AP, BP)), Not(checkF(k, A, B))))))
P1 = Store(P, g, True)
# (a) the gate is credited: all obligations hold, it passes, and phi is in S by the IH.
E1 = Store(E, g, TOP)
ob('T2-completeness', 'gate-credited', Implies(And(
    FULL, sub(req(l), EV), uniq_def(GATE), uniqF(GATE), witness(k, AP, BP, P, V, W, E, S),
    frame(k, BASE, (P1, V, W, E), g, BP), frame(k, (P1, V, W, E), (P1, V, W, E1), g, BP),
    eval_def(GATE, P1, V, W), wf_def(GATE, P1, V, W, E1, S, B)),
    witness(GATE, A, B, P1, V, W, E1, S)))
# (b) not credited: an obligation o is neither supplied nor provided. It fails here, so passing promises nothing.
E2c = Store(E, g, Store(TOP, o, False))
ob('T2-completeness', 'gate-uncredited', Implies(And(
    FULL, Select(req(l), o), Not(Select(om, o)), Not(Select(B, o)), uniq_def(GATE), uniqF(GATE), witness(k, A, B, P, V, W, E, S),
    frame(k, BASE, (P1, V, W, E), g, B), frame(k, (P1, V, W, E), (P1, V, W, E2c), g, B),
    eval_def(GATE, P1, V, W), wf_def(GATE, P1, V, W, E2c, S, B)),
    witness(GATE, A, B, P1, V, W, E2c, S)))
ob('T2-completeness', 'gate-cases', Or(sub(req(l), EV), Exists(o, And(Select(req(l), o), Not(Select(om, o)), Not(Select(B, o))))))

ob('T2-completeness', 'guard-reduction', Implies(And(check_def(GUARD, A, B), uniq_def(GUARD), uniqF(GUARD), Not(checkF(GUARD, A, B))), Or(
    And(Not(checkF(k, A, B)), uniqF(k)),
    And(Not(sub(G, A)), Not(sub(req(l), EV))),
    And(Not(sub(G, A)), Not(covered(A, scp(l)))))))
ob('T2-completeness', 'guard-cases', And(Or(sub(G, A), Exists(q, And(Select(G, q), Not(Select(A, q))))),
                                         Or(sub(req(l), EV), Exists(o, And(Select(req(l), o), Not(Select(om, o)), Not(Select(B, o))))),
                                         Or(covered(A, scp(l)), Exists(q, And(Select(G, q), Not(Select(A, q)), Not(Select(scp(l), q)))))))
# (a) rejected further on: escalate here. Two model components change, so the frame lemma applies twice.
Vx, Ex = Store(V, g, esc), Store(E, g, TOP)
ob('T2-completeness', 'guard-continue', Implies(And(
    FULL, uniq_def(GUARD), uniqF(GUARD), witness(k, A, B, P, V, W, E, S),
    frame(k, BASE, (P, Vx, W, E), g, B), frame(k, (P, Vx, W, E), (P, Vx, W, Ex), g, B),
    eval_def(GUARD, P, Vx, W), wf_def(GUARD, P, Vx, W, Ex, S, B)),
    witness(GUARD, A, B, P, Vx, W, Ex, S)))
# (b) an obligation is missing: it fails on this invocation only, the contract is vacuous, the guard accepts.
Sb, Eb, Vb = Store(TOP, q, False), Store(ALLTOP, g, Store(TOP, o, False)), Store(V, g, acc)
ob('T2-completeness', 'guard-obligation', Implies(And(
    FULL, Select(G, q), Not(Select(A, q)), Select(req(l), o), Not(Select(om, o)), Not(Select(B, o)),
    eval_def(GUARD, P, Vb, W), wf_def(GUARD, P, Vb, W, Eb, Sb, B), t == g),
    witness(GUARD, A, B, P, Vb, W, Eb, Sb)))
# (c) an open goal is outside the layer's scope: the guard accepts within its contract.
Ec = ALLTOP
ob('T2-completeness', 'guard-coverage', Implies(And(
    FULL, Select(G, q), Not(Select(A, q)), Not(Select(scp(l), q)),
    eval_def(GUARD, P, Vb, W), wf_def(GUARD, P, Vb, W, Ec, Sb, B), t == g),
    witness(GUARD, A, B, P, Vb, W, Ec, Sb)))
ob('T2-completeness', 'switch-reduction', Implies(And(check_def(SWITCH, A, B), uniq_def(SWITCH), uniqF(SWITCH), Not(checkF(SWITCH, A, B))),
                                                  And(Or(Not(checkF(k1, A, B)), Not(checkF(k2, A, B))), uniqF(k1), uniqF(k2))))
for label, branch, value in [('then', k1, True), ('else', k2, False)]:
    W1 = Store(W, g, value)
    ob('T2-completeness', 'switch-' + label, Implies(And(
        uniq_def(SWITCH), uniqF(SWITCH), witness(branch, A, B, P, V, W, E, S),
        frame(branch, BASE, (P, V, W1, E), g, B),
        eval_def(SWITCH, P, V, W1), wf_def(SWITCH, P, V, W1, E, S, B)),
        witness(SWITCH, A, B, P, V, W1, E, S)))

# ---- T3 monotonicity: if a model is pointwise no more permissive, it accepts no more.
def refines():
    i = Int('i!ref')
    return And(ForAll(i, Implies(Select(P2, i), Select(P, i))), ForAll(i, Select(W2, i) == Select(W, i)),
               ForAll(i, Implies(Select(V2, i) == acc, Select(V, i) == acc)),
               ForAll(i, Implies(Select(V2, i) == esc, Or(Select(V, i) == esc, Select(V, i) == acc))))


def accepted(T, P1, V1, W1):
    return Out.is_accepted(evalF(T, P1, V1, W1))


def mono(T):
    return Implies(accepted(T, P2, V2, W2), accepted(T, P, V, W))


ob('T3-monotonicity', 'deny', Implies(And(eval_def(D0, P, V, W), eval_def(D0, P2, V2, W2)), mono(D0)))
ob('T3-monotonicity', 'gate', Implies(And(refines(), eval_def(GATE, P, V, W), eval_def(GATE, P2, V2, W2), mono(k)), mono(GATE)))
ob('T3-monotonicity', 'guard', Implies(And(refines(), eval_def(GUARD, P, V, W), eval_def(GUARD, P2, V2, W2), mono(k)), mono(GUARD)))
ob('T3-monotonicity', 'switch', Implies(And(refines(), eval_def(SWITCH, P, V, W), eval_def(SWITCH, P2, V2, W2), mono(k1), mono(k2)), mono(SWITCH)))

# ---- T4 routes: an acceptance names a guard that accepted (no other way to accept: default deny).
routeF = Function('routes', H, ArraySort(IntSort(), BoolSort()))


def route_ok(T):
    return Implies(evalF(T, P, V, W) == Out.accepted(t), And(Select(routeF(T), t), Select(V, t) == acc))


def routes_def(T):
    decl = T.decl()
    a = T.children()
    if T.num_args() == 0:
        i = Int('i!rnone')
        return ForAll(i, Not(Select(routeF(T), i)), patterns=[Select(routeF(T), i)])
    if decl == H.gate:
        return routeF(T) == routeF(a[5])
    if decl == H.guard:
        return routeF(T) == Store(routeF(a[3]), a[0], True)
    i = Int('i!rt')
    return ForAll(i, Select(routeF(T), i) == Or(Select(routeF(a[1]), i), Select(routeF(a[2]), i)), patterns=[Select(routeF(T), i)])


ob('T4-routes', 'deny', Implies(And(eval_def(D0, P, V, W), routes_def(D0)), route_ok(D0)))
ob('T4-routes', 'gate', Implies(And(eval_def(GATE, P, V, W), routes_def(GATE), route_ok(k)), route_ok(GATE)))
ob('T4-routes', 'guard', Implies(And(eval_def(GUARD, P, V, W), routes_def(GUARD), route_ok(k)), route_ok(GUARD)))
ob('T4-routes', 'switch', Implies(And(eval_def(SWITCH, P, V, W), routes_def(SWITCH), route_ok(k1), route_ok(k2)), route_ok(SWITCH)))

# ---- T5 prefix locality: replacing what follows guard n leaves routes not reached through n unchanged.
graftF = Function('graft', H, IntSort(), H, H)
throughF = Function('through', H, Pa, Va, Wa, IntSort(), BoolSort())
n = Int('n')


def graft_def(T):
    decl = T.decl()
    a = T.children()
    if T.num_args() == 0:
        return graftF(T, n, K_) == T
    if decl == H.gate:
        return graftF(T, n, K_) == H.gate(a[0], a[1], a[2], a[3], a[4], graftF(a[5], n, K_))
    if decl == H.guard:
        return graftF(T, n, K_) == H.guard(a[0], a[1], a[2], If(a[0] == n, K_, graftF(a[3], n, K_)))
    return graftF(T, n, K_) == H.switch(a[0], graftF(a[1], n, K_), graftF(a[2], n, K_))


def through_def(T):
    """Did this proposal escalate past guard n?"""
    decl = T.decl()
    a = T.children()
    if T.num_args() == 0:
        return throughF(T, P, V, W, n) == False
    if decl == H.gate:
        return throughF(T, P, V, W, n) == And(Select(P, a[0]), throughF(a[5], P, V, W, n))
    if decl == H.guard:
        return throughF(T, P, V, W, n) == And(Select(V, a[0]) == esc, Or(a[0] == n, throughF(a[3], P, V, W, n)))
    return throughF(T, P, V, W, n) == If(Select(W, a[0]), throughF(a[1], P, V, W, n), throughF(a[2], P, V, W, n))


def local(T):
    return Implies(Not(throughF(T, P, V, W, n)), evalF(graftF(T, n, K_), P, V, W) == evalF(T, P, V, W))


def graft_step(T, gr):
    return And(graft_def(T), through_def(T), eval_def(T, P, V, W), eval_def(gr, P, V, W))


ob('T5-prefix-locality', 'deny', Implies(graft_step(D0, D0), local(D0)))
Ggate = H.gate(g, phi, l, om, dd, graftF(k, n, K_))
Gguard = H.guard(g, l, om, If(g == n, K_, graftF(k, n, K_)))
Gswitch = H.switch(g, graftF(k1, n, K_), graftF(k2, n, K_))
ob('T5-prefix-locality', 'gate', Implies(And(graft_step(GATE, Ggate), local(k)), local(GATE)))
ob('T5-prefix-locality', 'guard', Implies(And(graft_step(GUARD, Gguard), local(k)), local(GUARD)))
ob('T5-prefix-locality', 'switch', Implies(And(graft_step(SWITCH, Gswitch), local(k1), local(k2)), local(SWITCH)))

# ---- T6 non-interference: stages are functions of their views; equal views give equal decisions.
Prop = DeclareSort('Prop')
View = DeclareSort('View')
x1, x2 = Consts('x1 x2', Prop)
vw = Function('vw', IntSort(), Prop, View)
pf = Function('pf', IntSort(), View, BoolSort())
vf = Function('vf', IntSort(), View, Vd)
wf_ = Function('wfn', IntSort(), View, BoolSort())
evalx = Function('evalx', H, Prop, Out)


def evalx_def(T, x):
    decl = T.decl()
    a = T.children()
    if T.num_args() == 0:
        return evalx(T, x) == Out.denied
    if decl == H.gate:
        return evalx(T, x) == If(pf(a[0], vw(a[0], x)), evalx(a[5], x), Out.denied)
    if decl == H.guard:
        v = vf(a[0], vw(a[0], x))
        return evalx(T, x) == If(v == acc, Out.accepted(a[0]), If(v == esc, evalx(a[3], x), Out.denied))
    return evalx(T, x) == If(wf_(a[0], vw(a[0], x)), evalx(a[1], x), evalx(a[2], x))


def agree(T):
    i = Int('i!agree')
    return ForAll(i, Implies(Select(idsF(T), i), vw(i, x1) == vw(i, x2)), patterns=[Select(idsF(T), i)])


def noninterference(T):
    return Implies(agree(T), evalx(T, x1) == evalx(T, x2))


def ni(T):
    return And(evalx_def(T, x1), evalx_def(T, x2), ids_def(T))


ob('T6-noninterference', 'deny', Implies(ni(D0), noninterference(D0)))
ob('T6-noninterference', 'gate', Implies(And(ni(GATE), noninterference(k)), noninterference(GATE)))
ob('T6-noninterference', 'guard', Implies(And(ni(GUARD), noninterference(k)), noninterference(GUARD)))
ob('T6-noninterference', 'switch', Implies(And(ni(SWITCH), noninterference(k1), noninterference(k2)), noninterference(SWITCH)))

# ---- T7 cost: a decision visits at most depth(H) stages (requires depth(H) >= 0 by induction).
def cost(T):
    return And(stepsF(T, P, V, W) <= depthF(T), depthF(T) >= 0, stepsF(T, P, V, W) >= 0)


def cd(T):
    return And(steps_def(T, P, V, W), depth_def(T))


ob('T7-decision-cost', 'deny', Implies(cd(D0), cost(D0)))
ob('T7-decision-cost', 'gate', Implies(And(cd(GATE), cost(k)), cost(GATE)))
ob('T7-decision-cost', 'guard', Implies(And(cd(GUARD), cost(k)), cost(GUARD)))
ob('T7-decision-cost', 'switch', Implies(And(cd(SWITCH), cost(k1), cost(k2)), cost(SWITCH)))

# ---- T8 budget: over any trace, a gate that accepts only within the limit keeps the spend in [0, L].
Tr = Datatype('Trace')
Tr.declare('nil')
Tr.declare('cons', ('sel_head', RealSort()), ('sel_tail', Tr))
Trace = Tr.create()
spent = Function('spentAfter', Trace, RealSort(), RealSort())
L, s0, cost_ = Reals('L s0 cost_')
tl = Const('tl', Trace)
in_range = lambda x: And(x >= 0, x <= L)
def budget(tr, start):
    return Implies(in_range(start), in_range(spent(tr, start)))
ob('T8-budget', 'nil', Implies(spent(Trace.nil, s0) == s0, budget(Trace.nil, s0)))
next_s = If(And(cost_ >= 0, s0 + cost_ <= L), s0 + cost_, s0)
ob('T8-budget', 'cons', Implies(And(spent(Trace.cons(cost_, tl), s0) == spent(tl, next_s), budget(tl, next_s)), budget(Trace.cons(cost_, tl), s0)))

# ---- T9 taint: labels only grow along derivations, so secrecy cannot be laundered.
Lb = DeclareSort('Lb')
SetLb = ArraySort(Lb, BoolSort())
Dv = Datatype('Der')
Dv.declare('leaf', ('sel_own', SetLb))
Dv.declare('derive', ('sel_dn', SetLb), ('sel_left', Dv), ('sel_right', Dv))
Der = Dv.create()
lab = Function('label', Der, SetLb)
has = Function('hasLeaf', Der, SetLb, BoolSort())
m = Const('m', SetLb)
d1, d2 = Consts('d1 d2', Der)
own = Const('own', SetLb)
sensitive = Const('sensitive', Lb)


def lab_def(T):
    if T.decl() == Der.leaf:
        return lab(T) == T.arg(0)
    i = Const('i!lab', Lb)
    return ForAll(i, Select(lab(T), i) == Or(Select(T.arg(0), i), Select(lab(T.arg(1)), i), Select(lab(T.arg(2)), i)), patterns=[Select(lab(T), i)])


def has_def(T):
    if T.decl() == Der.leaf:
        return has(T, m) == (T.arg(0) == m)
    return has(T, m) == Or(has(T.arg(1), m), has(T.arg(2), m))


def taint(T):
    return Implies(And(has(T, m), Select(m, sensitive)), Select(lab(T), sensitive))


ob('T9-taint', 'leaf', Implies(And(lab_def(Der.leaf(own)), has_def(Der.leaf(own))), taint(Der.leaf(own))))
Dn = Der.derive(own, d1, d2)
ob('T9-taint', 'derive', Implies(And(lab_def(Dn), has_def(Dn), taint(d1), taint(d2)), taint(Dn)))


# ---- T10 meet: the composition condition is antitone in A and in the evidence, and preserved by
# intersection, so the condition over all paths of a DAG holds iff it holds at the meet.
Ameet, A2, e2 = Consts('Ameet A2 e2', SetOb)
omeet = Const('o!meet', Ob)
MEET = ForAll(omeet, Select(Ameet, omeet) == And(Select(A, omeet), Select(A2, omeet)))
ob('T10-meet', 'antitone', Implies(And(sub(A, A2), sub(e_, e2), locally_ok(l, e_, A)), locally_ok(l, e2, A2)))
ob('T10-meet', 'preserved', Implies(And(MEET, locally_ok(l, e_, A), locally_ok(l, e_, A2)), locally_ok(l, e_, Ameet)))

# ---- T11 transitive reasoning is strictly weaker: it accepts everything check accepts, and more.
B2 = Const('B2', SetOb)
def weaker(T, A_=A, B_=B, A2_=A2, B2_=B2):
    return Implies(And(checkF(T, A_, B_), sub(A_, A2_), sub(B_, B2_)), checkT(T, A2_, B2_))


EV2 = unionF(om, B2)
ob('T11-transitive', 'deny', Implies(transitive_def(D0, A2, B2), weaker(D0)))
ob('T11-transitive', 'gate', Implies(And(check_def(GATE, A, B), transitive_def(GATE, A2, B2),
    weaker(k, AP, BP, Store(A2, phi, True), unionF(EV2, dd)), weaker(k, A, B, Store(A2, phi, True), unionF(EV2, dd)), weaker(k, A, B, A2, EV2)), weaker(GATE)))
ob('T11-transitive', 'guard', Implies(And(check_def(GUARD, A, B), transitive_def(GUARD, A2, B2), weaker(k, A, B, A2, EV2)), weaker(GUARD)))
ob('T11-transitive', 'switch', Implies(And(check_def(SWITCH, A, B), transitive_def(SWITCH, A2, B2), weaker(k1), weaker(k2)), weaker(SWITCH)))
# A separating instance: evidence for o at the first guard, needed by the second.
l1, l2 = Consts('l1 l2', Lay)
om1, om2 = Consts('om1 om2', SetOb)
INNER = H.guard(Int('n2'), l2, om2, H.deny)
OUTER = H.guard(Int('n1'), l1, om1, INNER)
ob('T11-transitive', 'separation', Implies(And(
    Select(G, q), Not(Select(A, q)), Select(req(l2), o), Select(om1, o), Not(Select(om2, o)), Not(Select(B, o)),
    sub(req(l1), om1), covered(A, scp(l1)), covered(A, scp(l2)), sub(req(l2), om1),
    check_def(OUTER, A, B), check_def(INNER, A, B), check_def(H.deny, A, B),
    transitive_def(OUTER, A, B), transitive_def(INNER, A, unionF(om1, B)), transitive_def(H.deny, A, unionF(om2, unionF(om1, B)))),
    And(Not(checkF(OUTER, A, B)), checkT(OUTER, A, B))))

# ---- T12 order: hoisting a gate over a guard never loses acceptance by the check; deterministic gates commute.
GATE2 = H.gate(g, phi, l, om, dd, H.guard(n, l1, om1, k))
GUARD2 = H.guard(n, l1, om1, GATE)
ob('T12-order', 'hoist', Implies(And(check_def(GUARD2, A, B), check_def(GATE, A, B), check_def(GATE2, A, B),
                                      check_def(H.guard(n, l1, om1, k), AP, BP), check_def(H.guard(n, l1, om1, k), A, B), checkF(GUARD2, A, B)),
                                  checkF(GATE2, A, B)))
phi2 = Const('phi2', Ob)
g2 = Int('g2')
EMPTY = lambda x: ForAll(omeet, Not(Select(x, omeet)))
Inner1 = H.gate(g2, phi2, l1, om1, dd, k)
Inner2 = H.gate(g, phi, l, om, dd, k)
Outer1 = H.gate(g, phi, l, om, dd, Inner1)
Outer2 = H.gate(g2, phi2, l1, om1, dd, Inner2)
ob('T12-order', 'commute', Implies(And(EMPTY(req(l)), EMPTY(req(l1)), EMPTY(dd), unionF(B, dd) == B,
    check_def(Outer1, A, B), check_def(Outer2, A, B), check_def(Inner1, Store(A, phi, True), B), check_def(Inner2, Store(A, phi2, True), B)),
    checkF(Outer1, A, B) == checkF(Outer2, A, B)))


def solve_z3(formula, timeout_ms=120000):
    s = Solver()
    s.set('timeout', timeout_ms)
    s.add(Not(formula))
    start = time.perf_counter()
    answer = s.check()
    return str(answer), time.perf_counter() - start, s.to_smt2()


def unfolded(formula):
    """Formula with union replaced by its definition, which leaves no axiom for the model finder."""
    from z3 import Lambda, Var, substitute_funs
    o_ = Const('o!def', Ob)
    return substitute_funs(formula, (unionF, Lambda([o_], Or(Select(Var(2, SetOb), o_), Select(Var(1, SetOb), o_)))))


def hypotheses_satisfiable(formula, timeout_ms=8000):
    """Guard against vacuous obligations: the premises of an implication must be consistent."""
    if is_quantifier(formula.arg(0)):  # no premise beyond the union axiom
        return 'n/a'
    s = Solver()
    s.set('timeout', timeout_ms)
    s.add(unfolded(formula.arg(0).arg(1)))
    return str(s.check())


def refuted(formula, timeout_ms=6000):
    """Is the obligation false: is there a model of its premises and the negated conclusion?"""
    s = Solver()
    s.set('timeout', timeout_ms)
    if not is_quantifier(formula.arg(0)):
        s.add(unfolded(formula.arg(0).arg(1)))
    s.add(unfolded(Not(formula.arg(1))))
    return str(s.check())


def solve_cvc5(smt2: str, timeout_ms=120000):
    import cvc5
    solver = cvc5.Solver()
    solver.setOption('tlimit-per', str(timeout_ms))
    solver.setOption('produce-models', 'false')
    solver.setOption('enum-inst', 'true')
    solver.setLogic('ALL')
    parser = cvc5.InputParser(solver)
    parser.setStringInput(cvc5.InputLanguage.SMT_LIB_2_6, smt2.replace('(set-info :status unknown)', ''), 'obligation')
    manager = parser.getSymbolManager()
    start, answer = time.perf_counter(), 'none'
    while True:
        command = parser.nextCommand()
        if command.isNull():
            break
        text = str(command)
        if text.startswith('(check-sat'):
            answer = str(solver.checkSat())
        else:
            command.invoke(solver, manager)
    return answer, time.perf_counter() - start


def main():
    if '--z3-only' in sys.argv:  # used by mutate.py
        answers = [(theorem, case, refuted(formula)) for theorem, case, formula in OBLIGATIONS if solve_z3(formula, 4000)[0] != 'unsat']
        print(json.dumps([list(x) for x in answers]))
        return
    rows, timings = [], []
    for theorem, case, formula in OBLIGATIONS:
        z3_answer, z3_time, smt2 = solve_z3(formula)
        try:
            cvc5_answer, cvc5_time = solve_cvc5(smt2)
        except Exception as exc:
            cvc5_answer, cvc5_time = 'error: ' + str(exc)[:80], 0.0
        consistent = hypotheses_satisfiable(formula)
        rows.append({'theorem': theorem, 'case': case, 'z3': z3_answer, 'cvc5': cvc5_answer, 'hypotheses': consistent})
        timings.append({'theorem': theorem, 'case': case, 'z3_seconds': round(z3_time, 4), 'cvc5_seconds': round(cvc5_time, 4)})
        print(f'{theorem:22s} {case:18s} z3={z3_answer:8s} {z3_time:7.3f}s  cvc5={cvc5_answer[:40]:12s} {cvc5_time:7.3f}s  hyp={consistent}', flush=True)
    import cvc5
    out = ROOT / 'results/v2/proofs.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({'z3_version': get_version_string(), 'cvc5_version': cvc5.__version__ if hasattr(cvc5, '__version__') else 'unknown',
                               'obligations': rows}, indent=1) + '\n', encoding='utf-8')
    (ROOT / 'results/v2/timing').mkdir(exist_ok=True)
    (ROOT / 'results/v2/timing/proofs.json').write_text(json.dumps(timings, indent=1) + '\n', encoding='utf-8')
    failed = [r for r in rows if r['z3'] != 'unsat' or r['cvc5'] != 'unsat']
    vacuous = [r for r in rows if r['hypotheses'] == 'unsat']
    print(len(rows), 'obligations;', sum(r['z3'] == 'unsat' for r in rows), 'proved by z3;', sum(r['cvc5'] == 'unsat' for r in rows), 'proved by cvc5;',
          len(vacuous), 'vacuous;', sum(r['hypotheses'] == 'sat' for r in rows), 'premises shown satisfiable')
    sys.exit(1 if failed or vacuous else 0)


if __name__ == '__main__':
    main()
