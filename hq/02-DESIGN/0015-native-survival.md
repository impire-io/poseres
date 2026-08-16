# 0015 — The survival stack: the operating point that lives

**Status:** design (graduated from research topic native-survival,
2026-08-16, [episode 0103](../04-JOURNEY/0103-native-survival.md)).
This is the measured configuration under which the taught composition
sustains its own vitals on a live world's native economy — replicated
across two independent 100,501-step lives (99.3% / 98.1% fed, 13 / 12
eats at the world's own demand, zero starvation loss). It is the
reference configuration for any survival-shaped deployment and the
argument for the eventual promotion of the survival body into the
default anatomy.

## The stack

| Layer | Setting | Design of record |
|---|---|---|
| Body | `c1_anatomy(survival=True, flood=True, aim="worth")` — obs 86: the mouth (`use_held` + edible affordance), distal senses (drops + glance), flood channel, worth channel | specs/027 contract (native-survival + aim sections) |
| Bridge | `SURVIVAL=1 FLOOD=intrusion AIM=worth`, `PALATE_FILE` carrying the taught tongue, `SPAWN_ANCHOR` pinned | [0013](0013-the-aim.md) |
| Teaching | 45 sense-using lessons (three classroom variants, eat-heavy tapes, hunger-dose cycle decorrelated); tape-driven — policy flags irrelevant at teach time | distal-senses reteach (episode 0100 trail) |
| Policy at life-time | `RecipePolicy` + completion itch (κ 0.25) + recipe hold (λ 0.25) + **commitment** (`commit_kappa=0.1`, `explore_defers_holds=True`) | [0014](0014-the-last-crack.md), feature 043 |
| Deficit gate | **OFF** (`deficit_kappa=0.0`) — refuted as the live carrier; its one head-to-head coincided with collapse (below-12 time 0.452 gated vs 0.007 off) | episode 0103 verdict |
| World | Vanilla, difficulty normal, `doMobSpawning false`, melon patches with stems — food regrows by the game's own physics; NO harness meter anywhere | probe kit |

## The rig's living home

`examples/minecraft/survival/` — `probe/` (compose world +
provisioning + N1 probe) and `arms/` (the runner estate:
`n23_runner.py` shared helpers, `n23_committed.py` the blessed-stack
life runner, taught artifacts untracked beside them). Runbook: bring
up `probe/docker-compose.yml`, provision once, run
`arms/n23_committed.py confirm`.

## Measured expectations (what a healthy life looks like)

First-eat within ~2k steps unaided; a meal every ~7–8k steps at this
activity level (the native demand — do NOT bar eats against the old
synthetic drain's numbers); food fraction ≥ 12/20 above 95% after the
first meal; zero starvation loss; the palate's book staying
essentially {melon, melon_slice} with coincidental entries an order
of magnitude below the chain's.

## Open questions, deliberately parked (episode 0103)

Why the deficit gate's kd = 0.1 coincides with re-expression dying
(seed-luck check = repeat both arms); promotion of the survival body
into the default anatomy (a spec-kit feature when wanted); predation
(mobs), the market, multi-food worlds — each a fresh registration.
