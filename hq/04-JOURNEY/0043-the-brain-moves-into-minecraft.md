# Chapter 43 — The brain moves into Minecraft: C1's world, built to launch-ready (2026-07-20)

C1's world was chosen by its owner: not a cooldown HTTP game but a
small self-hosted Minecraft server — Docker to run, mineflayer to
reach, renewing enough to live in. The build (feature 027) rested on a
fact feature 013 had already created without naming it: `Ros2Body` is
transport-generic — the control tick, the staleness policy, the startup
gate, the declarative anatomy owe nothing to ROS. So the adapter is a
*transport*, not a body: `MinecraftTransport` speaks a versioned
newline-JSON protocol (pra-mc/1) to a bridge, and the one-seam claim of
chapter 26 now covers hardware, simulators, and a live game with zero
new body machinery and zero new hard dependencies.

The gate never touches Minecraft: an in-repo FakeBridge — a
deterministic voxel sketch speaking the full protocol over a real
localhost socket — carries all sixteen contract and integration tests,
including same-seed byte-identity and snapshot/exact-resume (fake mode
is Doc 06 §5b class 1; the live server is class 4, stated everywhere it
matters). Two resume semantics surfaced and are now explicit: a resumed
continuous stream never calls reset(), so the transport boots lazily at
first use, applying restored world state after the handshake — safe
here precisely because pra-mc delivers every channel every tick.

The real-stack smoke did what smokes are for: it found the two
failure modes that only exist against a live world. Unbounded
mineflayer awaits (a dig takes seconds; placeBlock can hang) stalled
the tick past the socket deadline — every world action is now bounded
by the tick's own budget, and a too-slow dig is abandoned mid-swing as
a world fact, not a protocol stall. And a brain killed mid-request
crashed the bridge through a write-to-dead-socket rejection — a
weeks-long bridge now logs what it cannot attribute and dies only when
its bot loses the server. Measured green end-to-end: a 1,960-step live
run against dockerized 1.21.1 (prediction error 0.50 → 0.10 — the
brain learns the real world), a hard kill after cycle 2, resume from
the snapshot reconnecting and completing, the one-client refusal
observed live, and the full gate re-run clean with the stack torn
down. The runbook (`examples/minecraft/README.md`) applies the arc-026
posture verbatim: cap on, snapshot cadence sized to the ~8 B/step
growth, ceiling population expected. **C1 is launch-ready; the
multi-week run — and its story — belongs to its operator.** Trail:
specs/027-minecraft-body/; commits `8e65551` (spec), `fc516ca`
(adapter), `b7b1d72` (example), `bb36ce4` (smoke + hardening).
(Numbering note: authored as "Chapter 42" while the vision chapter
landed on main in a parallel session; renumbered mechanically to 43 at
merge, content untouched — the ch. 37 precedent.)
