# N2/N3 arms plan (frozen before launch, 2026-08-13)

The bars are pre-registered in README.md; this records the exact
wiring, doses, and readings — c1e's discipline, applied.

## The composition (all shipped components, nothing custom)

- Body: `c1_anatomy(survival=True)` (obs 33 / n_actions 13) over the
  live SURVIVAL=1 bridge on the N1 world (the declared config, N1-met).
- Policy: `RecipePolicy` (feature 041) with the feature-042 deficit
  gate. `label_index = deficit_index = 6` — the native food channel is
  both the meter and the pay, exactly as the archived 0083/0084 arms
  used their energy channel. Operating points, all from the record:
  itch κ = 0.25, λ_r = 0.25, `deficit_kappa` = **0.1** (episode 0085's
  measured point of record), `event_head_eta` = 0.5,
  `weight_norm_cap` = 1.2, frontier drive, ε = 0.1, position channels
  (0, 1) at scale 64. **N3 differs by exactly one number:**
  `deficit_kappa = 0.0`.
- Recipes are policy-side state (041's declared assumption): the
  taught demonstrations are kept on disk and both lives rebuild
  `RecipeMemory` from the same files.

## The fabric

One temporal fabric (c1e amendment 1): world at `/tick rate 100`
(M\* = 5), 50 ms brain steps, teaching and lives alike. Known
asymmetry, recorded: digs are client-wall-clock (~1.5 s melon ≈ 30
steps) while eats are server-tick (32 game ticks ≈ 7 steps at 5×).

## Teaching (once; both arms inherit the same taught brain)

45 lessons at the patch-(5,5) stand `(5.5, -60, 2.5)` facing the
classroom melon at `(5, -60, 3)`. Per lesson the parent preps the
classroom (kill drops, set the melon, tp, hunger dose) and the tape
demonstrates **dig → collect → eat**:
`[dig]×40 + [fwd]×9 + [back]×9 + [hold] + [use]×12 + [idle]×4`
(75 steps). Hungry teaching (the 0083 protocol, c1e amendment 3):
hunger-effect doses cycle full/medium/light
(`5s@255 / 3s@127 / 3s@63`, game-seconds) so the meter is witnessed
across its range and the post-eat observation is each recipe's
max-food terminal. A lesson without both a collect and a genuine eat
is retried (≤3; the held-kind cycle makes attempts alternate, so a
retry recovers it). The teacher records the per-step observations;
each clean lesson becomes one `RecipeMemory` demonstration.

## The lives

Newborn prep between phases (world admin BETWEEN readings, never
during): clear pocket, kill drops, saturation + instant-health to
20/20, tp to the stand, re-provision the patches. Then **zero rcon
until the life ends** — the world's own clock, drain, and regrowth.
Each life: 1,340 cycles × 75 steps = **100,500 steps** (≥ the
registered 100k), segmented resume-chain (134-cycle segments,
snapshot at each boundary), rows to `arms/<arm>-status.jsonl`, stop
file `arms/<arm>-STOP`. N2 runs first; the world is re-prepped; N3
runs the same taught snapshot on the same world and bridge process
(same spawn anchor — the ep-0078/amendment-4 lesson) with the gate
off. A failed bar does not stop a life; the whole life is the reading.

## Within-run readings (per segment row)

Food-fraction ≥ 12/20 (segment + cumulative), genuine eat events
(slice count fell AND food rose), collects, min food, min health,
starvation health-loss flag (health fell while food = 0), R-explore
(unique columns; Chebyshev-2 dwell at each patch), policy watch
(completions fired/false, advance events, out-of-context, pred EMA),
steps/s, wall.

## Known mechanism question, stated before the run

The 042 gate reads at fired completions (pocket gains) and at
recipe-terminal selection. Eating *reduces* the pocket, so no
completion fires on the eat itself; the gate reaches the eat only
through recipe selection and the head's learned use→food outcome
under the drive pipeline. Whether that carries sustenance is exactly
what N2 measures — if the life digs and collects but fails to eat,
that mechanistic reading is the finding, not a run defect.

## Pilot before the arms

A fake-bridge pilot (5 lessons, ~2,400-step life on
`FakeBridge(survival=True)`) validates the wiring end-to-end —
recipes form, the life produces at least one genuine eat pathway
reading — before any live wall-clock is spent. Pilot rows are
published with the arms.

## Amendment 1 — the mouth's cracks (pilot 1 reading, 2026-08-13)

Pilot 1 measured the plan's stated mechanism question: the taught
life dug and collected but **ate zero times** in 2,400 steps — food
to 0, health to the floor, slices in the pocket. The cause is
structural, and it is c1e amendment 1's lesson transposed: the dig
hold survives in lives because its progress is *sensed* (the mining
channel — the cracks), so the completion itch can hold the intention;
the eat hold had no sensed progress, so nothing in the shipped
machinery could hold `use_held` across the consume, and a lone
ε-random use completes nothing.

The amendment is the same grammar, not new machinery: **in survival
mode the progress channel senses the held intention's progress,
whatever the intention** — a dig reports its cracks, a use reports
its chew (live: elapsed/1.61 s; fake: held ticks/6). The itch then
holds the eat exactly as it holds the dig; satiety self-gates (a
sated use no-ops, the head learns a zero delta, the value dies).
Additive, survival-mode-only, both bridges + contract + tests; the
registration's channel set is otherwise untouched. Also recorded from
pilot 1: the collect-event counter includes staging-grid churn
(cosmetic — the eat counter requires a food rise and is immune); the
lesson retry alternation predicted in the plan was observed exactly
(attempt 1 fails on the held-kind cycle, attempt 2 recovers).

## Amendment 2 — the parent empties the pupil's hands (teach run 1)

Live teach run 1 failed at seg 3: every attempt collected and never
ate. Measured cause: the held KIND is bridge-virtual state that
survives across lessons and even across a pocket clear (the name
revalidates the moment the dig refills the pocket), so the tape's
single `hold_next` toggled the hand to *empty* whenever a lesson
started with the slice still held — and retry parity did not reliably
alternate. The fix is classroom hygiene, not tape surgery: every
lesson (and each newborn) clears the pocket AND normalizes the hand —
one `hold_next` issued over an empty pocket forces held → null (the
cycle is [null] alone), making every lesson's toggle deterministic
and both arms' birth-hands identical. Retries remain as drop-scatter
insurance only.

## Amendment 3 — the split sample (teach run 2, seg 30)

Teach run 2 died at seg 30 with lessons that visibly ATE in the debug
window: food 0 → 2 on one view, the slice leaving the pocket on the
NEXT view. At the 50 ms fabric the server's food update and inventory
update can land on different bridge samples; the eat detector had
demanded both in the same view pair. Amended: an eat is a slice drop
with a food rise within ±2 views (100 ms skew tolerance) — applied
identically to lesson verification and to the lives' bar-N2 eat
counter, and recorded here as measurement tolerance. Teaching also
checkpoints per lesson now (a failed seg resumes, never re-teaching
the chain). Teach run 3: 45/45 clean, zero retries at the milestones.

## Run record and owner stop (2026-08-13)

Teaching: 45/45 clean (run 3). N2 life stopped by the owner at seg 2
(20,101 steps) as pointless-as-registered: food sat at 20/20
throughout (`n2-status.jsonl` rows 1–2 stand as the record), so the
deficit was zero everywhere and N2 ≡ N3 — the ablation could not
distinguish anything. Vanilla's native metabolism drains only under
work (N1's own arithmetic); a recipe-held life parks (dwell 0.82–0.87
at the taught stand) and never works up an appetite.

**Hungry-birth probe** (`hungry_probe.py`, instrument reading, not a
bar): the same taught brain born STARVING (food 7–8/20, deficit ≈
0.6), 1,500 steps, gate on vs gate off —
`{eats 0, collects 0, dwell 0.98}` vs `{eats 0, collects 0, dwell
0.94}`. **Indistinguishable.** The null is therefore NOT only "the
deficit never arises": when the deficit is present, the composition
still neither forages nor eats — the taught dig→collect→eat chain
does not re-fire in the live fabric (contrast: the SAME wiring in the
fake pilot life produced 5 genuine eats). The 042 gate amplifies
label weight at completions and recipe selection, but no completions
fire because the upstream dig→collect never happens live.

Bars N2/N3: NOT MET (run stopped; recorded honestly). N1 stands MET.
The sharpest open thread is the fake-vs-live contrast — candidate
mechanism: the live fabric's delayed drop/pickup (seconds between
break and pocket gain at 50 ms steps) starves the one-step event
head's dig→gain pairing that the fake's instant-pay physics provides.
Scenario direction is the owner's call from here.
