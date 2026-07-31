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
