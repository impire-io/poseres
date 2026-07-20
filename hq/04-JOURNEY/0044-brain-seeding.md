# Chapter 44 — Brain seeding: the head start is real, relevant, and compounds (2026-07-20)

The ROADMAP's compounding-intelligence horizon (ch. 42), made runnable and
measured. The question: does a snapshotted brain used as a *seed* give the next
brain a head start, is that head start *relevant transfer* rather than mere
maturity, and does it *survive chaining* across a body-growing hop? Built as
feature 028 through the full Spec Kit flow, entirely as orchestration over the
unchanged engine — no core edits. Two opt-in rover seams (a harness-owned
`layout_seed` so maps A/B/C are the same body with different obstacle layouts;
a *permuted rover* — action/sensor wiring scrambled at construction, learnable
but unrelated — for the maturity control), and a `pra-validate seeding` harness
that pre-trains → captures a snapshot → resumes on a new map, reading the
per-step prediction-error trajectory back out of `SystemState.pred_errors`. Time
to competence τ = the first probe-map step where the smoothed error crosses a
strict competence line; three arms per seed (seeded / fresh / maturity),
warmup-length-fair common-length censoring, the repo's one-sided ±1.9·SE bars.

**All three bars PASS at 24 seeds. B1** (transfer): seeded reaches θ_B before
fresh, +871, 21/24. **B2** (transfer not maturity): seeded before the
equal-experience unrelated control, +1186, 19/24. **C1** (compounding): the
seeded chain, grown by one sensor (obs_dim 10→11, a clean back-ray via the Doc
02 tool path → `FrameStore.resize`) and dropped on map C, beats fresh-C 24/24
(+1048), and the **head start does not shrink across the hop — it grew**, delta
+177 (non-shrink PASS). Median τ tells the story bare: on B, seeded 58 vs fresh
814; on C, seeded 14 vs fresh 821 — the transferred structure re-uses on a
third map *through a body change*.

Two honest findings the measurement forced. First, **the maturity control is, at
a strict competence line, mildly *worse* than a blank brain** (median τ 853 vs
814 on B): a mature brain from an unrelated world carries confidently-wrong
structure that must be unlearned before it helps — so B2 is the strongest
possible honesty check, and seeded clears it decisively. This also means the
reversal condition's suspect — earned persistence — is *exonerated*: it protects
the transferred frames for free rather than forgetting them. Second, the
pre-registered θ rule (p = 0.5 of the fresh initial→plateau gap) was **refuted by
the pilot as degenerate** — the rover curve drops so steeply that p = 0.5 gives a
line crossed inside the first cycle, and a loose line is reached almost instantly
by *any* mature brain (it tests maturity, not transfer). Amended openly (the T7
precedent): θ is a fresh-arm-only quantity — the strictest line all fresh seeds
reach (0.30 on the 10-dim map, 0.33 recalibrated on the 11-dim map) — and the
full θ-sweep is reported so the strictness dependence of B2 is visible, not
hidden (B1 and C1 are decisive at every line; B2 is variable at intermediate
lines).

What it opens: brain snapshots are usable seeds across rover maps *and* across a
`resize()` at reference scale — the first measured transfer benefit through
anatomy growth (previously only bit-preservation was guaranteed). Named
successors: resize-*magnitude* dependence, deeper chains (A→B→C→D), and
non-rover worlds. Trail: `hq/02-DESIGN/validate/SEEDING-DIAGNOSIS.md`,
`specs/028-brain-seeding/`; commits `1661fd4` (spec+US1 core), `844a38e` (US1
tests), `bd69e0b` (frozen pre-registration), `55d1576` (US2 + hop-1 verdict),
and this chapter's.
