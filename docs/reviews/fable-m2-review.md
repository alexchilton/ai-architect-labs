# Fable review — M2 vertical (RAG notebook, arch_kit, skills) — 2026-10-18

Independent critical review by a second model (Fable 5.1) of `nb02_rag_architecture.ipynb`,
`arch_kit.py`, `skills/system-architecture`, and the M1 exemplar. Findings ranked most-severe first.
This file is the record; the fixes applied in response are in the commit that follows.

## Severe
1. **"never worse" vs measured 83%** — the test rationale claimed RRF fusion is "never worse" while the
   eval cell measured hybrid recall@1 (83%) *below* dense (100%) in the same run. "Never worse" is true
   only for a single doc both retrievers rank #1; aggregate recall can drop. Prose "hybrid's win is the
   opaque case" is false — section 2 measured a tie.
2. **The 83% is a harness artefact taught as a RAG law** — `arch_kit` BM25 had no stopwords/stemming, so
   "deadline to submit expenses" matched only the stopword "to" and ranked junk; `submit`≠`submitted`,
   `expenses`≠`expense`. Production BM25 (Lucene/Elastic/Qdrant) always runs an analyzer. Fix the analyzer
   and hybrid ties at 100% on this corpus; the honest lesson is "no gain here, measure at scale".
3. **`order()` turns an all-zero BM25 ranking into fake RRF evidence** — stable sort returns zero-score
   docs in index order, so RRF credits docs that matched nothing. BM25 must expose only score>0 docs.
4. **Confidence gate is circular and inside the embedder noise band** — threshold 0.55 chosen after seeing
   the two test scores, then asserted on those same two; 0.55 < max inter-doc cosine (0.65). It passes
   "senior-staff limit" (0.675) and the model answers the wrong all-staff figure — the very absence
   blindness it claims to fix. "Model-independent" is wrong: it's embedding-model-dependent.

## High
5. **"Coreference collapse" mislabelled** — the demo shows mid-sentence truncation, not coreference; the
   chunking test passes only at `size=60` (size=100 → the strawman succeeds and the test fails). Skill's
   absolute "never fixed-size chunking" is cargo-cult in the other direction (token+overlap is a standard
   default, and the iwb Confluence index uses it).

## Medium
6. §1 narration says the fixed chunk holds "number or subject"; baked output shows it holds *neither* —
   truncation broke retrieval too (a stronger point than the prose).
7. Security demo **post-filters** (skill says pre-filter); tests only data-poisoning, not the promised
   indirect-injection+tool case; "trusted-only retrieval" is the allowlist special case, not the general
   control (trust-tiering). Companion-repo citation checks out (ai_security_labs module05 Lab 45,
   gap_mcp_jira_injection) — point at file+lab.
8. Skill §2 states "dense alone misses exact IDs/codes" (notebook measured dense rank 1 on both); §6
   prescribes a "hybrid ranks exact-ID above dense" test the notebook shows cannot pass.
9. Skill overstatements: "TTL/erasure are legal requirements" (only under GDPR for personal data);
   "skipping rerank" as universal anti-pattern (cross-encoder adds latency; measure it); missing the
   strongest controls the companion repo measured — least-privilege tools, URL/domain allowlist for fetch
   tools, ingestion-time scanning (white-on-white PDF text), per-answer chunk-ID audit, query-rewrite as
   an injection surface.

## Low
10. `arch_kit`: `cosine` silently truncates on length mismatch (should raise — hides mixed-embedder bugs);
    repeated query terms double-count (document it); `/api/embeddings`+`prompt` is Ollama's deprecated
    endpoint (`/api/embed`+`input` current).
11. M1/scoping: `classify()` else-branch label lies for discriminative+needs_fresh_knowledge+not-bounded;
    dangling "(see M2 legal case)" cross-ref (M2 has no legal case); scoping skill's FPR definition is
    wrong (FPR = wrongly-declined / all *legitimate*; the ops term is false-discovery rate); disqualifier
    mismatch (skill says zero-tolerance alone disqualifies; nb01 gates on catastrophic AND no-HITL — nb01
    is right).

## What was good
Reporting the dense tie instead of rigging a corpus; the paired over-abstention test; the provenance demo
flipping 99999→500 (measured, not described); nb01's generalization test; the companion-repo citation is
backed by a baked output.
