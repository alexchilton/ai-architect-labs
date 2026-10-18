---
name: ai-architect
description: Use to run the WHOLE enterprise-AI architecture process for a project brief, end to end — chain scoping -> architecture -> model selection -> integration -> governance -> evaluation -> production, each stage consuming the last, producing the full artifact set plus a leadership-facing capstone document. Trigger on "architect this project", "design the end-to-end AI system for <brief>", "run the full AI architecture process", "take this idea to a production design", or a project brief that needs more than one stage. Orchestrates the seven stage skills; it does not replace them.
---

# AI Architect — end-to-end orchestrator

Given a project brief, run the seven stages in order, each handing off to the next, and finish with a capstone
document a leadership team can read. This skill **chains** the stage skills; invoke each one in turn, don't
re-implement it.

## The pipeline (invoke each stage skill in order)
Each stage reads the prior stage's doc + its handoff block, and writes `docs/<stage>-<project>.md`.

1. **`scoping-document`** — is this an AI problem at all, which category, what are the gates/disqualifiers.
   → hands off: the chosen capability + its hard constraints.
2. **`system-architecture`** — the pattern(s), the RAG/agent stack with failure modes, security, eval hooks,
   cost/latency budget. → hands off: the component list + the per-component model need.
3. **`model-selection-memo`** — per component: prompt vs RAG vs fine-tune, and API vs managed vs self-host vs
   on-device, with a measured baseline + a cost model. → hands off: the chosen approach + tier per component.
4. **`integration-architecture`** — the gateway/adapter, three-tier output validation, AI NFRs, fallbacks.
   → hands off: the integration contract + the touchpoints that can fail.
5. **`governance-review`** — risk tier -> obligations, guardrail pipeline, tamper-evident audit, OWASP
   inventory (cross-ref `ai_security_labs`, don't duplicate). → hands off: the risk tier + the blocking controls.
6. **`evaluation-design`** — the golden set, three-layer metrics, a per-category CI gate, judge calibration.
   → hands off: the thresholds that gate the release.
7. **`production-readiness`** — capacity in tokens/sec, KV-memory budget, statelessness, streaming timeouts,
   queue-depth autoscale, multi-region, LLMOps. → hands off: the capacity + operational plan.

## The handoff contract
Every stage doc opens with a short block the next stage reads — the *decisions that constrain downstream*, not
a summary:
```
handoff:
  capability: <one line>
  hard_constraints: [residency: EU-only, latency: P95 < 2s, budget: <X>/mo]
  decisions: [pattern: RAG+rerank, model: <per component>, risk_tier: high-risk]
  open_questions: [<what the next stage must resolve or measure>]
```
A downstream stage that contradicts an upstream constraint must say so and **loop back**, not silently override.

## Loop-backs (the pipeline is not strictly one-way)
- Economics don't close in stage 3 → back to stage 2 (simpler pattern / smaller model), or flag the brief as
  infeasible at this budget.
- The eval gate (stage 6) can't be met by the architecture → back to stage 2/3, not "lower the bar".
- Governance (stage 5) forbids a data flow the architecture assumed → back to stage 2.
State the loop-back explicitly; don't paper over a contradiction to keep moving.

## The capstone document
Write `docs/capstone-<project>.md` — leadership-facing (~9–11 pages), **one scenario threaded through every
stage**, each module contributing one section:
- **Executive summary** (non-technical): what, why, the one headline risk, the go/no-go.
- **Problem framing & scope** (stages 1–2): the capability, what's out of scope, the disqualifiers checked.
- **System architecture** (stages 2/4): the pattern, a diagram, the data flow, the integration points.
- **Model strategy & cost** (stage 3): build/buy/fine-tune per component, the three-scale cost model.
- **Governance & security** (stage 5): risk tier + obligations, guardrails, audit, the OWASP posture.
- **Measurement** (stage 6): the golden set, the metrics + numeric thresholds, the CI gate.
- **Operations** (stage 7): scaling, LLMOps, the readiness checklist.
- **Risks & open questions**: honestly, including what is NOT yet measured.

## Discipline carried through every stage (non-negotiable)
- **Numbers, not adjectives**, and **measure before you claim** — if a figure wasn't run, write `NOT MEASURED`
  + the command to get it; never invent a baseline, a cost, or a latency.
- **Constraint cascade, not a weighted-vibe**: privacy/regulatory gates first, then capability, then economics.
- **Fail closed** everywhere a guard or classifier can't parse its input.
- **The model is probabilistic and sits outside the trust boundary**; the deterministic controls are the
  boundary. Diagrams colour-code by kind with a legend (see `system-architecture` §5a).
- **A review pass before sign-off**: re-read each stage's claims against its evidence (the discipline the
  module notebooks apply via a second-model review); a claim that can't be checked with one command is a flag.

## Output and handoff
Produce the seven stage docs + the capstone, then a one-screen summary: the recommendation (go / no-go / go-if),
the single biggest risk, the top unmeasured assumption, and the first thing to build (usually the thinnest
end-to-end slice that exercises the eval gate). Then stop and let a human decide — the orchestrator proposes;
it does not ship.
