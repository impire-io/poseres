# c1d-lab — run archive

The evidence trail of the provisioned life
([run plan](../C1D-LAB-RUN-PLAN.md), episode
[0079](../../../04-JOURNEY/0079-the-provisioned-life.md)): one brain,
one continuous world, 25,003,001 steps, 75,359 full chains, zero deaths,
stopped 2026-08-10 by the pre-registered goal rule.

| File | What it is |
|---|---|
| `c1d_runner.py` | The segmented-resume harness that ran the life (LifeWorld = meter + tapered childhood + 2,000-tick regrowth; stop rules; status rows) |
| `c1d_wrap.sh` | The relaunch wrapper (double-launch guard, process recycling) |
| `c1d-status.jsonl` | All 500 per-segment rows — every reading in the run plan derives from these |
| `c1d-seed-brain.bin` | The brain at birth: the G4 meter-cohort graduate, seed 1 |
| `c1d-final-brain.bin` | The brain after the life: the 25M-step snapshot (world state included; resumable) |

Recording caveats (also in the run plan): rows sample energy / dwell /
prediction-EMA at ~50k-step segment boundaries, so intra-segment
excursions are unobserved; `logs`/`sticks`/`cobble` are pocket *stocks*
(crafting consumes them), only `chains_cum` is a true counter.
