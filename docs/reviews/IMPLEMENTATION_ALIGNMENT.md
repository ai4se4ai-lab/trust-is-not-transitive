# Paper-to-implementation alignment review

Reviewed on 2026-11-02 against the active text of `paper/main.tex` and the current working-tree implementation. Commented-out manuscript sections were excluded. The paper and production code were not changed by this review.

## Assessment

The core calculus, composition condition, route-risk calibration and DevAgent walkthrough substantially agree with the implementation. Full alignment is not established: two reproduced implementation defects affect certificate validation or invalidation, and two additional discrepancies require a lifecycle restriction or a more precise algorithm description.

The findings below concern behavior permitted by the public Python API. The ordinary defaults and configurations in the existing tests do not exercise all these cases. Passing the proof goals does not prove the certificate and fingerprint implementation correct; the paper itself identifies those correspondence limits.

## Findings

### 1. High: invalid confidence shares bypass the global confidence budget

**Paper claim:** the engine enforces route confidence allocations and the global confidence budget (`paper/main.tex:1468`, `paper/main.tex:1477`).

**Implementation:** `src/tint/hsl/engine.py:183-195` sums supplied shares and compares each certificate's delta to its route share, but does not first require the shares to be finite, nonnegative probabilities. Individual certificate deltas are validated; allocation values are not.

**Reproduction:** with global `delta=0.05`, shares `{'a': 0.4, 'b': -0.35}` pass construction and permit route `a` to open with a certificate whose failure probability is `0.4`. The sum of the declared shares is approximately `0.05`, while the open certificate has eight times that confidence expenditure. A `NaN` share likewise makes the comparison false and permits a certificate with delta `0.8`.

**Impact:** the advertised confidence budget is not enforced for accepted API inputs. These configurations do not meet the intended probability-share premises of the statistical theorem; this finding does not refute the theorem under valid premises.

**Recommendation:** validate the global delta, risk budget and every supplied share for type, finiteness and probability range before any arithmetic. Require nonnegative allocations, positive shares for certificates that open, and enforce the total over statistical routes. Test negative values, `NaN`, infinities and partially reserved allocations.

### 2. High: direct callable instances can omit slot state from their fingerprints

**Paper claim:** component identities cover reachable instance state (`paper/main.tex:1499`).

**Implementation:** the direct callable-instance branch in `component_digest`, `src/tint/hsl/engine.py:84-90`, hashes the class source and `component.__dict__`. A callable storing its decision parameters only in `__slots__` has no such dictionary. The more complete slot traversal in `_value_digest` is not applied to this direct instance.

**Reproduction:** two instances of the same `SlotGuard` class, one returning `BLOCK` and the other returning `ALLOW`, have equal component digests when the decision parameter is stored only in a slot. Fresh engines built from them consequently have equal route fingerprints. The engine using the accepting guard opens the old blocking guard's certificate and accepts the proposal.

**Impact:** a behavioral change can retain the old certificate even when an engine is rebuilt. An explicit `config` reflecting the slot value can avoid this particular collision, but the implementation accepts these objects without requiring that declaration, contrary to the broad state-coverage wording.

**Recommendation:** include slot state throughout the class hierarchy when hashing direct callable instances, or reject unsupported state representations. Existing slot tests cover a slotted value captured inside a function closure, not a direct slotted callable.

### 3. Medium: certificate freshness is a construction-time check

**Paper claim:** at runtime an open certificate must match the current fingerprint, and changed routes close until recertified (`paper/main.tex:1477`, `paper/main.tex:1501`).

**Implementation:** `Engine.__init__` computes fingerprints once (`src/tint/hsl/engine.py:175`) and selects open certificates. Acceptance checks membership in `self.open`; it does not recompute component identities. Mutable guard instances and hierarchy dictionaries remain reachable after construction.

**Reproduction:** construct and certify an engine containing a mutable guard that blocks; change the guard's decision field in place. Its recomputed component digest differs, but the existing engine keeps the certificate open and accepts using the changed behavior.

**Impact and qualification:** the certified-risk theorem explicitly fixes the configuration. In-place mutation violates that premise. This is therefore a missing enforcement/lifecycle qualification rather than a counterexample to the fixed-configuration theorem. The implementation does not automatically detect such changes in an existing engine.

**Recommendation:** state that component behavior and dependencies must remain fixed for an engine's lifetime, and require reconstruction after changes. Alternatively enforce immutability or invalidate certificates when mutations are detected. The manuscript should distinguish construction-time matching from continuous runtime identity monitoring.

### 4. Medium: default exact exploration has a broader trigger than Algorithm 1

**Paper claim:** Algorithm 1 explores exact states when the first pass reports a failing guard and a reachable gate provides facts (`paper/main.tex:1308`). The implementation section states that the checker implements this algorithm (`paper/main.tex:1643`).

**Implementation:** `src/tint/hsl/__init__.py:395` triggers refinement when provided facts exist and either `witnesses=True` or the first pass finds an obligation/coverage failure. `witnesses=True` is the default, including the engine's constructor call. Refinement also computes precise residual dependencies.

**Reproduction:** a deterministic gate establishes the only goal, provides one fact, and leads to a guard. The first pass succeeds. Nevertheless, default `check(h)` reports `exact_states=2`; `check(h, witnesses=False)` reports `exact_states=0`, with both returning acceptance.

**Impact:** this does not demonstrate an incorrect verdict. It changes when potentially expensive exact exploration runs, so the pseudocode and implementation description are not execution-equivalent.

**Recommendation:** document the additional refinement used for exact diagnostics/residuals, distinguishing decision-only checking from the default report-producing API. Alternatively change the implementation trigger while preserving accurate residual reporting.

## Areas that aligned in this review

- `formal/calculus/core.py` and `reference.py` implement the four decision cases, invocation-local evidence, conditional gate credit, provided facts and unchanged guard continuations described by the paper. Absent gate goals are represented by `None` in the executable reference and HSL; the SMT encoding uses the shared sort described in the mechanization section.
- `usable`, `credited`, `check`, `_refine`, `witness_model` and `necessary` implement the local-evidence rule, separate goal/fact records, exact path-state refinement, constructive countermodels and one-entry-at-a-time necessity analysis. The refinement-trigger qualification above remains relevant.
- Guard acceptance terminates; escalation follows `next`; switches select a branch without adding provided facts; leaving the graph denies. Stage faults and checked-obligation failures are handled conservatively in the inspected paths.
- `gated` propagates goals established by deterministic gates, using intersection at merges. `certify` counts unsafe acceptance at each route over **all** calibration proposals. `binomial_upper` implements the manuscript's beta-quantile expression, including the all-losses case.
- Recomputing the DevAgent report gave routes `n3,n4`, the three stated residual entries, and the same three necessary entries. The exposed variant reports `safe_on_this_text` at `n3` with goal `phi3` and path `g1 g2 g3 n3`. Its generated witness respects the reference contracts and evaluates to acceptance at `n3`.

## Validation and limits

- Full existing test suite: **183 passed**.
- Existing proof obligations: **66 checked in Z3 and 66 in cvc5; every negated goal was unsatisfiable**. These checks were run in memory without rewriting experiment results. They do not independently verify the induction schema or the Python implementation.
- Notation registry, reference audit and empirical-number verification scripts passed. Registry lint is not a semantic consistency proof.
- The four findings were reproduced directly against the current code; see the script below. A passing existing suite does not cover these additional cases.

This review did not rerun the exhaustive multi-million-case experiments, timing experiments, corpus analysis, or statistical coverage simulations. Stationarity, representative labels, true contracts, a trusted host, complete mediation, declared external dependencies and stateless statistical prefixes remain premises; the runtime cannot establish them merely by loading a certificate.

## Reproduction

From the repository root:

```powershell
python docs/reviews/reproduce_alignment_findings.py
```

The script prints the confidence-allocation bypasses, slotted-callable collision, in-place mutation behavior, extra refinement and DevAgent cross-check. It is an audit diagnostic, not a proposed regression suite or a code fix. It does not overwrite result files or alter the paper.

## Resolution (2026-11-02)

The findings above record the state at review time. All four were reproduced before any change.

| Finding | Resolved in | Change |
|---|---|---|
| 1. Invalid confidence shares | code | `_probability` refuses a `delta`, `budget` or share that is not a probability before any arithmetic. Zero shares stay legal and cannot open a route. Shares for routes not yet built stay legal, so confidence can be reserved. |
| 2. Slot state missing from digests | code | `_instance_state` reads slots from member descriptors, for direct callables and nested values, including inherited, string-form and name-mangled slots. Digests of objects without slots are unchanged. |
| 3. Construction-time freshness | paper | The manuscript states that fingerprints are compared at construction, components must stay fixed for an engine's lifetime, and in-place mutation is undetected. The assumptions table has a new row. Behavior is unchanged. |
| 4. Broader refinement trigger | paper | The implementation section separates decision-only checking, which follows Algorithm 1, from default reporting. Behavior is unchanged. |

`tests/test_hsl_oracle.py` gained regression tests, and `reproduce_alignment_findings.py` now prints refusals for finding 1 and the corrected result for finding 2; findings 3 and 4 still print the documented behavior. See `docs/ERRATA.md` for rerun results and Amendment C of `experiments/v2/PROTOCOL.md`.
