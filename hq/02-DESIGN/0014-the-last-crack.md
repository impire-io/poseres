# 0014 — Commitment: the hold that finishes

**Status:** design (graduated from research topic the-last-crack,
2026-08-15, [episode 0101](../04-JOURNEY/0101-the-last-crack.md)).
Opt-in in `CompletionItchPolicy` today, defaults bit-exact with the
shipped byte-frozen behavior (RNG streams included); promotion into
the default operating point is a spec-kit feature this document is
written to argue. Every rule carries its measurement.

## The problem it closes

The action vote is re-fought every frame, and a multi-frame held
intention (a live dig: ~30 consecutive frames) must win every single
vote. Measured (L1, parked geometry): the hold's per-step margin is
only κ·Δ̂ ≈ 0.008 while frame-to-frame drive noise flips the ordering
by up to 0.069, and the ε-gate (0.1) breaks even winning holds —
survival by chance ≈ 0.9³⁰ ≈ 4%. Live worlds reset progress on
release (vanilla block damage), so near-misses pay nothing: the
shipped policy completed **0 digs in 4,500 parked steps**.

## The mechanism (three rules, one concept: intentions outlive frames)

1. **Incumbency** (`commit_kappa`, measured point 0.1 — above the
   largest observed flip margin 0.069): the candidate that repeats the
   previous emitted action earns +κ_c while the intention is
   ADVANCING — sensed progress rose since the previous frame, or sits
   pinned ≥ 0.995 awaiting the world's own confirmation. Hysteresis
   against knife-edge noise; inert when nothing advances.
2. **Exploration defers to a live hold** (`explore_defers_holds`):
   the ε-gate's uniform draw still happens (draw-order parity), but a
   would-be exploration is overridden to the directed path while the
   intention advances. ε returns in full at every boundary.
3. **The intention boundary**: a progress COLLAPSE (drop > 0.5 —
   the world's own completion/reset) clears the incumbent before the
   vote. Incumbency dies with its intention; the next vote runs
   fresh. Without this rule the mechanism is an addiction machine —
   measured: a 517-frame DIG lock across breaks (perseveration, the
   twin).

## Proof of function (L2, 3-repeat parked pair)

Flags off: 0 breaks / 0 eats in 4,500 steps. Flags on: 10 breaks, 11
collects, one full chain — contact → dig → break → collect → 6 eats
to satiation, **first eat step 333** (record best before: 1,119).
Flags-off bit-exactness: the full gate + byte-frozen T1–T6 green; 25
unit tests in `test_completion_itch_policy.py` pin all three rules.

## Composition notes

- Composes below the recipe layer and beside the itch: no new
  observation channels, no config fields yet (constructor kwargs).
- The deficit gate (042) and the label (041) are untouched; commitment
  amplifies whatever the vote already prefers — it does NOT create
  preferences. The faint chew (head-reading 2026-08-13) remains faint
  under commitment; commitment only stops its rivals from being
  broken mid-hold.
- Motivation-stack placement: the missing rung between the completion
  itch (G3) and borrowed goals — each layer patches the twin below
  and brings its own (this one's: perseveration; patched by the
  boundary; watch it in long lives).

## Promotion checklist (for the spec-kit feature)

Config fields (`commit_kappa`, `explore_defers_holds`) with 0.0/False
defaults; the frozen-suite parity test at the config layer; a
free-roam (non-decree) reading that the flags lift completed digs and
eats over the flag-off floors — the native-survival N2/N3 re-run is
exactly this measurement.
