# The PRA Journey

The narrative record of this project: what was built, what was measured, what
was believed and then refuted, and what each chapter taught. Specs say what the
system *is*; this file says how we *got here* — including the dead ends, because
the refuted hypotheses are as load-bearing as the shipped code.

> **Keeping this file alive:** whenever a feature lands, a research
> investigation concludes, or a load-bearing decision is made, append a chapter
> (or extend the current one). Follow the template at the bottom. Honesty rules
> apply here as everywhere: record what actually happened, including failures,
> reversals, and findings that contradicted expectations. This rule is anchored
> in `AGENTS.md`.

---

## Chapter 1 — Vision and design (up to 2026-06-20)

The goal: a **continuously-learning machine intelligence** — a configurable
body, a fixed innate drive, and a brain (the Pose Resolution Architecture) that
learns and restructures itself online, never trained-then-frozen. The design
was written as seven documents (`design/01`–`07`) with validation-maturity tags
([V] validated / [D] designed / [O] open problem), plus two normative specs:
PRA-01 (the system) and PRA-02 (the acceptance suite T1–T6 + investigatory
T-SCALE). The strategy: validate the risky core in a synthetic world before
building anything else.

## Chapter 2 — Prototypes and the STEP-0 gate (June 2026)

Four throwaway prototypes (`design/validate/pra_sim*.py`) evolved the scoring.
The **STEP-0 gate caught v3 red-handed**: its load-bearing dimensionality
result (T4) passed only at a lucky 18-cycle horizon and collapsed at 30, and
its population grew without bound. Diagnosis: the survival score was gameable —
pose-space prediction (a collapsed frame aces its own trivial pose), cherry-
picked scoring (frames graded only on what they elected to map), no parsimony,
and an eviction threshold scaled in the wrong direction. v4 fixed all four
(observation-space prediction, coverage-fair EMAs, `w_complexity·dim`, a
threshold that *divides* by crowding) and passed T1–T6 honestly.
**Lesson that became the project's constitution: read the spread, not the mean;
judge across horizons, not snapshots; never let the system grade its own
homework.** Commits `8b8c802`, `a6e6c6c`, `31dd186`.

## Chapter 3 — Feature 001: the validation harness + batched core (2026-06-21)

Adopted GitHub Spec Kit (`be5aea9`) and folded harness + real core + batching
into one feature. Built the `pra` package: the batched, `dim`-grouped
FrameGroup kernel (PRA-01 §7.2's hard requirement), five swappable seams (Bus,
Scorer, ProposalPolicy, DecayPolicy, EventSource), deterministic telemetry, and
the `pra-validate` CLI (suite / determinism / scale). The new core reproduced
the v4 oracle's trajectory **near bit-for-bit at ~40× the speed**, byte-identical
on re-run. T1–T6 all PASS at the reference (T4 within-one majority at every
checkpoint: 8/8, 8/8, 6/8). T-SCALE became runnable — and reported `best_dim≈1`
at `true_dim ∈ {20,35,50}`: the scale question was formally open. Commits
`7387bd7` → `d17354c`.

## Chapter 4 — The T-SCALE diagnosis: six scale-invariance rules (2026-06-29 → 07-06)

Why does structure-finding collapse at scale? A new `pra-validate scan`
diagnostic (train one frame per candidate dim with equal experience, measure
honest error) peeled **five compounding layers**, each a constant validated at
the reference scale silently leaving its regime:

1. the world's tanh emission saturating into a sign channel (pre-activation sd
   = √true_dim);
2. the learning rate diverging at obs_dim=60 (the binding constraint that
   masked everything else);
3. the init scale saturating newborn frames;
4. the linear parsimony penalty overwhelming the flattened error span;
5. the maturation window evicting candidates on transient scores (patience
   2/12/24/29 → mean best_dim 4.7/5.7/6.7/10.7 — dose–response).

All six fixes shipped as **reference-preserving effective rules** (every factor
exactly 1 at the reference scale, verified bit-for-bit). One seed climbed to
**dim 18 of a true 20**. The 8-seed scaled reference: medians 8 / 10.5 / 9.5 at
td 20/35/50, minimum 4 across 24 runs — no collapse anywhere. **The finding:
structure-finding survives scale; its convergence *rate* does not** (the ±1
ladder covers ~constant rungs per budget; the [O] proposal policy is the open
lever). Honest side-finding: even the validated system barely beat the
persistence baseline (0.157 vs 0.165) — which led directly to hardening T3 with
a learned-persistence ablation (`9c4db1a`). Also: parallel seed execution
(byte-identity proven), suite 132s → 21s (`c16f76b`). Trail:
`design/validate/SCALE-DIAGNOSIS.md`; commits `02559ca` → `647c50f`.

## Chapter 5 — Feature 002: motivation & action — the system becomes an agent (2026-07-07)

Doc 05 built: Drive seam (pure functions, structurally immutable parameters —
the system cannot rewrite its own drive), curiosity default (windowed learning
progress + novelty with automatic cold-start handover), Policy seam whose
default reproduces the old random draw **exactly** (the T1–T6 gate stayed
byte-identical), one-step curiosity lookahead, multi-drive mechanism, and the
`pra-validate agency` command with the new **T7** verdict. The honest-criterion
story: the planned sign-majority bar was measured first (3/8 — FAIL), found to
be degenerate for continuous margins near zero, and openly replaced with
one-sided noninferiority — the pre-registered claim was "directedness does not
hurt". Result at reference: curious ≈ random (margin −0.006 ± 0.036) — PASS,
equivalence. Commits `5e40bad` → `f6ac721`.

## Chapter 6 — Feature 003: state persistence (2026-07-08)

Doc 06 built: the complete learned state (frame tensors, drive bookkeeping,
counters, summary accumulators, RNG state, config in force) serializes to a
versioned, pickle-free blob through an atomic SnapshotStore seam. The build
exceeded the spec's bar ("a valid continuation"): **a run resumed from any
cycle-boundary snapshot is byte-identical to the uninterrupted run**, in both
policy modes — provable because consolidation boundaries fall between episodes,
so the world (environment, never snapshotted) is re-derived from the seed
prefix while the generator state is overwritten. Opt-in; validated modes stay
byte-frozen and file-free. Commits `03ad67e`, `4391910`.

## Chapter 7 — The agency diagnosis: curiosity loses, competence wins (2026-07-08)

The scaled T7 measurement failed: novelty-directed curiosity was
*systematically worse* than random at td=20 (margin −0.062, better in 1/8, 87%
directed). Five controlled experiments hunted the mechanism, refuting four
hypotheses with data: tanh-saturation walk (flat), fit-gate starvation (the
curious arm maps *more*), preference reshaping (two candidate shapes turned out
order-isomorphic — no help), action-marginal skew and walk extent (both ≈
random). The decisive control: a **content-free** state-coupled policy is
neutral (+0.014), while the **inverted** preference — familiarity-seeking —
beats random (+0.067, better in 6/8). The harm was the *content* of the novelty
preference: in a uniformly learnable world, spreading experience thin is a pure
cost and concentrated practice a pure gain. The remedy was already anticipated
by Doc 05 §5: a **CompetenceDrive** (mastery + familiarity), shipped in the
drive registry, selected by pure configuration — **T7 PASS at both scales,
beating random in 6/8 seeds at each (+0.064 scaled, +0.027 reference)** — the
project's first measured net-positive directed exploration. Open [O]:
the curiosity/competence blend for worlds with unlearnable regions (camping
risk), predicted-learning-progress lookahead. Trail:
`design/validate/AGENCY-DIAGNOSIS.md`; commits `1953832`, `41cfed2`.

---

## Where things stand (2026-07-08)

Built and validated: the batched sensorimotor core + structural learning
(Docs 03/04), motivation & action (Doc 05), state persistence (Doc 06), and the
honest harness (T1–T7, determinism, scale, scan, agency) with parallel seed
execution. **Unbuilt: Doc 02 (anatomy & bus — real sensors/actuators).** Open
research: the [O] high-dim proposal policy (convergence *rate* at scale), the
curiosity/competence blend, T3's persistence clause at scale.

## Recurring principles (what the journey keeps teaching)

- **Diagnose before fixing; one variable at a time.** Both diagnoses found the
  true mechanism only after refuting the obvious story with data.
- **Reference-preserving changes.** Every scale rule and every new layer keeps
  the validated behavior byte-identical; regressions are structurally
  impossible, not merely unlikely.
- **Honest criteria, amended openly.** When a pass-bar proved degenerate
  (T7), it was replaced in the open with the raw numbers recorded — never
  tuned quietly until green.
- **Negative results are results.** "Curiosity hurts at scale" produced the
  project's best positive finding one experiment later.

---

## Chapter template (append below)

```markdown
## Chapter N — <title> (<dates>)

<What happened, in a few sentences: the question, what was built/measured,
the honest outcome with key numbers.>
<What was refuted or reversed, if anything.>
<What it taught / what it opened.> Trail: <docs>; commits <hashes>.
```
