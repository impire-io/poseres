# lean-worlds — investigation journey (started 2026-08-17)

## 2026-08-17 — the calibration ladder, declared before the walk

The rig is the 0109 rig restored from its trail (commit 7af05d6) on
its own world (`lw1-minecraft`, port 25604; C1/N1 untouched):
subject, fabric, segments, instruments unchanged. `lean.py` adds the
parametric world and the meters.

**The declared ladder** (Bar L0's rungs; a config takes a PREFIX of
the probe builder's declared melon order ((-2,0),(2,0),(0,-2),(0,2),
(-2,-2),(-2,2),(2,-2),(2,2)) and stem order ((-1,0),(1,0),(0,-1),
(0,1)) around the spawn-side patch (5,5); the two far patch sites are
erased to plain ground at every birth):

| rung | patches | melons | stems | renewal |
|------|---------|-------:|------:|---------|
| C3 (anchor, not re-run) | three full patches | 8×3 | 4×3 | yes — the 0109 world; measured solo steady-state ge12 ≈ 1.0 |
| C2 | one | 8 | 4 | yes |
| C1 | one | 4 | 2 | yes |
| C0 | one | 4 | 0 | **none** |
| C-1 | one | 2 | 0 | **none** |

**Walk protocol**: one solo life (3 × 5,025 steps) per rung, walking
DOWN from C2; the frozen config is the leanest rung passing L0 (zero
starvation loss, ≥ 3 eats, steady-state below-12 ≤ 0.30, window =
segments 2–3). The freeze is written to `FROZEN.json` and journaled
before any hostile arm runs.

## 2026-08-17 — the walk: every rung passes; C-1 freezes

| rung | below12_ss | eats | starv | food_min | verdict |
|------|-----------:|-----:|------:|---------:|---------|
| C2 (8 melons, 4 stems) | 0.000 | 6 | 0 | 8 | L0 PASS |
| C1 (4 melons, 2 stems) | 0.000 | 6 | 0 | 8 | L0 PASS |
| C0 (4 melons, 0 stems) | 0.000 | 4 | 0 | 8 | L0 PASS |
| C-1 (2 melons, 0 stems) | 0.000 | 3 | 0 | 8 | L0 PASS |

**Frozen: C-1** — the leanest declared rung, passing at the exact
eat minimum (3). The walk taught a meter fact worth recording: at
this life length (15,075 steps ≈ 63 game-minutes) and activity
level, one body needs ~3–6 eats total, so solo hunger is unreachable
on any declared rung — every rung coasts at steady-state below-12 =
0.000. The L0 "headroom" intent (≤ 0.30 so a 3× rise is measurable)
landed at zero across the board; the entire question now rides on
the delta the second body causes on a fixed ~10-slice larder.

**Amendment to Bar L1's ratio clause, registered BEFORE the hostile
arm runs**: with solo below-12 at exactly 0.000, "≥ 3× solo" is
degenerate (any nonzero value passes it). The ratio clause therefore
carries an absolute floor: it counts only if hostile below-12
≥ 0.10 as well. Effective L1: hostile steady-state below-12 ≥ 0.10,
or ≥ 0.90, or starvation health-loss where solo had none. The floor
is a pre-registered judgment pick, chosen with no hostile data in
hand.

## 2026-08-17 — L1 PASSES: the war was two digs long

The hostile arm on frozen C-1 (peer policy = 0109's, unchanged;
never died, never kicked):

| seg | food_ge12_seg | eats | collects | food_min | flood err |
|----:|--------------:|-----:|---------:|---------:|----------:|
| 1 | 0.000 | 0 | 0 | 7 | 0.114 |
| 2 | 0.000 | 0 | 0 | 7 | 0.120 |
| 3 | 0.000 | 0 | 0 | 5 | 0.156 |

**Verdict: hostile below-12 steady-state = 1.000 vs solo 0.000 —
Bar L1 PASSES** on the ≥ 0.90 absolute clause (and the floored ratio
trivially). No starvation health-loss: food pinned at 5–7 because a
motionless body barely drains the meter — the subject spent its
whole life hungrier than it ever got in any prior arm of two topics,
never touched 12, never ate, never collected. The peer's entire act
log: **2 digs** in the birth minute; the larder was gone before the
subject's first approach. The 0109 dissociation completes in both
directions [measured]: hostile prediction error 0.0117 vs solo
0.0075 (+56%) — but the rise is entirely the flood, the channel that
senses the subject's OWN deficit (0.114→0.156, ~40× solo).
Excluding the flood's 4 channels, hostile reads 0.0059 vs solo
0.0075 — the emptied world is again EASIER to predict, even as the
body starves in it. The head heard nothing wrong except hunger
itself. Learnability was the wrong premise; the meters were the
right one.

**Rung 2 is licensed.** Registered before any rung-2 arm runs:

- The peers sense enters exactly in the house grammar, mirroring the
  drops sense: `peers` (8 — present, sin_b, cos_b, dist, count,
  sig0..2), nearest OTHER player within 16 blocks, signature =
  sha256 of the username (identity as property; hashed, never
  parsed). Opt-in at bridge (`PEERS=1`) and anatomy
  (`c1_anatomy(..., peers=True)` → 94/13, appended LAST so every
  shipped offset is unchanged).
- **Bar L2** as registered (the restored reading, all checks).
- **Bar L3 operationalization**: fresh 45-lesson teach on the 94-dim
  body (same recipe, no peer in any classroom; the channel reads
  zeros there), then C-1-solo-94 and C-1-hostile-94; L3 passes if
  hostile-94's below-12 steady-state ≤ 0.50 (= recovering ≥ 50% of
  the 1.000 − 0.000 gap against its own solo-94 baseline, which must
  itself pass L0).
- **Interpretive guard, registered now with no 94-dim data in
  hand**: C-1's damage is total (1.0) and the larder vanishes in the
  birth minute, so the world may offer no behavioral slack for ANY
  sense to exploit. If hostile-94 shows the identical signature of
  total loss (0 eats, 0 collects), an auxiliary C0 pair
  (solo-94 / hostile-94, plus hostile-86 on C0 as comparator) runs
  BEFORE the L3 verdict is signed — a 1.0-gap world that saturates
  behavior would measure the world, not the sense. This guard
  sharpens the protocol; the L3 bar itself is unchanged.
