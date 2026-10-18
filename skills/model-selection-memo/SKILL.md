---
name: model-selection-memo
description: Use to decide which model/approach a task should use and to defend it — prompt vs RAG vs fine-tune, and proprietary API vs managed-cloud vs self-hosted open-weight vs on-device. Produces a Model Selection Decision Memo with a weighted scorecard, a measured prompted baseline, and a cost model at three scales. Trigger on "which model should we use", "build vs buy vs fine-tune", "should we fine-tune", "pick a model for <task>", or after a scoping/architecture doc names a component that needs a model.
---

# Model Selection Decision Memo

Turn "which model?" into a defensible, written decision a CISO, a CFO, and a tech lead can each read.
Consumes a `scoping-document` / `system-architecture` component if one exists; produces
`docs/model-selection-<component>.md`.

## 1. Score the candidates on five dimensions (weighted for THIS task)
Not a fixed weighting — weight the dimensions for the task at hand, and show the weights.
- **Task-capability fit** — tested on a *small custom eval set* for this task, never a leaderboard rank.
- **Latency profile** — interactive vs batch; and *which* latency (time-to-first-token for streaming UX,
  total generation time for batch). Judge on P95.
- **Cost at production scale** — modelled at real volume, not pilot volume (see §4).
- **Data-privacy posture** — where the data is allowed to travel (API egress vs in-tenancy vs on-prem).
- **Operational complexity** — API (near-zero ops) → managed cloud → self-host → fine-tune, each a step
  up in ownership burden (GPUs, retraining, prompt upkeep).
"Thinking"/extended-reasoning is a per-task *dial* that trades capability vs latency vs cost — size it
against the eval set, don't treat it as a fixed scorecard row.

## 2. Prompt engineering is architecture — measure the baseline first
A system prompt is a versioned artifact: role, *explicit* constraints, an exact output schema, 2–3
curated few-shot examples; a logged version id per call; a behavioural test suite (format compliance,
edge cases, adversarial); staged rollout + rollback.
**Measure the best prompted baseline before anything heavier.** Record its numbers — format-compliance
*and* accuracy are separate bars (a reply can be well-formed and wrong), each with a confidence interval,
because a small eval set read as a point estimate lies. You cannot credit RAG or fine-tuning with a win
you never measured a baseline against.
**If you did not run the baseline in this session, write `NOT MEASURED` and the exact command to run it —
never invent a number.** A fabricated baseline is worse than none: it manufactures a ceiling the whole
decision then leans on.

## 3. Resolve the approach in order
- **Knowledge gap → RAG**, not fine-tuning. Fine-tuning is the *wrong tool* for knowledge that changes
  or must be cited — RAG retrieves it fresh and attributably. (Continued pretraining/SFT *can* inject
  facts, but it bakes them in statically and un-citably; that is rarely what a knowledge gap needs.)
  Fine-tuning's real job is shifting *style, format, or a narrow bounded behaviour*.
- **Consider fine-tuning only after a measured prompting ceiling.** Real-ceiling signals: persistent
  format violations, uncorrectable domain vocabulary, tone/safety misses standard guardrails don't
  catch, or an input space too large/diverse for prompting. Genuine fine-tune cases: strict output
  format, domain vocabulary, a narrow bounded task, consistent refusal/safety behaviour. Data: small
  curated sets (LoRA/QLoRA) from real production corrections / synthetic (verify a sample) / distillation
  from a teacher (check the provider's terms of service first). Always a held-out eval set + a plan for
  base-model deprecation.

## 4. Build vs buy vs self-host vs on-device + cost model
Four branches, each with its real trade: proprietary API (fastest, least control, data leaves your
infra); managed cloud (frontier/open models inside your own tenancy — the privacy/procurement middle
path); self-hosted open-weight (data sovereignty, deepest customisation, better economics above a volume
crossover); on-device/edge (no network dependency, narrowest capability ceiling).
- **Compare self-host against the cheapest API tier that passes your eval — not a mid-tier straw man.** A
  low-capability task uses the *cheap* tier, and against the cheap tier the self-host crossover often sits
  *above one box's capacity*, i.e. **there is no economic crossover**: self-host there is a control/privacy/
  latency decision, never a cost one. Compute the crossover per tier; say when it does not exist.
- Add a **hybrid router**: route routine traffic to a cheap tier, reserve the frontier model for complex
  requests — but cost the router *and the misroute* (every request pays the router; a misrouted request is
  re-done on the frontier tier, paid twice). A saving quoted without those two terms is fiction; the
  routable fraction and misroute rate must be *measured* on real traffic.
- **Lock-in isn't the API shape — it's your prompts, your eval set, and your fine-tunes.** A thin adapter
  so a provider swaps *by config not code* is worth having, but the real portability is a **provider-agnostic
  eval suite** you can re-run against any candidate. Don't build an elaborate abstraction and call it done.
- **Model cost at three scales — launch, 10×, projected peak — and stress-test the assumptions** (token
  sizes, cache-hit decay, usage concentration). Never extrapolate linearly from pilot numbers. State
  every assumption; a cost model is only as honest as its stated assumptions. Keep them as named constants.
- **Regulated data is a contract question, not a ban.** "Public API out regardless" is wrong: HIPAA permits
  PHI under a **BAA**, GDPR under a **DPA**, and vendors sell zero-retention / regional / in-tenancy
  endpoints. Resolve regulated + frontier to a **frontier model inside your own tenancy** (managed-cloud),
  or a public API under a signed BAA/DPA. State *where the data may travel and under what contract*.

## 5. The memo
Write `docs/model-selection-<component>.md` with: task definition (and whether it's a retrieval task);
candidate shortlist + the weighted scorecard; the *measured* prompted-baseline result; the fine-tuning
determination; the build/buy/self-host/on-device determination with the three-scale cost model and its
assumptions; a recommendation whose reasoning is addressable to CISO/CFO/tech-lead; an evaluation plan
(held-out set, human panel if domain-sensitive); and a maintenance/re-evaluation cadence.

## 6. When code is scaffolded
If you produce code (a router, an eval harness, a prompt-baseline measurement), it ships with
**meaningful tests** (each asserts a real behaviour + its reason, and can fail — e.g. the router sends a
flagged-complex request to the frontier tier; the cost model's crossover point is where self-host
undercuts API; the baseline harness rejects a format violation) and never a test that only moves
coverage. Keep the cost model's assumptions as named constants a reader can change.

## Anti-patterns to flag
Fine-tuning to inject knowledge that changes or must be cited (use RAG); benchmark-shopping (leaderboard
rank instead of a task eval); crediting fine-tuning without a measured prompted baseline — or *inventing*
that baseline number; comparing self-host against a mid-tier price when the task only needs the cheap tier;
"high volume → self-host" for a cheap-tier task (often no crossover exists); "regulated → no public API
regardless" (it's a BAA/DPA question); a hybrid-routing saving quoted without router + misroute cost; an
elaborate provider abstraction with no portable eval suite; ignoring the re-tune cost when a base model is
deprecated; linear cost extrapolation from pilot volume.

## Output and handoff
Write the memo, then a 3-line summary: the recommended approach + tier, the single biggest cost or
privacy risk, and the next step (usually `integration-architecture`, then `evaluation-design`).
