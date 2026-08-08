# C1C run journal — the frontier-drive run

Live notes on the multi-week `c1c` run (pre-registration:
[C1-RUN-PLAN.md](C1-RUN-PLAN.md), amendment v3). Entries appended by
the watch: a single "nothing special" line when the visit was routine;
a written-out note when something happened and why it matters. The raw
numbers behind every entry are in S3 under `pra/v1/c1c/`. Notability
bar (unchanged from c1b): first mined log, any grid offer, any craft,
persistence records (deepest held dig), camping/idle episodes,
population/error anomalies, restarts, gaps, disk events — plus the
episode-0058 reversal watch: **a self-produced multi-step crafting
chain reopens the self-set-goals topic.**

---

**2026-07-25 09:01 (07:01 UTC) — opening entry: catch-up after a
2½-day journal gap (the journal's fault, not the run's).** The c1b
journal closed 2026-07-22 18:47 saying the watch moves here — but this
file was never created, and no watch entry was written since. The one
recorded observation in between was the E0/E0b research read at
~328k steps (episode 0054: zero logs/planks/sticks; idle 3.1%, the
frontier drive vindicated). The run itself sailed through untouched.
Catch-up reading, live from the dashboard + host:

- **Progress**: step **891,270** (cycle ~3,713), launched 2026-07-22
  16:23 UTC — sustained pace **3.95 steps/s** (~342k steps/day), 99%
  of the 250 ms ideal. The ≥ 4.8M-step target lands ~Aug 5–6 at this
  pace.
- **Learning health (R3)**: pred-err EMA **0.082**; best frame score
  0.106 at best_dim 4 (best_dim breathing 3–5 over the recent window —
  complexity still exploring); population **37**, steady over the
  window; spawn/evict lifecycle active (latest spawn frame 3715 at
  step 891,160).
- **Drive (E0b watch)**: idle **3.7%** over the last 600 steps —
  the episode-0053 reversal bar (idle ≥ ~20% after maturity) stays
  unfired. All 12 actions in use, movement-dominant mix (forward 37%,
  turns 21%), crafting-mechanism levers (hold/grid/take) ~18% of
  steps. No action degeneracy.
- **The headline (R1) stays open, as expected**: ground truth right
  now is an inventory of `wheat_seeds ×1`, nothing held, no dig in
  progress — no log yet (the 12-tick wood dig unclimbed), so no
  offers, no crafts.
- **Ops (R5)**: brain unit up continuously since launch, **zero
  restarts** (NRestarts=0); bridge up since 07-21 20:46 UTC (spans the
  c1b→c1c handoff — only the brain was restarted); dash + flush up
  since 07-22 06:45 UTC, zero restarts. Telemetry: events_dropped 0,
  publish_failures 0, reconnects 0. The dash counts **seq_gaps 11**
  since its boot — small; to be audited against the S3 key ranges at
  read time (at-least-once delivery, gaps stay visible by design).
- **Disk**: 54G used / 40G free (58%). PRA-attributable ≈ 5G
  (~2.9G `~/pra-runs` incl. soak-era artifacts, 899M MinIO, 128M
  world, NATS negligible) — within the plan's budget. The 42G → 54G
  growth since the last c1b entry is the box's *other* tenants
  (`/var/lib/lemonade` 19G, containerd 11G), not the run; noted as a
  standing watch item on visits.

Watch items carried forward: first log / first offer / first craft
(the 0058 reversal condition), idle staying low as frames mature,
dig-streak records, disk on every visit.
**2026-07-27 20:26 (18:26 UTC) — owner-requested reading: on pace, and
the pocket has news.** Step **1,732,786** (5.09 days in, 3.944 steps/s
sustained; the ≥4.8M target lands in ~9 days, ~Aug 5). Ops spotless:
zero restarts since launch, zero dropped events / publish failures /
reconnects; dash seq_gaps 14 (+3 since 07-25, S3-auditable); disk 57G
used / 36G free (~1.2G/day — comfortable for the remainder). Learning:
pred-err EMA 0.147 (higher than 07-25's 0.082 — sweep-band variation),
population 23 (down from 37, an eviction sweep in progress), best_dim
steady at 4. Behavior: idle **5.8%** (reversal bar <20% — unfired),
all 12 actions in use, crafting levers ~17.8%. **Ground truth: the
inventory now holds `lead ×3` and `wheat_seeds ×5`, and the bot is
HOLDING the seeds** (a deliberate hold-class selection) — up from a
single seed two days ago. The leads cannot be self-crafted (a 3×3
recipe; the body has a 2×2 and no string), so they are a world event
pickup — likely a wandering-trader llama — an acquisition, not
crafting: the 0058 reversal watch does NOT fire. Still no log, offer,
or craft; the bot has surfaced (y = 72 vs y = −31 on 07-25) — wide
vertical range covered. All green; the emergence headline stays open.

**2026-07-31 20:00 (18:00 UTC) — owner-requested reading: a clean
mid-run restart absorbed, still on pace; the flusher has developed a
cough.** Cumulative step ≈ **3,089,900** (latest snapshot
`snap-000003085000-12850`, cycle 12,850), 9.07 days in — pace holds at
~3.94 steps/s, and the ≥4.8M target still lands **~Aug 5 evening
UTC**, ~5 days out. The notable ops event: on **07-29 06:37:27 UTC**
the brain, bridge, and dash were stopped and started together — a
deliberate `systemctl` restart (Stop→Start same second, NRestarts=0,
not a crash). The brain resumed from its newest snapshot exactly as
designed: cumulative now matches the zero-downtime projection within
noise, so effectively nothing was lost. Bookkeeping note for future
reads: since the resume, census/event `steps` count in-process
(844,885 now) while snapshot ids carry the cumulative count. Learning:
pred-err EMA **0.209** (0.082 → 0.147 → 0.209 across readings — a
rising trend to keep an eye on, not just sweep-band variation);
population **22** (stable post-sweep), best_dim 5 at score 0.196, dims
spread 1–8 with mass at 4–6; spawn/evict active. Behavior: idle
**5.2%** (reversal bar <20% — unfired), all 12 actions in use,
crafting levers 25.3%, dig 8.8%. **Ground truth: `lead ×6` +
`wheat_seeds ×5`, still holding the seeds** — the leads doubled (3→6),
more world-event pickups; still no log, no offer, no craft — the 0058
reversal watch does NOT fire. New watch items: **(1) pra-flush has
crash-restarted 4× since 07-29** (asyncio TimeoutError → exit 1 → 5 s
systemd restart, roughly every 6–24 h; JetStream's 1 h buffer spans
the gap so no data loss expected — S3 key ranges auditable); **(2)
disk growth is now the run's own**: 66G/98G used (71%),
`pra-runs/c1c/snapshots` = 11G across 1,028 never-pruned files
(~1.2G/day) → projected ~72G at target date. Fine to finish; snapshot
pruning is a post-run cleanup candidate. Bridge/dash telemetry
spotless: dropped 0, publish failures 0, reconnects 0, wire errors 0,
seq_gaps 7 since the 07-29 dash boot. The emergence headline stays
open.

**2026-08-08 14:29 (12:29 UTC) — RUN CLOSED: duration met at 16.61
days of brain-steps; the headline answered — no emergence, one mined
log, and a week-1 material flare that quietly died.** Stopped
deliberately at 12:29:14 UTC (`systemctl disable --now pra-brain@c1
pra-bridge@c1`, clean shutdown). Final cumulative step **5,740,930**
against the pre-registered ≥ 4.8M — the bar was crossed **Aug 5
~19:20 UTC** (flush stamp of the object carrying step 4,800,000;
within an hour of the 07-31 projection). Pace over the 16d 20h 6m
wall clock: **3.946 steps/s**, 98.7% of the 250 ms ideal. Segment
accounting from snapshot-id continuity: cum 1→2,247,711 /
2,246,000→3,271,037 / 3,266,000→5,740,930, with **1,712 and 5,038
steps replayed** at the two resumes — resume-from-snapshot exactly as
designed. All numbers below are computed from the S3 objects
(`pra/v1/c1c/`), segment-aware and redelivery-deduplicated.

- **R1 — emergence: NOT EMERGED; the final-7-days window reads
  chance-level.** Over the last 2,419,200 steps (cum ≈3.32M→5.74M):
  planks **0**, sticks **0**, completed digs **0**, material
  acquisitions **3** (all `lead` — wandering-trader world events).
  `take_result` was pressed 98,493 times in the window, 222,305 over
  the run — and **an offer was showing on 0 of the 5,669,662 recorded
  steps**: the bot never staged a craftable item, so the
  offer-conditioned-taking ratio never had a denominator. The
  episode-0058 reversal watch (a self-produced crafting chain) closes
  **unfired**.
- **The whole-run record still holds a surprise: the first-mined-log
  watch item FIRED — on ~Jul 26, and nobody noticed.** A **material
  era ran cum ≈0.9M→2.03M** (≈Jul 25 morning → Jul 28 afternoon):
  **449 completed digs** (all of the run's total), **605 dirt**, **448
  leaf_litter**, **15 oak_sapling**, **8 wheat_seeds** picked up — and
  **one `oak_log`** entering the inventory at cum ≈1,299,001, in the
  era's peak-dig bucket (98 completions/100k steps). It was held
  ~1,000 steps and then placed back into the world (offer_steps = 0
  proves it was never staged; there is no drop action). Every pickup
  was eventually re-placed (acquisitions and losses symmetric to the
  unit). Against the amendment-v2 chance bar (0/8 pilot seeds
  completed a single dig), that era is **real above-chance material
  acquisition** — which then **decayed to zero by cum ≈2.03M and
  never returned**: the final ~3.6M steps were world-inert except the
  leads (9 total; 3 in a burst at 1.365–1.385M, then singles, last at
  5.23M). The E0 zero-material read at 328k was correct for its
  window — the flare began later.
- **R2 — rungs: climbed, then abandoned; falling, not rising.**
  Weekly (2.4192M-step weeks): completions 449 / 0 / 0;
  place-with-material 1,100 / 0 / 0; hold→place 800 / 0 / 0. Dig
  *action* usage rose (6.5% → 9.4% of steps) while completions fell
  to zero — action without effect; sensed mining-progress steps fell
  1.81% → 1.0%. Streak counts stayed flat (≥4-streaks 7,218 / 8,877 /
  2,470; max 35). Grid levers stayed heavily exercised throughout —
  something staged 36.2% of all steps, grid_put-with-item-in-hand
  132,645, hold→grid_put 94,674 — with **zero recipes ever staged**.
- **R3 — learning health: the no-rot clause fires as written,
  qualified as a regime change.** Early plateau (cum 0.2–0.6M) mean
  pred-err **0.101**; final-week mean **0.164** (+62%). The break is
  a single event at cum ≈0.9M: an eviction sweep took the population
  38 → ~22 and pred-err jumped 0.09 → 0.199 in the same bucket —
  after which the error *improved* monotonically-ish 0.199 → 0.162
  through the rest of the run (still inching down at stop; EMA 0.178
  live pre-stop). Population stable 20–24 post-sweep (not at any
  ceiling); churn spawn 23,679 / evict 23,614 (≈1 per cycle). The
  material era sits *inside* the post-sweep regime — the flare began
  at the sweep, not before it.
- **R4 — reversal reading: the crafting=False fallback does NOT
  fire.** Grid primitives were anything but unused (36.2% staged,
  ~4.8% of all actions grid_put, 4.7% grid_take, 3.9% take_result),
  and improvement (EMA 1.0 → 0.162) is not materially below the
  pilot arm (0.778 → 0.143). The engagement data is the finding:
  the machinery was exercised massively and the gate that never
  opened was *staging a craftable* — the one log went back into the
  dirt instead of into the grid. The hierarchy arc opens with that
  exact shape.
- **R5 — operational honesty.** Brain: **2 mid-run restarts, both
  deliberate, zero crashes** (Jul 29 06:37:27; Aug 1 06:36:20 — the
  second was *between readings and previously unrecorded*; journald
  has since lost the Started lines for both, but the final process's
  CPU accounting — 1w 5h 52m wall ending 12:29:14 — pins the Aug 1
  start, and step-rate continuity shows no downtime). Bridge: **zero
  mid-run restarts** — the 07-31 entry's claim that the bridge
  restarted on 07-29 was wrong; only brain + dash restarted. Dash: 1
  (Jul 29). Flush: **14 crash-restarts** Jul 30 → Aug 6 (the
  asyncio-TimeoutError cough, worse than the 4× known on 07-31).
  Snapshot chain: 942 notices, cadence-25 clean per segment except
  2 missing notices (cycles 14,325 and 21,275). In-span seq gaps:
  7,090 step events missing (0.125%) — at-least-once with visible
  gaps, as designed; dash counted 18 union gaps at stop.
- **The incident, in the open: the disk finally bit.** MinIO refused
  writes from **08:30:47 UTC** (root disk 100% — the never-pruned
  c1c snapshot store, ~34G/1,912 files; root cause compounded by
  `pra-flush --snapshot-dir` still pointing at *c1b*, so c1c was
  never mirror-pruned). The 1 h JetStream buffer then expired seqs
  4,828,464→4,944,345 unrecovered: **≈57,695 steps of telemetry lost
  (~08:29→11:29 UTC, 2.4% of the final-7-days window)**. The final
  ~56 minutes (seqs 4,944,346→4,970,922; 43,079 records) were pulled
  off the buffer before expiry and held locally, to be landed into
  S3 once disk is freed. Ground truth brackets the gap: inventory
  identical on both sides (lead ×9 + wheat_seeds ×5), no offer at
  any recorded step, idle 5.6% in the rescued tail — no sign the gap
  hid an event. Newest snapshot `snap-000005737000-23900`; a future
  resume would replay 3,930 steps.

Post-run queue (none executed yet): prune the snapshot store, fix
`--snapshot-dir`, root-cause the flusher TimeoutError, land the
rescued tail, then the R1–R5 journey episode carries the numbers to
the public record.

**2026-08-08 16:20 (14:20 UTC) — postscript: the queue's first half
executed, and the loss figure sharpens slightly in our favor.** On
the owner's instruction the snapshot store was pruned to the newest
50 pairs (906 pairs deleted, **33.9 GB freed**; disk 100% → 66%,
newest `snap-000005737000-23900` kept). MinIO accepted writes again
on the flusher's next 60 s retry — **its stuck batch landed intact**
(`…T083047Z-000004828465-000004829419`, 476 step events through step
2,404,479), so the expired window is smaller than the closing entry
stated: **lost = seqs 4,829,420→4,944,345, exactly 57,219 steps**
(cum 5,670,479→5,727,697, ~08:31→11:29 UTC; 2.37% of the final-7-days
window — the closing entry's ≈57,695 was correct pre-recovery). The
**rescued tail is now landed in S3**: 42,665 records across all 8
persisted families as `…/20260808T141326Z-…` objects (the 414
unscoped `discover` records excluded, matching flusher semantics), so
the durable record now runs seq 1→4,829,419 and 4,944,346→4,970,922
with the one hole in between, visible by key ranges as designed.
Flusher healthy since (zero failures post-recovery; buffer down to
residual control chatter). Still open: `--snapshot-dir` still points
at c1b, the TimeoutError root-cause, and publishing the telemetry.

**2026-08-08 17:05 (15:05 UTC) — the ops tail closes.** Both flusher
defects are root-caused and fixed in the repo. **(1) The crash loop:**
journalctl holds the full trace — nats-py's `_fetch_n`
(`js/client.py:1289`) raises a **bare `asyncio.TimeoutError`** when a
partial batch expires, and the pump caught only `nats.errors.
TimeoutError`; the except now takes both (builtin `TimeoutError`
covers it on ≥3.11). First crash was actually 2026-07-21 15:57 (c1b
era) — the "cough" predates this run's journal. **(2) The prune miss:**
`pra-flush.service` hardcoded `--snapshot-dir …/c1b/snapshots`; the
unit now reads `PRA_SNAPSHOT_DIR` from `/etc/pra/s3.env` (empty =
mirroring off), so the store follows the run instead of fossilizing.
Archive sizes for the publishing decision: `pra/v1/c1c/` = **2.41 GB
in 83,634 objects** (c1b 0.11 GB, c1 0.02 GB, mirrored snapshots
0.11 GB). What remains open, deliberately: publishing the archive
(hosting choice is the owner's) and the observatory's fate — dash +
flush are still enabled on beno4 (idling on control chatter; the
fixed unit takes effect at the next provision).
