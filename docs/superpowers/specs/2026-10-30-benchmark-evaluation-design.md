# Benchmark evaluation of TINT with real open models (Approach A)

Status: draft for user review. Date: 2026-10-30.

## Goal

Replace the scripted test doubles with real open-weight models served by Ollama, and evaluate
TINT inside the standard protocols of AgentDojo and ASB, plus a judge-level study on R-Judge.
Compare against published defenses and learned guards on several axes. Report results whichever
way they come out; this closes hypothesis H7 ("not run") of the paper.

## Scope

In: AgentDojo, ASB, R-Judge adapters; Ollama model serving on Alliance Canada (Nibi) through the
`use-hpc` skill; baselines; paper and tutorial updates.
Out (later sub-projects): AgentHarm (use restriction), RedCode (code-execution risk), ToolEmu,
WildGuard, adaptive-attacker studies.

## 1. Adapters (`src/tint/bench/`)

Each adapter maps a benchmark tool call to TINT's typed action (kind, target, inputs, environment).
- Provenance: user prompt = trusted; tool outputs and third-party content = untrusted (U);
  credentials and account identifiers = secret (S). Unknown data = U and S (fail closed).
- Gate rules phi1 and phi2 are re-instantiated per domain (for example "secret data sent to a
  recipient outside the user's task"). Each adapter lists what it cannot express; the paper already
  states the spec language covers 2 of 5 policy classes.
- The judge receives only the closed structured record (`quarantine`); no benchmark text reaches it.
- Interface: `Adapter.to_action(tool_call, context) -> (Action, labels)`; the benchmark agent loop
  calls `GuardRuntime.evaluate` before each tool execution and treats `block` as a refused call.

## 2. Models

Roles: L2 scorer = small classifier (for example Prompt Guard or Granite Guardian class);
L3 judge = Ollama LLM; the agent under test = Ollama LLM with native tool calling.

Selection criteria (to be elaborated in main.tex):
1. distinct vendor and training lineage, because Propositions 3 and 4 predict that shared blind
   spots make guards fail together;
2. native tool calling in Ollama (AgentDojo needs it);
3. open licence permitting research use;
4. two size tiers that fit one H100 or a MIG slice;
5. prior use in published agent-security work.

Candidate families: Llama, Qwen, Gemma, Mistral, optionally gpt-oss or DeepSeek-R1.
**Unverified:** exact Ollama tags, tool-calling support per tag, and the prior-use claims must be
checked against sources before any appears in the paper. Mixed-family L2/L3 pairings test the
product-versus-minimum prediction.

## 3. Comparison axes

attack success rate; benign utility; utility under attack; cost (tokens, latency, layers used);
certificate coverage on a held-out split; shift robustness (ASB attack variants);
judge accuracy on R-Judge; ablations (raw vs structured view, with/without gate, with/without
certificate); correlated-failure analysis across model families.
Statistics: seeds and bootstrap intervals; paired comparisons; no claims from single runs.

## 4. Baselines

No defense; AgentDojo built-ins (tool filter, spotlighting, repeat prompt, PI detector);
a learned guard alone (Llama Guard or Granite Guardian class); the paper's B5 (exposed judge)
and B7 (provenance only); ASB's published defenses.

## 5. Execution

Install `use-hpc`; scaffold `hpc/`; stages: setup (online: pull models and pinned benchmark
commits from `experiments/benchmark_audit.json` into `$WORK`), calibrate, evaluate
(array: model x benchmark x defense x seed), collect. Ollama is served per stage via the hooks
mechanism (**to verify:** hooks README). Compute nodes may be offline, so later stages run offline.
Smoke run first; nothing large is submitted without user approval. Needs from user: Slurm
account, target GPU type, internet status of compute nodes. The skill cannot run on Windows,
so the cluster side runs over the user's remote connection.

## 6. Paper and tutorial

- Register hypotheses and amendments (PREREGISTRATION.md style) before any full run.
- New evaluation section in `paper/main.tex`, model-selection rationale, updated threats to
  validity, H7 replaced by the real outcome. Tutorial Part 12 and the glossary updated to match.

## Risks

- Mapping benchmark tools onto the typed action may leave most attacks outside what the gate
  can express; then the result is the semantic layers' contribution only, and we report that.
- Weak open judges may make the structured view costly; this is a measured outcome, not a failure.
- AgentDojo or ASB versions drift; pin commits.
- B7 (provenance only) may again match TINT; report it.

## Open items

Slurm account and GPU type; exact model tags; whether compute nodes have internet; compute budget.
