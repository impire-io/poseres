# Sequence encoding — how does an unbounded past fit through a fixed-width sense?

**State:** active
**Started:** 2026-08-23

## Abstract

Episode 0042's teacher-world gate has one prerequisite left:
observation encoding for unbounded sequences. The kernel's
observation is a fixed-width vector; a sentence-so-far is not. This
topic runs the question derisk-small, in the 0112 lab tradition: a
scripted deterministic teacher, a tiny token inventory (vocabulary
scale was answered in 0112; flat actions suffice here), and the
encoding of the sequence-so-far as the ONE variable — a
last-K-token window, an exponential recency summary (unbounded
length, fixed width, lossy), or both — every encoding
body-declared, zero kernel change. The discriminating structure is
dependency length: a repeating template of period P breaks a window
shorter than P by construction, while a decay summary carries a
soft count no window holds. A decisive answer either hands the
teacher-world its declared sense (and the plateau prediction its
first sub-test), or measures where every fixed encoding breaks —
which is the hierarchical-frames gate arriving early, with numbers.

## The question

Which fixed-width, body-declared encoding of the unbounded
sequence-so-far lets the kernel learn a sequence world — and where
does each encoding measurably break, as a function of the world's
dependency length?

## The world (declared functionally; exact mechanics journaled before the rig)

The **echo-teacher world**, on the kernel's EventSource seam: the
subject emits one of m tokens per step (m ≤ 8, flat actions — the
validated regime); a scripted teacher holds a declared target
structure and answers in the observation itself (a feedback channel:
progress/accept/violation), the world's only voice. A completed
conforming sequence is accepted and the target re-seeds — the redraw
novelty that makes acceptance drive behavior, no reward wire, the
dial world's grammar exactly. Structure families, each with a
dependency dial:

- **R(P)** — repeating template of period P ∈ {2, 4, 8, 16}: pure
  positional memory; a window of width K carries it iff K ≥ P by
  construction.
- **C(n)** — counting, AⁿBⁿ with n ∈ {2, 4, 8}: no finite window
  carries it; a decay summary holds a soft count. This family is
  where 0042's plateau prediction bites earliest, and it is
  registered as its first sub-test.

Encoding arms (senses, declared at the body): **W-K** — last K
tokens as K scaled channels, K ∈ {1, 2, 4, 8}; **DK** — recency-
weighted sum of token one-hots (λ = 0.5), width m, unbounded
horizon; **WD** — window-4 plus the decay summary. Feedback and
length channels identical across arms.

## Pre-registered bars

Protocol: 24 seeds per arm, one experience budget per rung frozen at
calibration with the thresholds (the 0112 freeze pattern; no
comparison arm before its thresholds froze counts). Instruments,
trail not bars: an oracle producer (scripted perfect knowledge of
the target — the production ceiling per rung) and a random-policy
floor, margins set against ceilings per the 0112 lesson.
Acceptance rate (accepted sequences per 1k steps, back half) is the
behavior meter; feedback-prediction error (the head anticipating
the teacher's answer — 0042's own "a systematic teacher makes
sensible utterances more predictable") rides as a registered
secondary reading.

- **Bar Q0 — the world calibrates:** some encoding arm on the
  easiest rung (R(2)) performs — acceptance beats the random floor
  by a margin frozen at calibration with the budget and all
  thresholds. The world may be revised openly during calibration;
  after the freeze it may not.
- **Bar Q1 — the wall is where the arithmetic says:** W-K passes
  rungs with P ≤ K and fails rungs with P > K (acceptance above /
  below the frozen lines) — the encoding, not the kernel, is the
  binding constraint, shown by the same kernel passing both sides
  of its own window.
- **Bar Q2 — beyond-window competence (headline):** a declared
  encoding containing no window of width ≥ P still passes R(16)
  (the DK or WD arm), or carries C-family structure no window
  passes — the fixed-width sense provably transmitting a longer
  past than it stores positionally.
- **Bar Q3 — the counting sub-test (the plateau prediction's first
  reading):** some arm passes C(4) at the frozen acceptance line.
  PASS makes the vision cheaper, exactly as 0042 wrote; FAIL at
  every encoding is the prediction's first measured support at the
  encoding layer, and hierarchical structure becomes the named
  gate with numbers attached.

## Reversal condition

- **Q0 fails after honest calibration** (no encoding performs on
  R(2)): the kernel cannot learn this sequence world at any
  encoding — the problem is upstream of encoding, the topic
  graduates to design carrying that constraint, and the
  teacher-world gate is blocked at the kernel, not the sense.
- **Q1 inverts** (W-K fails P ≤ K, or passes P > K): the window
  arithmetic is not what binds — the mechanism story is wrong and
  must be diagnosed before any Q2/Q3 claim is made.
- **Q2 and Q3 both fail with Q0/Q1 passing:** every fixed encoding
  is bounded by what it positionally stores; the teacher-world can
  proceed only with declared bounded context, and the plateau
  prediction gains support. Routing: design (the constraint is
  design content either way).
- Standing guard: thresholds frozen before arms; instrument
  readings are trail; one structure family change mid-topic
  requires an openly journaled amendment with numbers.

## Verdict

Measuring complete 2026-08-23; graduation routing is the owner's
call. The bars, as registered and as amended:

- **Bar Q0 — PASS** [measured]: every encoding performs on R(2)
  (medians 10.0–19.8 vs floor 3.077, oracle exact 250); the kernel
  learns sequence worlds through body-declared senses, unmodified.
- **Bar Q1 — INVERTED, diagnosed** [measured]: W4 failed its own
  covered rung; the acceptance meter demands 2P consecutive
  corrects (exp(T) fidelity) while learning plateaus
  budget-invariantly at 0.53–0.68 violations/step (2× budget moved
  it ≤ 0.003). The wall was never the window.
- **Bar Q1′ (amended) — FAIL as frozen** [measured]: pulse errors
  fall at harder rungs because collapsed behavior trivializes the
  stream; no window-edge step is visible through the artifact.
- **Bar Q2′ (amended) — PASS as frozen, caveat stated** [measured]:
  DK-over-W8 advantage grows +0.1001 (clause 0.03) to R(16); the
  growth reads width-under-load at least as much as horizon.
- **Bar Q3 / Q3′ — FAIL both forms** [measured]: C(4) dark on
  acceptance for every arm; the pulse comparison void by the same
  collapse (advantage growth −0.0497). At comparable competence the
  counting signal is real: DK leads C(2) outright — behavior 25.5
  vs W2's 19.7 (8.3× floor), pulse advantage +0.0522 over W4, while
  mid-field on phase structure.

Load-bearing claims: **the encoding was never the binder — the
competence envelope is** [measured: every encoding works inside it;
behavior collapses beyond it regardless of encoding capacity];
**structure–encoding affinity is real at comparable competence**
(the soft-counter leads counting, windows lead phase) [measured];
**width costs more than information at this scale** — narrower beat
wider on behavior, conformity, and anticipation at nearly every
rung [measured]; **the plateau is the kernel-and-drive's, not the
sense's** — one-step curiosity sustains partial conformity
(0.53–0.68 violations vs random's exact 0.750) and no meter
survives past it [measured; the mechanism split between drive
alignment and frame capacity is undiagnosed — a named successor,
not a claim]. Instrument lessons banked for the teacher-world:
acceptance-style meters die exponentially in sequence length;
anticipation probes are behavior-coupled and arbitrate only at
comparable competence [measured]. Confounds as journaled: one
world, m=4, one drive configuration; the plateau's mechanism
unattributed.
