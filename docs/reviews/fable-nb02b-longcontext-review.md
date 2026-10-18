# Fable review — nb02b (long context vs RAG) — 2026-10-18

Independent critical review (Fable 5.1), which **independently tokenized** the prompts with the Qwen2.5 tokenizer.
Record; fixes are in the commit that follows.

## Severe
1. **Section 2 was not a position experiment — it was truncation.**
The sweep prompt was 16,721 tokens against a 16,384 window, so Ollama cut every position to 8,194
(`num_keep + (num_ctx-num_keep)//2` = `4 + (16384-4)//2`). The found/missed pattern (F,F,F,T,T) was
**tail survival** (needles at 75%/100% in the kept tail; 0/25/50% in the discarded head), and the 0.9s rows
were KV-cache hits proving the surviving content was identical. Headline "lost-in-the-middle reproduced" was
false. Fix: lower N_DISTRACT so the prompt fits (used 400, ~9.6k < 16,384) and prove it with an independent count.
2. **The fit guard was invalidated by the notebook's own Section 1 lesson.** `pt < POSITION_CTX` does not prove
"held" — a truncated prompt also reports below num_ctx (8,194 < 16,384). Fix: assert `pt == independent_count`
and `pt != truncation_floor`.
3. **Section 2 "Read it" didn't read the result** — offered U-curve/flat, result was neither. Fix: write from numbers.

## High
4. Section 0 "pinned at num_ctx" is wrong (measured 1,026 at 2,048) and contradicts the test's own "why". Fix: floor formula.
5. Intro states lost-in-the-middle as measured; it wasn't. Keep as literature (Liu et al. 2023); sweep = one model/length.
6. Knob comment "tuned so the 7B retrieves a mid needle" — the 50% row was False (the truncation artifact).
7. "Verify the token count against your input" preached, never practised. Fix: add the independent count and compare.

## Medium
8. Section 3 RAG latency (2.0s) excludes 9 embedding calls — not head-to-head. Fix: time retrieval; note embeddings are ingest-time.
9. Say Ollama "kept the tail" in Section 1 rather than leaving the reader to guess.
10. Check `r_pt < s_pt` near-tautological (top-3 of 8); keep as sanity, not "meaningful".
11. Check `len(df)==5` only fails on an edit; drop or merge.

## Low
12. Q4 "non-deterministic" — at temp 0 it is deterministic for a fixed build; say "not stable across models/versions/hardware".
13. Diagram node "mid-context" — reword to "away from where the model attends".

## Skill diagrams
- system-architecture 5a: component diagram missing the business-rule→escalate path; `retry` is a dead end (loop to gen + exhausted→fallback); sequence diagram missing the pre-model abstain branch.
- integration-architecture 5a: cache is write-only (add a read/lookup before the gateway); `fb` and `retry` are dead ends.

## Good
Section 1 (same prompt, two windows, 1,026 vs 16,143, confident wrong code) is the best cell. Section 3 decision rule is honest. Test philosophy (assert structure, not the model's answer) is sound — only the fit guard was wrong.
