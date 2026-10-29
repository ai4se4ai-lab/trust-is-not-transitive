# Closest work and defensible contribution

The prompt's general novelty claim does not survive the literature search.
Conditional composition is classical assume-guarantee reasoning, and
calibrated cascades already have finite-sample guarantees. The research question
is whether **checking the applicability of those guarantees at every actual
acceptance route**, including the guard's own input provenance and context,
improves auditable enforcement for tool agents. The contribution is an
executable route-certificate discipline joining complete mediation of typed
actions, property-specific trust edges, sanitized guard interfaces, and
selection-aware risk accounting. It is an integration and falsifiable
engineering hypothesis, not discovery of non-transitivity or a new conformal
theorem. A lightweight evaluation can establish implementation feasibility and
expose composition errors, not superiority to state-of-the-art LLM guards.

## Closest five (primary full text opened)

1. **ContrAgent**, [2609.18128](https://arxiv.org/abs/2609.18128),
   Sections 3–5: already specifies assume-guarantee temporal contracts and
   compiles deterministic monitors for online and offline use. Do not claim
   contracts or temporal agent supervision as new. Our narrower target is
   applicability of statistical certificates at heterogeneous acceptance routes.
2. **Three-layer probabilistic A/G position**,
   [2605.18672](https://arxiv.org/abs/2605.18672), Section 3 and Appendix A:
   already composes probabilistic layer guarantees with explicit assumptions.
   Its dimensions are intent, operational validity and dynamics. Our target
   is an executable provenance and routing checker, with measured violations
   of the assumptions; no claim to first probabilistic guardrail composition.
3. **Conformal Arbitrage**, [2506.00911](https://arxiv.org/abs/2506.00911),
   Sections 3–4: already calibrates primary/guardian routing and studies
   optimality within score-gap routers. Our added engineering question is
   whether a guardian's certificate is applicable to its actual input context.
4. **Trust or Escalate**, [2407.18370](https://arxiv.org/abs/2407.18370),
   Section 2 and Appendix A: already supplies provable human-agreement
   guarantees for cascaded selective judges. Human agreement is a different
   oracle than policy safety; neither is evidence of prompt-injection immunity.
5. **AgentSpec**, [2503.18666](https://arxiv.org/abs/2503.18666),
   specification and implementation: already offers runtime triggers,
   predicates and enforcement. Our DSL deliberately implements a small
   AgentSpec-inspired subset and adds interface/trust obligations; it is not
   an official AgentSpec implementation or a comparison against its results.

CaMeL, Fides, RoboGuard and ScenicProver further constrain novelty: provenance
isolation, root-of-trust protection and provenance of compositional evidence
already exist. A convincing TSE extension needs external benchmark evidence
and a comparison to these mechanisms, beyond a synthetic pilot.

## Gap table

Y = directly established in reviewed source; U = unestablished in this review;
S = scoped to a different property/problem; P = proposed, not experimentally
established here. A U is never a claim that a capability is absent.

| Approach | Hierarchy | Formal spec | Deterministic guarantee | Statistical guarantee | Explicit conditioned trust | Cost/latency | Agent traces | Adaptive attacks | Tool |
|---|---|---|---|---|---|---|---|---|---|
| ContrAgent | U | Y | Y | U | Y | Y | Y | U | Y |
| Three-layer A/G position | Y | Y | S | Y | Y | U | U | U | U |
| Conformal Arbitrage | Y | Y | U | Y | S | Y | U | U | Y |
| Trust or Escalate | Y | Y | U | Y | S | Y | U | U | Y |
| AgentSpec | U | Y | Y | U | U | Y | Y | U | Y |
| ProbGuard | U | Y | S | Y | U | Y | Y | U | Y |
| CaMeL / Fides | Y | Y | Y | U | Y | Y | Y | Y | Y |
| LlamaFirewall / empirical classifiers | Y | S | S | U | U | Y | Y | Y | Y |
| RoboGuard | Y | Y | Y | U | Y | Y | Y | Y | Y |
| ScenicProver | Y | Y | Y | Y | Y | S | S | U | Y |
| Classical shielding / runtime assurance | Y | Y | Y | S | Y | Y | S | S | Y |
| TINT proposed route discipline | Y | Y | P | P | Y | P | P | P | P |

No individual checkbox is claimed novel. The testable contribution is the
integration and rejection of particular invalid certification paths. Evidence
for rows is tied to primary sources in `lit_review.csv`; abstract-only cells
should be treated as provisional until full-text extraction is expanded.
