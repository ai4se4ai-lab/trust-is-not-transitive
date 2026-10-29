# Blockers and feasibility limits

Initial audit: GNU make is not on PATH. A portable Python task runner will back
the Makefile, with equivalent commands documented for Windows.

No API credentials, GPU service or model/dataset license acceptance has been
established. Do not infer their availability or expose environment secrets.
Probe local capability and dataset licenses before deciding experimental scope.
No external publication, DOI registration or remote release is implied by a local
artifact build. Record unavailable release steps explicitly.

## Phase 4 capability audit

- Hardware: RTX 2050, 4096 MiB VRAM, driver 573.44; installed torch 2.9.1+cpu
  reports CUDA unavailable. A GPU exists; it would be false to report "no GPU".
- Known OpenAI/Anthropic/HF credential variables are absent (presence only
  checked; no secret values printed). No API-based agent experiment is possible
  with the established setup. No model access terms were accepted on the user's behalf.
- Protect AI small prompt-injection model card was opened and is gated behind
  authenticated access conditions. Prompt Guard/open-weight target evaluation
  is not established. Use explicitly labeled surrogates; generalization remains open.
- Docker binary is installed but Linux engine pipe is absent; image build and
  container execution cannot currently be validated. In-memory tools are the
  feasible isolated substitute.
- External benchmark code licenses were opened where available; their code
  license is not a blanket license for every upstream dataset. R-Judge repo
  LICENSE API returned 404; website states CC BY-NC-SA. No external data used.
