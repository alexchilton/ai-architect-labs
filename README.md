# AI Architect labs

Runnable notebooks and artifact-producing skills built from the ideas in the Udemy course
*AI Architect: Enterprise AI System Design* — RAG, agents, model strategy, enterprise
integration, governance/security, evaluation, and cost/LLMOps.

The notebooks run against local Ollama (qwen + bge-m3) where it fits, falling back to an
API model only where the reasoning needs it. Same discipline as the companion
`ai_security_labs` repo: every notebook is executed clean and only claims what it measured.

See `docs/PLAN.md` for the module → notebook/skill mapping and build order.

## Layout

    notebooks/        runnable examples, one per concept (Track A)
    .claude/skills/   skills that produce the architect's deliverables (Track B)
    docs/PLAN.md      the build plan
    transcripts/      course transcripts — GITIGNORED, paid content, local only

## Copyright

The course transcripts are paid content: they stay local, are gitignored, and are never
committed or reproduced. The notebooks and skills paraphrase the concepts and build
original examples.

## Run

    ollama serve
    ollama pull qwen3-coder:30b     # or qwen2.5:7b for lighter work
    ollama pull bge-m3              # embeddings
    jupyter lab notebooks/
