# Feature Specification: Two Doors — the Taught Arm vs the Blank (E1)

**Feature Branch**: `034-two-doors`
**Created**: 2026-07-24
**Status**: Draft
**Input**: User description: "E1 of the self-set-goals research
(hq/01-RESEARCH/self-set-goals/README.md): does taught knowledge plus the
existing intrinsic drives reproduce the crafting chain that 328k
frontier-alone steps never produced once (E0)? A scripted teacher drives
the body through the full log→planks→sticks chain on the FakeBridge world
while the brain learns from the lived stream (door 1, the senses); the
graduate then free-runs on frontier alone. Measured against the blank at
the bars registered 2026-07-23, before any run."

## Overview

E0 measured the floor: frontier-alone produced **zero** logs, planks, or
sticks in 328,560 live steps, and the 033 pilot put undirected chance at
≈ 0 (0/8 digs). Any full chain from a taught brain is therefore
unmistakable. E1 asks the premise-deciding question: **is demonstration
enough, or does directed multi-step behavior need goal machinery (E2)?**

**The arm dissolution (owner's call, 2026-07-24).** The topic README
registered three arms (E1a guided body / E1b donated brain / blank). At
plan time the mechanism argument showed E1a and E1b collapse: 028 seeding
is a full-state resume, and E1b's donor *is* E1a's graduate, so at the
free-run boundary the two arms hold byte-identical brains — only the world
could differ, and either choice makes the comparison empty (fresh world =
identical runs) or confounded (teacher-depleted world = material
handicap). The owner dissolved the split before any run: **two arms,
taught vs blank**. The frozen ordering prediction (E1a ≥ E1b) is recorded
as *untestable with current machinery*, not dropped; a partial/structural
transfer mechanism (structure without the lived episode) is the named
successor that would make the two-doors contrast testable. The primary
prediction — taught > blank — stands and is what E1 decides.

**Architecture — zero core edits, all seams:**

1. **The teacher is a Policy.** A `ScriptedTeacher` injected at Engine
   construction plays a fixed 22-action tape; learning is
   policy-independent (the store learns before the policy is consulted,
   `engine.py` online step order), so the brain learns the demonstrated
   stream exactly as it learns everything — door 1.
2. **The tape** (verified against `_World.apply` mechanics; P0 proves it
   live): from spawn — `turn_left ×2` (45°/turn; faces the starter wood at
   (−1,0)), `dig_ahead ×12` (wood takes 12 consecutive ticks; gain
   `oak_log`), `hold_next`, `grid_put`, `take_result` (planks ×4),
   `hold_next` (deterministic cycle lands on planks), `grid_put ×2`,
   `take_result` (stick ×4), `idle`. One full chain, 22 steps.
3. **The teacher resets the spoon.** Each demonstration needs a fresh
   world (the starter column digs once). The guided phase is a chain of
   snapshot-bridged engine runs: each segment resumes the prior brain with
   `world_state=None` (the engine then boots a fresh world — traced legal)
   and plays the tape once. 45 segments ≈ **45 demonstrations, 1,012
   guided steps** (segment 1 carries one 22-step warmup episode plus one
   22-step cycle; segments 2–45 are one cycle each). *Open deviation from
   the plan sketch:* the dose was agreed as "~45 demos ≈ 1,000 steps,
   15 segments × 3 chains"; pathing to the two far wood columns would make
   the tape fragile, so the same dose ships as 45 segments × 1 chain —
   dose unchanged, registered here before any run.
4. **The free-run.** The graduate resumes (world stripped, fresh world)
   with no injected policy and the config's own
   `drive_weights=(("frontier", 1.0),)` — the curiosity-lookahead policy
   rebuilds from config, matching the c1c posture E0 measured. 228 cycles
   × 22 steps = 5,016 steps; the analysis window is the registered
   **H = 5,000**.
5. **The blank** is a fresh brain, same config family, frontier from
   birth; its window is its first 5,000 steps. Arms are seed-paired
   (resume requires learner seed = donor seed; the world is deterministic
   and identical for every seed, so all variance is the brain's RNG).

**Detection** is the E0 ground-truth reader over the transport's
`on_view` stream: a **full chain** requires, in causal order within the
window, a log entering the pocket (dig), a planks-craft (planks rise while
logs fall), and a stick-craft (sticks rise while planks fall). Placed-and-
re-dug items change no craft count (no rise-with-fall signature), so the
detector cannot be gamed by shuffling blocks.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The tape drives the chain (Priority: P0)

The scripted teacher, run against a fresh FakeBridge world, completes the
full chain every segment — before any arm runs.

**Independent Test**: one seed, guided phase only; assert via ground truth
that every segment ends with exactly one more stick-craft event.

**Acceptance Scenarios**:

1. **Given** a fresh world, **When** the tape plays, **Then** the pocket
   holds sticks by step 21 and the view stream shows dig → planks-craft →
   stick-craft in order.
2. **Given** 45 chained segments, **Then** 45/45 demonstrations complete
   (any miss stops the experiment at P0 — the gate is the tape, not the
   brain).

### User Story 2 - Pilot before power (Priority: P1)

8 seed-paired seeds, both arms, eyes on everything (chains, partial
progress, action mixes, frame counts) — published as
`specs/034-two-doors/pilot-results.md` before the confirmatory run.

**Acceptance Scenarios**:

1. **Given** the pilot, **Then** per-seed chain counts and partial-chain
   context (digs, planks-crafts, stick-crafts) are recorded for both arms.

### User Story 3 - The registered read (Priority: P1)

24 seed-paired seeds against the bars frozen in the topic README
(2026-07-23, commit 11725f1): **taught ≥ 6/24 seeds with ≥ 1 full chain in
H = 5,000; blank = 0/24** (any nonzero blank re-opens the 0052 baseline
and voids the read).

**Acceptance Scenarios**:

1. **Given** the confirmatory run, **Then** the bar is decided — PASS or
   an honestly recorded FAIL — and the outcome propagates to the topic
   README and journey episode 0054 whatever the verdict.

### Edge Cases

- **Warmup consults the injected policy** (same loop), so the tape plays
  from step 0 of a deterministic world — no random prefix to desync it.
- **Stale held item after the log is consumed**: `hold_next` cycles
  `[None] + kinds`; a held name no longer in the cycle resolves to index 0
  → next is the first kind — deterministic, tape-safe.
- **A second log in the grid kills the planks offer** (033 trap): the tape
  stages exactly one; P0 asserts offers actually appeared by checking the
  crafts landed.
- **Blank warmup**: the blank's first 5,000 steps include its single
  22-step warmup episode — "from birth" as registered.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The guided phase MUST use only existing seams — an injected
  Policy, snapshot capture, and resume with `world_state=None` — zero
  src/pra edits for the experiment itself.
- **FR-002**: The guided dose is **45 demonstrations / 1,012 steps** as 45
  snapshot-bridged single-chain segments; registered here before any run;
  if the taught arm FAILs, dose is the first openly-amendable candidate.
- **FR-003**: Free-run and blank arms MUST run frontier-alone
  (`drive_weights=(("frontier", 1.0),)`), matching the E0-measured
  posture; H = 5,000 steps per the registered bars.
- **FR-004**: Chain detection MUST use the ground-truth view stream with
  the causal-order rule (dig → planks-craft → stick-craft), never the
  sensed channels.
- **FR-005**: The bars in `hq/01-RESEARCH/self-set-goals/README.md`
  (registered 2026-07-23) are normative; this spec adds no new bar and
  amends none.
- **FR-006**: The experiment runner lives in the session scratchpad per
  the arc convention (committed only if the arc graduates to a shipped
  feature); committed artifacts are this spec, `pilot-results.md`, the
  topic-README outcome, and journey episode 0054.

### Key Entities

- **ScriptedTeacher**: a Policy playing the 22-action tape, then `idle`;
  stateful step index, no RNG draws.
- **Segment chain**: 45 capture→strip→resume hops, same seed throughout.
- **The read**: per-seed full-chain counts in the 5,000-step window, both
  arms, plus partial-progress context rows.

## Success Criteria *(mandatory)*

- **SC-001**: P0 proves the tape (45/45 demonstrations) before any arm
  runs.
- **SC-002**: The pilot publishes 8-seed results for both arms before the
  confirmatory run.
- **SC-003**: The registered 24-seed read is decided — PASS or recorded
  FAIL — with blank = 0/24 verified.
- **SC-004**: Outcome propagated (topic README, journey 0054) whatever
  the verdict; the arm dissolution and the untestable-prediction note are
  recorded in the topic README as part of this feature's landing.

## Assumptions

- The 028 same-seed resume constraint makes arms seed-paired by
  construction; the deterministic world means cross-seed variance is
  entirely brain RNG — 24 seeds measure the brain, not the world.
- FakeBridge at `tick_ms=1` is fast enough for 2 arms × 24 seeds × ~6k
  steps sequentially; parallelism is an implementation convenience, never
  a results-changer.
- Feature numbering follows the branch (`034-two-doors`); journey episode
  0054.
