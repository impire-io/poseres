# Episode 0068 — The run has spoken: no emergence, one mined log (2026-07-22 → 2026-08-08)

The pre-registered multi-week Minecraft run (`c1c`, C1-RUN-PLAN
amendment v3) closed deliberately on 2026-08-08 12:29:14 UTC at
cumulative step **5,740,930** — **16.61 days of brain-steps** against
the registered ≥ 14 (~4.8M; the bar crossed Aug 5 ~19:20 UTC), at
3.946 steps/s, 98.7% of the 250 ms real-time ideal `[measured]`. The
R1–R5 readings were computed from the S3 objects (`pra/v1/c1c/`),
segment-aware across the run's two mid-run restarts and deduplicated
against flusher redeliveries; full numbers in the journal's closing
entry.

**R1 — the headline: crafting did not emerge.** Zero planks, zero
sticks; over the final 7 days of brain-steps: zero completed digs and
three acquisitions, all wandering-trader leads. Sharpest single fact
of the run: **an offer was showing on 0 of 5,669,662 recorded steps**
— the bot never once staged a craftable item, so offer-conditioned
taking never had a denominator `[measured]`. The episode-0058
self-set-goals reversal watch closes unfired.

**And yet the record hides a fired watch item nobody saw: the first
mined log.** A material era ran cum ≈0.9M→2.03M (≈Jul 25–28): **449
completed digs — all of the run's total — 605 dirt, 448 leaf_litter,
15 oak_sapling, 8 wheat_seeds picked up, and one `oak_log`** entering
the inventory at cum ≈1,299,001 in the era's peak-dig stretch,
held ~1,000 steps, then placed back into the world `[measured]`. That
the log was mined rather than gifted is `[mechanism-argument]`: the
body has no drop action, no world event drops logs, and the pickup
sits in the run's densest dig-completion bucket; that it was placed
(not staged) is `[measured]` — offer_steps 0 excludes staging. Every
pickup of the era was eventually re-placed (acquisitions = losses per
item). Then the loop decayed to zero and **never returned**: the
final ~3.6M steps were world-inert except the leads. R2 accordingly
reads *climbed, then abandoned*: weekly dig completions 449/0/0,
place-with-material 1,100/0/0 — while dig-action usage *rose*
(6.5% → 9.4% of steps) and the grid levers stayed heavily exercised
to the last hour (36.2% of all steps with something staged, 132,645
grid-puts with an item in hand, zero recipes ever among them)
`[measured]`.

**R3 fires the no-rot clause as written**: early-plateau pred-err
0.101 vs final-week 0.164 (+62%) `[measured]`. The break is one
event: an eviction sweep at cum ≈0.9M (population 38 → ~22, error
0.09 → 0.199) after which error *improved* steadily to 0.162 at
close — a regime change absorbed and re-learned rather than rot
`[judgment]`; notably the material era began *at* the sweep. Idle
4.92% run-wide (the 0053 anti-idle reversal bar of ≥20% never
approached — frontier's anti-camping vindication holds at 5.7M
steps). **R4's crafting=False fallback does not fire**: grid
primitives were the opposite of unused, and improvement (EMA
1.0 → 0.162) is not materially below the pilot arm (0.778 → 0.143)
`[measured]`. The hierarchy arc opens with its target named exactly:
5.7M steps of contact with the crafting machinery produced zero
stagings of a craftable — the gap is not engagement but *sequence*.

**R5 — operational honesty.** Brain: two mid-run restarts, both
deliberate, zero crashes (Jul 29 06:37; Aug 1 06:36 — the second was
between readings and previously unrecorded; journald has since lost
both Started lines and the final process's CPU accounting pins it
`[measured]`). Bridge: zero mid-run restarts — the 07-31 journal
claim it restarted on Jul 29 was wrong, corrected in the closing
entry. Flush: 14 crash-restarts (Jul 30–Aug 6). Resume replay losses
1,712 and 5,038 steps; snapshot chain cadence-clean but for 2 missing
notices; 0.125% of step events missing in-span (at-least-once, gaps
visible as designed). And the flagged disk risk bit on the final
morning: **MinIO refused writes from 08:30:47 UTC Aug 8** (root disk
100% — the never-pruned c1c snapshot store, compounded by
`pra-flush --snapshot-dir` still pointing at c1b), the 1 h buffer
expired **≈57,695 steps of telemetry** (~2.4% of the final-7-days
window) before the stop was called, and the final ~56 minutes were
rescued off the buffer minutes before expiry. Ground truth brackets
the gap (inventory identical both sides, no offer in the tail).

What it taught: **(a)** the emergence question now has a precise
successor — not "will it touch the machinery" (it did, relentlessly)
but "what makes a staged *craftable* reachable" — the hierarchy arc's
opening brief; **(b)** the owner-request watch cadence (readings days
apart) missed the run's only headline-adjacent event by construction
— if a watch item matters, its detector must run continuously on the
stream, not on visit; **(c)** the observatory's disk is part of the
experiment: telemetry durability failed not from crash or gap but
from growth nobody pruned, in the run's final hours.

Reversal condition: none — records a completed pre-registered
measurement; the run's standing reversal watches (0053 anti-idle,
0058 self-set-goals) close unfired, and reopening either requires a
new run under a new pre-registration.

Trail: `hq/02-DESIGN/validate/C1C-JOURNAL.md` (closing entry, full
numbers); `hq/02-DESIGN/validate/C1-RUN-PLAN.md` (pre-registration);
S3 `pra/v1/c1c/` on beno4 (the artifact behind every number);
committed together with this episode.
