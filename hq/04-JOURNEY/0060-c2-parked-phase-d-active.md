# Episode 0060 — C2 parked, Phase D active: the road re-prioritized (2026-07-26)

With the staleness-detection program closed
([episode 0059](0059-scheduled-probing.md)) and the c1c run soaking on
its own toward the R1–R5 read, the owner re-prioritized the roadmap's
front: **C2 (the hardware body) parks, Phase D (make it a product)
activates.** [judgment — an owner's priority call, recorded as such]

Nothing technical moved. C2's gates were met before this decision and
stay met after it — the ROS2 adapter (episode 0026) and learned channel
weighting (episode 0030) are built and validated; the parking is
sequencing, not a gate. Phase D's items (API stability & v1.0, docs
site, shareable brains, contribution surface, demo videos, the book)
are cheap individually and decisive together, and none of them waits on
a showcase: C1's run supplies the honest telemetry the show-then-tell
rule requires.

Order inside Phase D, with the reasoning recorded: **API stability &
v1.0 first** — the docs site documents the seams, shareable brains ride
the SnapshotStore seam, and the contribution surface points contributors
at the seams, so freezing the seam surfaces (Body, Sensor/Actuator,
Drive, SnapshotStore) before documenting them prevents every downstream
item from chasing a moving target [mechanism-argument].

Reversal condition: C2 un-parks on the owner's call at any time; the
readings that should prompt the revisit are (a) the c1c R1–R5 read
landing (the run's telemetry is the showcase family's demo material —
a natural moment to re-weigh showcase vs product), or (b) a Phase D
item measurably blocking on a physical build (e.g. the growth video
judged unconvincing from simulation alone).

Trail: `hq/03-IMPLEMENTATION/roadmap.md` (C2 section and Phase D header
updated this commit); decision made in-session 2026-07-26.
