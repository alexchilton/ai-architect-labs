# Fable review — nb05 (governance & security) — 2026-10-18

Independent critical review (Fable 5.1), which **re-measured** cosine/latency/judge live against the same
models. Record; fixes are in the commit that follows. No Severe (the hedges held); 5 High, all fixed.

## High (fixed)
1. **The cosine "fails" demo didn't show failure** — 0.86 vs 0.73 is separable (threshold 0.80 works). Fixed:
   added a one-word fabrication ("18 days", measured 0.852 ≈ truth 0.861) and a true paraphrase (0.764); now a
   *false* statement outranks a *true* one, so no threshold separates them. Narration rewritten to that pair.
2. **The safety guard failed OPEN** (`else "SAFE"`). Fixed: extracted `_safe_verdict` that returns SAFE only on
   an explicit SAFE token — fail closed; the grounding judge likewise returns UNSUPPORTED on anything
   unparseable. Added a deterministic fail-closed test.
3. **"Hash-chain detects any edit" ignored re-chaining.** Fixed: the cell now shows an insider recomputing every
   hash so `verify` passes again; narration says the chain is evidence only once the head is signed/anchored
   where the writer cannot reach. Dropped the wrong "Merkle" term.
4. **The judge (the working check) was untested; the only test asserted the embedder's weakness.** Fixed: assert
   the judge separates grounded/fabricated (labelled model-dependent) AND assert the cosine *gap* between truth
   and the one-word fabrication is < 0.05 (the measured limitation), not an absolute floor.
5. **`risk_tier` failed open** — unknown domain → silent minimal-risk. Fixed: validate domain/autonomy/data
   against known vocabularies and return `needs-review`; test that an unknown domain is not minimal-risk.

## Medium (fixed)
6. The Act has no "autonomy" axis and does not tier on data type; GDPR applies at every tier. Fixed: tier is now
   `f(domain)` only; `data`/`autonomy` attach **cross-cutting** obligations (GDPR/HIPAA, stricter oversight) at
   any tier; explicit "big simplification, not legal advice" caveat; "touches PHI → limited-risk" removed.
7. `untargeted-scraping` → `untargeted-face-scraping` (the Act bans facial-image scraping specifically).
8. Test titled "unseen high-risk domain generalises" — credit was already listed; renamed to "a new system name
   in a listed domain classifies from its domain".
9. Diagram trust-boundary label "deterministic controls" enclosed model-based guardrails; relabelled "controls
   enforced in code (some deterministic, some model-based)".
10. "ASYNC-parallel" → "ASYNC-after" (nothing parallel); latency now median of 3 + the guard-alone figure.
11. Dropped the "doubling / Llama Guard" extrapolation; inline "adds the guard's full latency (~guard-alone)".
12. Named the cross-referenced security notebook (`ai_security_labs/gap_mcp_jira_injection`) for the 0/3 figure.

## Low (addressed)
Hardcoded ~0.86/~0.73 removed from prose (reads the rows); redact demo clarified (raw shown only as demo input,
only `clean` flows onward); phone-regex over-match of dates/invoice numbers noted; "tamper-evident logging"
Act-obligation reworded to "automatic logging + traceability (Art 12)".

## Good
Pillars→controls (each a thing a reviewer can point at); risk tier as a function with obligations as a lookup;
the judge catches what cosine misses; the hash-chain code is correct and names the broken index; the inline-vs-
async prose is honest about its own (small) number; the ai_security_labs boundary is honest (cross-referenced,
not re-measured). Post-fix: all claims match the measured output; 10/10 checks, 0 errors.
