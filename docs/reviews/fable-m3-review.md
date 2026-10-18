# Fable review — M3 (model selection) — 2026-10-18

Independent critical review (Fable 5.1) of `nb03_model_selection.ipynb` + `model-selection-memo/SKILL.md`.
Record; fixes are in the commit that follows.

## Severe
1. **Cost model compares self-host against the wrong API tier.** A low-capability task uses the *cheap*
   tier (0.0006), not mid (0.004). Against cheap, self-host per-request (0.00050) > cheap-API per-request
   (0.00042) → no crossover below one box's 8M capacity. "High-volume + low-capability → self-host
   economics" is false. Self-host is a privacy/control decision; compare against the cheapest tier that
   passes the eval, and state utilisation/peak-headroom/redundancy assumptions.
2. **No "weighted scorecard".** It's a 7-branch cascade reading 3 of 5 attributes; `latency` is never read
   (swept 144 combos — 0 change); "operational complexity" has no attribute. And `deployment()`'s 1M
   volume threshold disagrees with the model's own 1.43M crossover. Fix: call it a cascade (privacy gate →
   capability → economics via the cost functions → latency picks locus) OR build a real weighted scorecard;
   make latency do something; use the cost functions not a magic constant.
3. **"Regulated → public API out regardless" is a false absolute** (prose/test harden what the code hedges
   as "likely"). HIPAA permits PHI under a BAA; GDPR under a DPA; vendors offer BAA/zero-retention/regional
   endpoints; managed-cloud serves frontier in-tenancy. Teach: where may data travel + under what contract.
   Resolve regulated+frontier → managed-cloud in-tenancy.

## High
4. Baseline over-claims from n=6 (95% LB for 6/6 is 60.7%); gates fine-tuning on *format* while ignoring
   *accuracy*; harder tickets show 8/8 format but 6/8 accuracy; `good_format` counts `{"label":"Billing"}`
   as FMT-BAD (case); no `parse_label` test though the skill promises one. Fix: print CI, add ambiguous
   items so format/accuracy diverge, gate on format OR accuracy, state/relax strictness, test parse_label.
5. Generalisation test asserts a WRONG answer (wake-word detection → "self-host LLM, fine-tune candidate");
   passes only because latency is ignored and there's no on-device branch. Use a task whose correct answer
   the rules produce; add on-device branch; prefer property tests (regulated never→unconditional API;
   knowledge_gap never→fine-tune).

## Medium
6. Tests that can't fail / test prose: routing tautology; regulated test string-matches wording. Keep the
   crossover test (has teeth). Return structured Decision objects, assert on fields.
7. Hybrid routing: three unreconciled API prices (3M = $8,400 vs $31,500); no router cost or misroute
   double-pay. One price table; add misroute_rate + router_cost; show sensitivity.
8. "Fine-tuning changes behaviour not knowledge" as absolute (continued pretraining/SFT do inject facts).
   Reword: wrong tool for knowledge that changes/must be cited → RAG; fine-tune shifts style/format/narrow
   behaviour.
9. Skill: §2 invites fabricating a baseline number (LLM writes the memo) — add "if not run this session,
   write NOT MEASURED + the command; never invent a number"; label cost figures illustrative/dated/sourced;
   §4 crossover may not exist; lock-in abstraction is cargo-cult (real lock-in is prompts/evals → mitigate
   with a portable eval suite); add DPA/BAA path for regulated.

## Low
10. Scorecard task volume (2M) never matches the cost scales (300k/3M/12M); knowledge_gap short-circuits
    RAG without a baseline; a thinking model would blow num_predict=40 → false format ceiling.

## Good
Named-constant cost model + ceil-boxes; the crossover test (has teeth); "measure before fine-tune"; Q3;
skill's "thinking is a dial" and deprecation-plan points.
