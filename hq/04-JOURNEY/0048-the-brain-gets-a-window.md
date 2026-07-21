# Episode 0048 — The brain gets a window (2026-07-21)

The C1 stack could be watched two ways — through a spectator's eyes in the
Minecraft world (the `up.sh` one-command stack, added this same day) and
through the run-level dashboard — but the brain itself was a black box: the
observation vector crossed the wire unnamed, the census aggregated the
per-frame states away, and frame births/deaths were never published at all.
Feature 029 (`029-brain-telemetry-dashboard`) closed that: an additive
`brain.*` family under pra.v1 — anatomy/channel metadata announced at world
construction and heartbeat-republished, complete per-frame census rows on
the census cadence, spawn/evict lifecycle events — and a Brain tab in
pra-dash: a metadata-driven body schematic (live per-channel bars, chosen
action highlighted), named strip charts with a decoded scrolling log, the
frame table, and the lifecycle timeline.

The load-bearing design fact: **zero core engine edits** [measured — no
`src/pra/core` diffs in the branch]. All three data sources already crossed
the tap's seams: steps were mirrored (just unnamed), the census already
walked `frame_states()` and discarded the rows, and the engine routes every
population change through `bus.register`/`bus.unregister` on the bus the
tap constructs — so a delegating `_TapBus` mirrors lifecycle completely.
Metadata comes from the bodies themselves: `Body.anatomy_meta()` on the
base composition (live lists, so grown tools stay correct), an
`action_labels()` hook on `CommandActuator` (preset keys; `{}` → `idle`)
and `RoverDrive`, structural fallback on `GymnasiumWorld` — one dashboard
renderer serves Minecraft, rover, and Gymnasium with zero body-specific
code [measured: the same tab rendered rover metadata in the gate and the
C1 anatomy live].

Honest bars, all green [measured]: rows==census (count and best frame) at
100% of mid-run censuses; lifecycle exactly-once, seq-ordered, and
Σspawn−Σevict equal to the final population from boot *and* from a mid-run
attach census, under forced churn (`max_frames=4`); engine outputs
byte-identical with and without the tap bus; the byte-frozen baseline
suite untouched. Live verification against the real stack (nats-server +
mineflayer + 1.21.11 world): the Brain tab showed all four panels with
real data — vitals flat at 1.0 (peaceful mode), the env channels ramping
with the day cycle, frame 3 spawning at step 1240 on the timeline, `idle`
highlighted as the newest action — while the run completed cleanly
(2,440 observation steps, final population 7).

Two scope choices recorded as spec assumptions rather than debated
[judgment]: "inside the frames" means the statistics the engine judges
frames by, not raw weight matrices; logs/timelines are bounded live
windows (steps 600, events 512), not archives. Both have natural
extensions if wanted. The vocabulary choice that made reconciliation
exact [mechanism-argument]: `spawn` includes boot/restore registration —
the timeline shows the population *appearing*, and the arithmetic closes
from any attach point.

Reversal condition: none — records a completed build/measurement. The
assumptions above are the named extension points; if raw-weight export or
durable history is ever wanted, it is an additive follow-up, not a
reversal.

Trail: specs/029-brain-telemetry-dashboard/ (spec, plan, research,
data-model, contracts/brain-subjects.md, quickstart, tasks);
hq/02-DESIGN/ propagation in the same change-set; commits e76ff08
(spec), 014b171 (plan), 01d0b13 (tasks), 892b84a (US1), 74e3b3e (US2),
b4bd04c (US3), 22729be (US4), 1400611 (polish).
