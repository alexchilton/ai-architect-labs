# Fable review — nb06 (evaluation) — 2026-10-18

Independent critical review (Fable 5.1). Record; fixes are in the commit that follows. 2 Severe + 4 High +
Mediums/Lows, all fixed and re-verified.

## Severe (fixed)
1. **The real gate BLOCK rested on nothing the system did wrong, unacknowledged.** `faithfulness 0.83 < 0.85`
   is a judge **false-negative** (the "second approver for a 2000 CHF expense" answer is grounded; the golden
   set labels it `human_grounded=True`), and `containment 0.40` is a **constructed** number from the ticket
   log — but the comment claimed "THIS release's measured metrics." Fixed: §3 now prints the judge-vs-human
   disagreement (`!!` line, using the previously-dead `human_grounded` field); the gate comment separates
   measured (recall/faithfulness/answer_correct) from the constructed containment; and the §6 "Read it" states
   both breaches are a judge error + a constructed number, with the lesson: **fix the judge and re-run, never
   lower the bar after seeing the result** (what §1/Q1 forbid).
2. **§5 "100% agreement" contradicted §3's judge miss.** The calibration set had only lexical fabrications, not
   the numeric-entailment case §3 tripped on — and when first added with the single-doc context the judge got
   it *right*, still 100%. Fixed: the calibration case now uses the **same top-3 retrieved context §3 judged**,
   so it reproduces the miss → agreement is now **6/7 = 86%**, reconciled with §3. Added the caveat that
   calibration only covers the failure modes (and contexts) in the set.

## High (fixed)
3. Thresholds unreachable at n=6 (0.85 faithfulness = zero misses). Added a §1 caveat on threshold-vs-sample
   size and that this is a toy golden set (real ones are hundreds per category).
4. `human_grounded` was declared "used to calibrate" and never read. Now used in the §3 disagreement detector.
5. Diagram contradicted §4 (`gold→L3`; `pr→L2` missing). Fixed: added a `ticket log / prod outcomes` data node
   → L3; added `pr→L2`; kept `gold→L1,L2`.
6. §6 per-category demo numbers were hand-typed but read as measured. Labelled "[hand-set demo]" in code + prose.

## Medium (fixed)
7. §2 real data has no failing slice (both 1.00, n too small) — said so; fixed the "next section" reference (§6).
8. answer-correctness substring metric over/under-counts (negation, number-substrings, paraphrase) — stated in §3.
9. Two tautological tests replaced: a fail-closed `_supported` parser test and a faithfulness-breach gate test.
10. Canary: labelled the regression SIMULATED; the "caught" suffix is now conditional on the measured result.
11. n=7 calibration can't establish a rate — stated, with what n a 0.85 bar needs.

## Low (addressed)
"FAILS CLOSED" reworded (unparseable → UNSUPPORTED; transport errors raise); "BLOCK → rollback" → "candidate
cannot merge" (rollback is post-deploy); L3 reasons prefixed "e.g." and noted TICKETS has no reason field.

## Good
Thresholds in code before measurement; the gate is a function returning a boolean + named breaches with a real
per-category check; `TICKETS` labelled constructed; no run-dependent number hardcoded in prose. Post-fix the
gate block is fully explained (judge error + constructed number), calibration (86%) reconciles with the §3
miss, 6/6 checks, 0 errors.
