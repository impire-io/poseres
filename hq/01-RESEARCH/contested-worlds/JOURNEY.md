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

## 2026-08-16 — the solo baseline (rung 1, first arm)

Three segments, 15,075 steps, every step's prediction settled
(pred_n 5,024/segment, 0 missing):

| seg | pred_err_all | mining | blocks | glance | drops | flood | aim |
|----:|-------------:|-------:|-------:|-------:|------:|------:|----:|
| 1 | 0.020370 | 0.1396 | 0.0357 | 0.0236 | 0.0240 | 0.0602 | 0.0277 |
| 2 | 0.021118 | 0.1856 | 0.0405 | 0.0279 | 0.0240 | 0.0105 | 0.0368 |
| 3 | 0.024275 | 0.2019 | 0.0411 | 0.0345 | 0.0174 | 0.0029 | 0.0511 |

Arm mean (the registered aggregate): **0.021921**. Body-private
channels near-silent (vitals ≤ 3e-4, pocket ≤ 7e-4); the error mass
sits in mining progress, the block column, and the distal senses —
the channels a peer would perturb. The life behaved: 6 eats, food
≥ 12 for 72.2% of steps cumulative, food floor 8, no health loss.
This is the number the paired arm must beat by ≥ 25% (Bar 1) or
undercut by < 10% everywhere (reversal).

## 2026-08-16 — the paired arm, and a verdict nobody registered for

Same protocol, the peer "rook" in-world from birth admin to the last
step (verified present, never died, never kicked):

| seg | pred_err_all | mining | blocks | glance | drops | flood | aim |
|----:|-------------:|-------:|-------:|-------:|------:|------:|----:|
| 1 | 0.014214 | 0.1848 | 0.0348 | 0.0162 | 0.0161 | 0.0168 | 0.0117 |
| 2 | 0.013255 | 0.1907 | 0.0281 | 0.0215 | 0.0139 | 0.0016 | 0.0025 |
| 3 | 0.013377 | 0.2136 | 0.0254 | 0.0226 | 0.0108 | 0.0012 | 0.0019 |

Verdict as registered (`rung1.py verdict`): solo mean 0.021921,
paired mean 0.013615, rise **−37.9%** (per segment −30.2%, −37.2%,
−44.9%). **Bar 1 FAILS.** The reversal's registered operationalization
(rise < 10% on every segment) **fires** — but honesty about what it
was written for: the reversal anticipated a *null* ("within noise of
the solo baseline"). What happened is not a null. The peer's presence
*improved* the subject's prediction error by more than a third and
its life outright: food ≥ 12 for **97.2%** of steps cumulative
(vs 72.2% solo), first segment 91.4% (vs 16.7%), same 6 detected
eats, completions 257 vs 163, false-completion rate lower (61% vs
73%).

**The peer's record** (paired-peer-acts.jsonl): 69 melons dug, 0 dig
failures, 112 patch-empty rotations, 16 stuck-jumps, 2 abandons,
0 deaths — and **0 drop-chases**, meaning drops mostly fell at its
feet and were picked up instantly; the far-scattered remainder (the
c1e far-scatter measurement) was left in the world.

**Two candidate mechanisms, both consistent with these numbers,
neither yet discriminated:**

1. *Windfall commensalism* — the peer's 69 broken melons scattered
   slices the subject collected without digging; the subject lived in
   its taught collect-and-eat contexts, which the head predicts well.
   The food trajectory supports this.
2. *World-quieting* — 112 patch-empty rotations say the peer stripped
   the patches bare much of the time; a world with fewer standing
   appearances gives the distal senses less to mispredict (glance,
   drops, aim, flood all fell hard; those wide groups dominate the
   mean).

**The interference fingerprint is real but small**: mining — the
subject's own held-dig progress — is the ONE group that rose in every
segment (+32%, +3%, +6%): digs whose target vanishes under you are
exactly the unattributable perturbation the premise predicted. It is
just swamped by the two effects above.

**Confounds, named**: sequential arms on one world (birth admin
repairs floor and patches between, but micro-state differs); one life
per arm (no across-life error bars); one peer configuration — a
generous forager, not an adversary; the eat detector can undercount
at the 50 ms fabric; the subject's per-step views were not persisted,
so subject-side collect counts (the discriminator between mechanisms
1 and 2) are unavailable — a follow-up must persist views.

**Status**: Bar 1's verdict stands as registered — FAIL. The
reversal's registered consequence (topic graduates abandoned) is a
topic-closing act and goes to the owner with these numbers, because
the result is materially different from the null the reversal was
written for: this configuration did not show "no problem", it showed
a large *benefit* plus a small genuine interference signal on the
contended channel. The open-amendment path (how-we-work: bars amend
only openly, with the degenerate raw numbers recorded here) would be
to re-scope rung 1's premise around peer *hostility* — e.g. a peer
that takes drops near the subject rather than gifting them — before
any attribution-sense work is licensed. Owner's call.

*(The owner delegated the fork the same evening — "continue as you
see fit" — and Amendment 1 was registered and committed before the
hostile arm ran.)*

## 2026-08-16 — the hostile arm settles Bar 1a: the adversary helps too

Same protocol, PEER_MODE=hostile (shadow the subject, steal drops
near it, dig the melon nearest it). Peer record
(hostile-peer-acts.jsonl): 41 melons dug, 0 failures, 0 deaths,
0 kicks, 42 stuck-jumps (shadowing is harder navigation), 3 abandons,
and again 0 drop-chases (drops at its feet, swallowed instantly).

| seg | pred_err_all | vs solo | mining | glance | drops | collects_seg | eats_seg |
|----:|-------------:|--------:|-------:|-------:|------:|---:|---:|
| 1 | 0.015351 | −24.6% | 0.1768 | 0.0209 | 0.0168 | 1 | 5 |
| 2 | 0.016171 | −23.4% | 0.1967 | 0.0261 | 0.0220 | 0 | 0 |
| 3 | 0.017599 | −27.5% | 0.2142 | 0.0307 | 0.0171 | 1 | 0 |

Verdict (rung1.py verdict): hostile mean **0.016374**, rise
**−25.3%**. **Bar 1a FAILS; the amended reversal FIRES** (< 10% on
every segment — all three are large negatives). The charitable
single-channel reading fails too: mining, the most-affected channel,
rose +26.7/+6.0/+6.1% — mean +12.9%, under the 25% bar even alone.

**The mechanism, now discriminated** (the views persisted this time):
the hostile subject collected essentially nothing — 2 collects in
15,075 steps — yet its error still dropped 25%. Windfall commensalism
is therefore NOT necessary for the drop; **world-quieting is
sufficient**: a peer that strips the standing world leaves the distal
senses reading mostly nothing, and nothing is easy to predict. The
forager's deeper drop (−37.9%) is quieting plus windfall. The
subject's life stayed healthy in both peer arms (hostile: food ≥ 12
for 96.5% of steps, 5 eats, no health loss — it ate early, then the
emptied world had little to offer OR demand).

**Both registered reversals have now fired on honest margins.** Per
Amendment 1, registered before the arm ran: the attribution sense is
unlicensed by the senses-first rule at this rung, and the topic
graduates abandoned carrying both measured results — the gift
(−37.9%) and the adversarial null-that-is-also-a-gift (−25.3%) —
with the interference fingerprint (mining +12.9% mean, swamped) on
the record for whoever reopens this. Bars 2–6 (rungs 2–3) were never
licensed and did not run. What a successor topic would need to
reopen the question: a premise about *outcome* contention rather
than learnability (rung 3's territory — scarce, non-renewable
resources where the meters, not the head, pay the price), or a world
where the peer's acts create structured surprise the subject must
predict to survive rather than an emptier, quieter field.
