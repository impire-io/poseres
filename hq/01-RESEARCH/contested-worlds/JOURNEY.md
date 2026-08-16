# contested-worlds — investigation journey (started 2026-08-16)

## 2026-08-16 — the rung-1 rig, built and proven before any arm runs

The rig lives in `rig/`: the N1 probe world's declared config verbatim
on its own container and port (`cw1-minecraft`, 25603 — the C1 and N1
worlds untouched), provisioned with the three melon patches.

**Subject** — the blessed stack, exactly `n23_committed.py confirm`:
`c1_anatomy(survival=True, flood=True, aim="worth")` (obs 86/13),
worth-taught.bin (45 lessons, W(13,86,87)), palate restored at birth,
RecipePolicy κ=0.25 λ=0.25, deficit gate OFF, commit_kappa=0.1,
explore_defers_holds. Hungry-born, free roam, world admin at birth
only. Engine seed 1, tick rate 100 / 50 ms — the one temporal fabric.
3 segments × 67 cycles × 75 = 15,075 steps per arm (≥ the registered
3 × 1,500).

**Instrument** — Bar 1's operationalization, registered now, before
any arm runs: a measurement-only policy wrapper captures the event
head's predicted delta for the chosen action each step
(`context.predict_event_delta` — read-only, no RNG; the inner
policy's draws are untouched) and settles it against the realized
observation next step. Primary metric: mean over all 86 channels and
all steps of |predicted − realized| per segment; the arm number is
the mean of the three segment means; Bar 1 passes on a paired/solo
rise ≥ 25%, the reversal fires below 10% on every segment.
Per-channel-group means recorded for diagnosis; food/eat outcomes
recorded honestly but claim nothing at this rung.

**Peer** — `peer.js`, the scripted body "rook": fixed non-adaptive
policy (cycle the three patches, dig the nearest melon, walk over
drops), no admin commands, no reading of the subject, every act one
JSONL line. No pathfinder exists in the rig's node_modules, so
navigation is straight-line with a fixed escape ladder (stuck → jump →
veer 60° alternating → abandon + blacklist), every escape logged.

**Invisibility is by construction, measured**: the 86 channels carry
no player-entity sense — the glance senses block appearances, the
drops sense ground items, and the bridge's `playerCollect` handler
ignores other collectors. The peer reaches the subject only through
world effects.

**Instrument checks, green before the arms**: the live contract check
against this stack (`contract_check.py --bridge-port 25591`) — 
CONTRACT OK; a 60 s peer smoke run — 17 melons dug across all three
patches, travel between patches confirmed, escape rules exercised
(one water-bowl recovery, one abandon). Smoke damage to the patches
is repaired by the birth admin (`repair_floor` rebuilds them).
