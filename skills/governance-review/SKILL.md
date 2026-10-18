---
name: governance-review
description: Use to make AI governance and security a day-one design input, not a pre-launch checkbox — map the responsible-AI principles to concrete controls, classify the regulatory risk tier and derive its obligations, design the guardrail pipeline (input + output layers, mode per stakes), specify a tamper-evident audit trail and human oversight, and inventory the OWASP agentic risks with structural mitigations. Trigger on "governance review", "is this compliant / high-risk", "AI risk assessment", "guardrails design", "EU AI Act / GDPR / HIPAA for this system", or after an architecture/integration doc needs its safety and compliance posture. Produces a governance document AND, when built, secure control code + meaningful tests. Cross-references the companion ai_security_labs repo for measured attacker/defender efficacy — does not duplicate it.
---

# Governance & Security Review

Turn "is it safe / compliant?" into controls a CISO, a DPO, and an auditor can each point at. Consumes a
`system-architecture` / `integration-architecture` doc; produces `docs/governance-<component>.md`.

**Scope boundary.** This covers governance *architecture* (controls, risk tier, guardrail design, audit,
oversight). For *measured* attack/defence efficacy (prompt injection, tool misuse, jailbreaks) reference the
companion **`ai_security_labs`** repo — cite its results, don't re-run them here.

## 1. Responsible-AI principles → concrete controls (not slogans)
Each principle must become a build item with an owner and a test, or it didn't happen:
- **fairness** → a bias audit on a representative set + a per-subgroup metric in the eval gate;
- **reliability** → guardrails + a defined fallback per touchpoint + a circuit breaker;
- **privacy** → PII detection/redaction before egress, purpose tags, TTL, an erasure index;
- **transparency** → disclose it's AI; log model+version+prompt-version per answer; cite sources;
- **accountability** → a tamper-evident audit trail + a named human owner + override logging;
- **inclusiveness** → representative test data across languages/locales/accessibility needs.
Bias enters at multiple points (base model, fine-tune, embedding space, retrieval corpus, prompt) — each
needs its own check, not one audit at the end.

## 2. Risk tier drives the obligations (don't carry a flat checklist)
Classify from attributes (domain, autonomy, data sensitivity), because the obligations are *gated by tier*:
- **prohibited** (social scoring, subliminal manipulation, untargeted scraping) → do not build;
- **high-risk** (employment, credit, health, legal, safety, education, biometric, essential services —
  especially when the system recommends/acts) → risk-management system, data governance, technical docs,
  **tamper-evident logging, human oversight**, conformity assessment + registration;
- **limited-risk** (user-facing, or touches PII/PHI/financial) → disclose it's AI, basic audit trail, GDPR;
- **minimal-risk** → voluntary codes.
Regulatory anchors: **EU AI Act** (risk tiers; high-risk obligations binding ~Dec 2027), **GDPR** (erasure vs
mandatory retention via the legal-obligation exemption + lineage), **HIPAA** (PHI needs a BAA before a
third-party model — often self-host), **US sector** (ECOA/FCRA adverse-action explainability; model-risk).
State the tier, cite the regime, and **flag that a real classification needs counsel** — this is a decision aid.

## 3. Guardrails are a pipeline, with a mode per stakes
- **Input layer** (before the model): PII detect/redact, length limits, jailbreak/again-the-policy screening,
  trust-tier tagging of untrusted content.
- **Output layer** (after the model): grounding/faithfulness vs the retrieved context, toxicity, format
  validation, an **output PII scan** (the model can emit PII the input layer never saw — defence in depth).
- **Three execution modes**, chosen by stakes vs latency: **inline-blocking** (high stakes; a model-based
  guard roughly doubles latency — measure it), **async-parallel** (fast answer, log/revoke after),
  **offline-batch** (sample low-stakes volume). The mode matters most when the guard is itself a model
  (Llama Guard / Azure AI Content Safety); for a regex it's free.
- Agents also guard **actions/tool calls**, not just text: policy in app code (allowlist action + validate
  arguments + check caller identity), reversible-first tools, and escalation for high-stakes actions — a
  prompt instruction is not a boundary. (See the measured deny-by-default result in `ai_security_labs`.)

## 4. Audit trail: "we have logs" is not an audit trail
A high-risk system must prove records weren't altered. Ordinary logs are editable. Use a **tamper-evident**
design: a **hash-chain** (each entry commits to the previous one's hash) + signing + an external anchor +
append-only storage. Log model+version, prompt-version, retrieved chunk IDs, the guard verdicts, and any
human override — the fields an incident review and a regulator actually need.

## 5. Human oversight & agent autonomy
Specify the approval checkpoints, the override path (and that overrides are logged), and the agent's autonomy
envelope: reversibility, bounded tool scope, escalation thresholds, logged transparency. Match autonomy to
stakes — text-only vs takes consequential action.

## 6. OWASP agentic risks — a named structural mitigation each (not a prompt reminder)
Inventory ASI01–ASI10 (goal hijack, tool misuse, identity/privilege abuse, agentic supply chain, unexpected
code execution, memory/context poisoning, insecure inter-agent comms, cascading failures, human-agent trust
exploitation, rogue agents) and give each a **structural** mitigation in app code. For efficacy evidence,
cite `ai_security_labs` (e.g. a read-only connector compromised 0/3 behind a deny-by-default gate while
prompt-level framing did not hold on a 7B).

## 7. The governance document
Write `docs/governance-<component>.md`: the risk tier + regime + obligations; the principle→control table
(owner + test each); the guardrail pipeline (layers + the mode per touchpoint + what each catches); the
audit/logging design (tamper-evidence, fields, retention vs erasure); the human-oversight + autonomy plan;
the OWASP-agentic inventory with mitigations; data residency/PII/redaction notes; and explicit caveats
(what needs legal review).

## 8. When control code is scaffolded
Ships **secure-by-default**: PII redaction before egress, the input/output guardrail pipeline, the action
gate (allowlist + argument + identity checks), and a hash-chain audit logger. With **meaningful tests** (each
a real property, able to fail): redaction removes the raw value; the risk-tier function puts a high-risk
domain in the high-risk tier with human-oversight + audit obligations; the output scan flags a fabricated
answer; the action gate denies a cross-record write and refuses an out-of-range argument; the hash-chain
verifies clean and **detects a retroactive edit**. Never a coverage-only test.

## Diagram
Draw governance as **layers around** the system (risk-tier gate → input guardrail → model → output guardrail
→ audit log, with human oversight on the escalate path), following the colour + legend + trust-boundary
convention in `system-architecture` §5a: the model is **probabilistic and sits outside the trust boundary**;
the deterministic controls (guardrails, gate, redaction) are the boundary.

## Anti-patterns to flag
Governance as a pre-launch checkbox, not a day-one input; prompt-only safety for agents; no document-level
ACLs in RAG; LLM-as-judge treated as ground truth without human calibration; ordinary logs presented as a
regulatory audit trail; red-teaming the model in isolation instead of the integrated system; one bias audit
at the end instead of a check at each point bias enters.

## Output and handoff
Write the document and any scaffolded controls/tests, then a 3-line summary: the risk tier + the two or three
obligations that most shape the build, the single biggest residual risk, and the next step (usually
`evaluation-design`).
