"""The guardrail-hierarchy calculus, as first-order definitions for SMT proofs.

Terms: deny | gate(id, phi, layer, Omega, D, k) | guard(id, layer, Omega, k) | switch(id, a, b).
A gate's pass establishes phi and provides the facts D if its layer's obligations hold; a
deterministic gate has none. A provided fact is an obligation that holds on every later
invocation of the run. A guard provides nothing: a verdict carries no evidence forward.
A model gives each node id its behaviour on one fixed proposal: P (gate passes),
V (guard verdict), W (switch branch), E (obligations that hold on this invocation),
and S (the set of goals the proposal satisfies). Model components are unconstrained
apart from the contract premises in `wf`, so a guard may be arbitrarily adversarial.
`wf` also threads T, the facts provided so far on this run.

Every recursive function is defined by one equation per constructor, in `UNFOLD`.
A structural induction is the base and step obligations, each a closed formula
stating that the step follows from its induction hypotheses and those equations.
Definitions are primitive recursive, hence conservative. The induction schema is
the one for the inductive datatype `H`; it is applied by this script, not by the solver.
"""
from __future__ import annotations
import os
from z3 import (And, Array, ArraySort, BoolSort, BoolVal, Const, Consts, Datatype, DeclareSort, ForAll, Function, If, Implies,
                Int, IntSort, Ints, K, Not, Or, Select, Store)

Ob = DeclareSort('Ob')
Lay = DeclareSort('Lay')
SetOb = ArraySort(Ob, BoolSort())

VerdictD = Datatype('Verdict')
for name in ['acc', 'blk', 'esc']:
    VerdictD.declare(name)
Vd = VerdictD.create()
acc, blk, esc = Vd.acc, Vd.blk, Vd.esc

OutD = Datatype('Out')
OutD.declare('denied')
OutD.declare('accepted', ('sel_route', IntSort()))
Out = OutD.create()

HD = Datatype('H')
HD.declare('deny')
HD.declare('gate', ('sel_gid', IntSort()), ('sel_phi', Ob), ('sel_gl', Lay), ('sel_gom', SetOb), ('sel_gd', SetOb), ('sel_gk', HD))
HD.declare('guard', ('sel_uid', IntSort()), ('sel_lay', Lay), ('sel_om', SetOb), ('sel_uk', HD))
HD.declare('switch', ('sel_sid', IntSort()), ('sel_sa', HD), ('sel_sb', HD))
H = HD.create()

Pa, Va, Wa = ArraySort(IntSort(), BoolSort()), ArraySort(IntSort(), Vd), ArraySort(IntSort(), BoolSort())
Ea = ArraySort(IntSort(), SetOb)
IdSet = ArraySort(IntSort(), BoolSort())

G = Const('G', SetOb)                         # goals of the hierarchy
req = Function('req', Lay, SetOb)             # O_l, the layer's assumption
scp = Function('scp', Lay, SetOb)             # the goals the layer's contract covers

evalF = Function('eval', H, Pa, Va, Wa, Out)
wfF = Function('wf', H, Pa, Va, Wa, Ea, SetOb, SetOb, BoolSort())
checkF = Function('check', H, SetOb, SetOb, BoolSort())
checkT = Function('checkTransitive', H, SetOb, SetOb, BoolSort())
unionF = Function('union', SetOb, SetOb, SetOb)
idsF = Function('ids', H, IdSet)
uniqF = Function('uniq', H, BoolSort())
stepsF = Function('steps', H, Pa, Va, Wa, IntSort())
depthF = Function('depth', H, IntSort())


def sub(a, b):
    o = Const('o!sub', Ob)
    return ForAll(o, Implies(Select(a, o), Select(b, o)), patterns=[Select(a, o)])


def covered(a, b):
    """Every goal is in a or in b."""
    o = Const('o!cov', Ob)
    return ForAll(o, Implies(Select(G, o), Or(Select(a, o), Select(b, o))), patterns=[Select(G, o)])


def union_axiom():
    """The defining property of union. A premise of every obligation that mentions it."""
    x, y = Const('x!un', SetOb), Const('y!un', SetOb)
    o = Const('o!un', Ob)
    return ForAll([x, y, o], Select(unionF(x, y), o) == Or(Select(x, o), Select(y, o)), patterns=[Select(unionF(x, y), o)])


MUTANT: str | None = os.environ.get('TINT_MUTANT')  # set only by mutate.py, to show the proofs are not vacuous


def locally_ok(l, e, A):
    """The per-guard condition: open goals need the obligations (supplied evidence e) and the scope."""
    if MUTANT == 'check-ignores-obligations':
        return Or(sub(G, A), covered(A, scp(l)))
    if MUTANT == 'check-ignores-scope':
        return Or(sub(G, A), sub(req(l), e))
    if MUTANT == 'check-always-needs-obligations':
        return And(sub(req(l), e), covered(A, scp(l)))
    return Or(sub(G, A), And(sub(req(l), e), covered(A, scp(l))))


def credit_condition(l, om, B):
    if MUTANT == 'gate-credits-without-obligations':
        return BoolVal(True)
    return sub(req(l), unionF(om, B))


def eval_def(t, P, V, W):
    """Equation for eval at constructor instance t."""
    decl = t.decl()
    a = t.children()
    if t.num_args() == 0:
        return evalF(t, P, V, W) == Out.denied
    if decl == H.gate:
        if MUTANT == 'gate-fails-open':
            return evalF(t, P, V, W) == evalF(a[5], P, V, W)
        return evalF(t, P, V, W) == If(Select(P, a[0]), evalF(a[5], P, V, W), Out.denied)
    if decl == H.guard:
        v = Select(V, a[0])
        if MUTANT == 'block-falls-through':
            return evalF(t, P, V, W) == If(v == acc, Out.accepted(a[0]), evalF(a[3], P, V, W))
        return evalF(t, P, V, W) == If(v == acc, Out.accepted(a[0]), If(v == esc, evalF(a[3], P, V, W), Out.denied))
    return evalF(t, P, V, W) == If(Select(W, a[0]), evalF(a[1], P, V, W), evalF(a[2], P, V, W))


def wf_def(t, P, V, W, E, S, T):
    """Contract and realization premises on the invocations this proposal reaches; T: facts so far."""
    decl = t.decl()
    a = t.children()
    if t.num_args() == 0:
        return wfF(t, P, V, W, E, S, T) == True
    realized = lambda om, e: And(sub(om, e), sub(T, e)) if MUTANT != 'facts-not-realized' else sub(om, e)
    if decl == H.gate:
        g, phi, l, om, dd, k = a
        e = Select(E, g)
        return wfF(t, P, V, W, E, S, T) == Implies(Select(P, g), And(realized(om, e), If(sub(req(l), e),
            And(Select(S, phi), wfF(k, P, V, W, E, S, unionF(T, dd))), wfF(k, P, V, W, E, S, T))))
    if decl == H.guard:
        g, l, om, k = a
        v, e = Select(V, g), Select(E, g)
        if MUTANT == 'contract-ignores-assumption':
            return wfF(t, P, V, W, E, S, T) == And(realized(om, e), Implies(v == acc, sub(scp(l), S)), Implies(v == esc, wfF(k, P, V, W, E, S, T)))
        if MUTANT == 'evidence-not-realized':
            return wfF(t, P, V, W, E, S, T) == And(sub(T, e), Implies(And(v == acc, sub(req(l), e)), sub(scp(l), S)), Implies(v == esc, wfF(k, P, V, W, E, S, T)))
        return wfF(t, P, V, W, E, S, T) == And(realized(om, e), Implies(And(v == acc, sub(req(l), e)), sub(scp(l), S)),
                                               Implies(v == esc, wfF(k, P, V, W, E, S, T)))
    return wfF(t, P, V, W, E, S, T) == If(Select(W, a[0]), wfF(a[1], P, V, W, E, S, T), wfF(a[2], P, V, W, E, S, T))


def check_def(t, A, B):
    """A: goals established on this path. B: facts provided on it. Evidence is never inherited."""
    decl = t.decl()
    a = t.children()
    if t.num_args() == 0:
        return checkF(t, A, B) == True
    if decl == H.gate:
        g, phi, l, om, dd, k = a
        if MUTANT == 'gate-does-not-establish':
            return checkF(t, A, B) == checkF(k, A, B)
        return checkF(t, A, B) == If(credit_condition(l, om, B), checkF(k, Store(A, phi, True), unionF(B, dd)), checkF(k, A, B))
    if decl == H.guard:
        g, l, om, k = a
        if MUTANT == 'evidence-inherited':
            return checkF(t, A, B) == And(locally_ok(l, unionF(om, B), A), checkF(k, A, unionF(B, om)))
        return checkF(t, A, B) == And(locally_ok(l, unionF(om, B), A), checkF(k, A, B))
    if MUTANT == 'switch-checks-one-branch':
        return checkF(t, A, B) == checkF(a[1], A, B)
    return checkF(t, A, B) == And(checkF(a[1], A, B), checkF(a[2], A, B))


def transitive_def(t, A, B):
    """The check under transitive reasoning: evidence supplied at a stage counts at all later ones."""
    decl = t.decl()
    a = t.children()
    if t.num_args() == 0:
        return checkT(t, A, B) == True
    if decl == H.gate:
        g, phi, l, om, dd, k = a
        e = unionF(om, B)
        return checkT(t, A, B) == If(sub(req(l), e), checkT(k, Store(A, phi, True), unionF(e, dd)), checkT(k, A, e))
    if decl == H.guard:
        g, l, om, k = a
        e = unionF(om, B)
        return checkT(t, A, B) == And(locally_ok(l, e, A), checkT(k, A, e))
    return checkT(t, A, B) == And(checkT(a[1], A, B), checkT(a[2], A, B))


def ids_def(t):
    decl = t.decl()
    a = t.children()
    if t.num_args() == 0:
        i = Int('i!none')
        return ForAll(i, Not(Select(idsF(t), i)), patterns=[Select(idsF(t), i)])
    if decl == H.gate:
        return idsF(t) == Store(idsF(a[5]), a[0], True)
    if decl == H.guard:
        return idsF(t) == Store(idsF(a[3]), a[0], True)
    i = Int('i!ids')
    return ForAll(i, Select(idsF(t), i) == Or(i == a[0], Select(idsF(a[1]), i), Select(idsF(a[2]), i)),
                  patterns=[Select(idsF(t), i)])


def uniq_def(t):
    """No node id repeats along any path. Ids may be shared across a switch's branches."""
    decl = t.decl()
    a = t.children()
    if t.num_args() == 0:
        return uniqF(t) == True
    if decl == H.gate:
        return uniqF(t) == (uniqF(a[5]) if MUTANT == 'uniq-allows-repeats' else And(Not(Select(idsF(a[5]), a[0])), uniqF(a[5])))
    if decl == H.guard:
        return uniqF(t) == (uniqF(a[3]) if MUTANT == 'uniq-allows-repeats' else And(Not(Select(idsF(a[3]), a[0])), uniqF(a[3])))
    return uniqF(t) == And(Not(Select(idsF(a[1]), a[0])), Not(Select(idsF(a[2]), a[0])), uniqF(a[1]), uniqF(a[2]))


def steps_def(t, P, V, W):
    decl = t.decl()
    a = t.children()
    if t.num_args() == 0:
        return stepsF(t, P, V, W) == 0
    if decl == H.gate:
        return stepsF(t, P, V, W) == 1 + If(Select(P, a[0]), stepsF(a[5], P, V, W), 0)
    if decl == H.guard:
        return stepsF(t, P, V, W) == 1 + If(Select(V, a[0]) == esc, stepsF(a[3], P, V, W), 0)
    return stepsF(t, P, V, W) == 1 + If(Select(W, a[0]), stepsF(a[1], P, V, W), stepsF(a[2], P, V, W))


def depth_def(t):
    decl = t.decl()
    a = t.children()
    if t.num_args() == 0:
        return depthF(t) == 0
    if decl == H.gate:
        return depthF(t) == 1 + depthF(a[5])
    if decl == H.guard:
        return depthF(t) == 1 + depthF(a[3])
    x, y = depthF(a[1]), depthF(a[2])
    return depthF(t) == 1 + If(x >= y, x, y)
