# Fable review — nb04 (integration architecture) — 2026-10-18

Independent critical review (Fable 5.1). Record; fixes are in the commit that follows.

## Severe (fixed)
1. **"the correction worked" was false** — the retry loop never fed the error back to the provider; the sim
   recovered by construction. Fixed: `resilient_generate` threads `last_error` into the provider, and the sim
   returns valid JSON only *after* it receives a correction, so the recovery is genuinely the correction.
2. **"latency has a long tail" contradicted by the data** — P50 0.98 / mean 0.92 on 8 identical calls, and
   "P99" was just the max of 8. Fixed: measure a **mixed** workload (alternating cap 20/120), report `max` not
   a fake P99, and add token timers (decode 120 tok 12.0s vs prefill 37 tok 0.14s = 88x) to explain the tail.

## High (fixed)
3. **Cache key omitted model/num_predict/version and cached unvalidated output** — the code demonstrated the
   bug it warned against. Fixed: `cache_key(model, system, prompt, num_predict, PROMPT_VERSION)`; a changed
   decode setting now correctly misses; measured hit time with `perf_counter`; narration says cache validated
   output only (diagram writes cache on the `ok` path).
4. **"business-rule fault is not a model problem" overstated; tier-2 retries carry the same laundering risk.**
   Fixed: rewrote the escalate argument to "can't distinguish policy violation from hallucination; a
   correction biases toward a pass → escalate so a human sees the source text"; narrated that tier-2 value
   faults are only retryable when the fix is pure normalisation, never by stating the allowed values.
5. **The model swap was never performed.** Fixed: actually mutate `ROUTES["classify"]` and re-run the same
   caller; `CALLS` shows traffic move tier-A → tier-B; added "a swap moves the call, not the behaviour —
   re-run the eval after every swap."

## Medium (fixed)
6. num_predict A/B changed two variables → same prompt at cap 10 vs 120.
7. token counts never printed → print prefill/decode durations; qualify "decode dominates for short prompts".
8. hit latency hardcoded 0.0 → measured with perf_counter.
9. Section 4 never said "simulated" → added "(simulated outage)" + transport-only note.
10. diagram logic → added transport-error edge, retry re-checks breaker, cache-on-ok; labelled "how they compose".
11. real-model section showed only good cases → added a real 25,000 EUR input that lands at tier 3.

## Low (addressed)
dead subexpression removed; SPEND→CALLS; bool excluded from amount (bool is a subclass of int);
breaker transport-only note; pctl uses ceil; added a stop-at-first-ordering test.

## Also fixed post-review
- A stateful test bug: the cache test reused `num_predict=10` already cached in Section 5, so its "should
  miss" assertion hit. Rewritten to assert on `cache_key` directly (state-independent).

## Diagrams
All notebook diagrams converted from Mermaid (which GitHub does not render inside .ipynb cells) to
graphviz-rendered PNG cell outputs, which GitHub's notebook renderer does display. Skill files keep Mermaid
(GitHub renders it in .md).

## Good
The 50,000 EUR case (schema-valid, semantically sane, business-invalid) is the sharpest example; stop-at-first
tiering; escalate-never-retry as control flow; the breaker demo with its half-open caveat; the num_predict
latency lever (0.89s vs 12.3s) is real and large.
