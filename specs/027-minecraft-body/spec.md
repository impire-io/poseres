# Feature 027 — Minecraft body: the C1 deployment world (spec)

**Branch** `027-minecraft-body` · **Date** 2026-07-20 · **Status** planned
**Owner intent**: C1 (ROADMAP) with the target world chosen by the user:
a small self-hosted Minecraft server (Docker), not a cooldown HTTP game.
The C1 exit is unchanged — one character, learning continuously for
weeks, published telemetry — and the arc-026 soak's launch posture and
config notes apply as recorded.

## Story

A hobbyist runs two commands — `docker compose up` for a small Minecraft
server plus the bot bridge, and `python run_c1.py` for the brain — and
walks away. The brain lives in the world through a body of named parts
(where am I, how am I, what is around me / move, turn, dig, place),
learns continuously without resets, snapshots itself on a cadence, and
resumes exactly (its own state) after any interruption. The dashboard
(B7) can attach at any time. Weeks later the telemetry tells the story.

## Functional requirements

- **FR-001** The adapter is a **Transport** for the existing feature-013
  seam: `Ros2Body` mounts unchanged over `MinecraftTransport`
  (start/subscribe/publish/tick/can_reset/reset_world/overruns/close).
  No new body machinery; the ch. 26 "one seam" claim gains its second
  transport.
- **FR-002** The bridge wire protocol is versioned, newline-delimited
  JSON over TCP (stdlib only on the Python side). The `hello` handshake
  carries the bridge's channel table (name → width); subscribing to an
  unknown channel, or a width mismatch against the declared anatomy, is
  loud at mount time — never a shape error mid-run.
- **FR-003** One engine step = queued command presets + exactly one
  bridge `tick` round-trip (the bridge executes the control burst for
  `tick_ms`, samples the world, answers with every channel's vector),
  then delivery to the subscribed sensors. The 013 ordering contract
  (publish → one tick → sample) is asserted against a journal, not
  assumed.
- **FR-004** Hold-last-value staleness, startup gate, and loud limits
  are inherited from the 013 body unchanged. A broken bridge connection
  fails the run loudly (no silent retry loops); recovery is
  resume-from-snapshot, which is the C1 runbook's stated restart path.
- **FR-005** An in-repo **FakeBridge** — a deterministic voxel
  mini-world speaking the same wire protocol over a real localhost
  socket — carries the entire test gate: framing, handshake, tick,
  delivery, staleness, single-boot, close. No Minecraft, Node, or
  Docker anywhere in the gate.
- **FR-006** Reproducibility classes stated per mode (Doc 06 §5b): the
  live server is **class 4, openly non-reproducible** (the 013
  free-running precedent); FakeBridge mode is deterministic — two
  same-seed runs are byte-identical, and the gate proves it.
- **FR-007** Continuous mode with snapshots works in both modes: the
  transport exposes `state_dict`/`load_state_dict`; against FakeBridge
  it round-trips the full world state (exact resume, gate-proven);
  against the live bridge it carries a stated live-world marker (brain
  state exact, world resumes wherever the live server is — class 4,
  recorded).
- **FR-008** Zero new hard dependencies. Node/mineflayer and Docker
  live in `examples/minecraft/` only, like Gazebo in 013.

## Success criteria

- **SC-001** Full quality gate green with no external software, no
  skips.
- **SC-002** Two same-seed continuous runs over FakeBridge produce
  byte-identical run summaries; snapshot mid-run + resume reproduces
  the uninterrupted final state byte-for-byte (fake mode).
- **SC-003** The worked example runs against a real dockerized server:
  bot spawns, brain steps, snapshot written, resume reconnects — the
  smoke measured and recorded (014 discipline: real stack green, then
  the gate re-run clean without it).
- **SC-004** The C1 runbook is two commands plus a stated
  stop/resume/watch procedure, with the arc-026 config notes applied
  (cap on, snapshot cadence, ceiling-population expectation).
