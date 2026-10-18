---
name: scoping-document
description: Use at the very start of a new AI/LLM/agent initiative, before any architecture or code, to produce an AI System Scoping Document — a feasibility assessment, problem classification, scope boundary, and success metrics for THIS project. Trigger when someone says "scope this AI idea", "is this a good fit for AI", "write a scoping doc", or hands you a vague business request like "we need AI for X".
---

# AI System Scoping Document

Turn a vague business request into a disciplined, one-pass scoping document that says whether AI is
the right tool, what the system is and is not, and how success will be measured — before anyone designs
or builds. This is the first stage of the AI-architect pipeline; its output feeds `system-architecture`.

## When to use
A new AI initiative is proposed and the scope is unclear or over-broad ("we need AI for customer
service"). Use this before architecture, model selection, or any prototype.

## Process

Work through these in order. Do not skip the feasibility pass — jumping to design is the top failure.

### 1. Gather the brief, then fill the gaps
Read whatever the user gave you. Then ask only the questions still unanswered — do not interrogate:
- The business metric or pain point behind this, its current baseline and volume.
- Does the needed data exist, where, who owns it, is access/legal clearance in hand.
- Can they write a rubric or test cases that define a "correct" output.
- What happens, concretely, when the system is wrong — cost, safety, compliance exposure.
- Acceptable response time, and whether it is a hard real-time constraint.
- Whether a human can realistically sit in or over the workflow at the expected volume.
- Any regulatory, audit, or explainability obligations.
- What is explicitly in and out of scope; upstream and downstream systems.
- The numeric success target and the date by which it must be met.

If the user cannot answer a feasibility-critical item, record it in **Key unknowns** rather than guessing.

### 2. Feasibility assessment (five dimensions + four disqualifiers)
Score each dimension (strong / workable / weak), with one line of evidence each:
- **Data availability** — existence, access rights, cleanliness.
- **Task structure** — can success be specified and tested.
- **Error tolerance** — the real cost of a wrong output.
- **Latency tolerance** — design to P95, never the median.
- **Human-in-the-loop viability** — can a checkpoint fit the actual workflow and volume.

Then check the four hard disqualifiers. If any holds, say so plainly and stop recommending AI:
the problem is actually deterministic; the required data does not exist; error tolerance is
effectively zero; regulation forbids it.

### 3. Classify the problem
- Place it on two axes: **generative vs discriminative** (open-ended output vs a bounded category/score)
  and **retrieval vs reasoning** (surfacing known information vs inferring something new).
- Place it on the automation spectrum: fully automated / human-in-the-loop / human-on-the-loop.
- Apply the resolution order and recommend the simplest approach that can work:
  prompt first → add **RAG** only if the answer needs knowledge outside the model's training →
  consider **fine-tuning** only after a measured prompting ceiling → fall back to **classical ML**
  whenever the task is discriminative, bounded, labelled, and latency/cost-constrained.

### 4. Decompose the request
Treat the business ask as a bundle, not one task. Break it into component sub-tasks
(classification, retrieval, generation, routing, …). This routinely reveals that part of the
"AI system" is actually deterministic and should not use a model at all. Produce a per-component
table: task type, candidate approach, latency/criticality.

### 5. Write the document
Produce a professional markdown file (default `docs/scoping-<project-slug>.md`) with exactly these
sections:
1. **Problem statement** — the real business outcome, tied to a metric a sponsor cares about.
2. **AI approach category** — RAG / classifier / generative pipeline / agent / hybrid, one-line rationale.
3. **System boundary** — what it owns, what it explicitly does not, upstream inputs, downstream consumers.
4. **Success metrics** — business-level, numeric, time-bound (not model accuracy alone).
5. **Key unknowns** — what must be resolved before design proceeds.
6. **Stakeholder communication summary** — one plain-language paragraph a non-technical exec reads in under two minutes.
Add, when relevant: the per-component table; a fast-path vs slow-path split when a synchronous
decision and an asynchronous explanation coexist; an audit-trail component for regulated domains;
a feedback/retraining-loop component when ground truth arrives late.

## Quality gates (the document is not done until these hold)
- Metrics are numeric and time-bound. Reject "improve accuracy"; require "cut escalation rate from
  X% to Y% by <date>".
- Disambiguate loaded terms: "false positive rate" means different things to the business (share of
  all cases wrongly declined) and to operations (share of flagged cases that are false alarms) —
  state both when they appear.
- Separate containment (resolved without a human) from resolution and from satisfaction; do not
  collapse them.
- Latency targets are P95, not median; name the synchronous path separately from any asynchronous one.
- Every recommendation names its evidence or is moved to Key unknowns.

## Anti-patterns to avoid (flag them if the brief pushes you toward one)
- Treating the AI call as a bolt-on feature with no validation, fallback, or monitoring around it.
- Designing or prototyping before the feasibility pass.
- Leaving system-level ownership (integration, fallback, monitoring, governance) unassigned.
- Scoping the whole customer journey at once instead of one decomposed, buildable component.
- Declaring success on model/benchmark accuracy instead of a business-level system metric.

## Output and handoff
Write the file, then give the user a 3-line summary: the recommendation (fit / not a fit / fit with
caveats), the single biggest risk, and the next step. If the recommendation is "fit", the natural
next step is the `system-architecture` skill, which consumes this document.
