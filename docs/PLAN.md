# AI Architect labs — build plan

Based on the Udemy course *AI Architect: Enterprise AI System Design* (Carlos Oliveira):
8 modules, 84 lectures, a running capstone.
The transcripts are **local and gitignored** (paid content); everything here **paraphrases** the ideas and builds original, runnable examples — no course text is reproduced.

Two tracks, because the course has two kinds of output:
the **Tooling Walkthroughs / Labs** → runnable notebooks, and the **"Optional: … Document / Memo / Design"** closers → artifact-producing skills.

## Track A — runnable notebooks

Local Ollama (qwen + bge-m3) where it fits; an API/Claude model only where the reasoning needs it.
Same bar as the other labs: executed clean, outputs baked, measured claims only.

| # | Notebook | Source lectures | Builds / measures |
|---|---|---|---|
| 1 | `nb02_rag_architecture` | M2 RAG stack, RAG failure modes, Advanced RAG, RAG Security | RAG stack component-by-component; indirect-injection defence; structured-query routing; a golden eval set + threshold calibration |
| 2 | `nb02_vector_index` | M2 Vector Index HNSW vs IVF | build a small index both ways; measure the recall/latency trade-off and when it matters |
| 3 | `nb02_agent_memory` | M2 Agent Memory tiers + failure modes | in-context / short / long tiers with write-gates; trajectory-based eval |
| 4 | `nb02_agent_protocols` | M2 MCP & A2A, Agent Runtimes | mock MCP/A2A tool-calling; runtime comparison |
| 5 | `nb04_gateway_litellm` | M4 AI Gateway with LiteLLM | routing, caching, fallback, cost/latency logging through one gateway |
| 6 | `nb05_security_guardrails` | M5 OWASP Agentic, Guardrails, Red-teaming | reuses/links the `ai_security_labs` efficacy work; guardrail architecture |
| 7 | `nb06_eval_stack` | M6 Offline/Online eval, Langfuse + RAGAS | three-layer eval stack; golden set; drift detection |
| 8 | `nb07_cost_scaling` | M7 Cost architecture, Scaling, LLMOps | a cost/scaling model; production-readiness checks |

## Track B — skills that produce the architect's artifacts

Each maps to an "Optional: …" closer. A skill takes a short brief and scaffolds the deliverable (structure paraphrased from the course template; no template text copied).

| Skill | Produces | Source |
|---|---|---|
| `scoping-document` | an AI system scoping doc (feasibility, problem classification, scope) | M1 |
| `rag-architecture` | a RAG architecture spec with failure modes handled | M2 |
| `model-selection-memo` | a build-vs-buy-vs-fine-tune decision memo | M3 |
| `integration-architecture` | an enterprise integration / gateway design | M4 |
| `governance-review` | a governance / responsible-AI / security review | M5 |
| `evaluation-design` | a three-layer evaluation design + golden-set template | M6 |
| `production-architecture` | a scaling / cost / LLMOps production design | M7 |
| `capstone-proposal` | the end-to-end architecture proposal (composes the above) | M7 capstone |

## Build order

Notebooks first (per decision 2026-10-18): **nb02_rag_architecture → nb02_vector_index → nb02_agent_memory → nb04_gateway_litellm → nb06_eval_stack → nb05_security_guardrails → nb07_cost_scaling → nb02_agent_protocols**, then the Track-B skills.

Before each notebook: read that module's transcripts (local) so the build reflects the course's actual framing, not an inference.

## Comprehension checks (every notebook)

Each notebook ends with a **"Check your understanding"** section: 4–6 questions tied to what the
notebook actually demonstrated (not trivia), each answer hidden behind a collapsible block so you can
self-test before revealing:

```markdown
**Q1.** Why does structured-query routing beat forcing everything through vector search?
<details><summary>answer</summary> ...grounded in the result the notebook showed... </details>
```

Mix of recall ("what did X measure"), application ("which control would you add here"), and
design-judgment ("when would HNSW lose to IVF") questions. Answers reference the notebook's own
measured output where possible, so the check stays honest to what was shown.
