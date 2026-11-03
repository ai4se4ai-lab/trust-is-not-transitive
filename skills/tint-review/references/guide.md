# TINT agent integration

TINT checks whether declared guardrail contracts compose to cover every goal on
every accepting route. It does not evaluate a prompt's safety, validate real
guards, execute tools, or issue statistical certificates. A passing verdict is
conditional on the declared contracts, evidence and trusted gate claims.

## Tools and workflow

1. `list_examples`, then `get_example(example_id)` for a complete starting point.
2. Map the user's pipeline to an explicit HSL specification and review the mapping.
3. `check_hierarchy(specification)` with the specification serialized as a JSON string.
4. `explain_finding(specification, finding_index=0)` for a rejection's abstract witness.
5. Propose a repair, disclose new premises, and recheck the revised specification.
6. `necessary_obligations(specification)` on a passing hierarchy tests removal of
   each assumed evidence entry separately; it does not find jointly necessary sets.
7. `compare_hierarchies(specification, revised_specification)` on two passing
   specifications reports conservative structural dependencies. It does not compare
   component code or decide runtime certificate freshness.

Results include package/service versions and a canonical-input SHA-256. The package
version is not a source commit or a proof of implementation identity; pin a commit
when reproducing an analysis. Findings and warnings are separate. An empty graph
can pass because it has no accepting routes; inspect `routes` before interpreting success.

## HSL JSON format

The closed root schema is:

```json
{
  "version": "hsl-1",
  "goals": ["inside_workspace"],
  "obligations": [],
  "layers": [{"name": "finish", "scope": [], "requires": [], "view": "metadata"}],
  "nodes": [
    {"type": "gate", "id": "boundary", "rule": "canonical_path_check", "establishes": "inside_workspace", "next": "accept"},
    {"type": "guard", "id": "accept", "layer": "finish", "evidence": [], "next": null}
  ],
  "entry": "boundary"
}
```

- Goals and obligation names are unique nonempty strings. References must exist.
- Obligations: `{"name":"o","kind":"assumed"}`. Kinds are `assumed`, `checked`,
  `construction`; optional `view` is `metadata`, `raw`, or `structured`.
- Layers: `name`, `scope` (goals covered on acceptance), `requires` (obligations),
  `view` (one of the three views). A declared layer contract is a premise.
- Gates: `type`, `id`, `rule`, `establishes` (goal or null), `next` (ID or null).
  Optional `layer` makes it a conditional veto stage, with optional `evidence`.
  Optional `provides` records obligation facts available downstream after crediting
  the gate. Without `layer`, a gate's correctness is a trusted premise.
- Guards: `type`, `id`, `layer`, `evidence`, `next`. Acceptance ends the decision;
  blocking denies; escalation follows `next`. Evidence on a guard invocation does
  not transfer to the next guard. Adding an obligation name merely declares evidence.
- Switches: `type`, `id`, `condition`, `then`, `otherwise`. Both branches are checked;
  a switch itself establishes no goal. The condition is a trusted routing premise.
- Null successors deny; the graph must be acyclic. Rule and condition strings are
  identifiers, never Python or shell code. They are not executed by this server.

The first example above passes only under the trusted claim that the boundary gate
correctly establishes `inside_workspace`. A real adapter would need canonicalization,
symlink handling, filesystem race handling and complete mediation as appropriate.

## Limits and deployment

The local server speaks stdio, requires no API key, and opens no listening socket.
It reads only its bundled examples/guide; tools take inline data, not file paths.
Analysis runs in a child Python process with a 10-second timeout, at most 128 nodes,
32 goals/layers/obligations each and 128 KiB per specification. A timeout/error is
not a composition rejection and never a passing verdict. Exact analysis with
provided facts can be exponential. These limits bound local use, not public hosting.

This is an advisory tool. An assistant can skip it. Skills are instructions rather
than an enforcement boundary. Production enforcement requires a trusted host that
mediates effects and validates its real contracts. Existing runtime fingerprints
are checked at construction; fixed components remain an engine-lifetime premise.
The verification study does not establish the effectiveness of learned guards.
