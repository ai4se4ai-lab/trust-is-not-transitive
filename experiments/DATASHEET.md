# DevAgent fixture-law datasheet

Purpose: expose routing and contract errors under fully inspectable typed tool
semantics. Data are synthetic, generated locally from authored templates with
seeded sampling. They are not AgentDojo, ASB or evidence of real LLM behavior.
No personal data, real secrets, real production hosts or third-party exploits
are included. `sink.invalid` is a non-resolving example and the interpreter has
no network client. Secret values are conspicuously fake canaries.

Unit: a proposed action with an issue string, monitor-owned provenance and an
authored unsafe label. Families and sample counts are frozen in preregistration.
Labels are ground truth **by construction**, not independent expert annotations;
this can favor features used by the designer. Semantic labels are especially
limited: an implicit unauthorized patch is unsafe because the authored task
oracle says so, although the guard's restricted feature view may not distinguish
it from an authorized patch. This is a designed observability limit.

Calibration/dev/test have separate identifiers; template families overlap in
the iid experiment. Shift uses a family absent from calibration. Seeds are
replications of a known generator, not independent organizations or developers.
Generated raw records are released under CC0-1.0; code is MIT. Source papers and
external datasets retain their own licenses and are not bundled as our data.

Not suitable for measuring production prompt-injection attack success, model
ranking, human utility, usability, or external validity. Publish all failures
and all comparison controls. No external model output was used to create labels.
