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
