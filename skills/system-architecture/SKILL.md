---
name: system-architecture
description: Use after scoping, to design the AI system architecture for a project — choose the architectural pattern(s), design the RAG and/or agent stack with its production failure modes handled, and specify security, evaluation, and cost/latency budgets. Trigger on "design the architecture", "how should this RAG/agent be built", "architecture for <AI system>", or when handed a scoping document to turn into a design. Produces an architecture document AND, when a component is to be built, secure reference code + meaningful tests + an eval harness.
---

# AI System Architecture

Turn a scoped problem into a concrete, defensible architecture: the pattern, the stack, the failure
modes designed against, and the security/eval/cost budgets — then, for anything to be built,
secure-by-default reference code with meaningful tests and an evaluation harness. Consumes a
`scoping-document` (read its YAML front-matter) when one exists; feeds `model-selection`,
`governance-review`, and `evaluation-design`.

## 1. Choose the pattern(s) — name the trigger, not the fashion
Pick from the six core patterns and justify each against the scoped need, not because it sounds good:
- **Inference pipeline** — single-pass, stateless, bounded input/output (classify, tag, extract).
- **RAG** — needs knowledge not in training, available at query time.
- **Agentic loop** — multi-step, steps can't be fully pre-specified, needs external tool use.
- **Ensemble/router** — mixed request complexity; tier cheap vs frontier for cost.
- **Human-in-the-loop** — high-stakes/regulated, low error tolerance.
- **Multimodal** — the modality (vision/voice) is the task, with its own latency envelope.
A system is usually a composition. State which capability uses which pattern.

## 2. Design the RAG stack (if used), component by component
- **Ingestion:** parse → **semantic-boundary chunking** (never fixed character counts — that causes
  coreference collapse) → embed → vector store. Record source version + timestamp per chunk.
- **Retrieval:** query rewrite (condense chat history to a standalone query) → embed with the *same*
  model as the corpus → **hybrid search** (dense + BM25, fused with RRF — dense alone misses exact
  IDs/codes) → **cross-encoder rerank** → context assembly → generation with explicit grounding.
- **Design against the production failure modes, by name:**
  - *coreference collapse* → contextual chunk enrichment.
  - *absence blindness* (no "I don't know") → a retrieval-confidence gate before generation.
  - *write-side neglect* (stale/duplicate chunks) → version tracking, event-driven re-ingestion, a
    staleness SLA.
- **High-stakes/citation-grade retrieval** (legal, medical, financial): standard RAG is insufficient —
  add citation verification and stronger reranking; say so explicitly.

## 3. Design the agent (if used)
- **ReAct** loop (reason→act→observe); tools **atomic and reversible-first** (read before write, soft
  delete, staging).
- **Memory tiers:** in-context / external short-term / external long-term / procedural — matched to real
  persistence needs, with **write gates** (explicit / confidence-gated / extract-then-store) so poisoned
  or low-quality facts never enter long-term memory. TTL and an erasure index are legal requirements,
  not hygiene.
- **Multi-agent:** orchestrator-owns-state to start; treat every inter-agent message as **untrusted**.
- **Design against:** cost spirals (token/step budgets + alerts), non-determinism (version logging +
  deterministic post-processing + a human gate for high-stakes), context mismanagement (summarisation /
  retrieval / budgets + prompt/semantic/embedding caching).

## 4. Security section (always) — structural, not prompt-level
Retrieved content and tool output are an **attack surface** (indirect injection). Required controls,
enforced in code not the prompt:
- trust-tier / provenance labelling of all external content;
- no consequential tool call in the same turn as freshly-ingested untrusted content;
- access control as a **query-time pre-filter** (never post-processing), with document-level ACLs;
- output sanitisation against auto-rendering exfiltration (e.g. markdown images).
(These mirror the measured results in the companion `ai_security_labs` repo — prompt-level framing does
not hold; structure does.)

## 5. The architecture document
Write `docs/architecture-<project-slug>.md` with: problem + chosen pattern(s) and why; a **context
diagram**, **component diagram** (annotate model versions + latency), **data-flow** and **sequence**
diagrams (use Mermaid); per-capability design with failure modes handled; access-control / multi-tenancy
model; freshness/staleness SLA; the security section; an evaluation plan (golden set, recall@k or
task/trajectory/safety metrics, where it attaches); a cost + latency budget (token ceilings, step
limits, circuit breakers); and explicit caveats (what the design simplifies, what needs legal review).

## 6. When a component is to be built — the factory outputs
Do not stop at the document. Scaffold, to the project's language:
- **Secure-by-default reference code** for the component (e.g. a retrieval function with the query-time
  ACL pre-filter and trust-tiering already in place — security is the default, not a TODO).
- **A small set of meaningful tests** — each asserts a real behaviour, contract, or security property
  and carries a one-line rationale. Examples worth their place: hybrid retrieval ranks an exact-ID query
  above dense-only; the confidence gate abstains on an unanswerable query; a planted indirect-injection
  doc does **not** cause a tool call; an unauthorised caller never retrieves a restricted document. Never
  write a test whose only effect is to raise coverage.
- **An eval harness** for the AI component: a small golden set and the metric that matters (recall@k for
  retrieval, groundedness/abstention for generation), runnable as a gate.

## Anti-patterns to flag
Fixed-size chunking; vector-only retrieval; skipping rerank; ignoring the write/freshness side;
unbounded agent loops; treating the system prompt as the safety layer instead of application-layer
enforcement.

## Output and handoff
Write the document and any scaffolded code/tests/eval, then give a 3-line summary: the pattern chosen,
the one failure mode most likely to bite in production, and the next step (usually `model-selection`
then `evaluation-design`).
