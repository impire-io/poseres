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

## 2026-08-17 — rung 2 built: the sense, its proof, the brain, the baseline

**Bar L2 PASSES 27/27** — on the *second edition* of the reading.
The first edition read 9/16 and the instrument caught its own
assumption: every bearing/distance failure reverse-engineered to a
~2.3-block subject displacement (the script trusted that pra stood
where rcon tp sent it; solved positions matched the read channel to
three decimals). The reading is now SELF-LOCATING — expectations
derive from the world's own measured facts (bridge view position,
pose yaw, `data get entity` for the peer) — and passes with bearings
within 0.006, distances within 0.002, signatures sha256-exact and
stable across reconnects, the range cap honest, and the bearing
frame rotating with the body's own turn. East sign declared from
measurement: −1 facing +z (the drops convention, same formula).
The sense itself: bridge `PEERS=1` + `c1_anatomy(peers=True)` →
94/13, appended last, default untouched (pinned), contract check
green, full pytest suite green.

**The 94-dim brain**: 45/45 lessons, zero retries, same recipe, no
peer in any classroom (the channel read zeros throughout — the head
has NO learned dynamics for peers ≠ 0; whatever the sense pays in
the hostile arm, it pays through within-life learning). Born tongue
reused (worth-palate-taught.json) to remove the palate confound.

**C-1-solo94 passes L0** — below-12 steady-state **0.0912**, 6 eats,
0 starvation — but the record keeps the wobble honest: segment 1 was
a total blank (0 eats, ge12 0.000; it dug floor, held dirt 3,075 of
5,026 steps, destroyed melon B without pocketing a slice), then
competence expressed in segment 2 (6 eats off melon A, ge12 0.818,
seg 3 coast at 1.000). Expression latency in the D3-measured band —
a different teach draw expresses later than the 86 brain did, and it
wasted half the larder learning. Baseline for L3 is therefore 0.0912
(not the 86's 0.000); the L3 bar as registered: hostile-94 below-12
steady-state ≤ 0.50 with this baseline passing L0 — it does.

## 2026-08-17 — the C0 auxiliary: no gap for anyone; Amendment 2 (the knife edge)

The C0 pair plus comparator, measured:

| arm | below12_ss | eats | starv |
|-----|-----------:|-----:|------:|
| C0-solo94 | 0.000 | 6 | 0 |
| C0-hostile94 (the sense) | 0.000 | 3 | 0 |
| C0-hostile (86, blind) | 0.000 | 6 | 0 |

Four melons is enough for both bodies — the blind brain ate *more*
than the sensing one against the same adversary. So the meter cost
lives on a razor-thin band: at 2 melons the war ends before either
brain expresses (total, unrecoverable — measured both bodies), at 4
there is no war at all (measured both bodies). **Amendment 2,
registered before it runs**: one finer rung, C-0.5 (one patch,
**3 melons**, 0 stems), decides whether a *recoverable* middle
exists. Protocol: C-0.5-hostile (86) runs first to establish the
gap; its solo-86 baseline is stated by inference, not measurement —
a 3-melon world is strictly richer than the measured C-1 solo
(0.000), so 0.000 bounds it. If the 86 gap lands partial (below-12
ss in (0.10, 0.90)), the 94 pair runs and L3 signs on C-0.5 (same
bar: hostile94 at or under half the 86 gap, solo94 passing L0). If
the gap lands at 0.000 or ~1.000 again, the all-or-nothing dynamic
is confirmed across three scarcity rungs, L3 is honestly
unmeasurable-as-failed on this geometry, and the registered
L3-after-L1 reversal routes the topic to design: with a fast
adversary on non-renewable resources, contests are decided by race,
not information — the machinery conversation (what world geometry or
body speed makes information worth anything) is licensed by these
numbers.

## 2026-08-17 — C-1-hostile94: total loss again; the slack guard FIRES

All three segments ge12 = 0.000, 0 eats, 0 collects — below-12
steady-state **1.000**, the identical signature to the 86 arm. The
peers channel was alive and learning (err 0.0036 → 0.0063 across
segments — the head's first-ever nonzero peer signal), and it made
no difference to the meters, because there was nothing left to
sense one's way toward: the peer's act log reads **2 digs** in the
birth minute, again. The registered interpretive guard fires on its
exact trigger (identical total-loss signature): the L3 verdict is
NOT signed on C-1. The auxiliary C0 pair runs first — C0-solo94
(the wider baseline), C0-hostile94, and C0-hostile (the 86
comparator) — because a world with zero behavioral slack measures
the world, not the sense. The L3 bar itself stands unchanged; on
C0 it reads: hostile94 recovers ≥ 50% of the C0 gap (C0-hostile-86
vs C0-solo94's own baseline), i.e. below-12 steady-state at or
under the midpoint of those two, with C0-solo94 passing L0.
