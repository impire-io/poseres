# Chapter 13 — The scorer diagnosis finds the rot: lifetime stability is the real frontier (2026-07-11)

Opened to answer "can the flat score basin be made informative?" and closed
having found something that outranks the question. The experience
dose–response first split the basin cleanly: the *error* surface is
experience-limited (4× training moved the honest prediction minimum to dim
28 and deepened it everywhere), but the *score* minimum stays
parsimony-pinned at 12 — the linear charge outruns the marginal gain at
every measured budget. Then the 16× scan broke the pattern: dims 8–24
**roughly doubled their error** between 2400 and 9600 episodes, consistently
across seeds. The longevity probe pinned the mechanism with both hands:
frozen honest error bottoms exactly where the weight norm turns from healthy
compression (20→18) to runaway growth (18→29), onset ≈ 400–800 live cycles
at obs=60, capacity-dependent — mid dims rot, dim 4 and dim 32 largely do
not. Rereading the E4′ censuses against the rot profile closed the loop:
the live scaled ecology's anchors sit at dims 4–8 — the rot-resistant dims —
and the "inter-age downward drift" is the rot differential compounding.
**Constant-lr continual learning is lifetime-bounded, the long-run ecology
selects for rot-resistance rather than structure quality, and every scaled
best_dim reading is downstream of this.** No fix shipped in this chapter —
the diagnosis is the deliverable; the named successor is the eighth
rule-class problem, lifetime stability, with per-tensor max-norm control as
the reference- and premise-preserving candidate (no freezing; the system
stays never-trained-then-frozen). Trail:
`hq/02-DESIGN/validate/SCORER-DIAGNOSIS.md`; committed together with this chapter.
