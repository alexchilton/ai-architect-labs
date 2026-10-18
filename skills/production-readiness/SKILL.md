---
name: production-readiness
description: Use to take an AI component from pilot to production — size capacity on tokens/sec (not QPS), treat long context as a KV-memory problem, design stateless workers with externalised session state, set streaming-aware timeouts, autoscale on the queue (not CPU), choose a multi-region posture by its driver, and specify the LLMOps (runbooks, on-call, prompt-versioning, rollout/rollback). Trigger on "take this to production", "it works in the pilot, now scale it", "capacity / scaling plan", "why does it OOM / time out / not autoscale", "multi-region?", or after an evaluation gate is green and the component must ship. Produces a production-readiness doc AND, when built, scaling configs + runbooks + meaningful tests.
---

# Production Readiness (LLMOps)

Turn "it worked in the pilot" into a plan that survives real load. Consumes an `evaluation-design`-gated
component; produces `docs/production-<component>.md`.

## 1. Size on tokens/sec, not QPS
An LLM request's work is its **output length**, so two services at the same QPS can need an order of
magnitude different capacity. Plan on **tokens/sec = QPS × output-tokens**, and measure a box's *real*
sustained decode throughput under production concurrency and context length (it is far below the single-request
number, and real serving uses **continuous batching** to claw some back — measure it, don't assume linear).

## 2. Long context is a memory problem — the KV cache
Every context token holds a KV-cache entry on the GPU for **every concurrent request**, so KV memory grows
linearly with **context-length × concurrency** and OOMs the box long before compute does. The lever is a
**smaller context** — trim old turns, summarise agent memory, page/retrieve instead of stuffing — or sharding.
Agent memory and long multi-turn histories are the usual culprit; M2b's "retrieve, don't stuff" is a capacity
decision too.

## 3. Stateless workers + externalised session state
Default to **stateless, horizontally-scaled** inference with session state in a **shared store** (Redis/DB),
so any worker serves any turn and a dying or scaled-down worker costs nothing. **Sticky sessions lose the
conversation** on crash/rebalance/scale-down — reserve them only for state you've measured is too large to
fetch each turn.

## 4. Streaming-aware timeouts
A long generation can outlast a default load-balancer/API-gateway timeout tuned for web APIs (often 30–60s,
sometimes 10s), which **severs it mid-generation**. **Stream** the response — first token arrives in a small
fraction of the total, keeping the connection alive and the user seeing progress — and set the timeout against
the **P99 total**, not a web default. Cap max output tokens as a latency lever.

## 5. Autoscale on the queue, not the CPU
Inference is GPU-bound: CPU sits near-idle while the GPU saturates and the **queue** backs up, so a CPU-
threshold autoscaler never fires and you silently under-provision. Scale on **queue depth / P95 queue-wait /
token-throughput saturation / GPU-memory pressure**. Plan for bursty/seasonal load explicitly (pre-warm,
headroom), not just steady-state.

## 6. Multi-region posture — chosen by the driver
Going multi-region is a deliberate trade; the **driver** picks the shape: **latency → active-active** (serve
from the nearest replica), **cost → active-passive** (one live region + warm standby, accept failover time),
**residency → region-locked** (data cannot cross the jurisdiction; no cross-region replication even if you
want the latency). "Multi-region because it sounds robust" overpays or breaks residency.

## 7. LLMOps the component needs to be operable
Prompt/version pinning + logging of model+version+prompt-version per call; staged rollout + instant rollback;
canary + drift monitors (format-compliance, token baselines, similarity-to-baseline) wired to the eval gate;
on-call with a runbook per failure mode; a cost monitor against the budget ceiling; and a defined degraded
mode (the fallback from `integration-architecture`) for when the model is slow/down.

## 8. The production-readiness document
Write `docs/production-<component>.md` with: current scale + 3-horizon targets (launch / 10× / peak); the
capacity model in **tokens/sec** with the measured per-box throughput and the KV-memory budget; the
state/statelessness design; latency/timeout/streaming plan against the SLA; the autoscale signals + thresholds
+ burst plan; the multi-region posture + its driver; hosting constraints (self-host/residency/regulatory); the
LLMOps plan (rollout/rollback, monitoring, on-call, runbooks, prompt-versioning); the cost model vs the budget
ceiling; and explicit caveats (what is assumed, what needs a load test).

## 9. When configs/runbooks are scaffolded
Ship with **meaningful tests** (each a real property, able to fail): the capacity model needs more boxes for a
longer-output service at the same QPS; KV memory scales linearly with ctx × concurrency and the planned peak
fits the GPU budget; a stateless worker serves a turn after a simulated worker loss; the autoscaler scales on
the queue signal where a CPU signal would not; the region-posture function fails closed on an unknown driver.
Never a coverage-only test. Keep capacity constants named and measured.

## Diagram
Draw the production topology — load balancer (streaming-aware timeout) → request queue → **stateless** worker
pool ↔ externalised shared state, with the autoscaler reading **queue depth** — following the colour + legend +
trust-boundary convention in `system-architecture` §5a; the inference workers are the **probabilistic** nodes
(annotate model + version). Mermaid in `.md`; a graphviz PNG in a notebook.

## Anti-patterns to flag
Sizing on QPS; autoscaling on CPU% for a GPU-bound service; a default web timeout that cuts off generations;
sticky sessions by default; ignoring KV memory until it OOMs; going multi-region with no driver; no
prompt-versioning / rollback / runbooks; capacity-planning from single-request throughput (ignoring
concurrency and continuous batching); no load test before the peak event.

## Output and handoff
Write the doc and any configs/runbooks/tests, then a 3-line summary: the binding capacity constraint (usually
tokens/sec or KV memory), the single biggest operational risk (usually the untuned timeout or the CPU-based
autoscaler), and the next step (a load test, or back to `model-selection` if the economics don't close).
