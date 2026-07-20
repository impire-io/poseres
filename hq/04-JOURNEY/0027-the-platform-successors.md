# Chapter 27 — The platform successors: NATS at the seams, the dashboard behind it, and the robot's real gate (2026-07-18)

A sequencing decision, not a build — recorded because roadmap changes are
decisions. Three candidate directions were on the table: put NATS
"underneath" PRA as its storage and messaging substrate, build a web
dashboard/monitor, and start the physical robot. Examining them against
the repo's own record reordered all three.

The NATS direction survived; its framing did not. **Rejected: NATS
underneath the engine.** The fast loop is a batched in-process kernel
(~60k obs×frame evals/s, feature 001) whose entire validation story is
byte-identity — a network hop inside it would break throughput and the
T1–T7 gate at once. What the architecture actually permits — and what the
horizon-ambitions chain (A1 → B4 → external bus backend → multi-machine)
had already named as the step after B4, which closed in chapter 22 — is
**NATS at the seams, opt-in, reference byte-frozen**: the Doc 02 bus as
telemetry subjects, the SnapshotStore over a JetStream object store
(Phase D's shareable-brains transport, bought once), a request/reply
control plane, with inter-brain communication named as the horizon this
enables but excluded from the exit. The determinism line is pre-drawn:
telemetry *out* is observer-safe (the B1 viewer precedent); experience
*in* over a network joins free-running ROS2 as a Doc 06 §5b class-4
mode, stated up front. Scheduled as **B6**, design-first.

The dashboard turned out to be half-built and half-mis-sequenced: the B1
viewer already proved the observer discipline (byte-identity with the
viewer attached), and the dashboard's natural data source is B6's
subjects — building it first would mean building the transport twice.
Scheduled as **B7, gated on B6**, with its two purposes split honestly:
the monitor half (simple + advanced modes) is an instrument; the
"show what makes PRA unique" half is a showcase spend under principle 1.

The robot was never a new item — it is C2's remaining showcase half
(the platform landed as feature 013) — but writing it down surfaced its
real gate: chapter 26's Gazebo lidar NaN-poisoned a run, chapter 25
measured channel static collapsing selection, and a physical robot's
sensors are exactly that world. **Learned channel weighting is a de
facto research gate for the C2 showcase**, now stated in the roadmap;
the CAD/electronics build may proceed in parallel because hardware is
cheap and the brain is the bottleneck. Nothing was built in this
chapter; the tracking system remains the existing one (roadmap exit
criteria + spec-kit + this file) — a separate workflow tool was
considered and rejected as duplication. Trail: `ROADMAP.md` diff (B6,
B7, C2 note, sequencing summary); committed with this chapter.
