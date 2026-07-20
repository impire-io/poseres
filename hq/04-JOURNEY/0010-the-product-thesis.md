# Chapter 10 — The product thesis: an OSS brain for makers (2026-07-08)

The question was not technical: what is PRA *for*? Until now the honest answer
was "an academic exercise" — every document specified the system, none named a
user. Decision: **PRA is an OSS product for hobbyists and makers** — install in
one command, mount a world through the Body API, watch it learn live, keep and
share what it learned. Explored and rejected along the way: Minecraft-first
onboarding (setup friction + real-time non-determinism + the brain isn't ready
to look good in it), an MMO (Artifacts) as a lab (3–30s enforced cooldowns —
kept instead as a future long-horizon *deployment* showcase), and an embedded
Go game server (viable only as a tick-steppable fork; parked with the idea
recorded). The load-bearing sequencing principle that fell out: **research
gates before showcase spends** — the bottleneck is the brain, not the
plumbing, so no user-facing milestone ships ahead of the capability that makes
it worth watching. The plan is `ROADMAP.md` (milestone-gated, no dates);
`GETTING-STARTED.md` shipped alongside it as the first Phase-B artifact.
Amended same day: the original non-goals list was partly wrong. Distributed
operation (the Doc 02 bus seam's purpose), tool self-invention ([O] since the
design docs), and the long-range paradigm claim are *horizon ambitions*, not
non-goals — with the positioning sharpened: PRA competes with **frozen**
intelligence (trained-then-deployed) on continual learning and online
restructuring, not with LLMs on language. Remaining non-goals: benchmark
theater, hosted services, language/knowledge competition.
Trail: `ROADMAP.md`, `GETTING-STARTED.md`; commit follows.
