# What the head learned about digging (live reading, 2026-08-13)

`arms/head_reading.py` read the taught brain's event head (3,375
taught updates, frozen W) at nine REAL observations on the live server
— the contexts a foraging life faces at the patch. Per the live-world
evidence rule; rows in `arms/head-reading-rows.json`. Key channels:
food (6), held-intention progress (14), pocket total (15); itch term
κ·Δprogress at κ = 0.25; completion threshold 1/128 ≈ 0.0078.

## The head's knowledge, measured

| context | dig d_prog | use d_prog | use d_food | max d_pocket (any action) |
|---|---|---|---|---|
| melon ahead (sated or hungry, any hand) | **+0.43** | +0.018 | ≈0 / −0.02 | +0.0020 |
| holding a slice, hungry | +0.43 | **+0.034** | −0.003 | +0.0011 |
| mid-dig (progress 0.13) | +0.30 | +0.034 | −0.004 | −0.0002 |
| NOTHING ahead (the parked context) | **−0.017** | +0.029 | −0.003/−0.019 | +0.0005 |

Three findings, one mechanism chain:

1. **Digging was learned well, and truthfully.** A melon ahead: the
   head predicts cracks at +0.43 and the itch term (+0.108) stands
   ABOVE the drive band (0.06–0.15, Doc 0011) — dig wins selection,
   which is why the life dug its one classroom melon (seg 1 collect).
   Nothing ahead: the prediction flips to −0.017 — the head correctly
   knows digging air makes nothing, so the itch offers nothing at the
   parked stand. The dig knowledge is not the gap.

2. **The chew was learned faintly — an order of magnitude too faint.**
   `use` holding a slice predicts progress +0.034 (13× weaker than the
   dig's +0.43; lessons gave the chew ~6 progress ticks per lesson vs
   ~30 for the dig), and its pay was never learned at all: `use`
   predicts d_food ≈ 0 to NEGATIVE in every context — the +2 food rise
   landed on split samples (amendment 3's skew) too rarely to survive
   NLMS against ~450 zero-outcome use steps. The itch's chew term
   (+0.007) is therefore buried an order of magnitude below the drive
   band: even starving with food in hand, eating never surfaces in
   selection. (In the parked context `use` IS the itch argmax — at
   +0.007, which the drives drown.)

3. **No completion fires anywhere — the deficit gate is connected to
   nothing.** Max predicted pocket delta across all nine contexts and
   all actions: +0.0020, four times below the 1/128 threshold. Live,
   the pocket pays SECONDS after the break (drop physics + pickup),
   never on the dig transition the one-step head could pair — so the
   head never learned that anything yields wealth, completions never
   fire, and the 042 gate (which reads only at completions and
   recipe-terminal selection) gates nothing. The fake paid the pocket
   on the break tick, which is exactly why the fake pilot ate and the
   live life parked.

## The senses-first question this reading forces

The lesson's collect-walk worked because the tape walked blind; a life
cannot — **the body has no sense for food lying on the ground**. The
drop is a world object (an item entity, position and kind the game
knows) that the anatomy cannot see, so "walk toward the drop" can
never become a predictable, completable act. Candidate (owner's call,
NOT registered): a drops channel in the survival instrument — nearest
drop's bearing/distance/count as properties + signature, feature-033
grammar — plus eat-heavier teaching so the chew's progress signal and
its pay reach the drive band. Whether to add the sense, re-weight the
teaching, or return the reframe to design is the owner's decision.
