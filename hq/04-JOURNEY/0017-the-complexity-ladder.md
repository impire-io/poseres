# Chapter 17 — Feature 005: the complexity ladder — every failure names its cause (2026-07-13)

ROADMAP A3, spec-kit flow start to finish in one arc (spec → plan → tasks
→ implement → first results). Three opt-in worlds, each **one known
difficulty axis** off the validated staircase, behind the existing
`EventSource` seam with zero engine changes: `nonuniform` (a half-space
region of latent space with irreducibly random transitions — the A4
noisy-TV/camping testbed, with world-side occupancy counters),
`compositional` (factored dynamics via mask-after-draw under the joint
emission, so parts never leak through channels), `distractor` (appended
channels from an autonomous drift latent, dial to pure noise). One
load-bearing spec amendment before planning: non-uniformity must be
**state-dependent** (a region policies can seek or avoid), not channel
noise — channel noise is exposure-constant under every policy and
measures nothing about drives; it folded into the distractor dial
instead. Every rung's degenerate dial is **byte-identical** to the
reference world (integration-tested — the discipline that also guards
the deliberate duplication of the byte-frozen reference core), ground
truth lives behind a harness-only accessor, and `pra-validate ladder`
runs pre-registered criteria (LADDER-CRITERIA.md, committed before
results) as investigatory verdicts. 193 tests green, 36 new.

First results (one instrument run, 103 s, six dial sets): **the ladder
works exactly as designed — each verdict is attributable.**
L2 **PASS** at both factorizations, with the census answering the
pre-stated open question: selection lands **part-sized** (best_dim 2–4,
populations at the part scales, no seed buying the Σd_k = 6 monolith) —
the parsimony finding recurring compositionally. L3 structured **PASS**
(selection never buys a *predictable* distractor), but L3 noise **FAIL**:
half the observation carrying unit-scale static collapses the landing to
dim 1 in 5/8 seeds — **channel-noise robustness**, the ladder's first new
open problem, named with its reproducible failing configuration. L1
FAILed as written and the diagnosis split it honestly: the structure
clauses pass at mild noise (7/8, 8/8) and genuinely degrade at strong
noise (4/8 — dose-dependent, real); what broke at mild noise was the
**criterion's occupancy band** — per-world occupancy is drift-dominated
and bimodal (each world's four fixed displacements carry a net latent
drift that dwarfs episode starts), not concentrated at the analytic ½.
Amended openly per the T7 precedent (numbers kept; the amended clause
certifies what A4 actually needs: per-seed occupancy baselines,
non-degenerate); amended verdicts from the same table: mild PASS, strong
FAIL. Chapter lesson, now thrice-learned and once pre-empted: write the
criterion first, and when it breaks, diagnose *which* broke — the claim
or the measure — before touching either. Trail:
`hq/02-DESIGN/validate/LADDER-CRITERIA.md`; A4 is unblocked with its baselines
in hand.
