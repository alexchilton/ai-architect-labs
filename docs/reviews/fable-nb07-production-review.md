# Fable review — nb07 (production / LLMOps) — 2026-10-18

Independent critical review (Fable 5.1). Record; fixes are in the commit that follows. 2 Severe + 4 High +
Mediums/Lows, all fixed and re-verified (6/6 checks, 0 errors).

## Severe (fixed)
1. **"We measure both" was false — only the streaming call ran; the non-streaming cut-off was arithmetic.**
   Fixed: a real `stream=False` request with `timeout=(5, DEFAULT_LB_TIMEOUT)` in a `try/except ReadTimeout`,
   which now **observes** the cut-off (`*** CUT OFF at 10.0s (ReadTimeout) ***`).
2. **"Throughput drops under concurrency" was backwards for the aggregate the formula uses.** Aggregate decode
   throughput *rises* with batching (continuous batching) to a saturation point; per-request speed falls. Fixed
   the §1 "Read it": measure the **aggregate** at target concurrency/context, never a single stream (which
   over-provisions badly).

## High (fixed)
3. KV "OK" rows ignored the ~15 GB of weights — on a 24 GB card 15 GB of KV is OOM. Fixed: `WEIGHTS_GB=15`,
   compare KV against `GPU_GB - WEIGHTS_GB` (9 GB); `8192×32` now correctly OOMs.
4. Streaming only beats **idle** timeouts (bytes reset the clock); a **total-duration** cap (API Gateway 29s,
   serverless) still cuts you off. Added the distinction; P99-total setting is mandatory either way.
5. "An LLM request is its output length" ignored **prefill** (the "summarise" example is input-heavy). Relabelled
   to "report gen (very long out)" and noted input/prefill also costs (cheaper per token, run in parallel).
6. Stateless omitted the LLM-specific cost: **re-prefill** on reroute (the shared store holds text, not the KV
   cache); added prefix-cache-aware routing as the production middle ground.

## Medium (fixed)
7. `cpu=35` is an assumption — now narrated as "we assume CPU is flat (typical of a GPU-saturated server)".
8. "memory before compute" softened to "at long context ... memory is the binding limit" (prefill is compute-heavy).
9. CUT OFF won't reproduce on fast GPUs — the print is conditional and the prose says the timeout is set low to
   show the effect at 200 tokens (ALB/nginx default ~60s).
10. The streaming test now asserts `ttft < total*0.25` (hardware-robust) instead of an absolute `< timeout`.
11. §7 heading reworded: "checks that the models here behave as narrated", not "production guarantees".

## Low (addressed)
Labelled the KV dims as the real Qwen2.5-7B values (not "illustrative"); "worker unavailable; rerouted" instead
of "dies"; noted the queue sim omits scale-in and provisioning lag (pre-warm + headroom).

## Good
tokens/sec-not-QPS with a one-line formula; the real Qwen KV dims (56 KB/token); the warm-up before TTFT; the
now-measured streaming-vs-non-streaming cut-off; the queue-depth autoscale signal matching real vLLM/KServe
practice; driver-derived region posture with a fail-closed branch. Post-fix: all claims match measured output.
