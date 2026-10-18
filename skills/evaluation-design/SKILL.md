---
name: evaluation-design
description: Use to design how an AI component is evaluated and to make the evaluation a deploy GATE, not a dashboard — define numeric success/failure thresholds before building, build a golden set with categories, pick the three-layer metrics (L1 component, L2 quality, L3 business outcome), calibrate any LLM-judge against humans, and wire a per-category CI gate with a diagnostic runbook. Trigger on "how do we evaluate this", "set up evals / an eval harness", "what metrics / thresholds", "is it good enough to ship", or after an architecture/integration/governance doc names a component that must be measured. Produces an evaluation plan AND, when built, an eval harness + meaningful tests runnable as a CI gate.
---

# Evaluation Design

Turn "it looks good" into a numeric gate that blocks a bad release. Consumes a `system-architecture` /
`integration-architecture` / `model-selection` component; produces `docs/evaluation-<component>.md`.

## 1. Define "good" — numerically, before you build
Write the thresholds **before the first line of the component**, or you'll draw them around whatever you got.
Numbers, not adjectives: "faithfulness ≥ 0.85", "recall@3 ≥ 0.80", never "high quality". For 5+ representative
cases per category write down *what good looks like* up front. **Set thresholds with the golden-set size in
mind**: at n=6 a 0.85 bar means zero misses; a real golden set is hundreds of cases per category, owned, with
a documented growth process (every production failure becomes a new case).

## 2. The three-layer metric model — and L2 ≠ L3
- **L1 component**: does the piece work? (retrieval recall@k, classifier F1, parse rate). Cheapest; read it
  **per category**, never one aggregate that hides a failing slice.
- **L2 quality**: is the answer good? (faithfulness/groundedness, answer-relevance, exactness). RAGAS /
  DeepEval / an NLI model. Faithful and correct are different axes.
- **L3 business outcome**: is it solving the problem? (containment, straight-through processing, escalation
  rate, conversion). **You can ace L2 and fail L3** — a correct answer that doesn't resolve the user's need.
  L3 is measured against real outcomes (a ticket log / production telemetry joined by a correlation ID), not
  against the model's own answers.
- **Signal hierarchy / conflict rule**: when they disagree, business (L3) outranks quality (L2) outranks
  component (L1) — but a breach at **any** layer blocks.

## 3. An LLM-judge is a ruler you must measure first
Before gating on a model-judged metric, measure its **agreement with human labels** on a set that includes
the **failure modes and the contexts** you'll see in production (a judge can be right on a clean single doc and
wrong on the real multi-doc retrieval). High agreement → automate with spot re-checks; low → a human stays in
the loop. Never treat an uncalibrated judge as ground truth, and the judge **fails closed** (an unparseable
verdict is a fail, not a pass). Re-measure as the model/version changes.

## 4. The eval is a gate, not a report
The harness returns a boolean + named breaches a CI step acts on: **block the candidate from merging on any
breach**, green only when every metric *and every category* meets threshold. When a block is **disputed**,
the honest move is to fix the judge/golden label and re-run — **never lower the threshold after seeing the
result** (that's rationalisation, not evaluation). Add a **canary**: a fixed input with a known-good property,
re-run continuously, so a regression from a new model/prompt is caught before users see it. Track token
baselines and format-compliance as drift monitors.

## 5. Online evaluation
Production is the real test set: sample a stratified slice into a review queue, with an escalation path for
low-confidence or high-stakes cases; join model calls to outcomes via a **correlation ID** so L3 is
measurable; watch drift (canary inputs, format-compliance rate, output-length and token distributions,
similarity-to-baseline).

## 6. The evaluation document
Write `docs/evaluation-<component>.md`: the task definition (what "good" and the failure modes are, with
severity); the three-layer plan (named metric + numeric threshold per layer); the golden-set spec (categories,
owner, growth); the judge-calibration result (agreement + n) if a judge is used; the correlation-ID/data-join
design for L3; the online-eval plan (sampling, review queue, escalation); the drift/efficiency monitors; the
signal hierarchy + conflict rule; the CI gate (steps, blocking thresholds, rollback/merge-block); and a
**diagnostic runbook**: business symptom → which L2 metric broke → likely root cause → action.

## 7. When the harness is scaffolded
Ships with **meaningful tests** (each a real property, able to fail): recall@k reflects whether the gold doc
was retrieved; the gate blocks a per-category breach an aggregate would hide; the gate passes only when every
slice meets threshold; the judge parser fails closed on garbage; a canary catches a regressed format. Never a
coverage-only test. Keep thresholds as named constants.

## Diagram
Draw the eval gate in CI (release candidate + golden set → L1/L2/L3 metrics → per-category threshold gate →
merge / block), with L3 fed by the **ticket log / prod outcomes** (not the golden set) and the judge node
coloured as the probabilistic one. Follow the colour + legend + trust-boundary convention in
`system-architecture` §5a (Mermaid in `.md`; a graphviz PNG in a notebook).

## Anti-patterns to flag
Eval as a status dashboard, not a blocking gate; thresholds set after seeing results; vibes/spot-checks instead
of a golden set; an LLM-judge trusted as ground truth without calibration; a single aggregate metric hiding a
per-category failure; gating only on L2 and ignoring the business outcome; gaming a metric; calibration on
clean cases that don't match production contexts.

## Output and handoff
Write the plan and any harness/tests, then a 3-line summary: the metric + threshold that most constrains the
release, the biggest measurement risk (usually an uncalibrated judge or a too-small golden set), and the next
step (usually `production-readiness`).
