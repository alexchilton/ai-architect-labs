# Fable review — nb_case_studies (legal RAG + HR agent) — 2026-10-18

Independent critical review (Fable 5.1), which **ran live probes** against qwen2.5:7b (tool-calling) + bge-m3.
Record; fixes are in the commit that follows.

## Severe
1. **Q1 answer taught a failure the setup doesn't produce.** It claimed the model "misattributes the 30-day
   payment term"; measured: 4/4 absence probes abstained correctly, and `payment_terms` wasn't even retrieved
   for the termination question. Invented example beside a contradicting measurement. Fix: delete it; state the
   measured abstention; the relational query is the real failure.
2. **"structured traversal provides all of them" was a printed string literal** — no traversal code existed.
   Fix: implement a real clause-link graph (`LINKS`) + `traverse()` and show the GraphRAG win.

## High
3. **The injection demo had no injection.** `injected` was assigned, never read; no model saw it; the author
   called `gate("update_salary")`. Measured: qwen2.5:7b, given tools and that exact text, **does** emit
   `update_salary(200000)`; with a "never change salaries" system prompt it did not (one crude injection).
   Fix: send `injected` to the model with the tools, route its `tool_calls` through the gate, show the block.
4. **"injection cannot bypass app-code policy" held only for the action name.** The gate didn't check arguments
   (`days=-1000` would increase the balance) or identity (`eid` never compared to caller). Fix: add bounds +
   `eid==caller` checks and tests; state what the gate does/doesn't cover.
5. **"Answers absence with certainty" holds only because `CLAUSES` is hand-typed.** Real index = extraction
   (fallible); "absent" = "not extracted". Fix: caveat that extraction recall is the thing to test.
6. **k=1 relational demo is a straw man; k=2 (the default) also fabricates; k=4 correct.** Fix: show a k-sweep
   table; state the honest limit (raising k re-introduces lost-in-the-middle/cost at real length).

## Medium
7. "luck, not safety" -> "not evidence" (the abstention was reproducible).
8. "thinner -> fabricates" is wrong (k=2 also fabricates); driver is answer-shaped cues in the fragment.
9. "fully fabricated" overstates — "German law" is inferred from "GmbH"; the figure is fabricated. Say "confabulates from surface cues".
10. "every step is in the audit trail" false — `_stage` wasn't logged. Fix: log staging.
11. "~10×" is a course rule-of-thumb — label it, not a measured fact.
12. The `ai_security_labs` line imported a result; make it a cross-reference, not a finding of this run.
13. Tests: two were duplicates; add unknown-action-refused, negative days, cross-record, confirm-without-stage.

## Low
14. Mermaid "parse intent" node had no code — now the model is in the loop.
15. `undo` after two interleaved stages on one field restores the wrong old value (tutorial caveat).
16. Heading "top-1 drops a needed clause" — it dropped all three; say so.
17. `gate("read_employee","E9999")` raised KeyError — the gate must refuse.

## Good
The retriever-level absence-blindness argument is correct and survives the model abstaining. The relational
fabrication (wrong figure, wrong jurisdiction, from one wrong fragment) is real and reproducible. Stage/
confirm/undo with the balance printed is the right reversible-first demo, and its test can fail. Read/write
split and "escalate, don't write" are correctly modelled; the gate being a plain function the model can't
reach around is the right lesson — it just needed the model actually in the loop to earn the word "injection".
