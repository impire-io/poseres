# Coupling promotion — the deficit gate ships on timing-primary bars

**State:** active
**Started:** 2026-08-10

## Abstract

The deficit→value coupling is measured on two bodies (episodes 0083,
0084): the dial is monotone in deficit, sated curiosity survives,
and the survival effect is decisive (+4 lives on C1 at a biting
drain; 0 vs 16 deaths on the sample field). It failed only its
original *aggregate-share* bar — the summary Doc 0010 now records
as mis-targeted, with the mandate that any promotion be judged on
**timing** (crisis behavior and survival), frozen before the run.
The owner has called the promotion ("promote the coupling with a
timing-primary bar"). This topic is the promotion's registration:
the shipped form, the closure requirement, and the timing-primary
bars.

## The question

Does the shipped, additive, off-by-default deficit gate — promoted
from the six-line instrument into `CompletionItchPolicy` /
`RecipePolicy` (feature 042) — reproduce the measured coupling
behavior exactly, judged by the timing-primary criteria the
instrument earned?

## The shipped form (frozen; general vocabulary)

Constructor parameters on `CompletionItchPolicy` (inherited by
`RecipePolicy`), keyword-only, defaulted off:

- `deficit_index: int | None = None` — the sensed homeostatic
  channel (the meter).
- `deficit_kappa: float = 0.0` — the gating gain.

Per directed step, the **effective label weight** becomes
`label_beta + deficit_kappa · clip(1 − obs[deficit_index], 0, 1)`,
applied at both existing label sites (the completion read and, in
`RecipePolicy`, terminal selection). `deficit_index=None` or
`deficit_kappa=0` MUST be bit-identical to v1.3.0 behavior (no
extra observation reads, RNG untouched). Validation:
`deficit_index` requires `label_index`; `deficit_kappa ≥ 0` finite.
No new snapshot state (pure policy arithmetic). Surface additive:
inventory + Doc 0008, version 1.3.0 → 1.4.0.

## Pre-registered bars

- **Bar P1 — closure by behavioral identity:** the shipped gate
  (arm run with `label_beta=0, deficit_kappa=0.1, deficit_index=`
  the energy channel), replacing the instrument subclass in the
  *unchanged* archived runners, reproduces episode 0083's W1 arm
  and episode 0084's T2 arm **row-for-row** against the archived
  row files (every recorded per-seed field identical). This is the
  bar that carries implementation risk; P2/P3 are then arithmetic
  on the same rows, stated openly.
- **Bar P2 — timing-primary, C1 body (anchors from 0083):**
  crisis-bin (deficit > 0.3) nourishing share ≥ **2×** the
  uncoupled arm's (anchor 0.741 vs 0.334 = 2.22×); survival gap ≥
  **4** seeds (anchor 4); sated rotation ≥ **12/24** (anchor 22);
  chains ≥ **18/24** (anchor 24).
- **Bar P3 — timing-primary, second body (anchors from 0084):**
  hungry-bin nourishing margin ≥ **+0.15** (anchor +0.216) and
  coupled deaths ≤ **half** of uncoupled (anchor 0 vs 16).

## Reversal condition

If P1 fails — the shipped arithmetic diverging from the instrument
on any row — the divergence is diagnosed before any merge; the
feature does not ship on "close enough." If P2/P3 fail *after* P1
passes (impossible unless the archived rows themselves fail the
bars), the registration is inconsistent and returns to the owner.

## Verdict

<Empty until graduation.>
