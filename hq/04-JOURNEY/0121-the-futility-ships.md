# Episode 0121 — Futility ships: the brain gives up on a blocked place, and peeks back (2026-08-29)

Feature 045 / v2.3.0 — the first rung of the mechanism ladder design
[0021](../02-DESIGN/0021-the-long-carry.md) registered, promoted
from the-long-carry's rig prototype into the kernel within a day of
the topic's graduation. `RecipePolicy` gains `futility_k` /
`futility_w` (keyword-only, off by default): a subgoal pointer that
makes no progress for K followed steps poisons the pointed PLACE —
the subgoal on the block grid — for W selection steps; every recipe
currently pointing there is ineligible together; with none eligible
the policy is exactly its parent (the wander phase); expiry is a
clean peek, so re-poisoning takes K fresh steps and the
revive-peek-wander cadence emerges from the constants alone
[measured at rig grain, episode 0120: K=200/W=800 abolished a
4,672-step futile press and produced the larder arena's first
brain-driven crossings]. Off is bit-exact pre-045 behavior, RNG
stream included [measured: the three-arm parity test — default,
explicit off, armed-but-never-firing — identical action streams and
generator states]. Full gate green, nothing skipped.

Nothing was refuted here; the two already-refuted forms became
constraints. The ONLY futility state is per-place, excluding by
construction naive per-recipe erosion (boundary thrash, 556
die/revive events in one rig life) and per-recipe hysteresis
(cohort fallback among ~15 near-identical recipes) — both pinned by
tests that stage the cohort and count zero fallback presses at the
poisoned place [measured].

What it opened: the promoted form generalizes the prototype — the
rig's layer-wide fatigue is the place-keyed mechanism's degenerate
case when every pointer coincides, so the measured crossings carry
over [mechanism-argument]; the shipped defaults (off; K=200/W=800
as the documented operating point) await their next measured
reading on the revived arena. Rungs 2 (process recipes) and 3
(stage-conditional selection) remain, and rung 2 already leans on
this one: a dying process recipe's stalled subgoal must poison the
turn-in place, or the lap recipe dies with its cohort.

Reversal condition: an arena-revival reading where the place-keyed
form fails to reproduce the prototype's behavior — the futile press
returns, or fatigue events run far beyond genuine stall episodes
(the thrash signature) — reopens the promoted form with those
numbers; 0120's standing conditions on the ladder itself transfer
unchanged.

Trail: spec/plan/tasks `specs/045-progress-keyed-futility/`; design
0021 (rung 1 marked shipped), Doc 0008 (surface + 2.3.0 note), Doc
0010 (mechanism), Doc 0011 (dial rows + section), CHANGELOG
[2.3.0]; commits d57aff3 (spec), d4b7a00 (plan), 37fd773 (tasks),
27493db (the mechanism, v2.3.0).
