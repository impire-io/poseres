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
