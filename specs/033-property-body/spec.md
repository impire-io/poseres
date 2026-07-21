# Feature Specification: The Property Body — Senses Without My Ontology

**Feature Branch**: `033-property-body`
**Created**: 2026-07-21
**Status**: Draft
**Input**: User description: "Classifier-free senses: properties and appearance signatures instead of material classes; dig as a held intention with sensed progress; named channels and a ground-truth world view"

## Overview

Three owner arguments, accepted in full, form this feature — all
surfaced by the first hours of the live run:

1. **"Why do you need material classifiers? Isn't it up to the brain to
   figure out what can be used as materials?"** The four named classes
   (blocks/logs/planks/sticks) were my taxonomy baked into the senses —
   and it broke measurably: the live bot carried 12 real items (pale
   moss, gravel, a dripleaf) while its pocket channels read 0.0 forever,
   because the name-filter knew only "dirt" and "stone". Any name list
   is somebody's opinion. Replacement: **sense properties and
   appearance** — world-mechanical facts the game itself defines (is
   the item placeable, how many) plus a small stable **appearance
   signature** (deterministic hash of the item identity: things look
   different, no semantics chosen by anyone). Categories become the
   brain's job, literally.
2. **"The action budget cannot be a flat timeout."** The 1-second bound
   silently made logs (3 s bare-handed) unmineable — the crafting
   question was structurally dead. Digging becomes a **held intention**:
   `dig_ahead` starts breaking; repeating it continues; any other
   action cancels; a sensed **progress channel** rises as the block
   gives (vanilla shows cracks — the world's own honesty). No
   behavior-shaping timeout remains; the owner's ~10 s is only a safety
   cap on a dig making no progress.
3. **"We need a better understanding of what the channels are."**
   Metadata gains **per-channel labels** (the 029 format always
   supported them; no body filled them in) — `env.sin_time`, not
   `env[1]` — and the dashboard gains a **ground-truth panel**: the
   world narrates the bot's real inventory (actual item names), held
   item, and position through the feature-015 world-view channel. Two
   truths side by side: what is there vs what the brain senses of it.

The builder's body becomes **obs 32 / actions 12** (same 12 actions;
`hold_next` now cycles the pocket's distinct item kinds). The
feature-027 legacy body (14/8) stays one flag away; on the new bridge
its `place_ahead` is inert (nothing held, nothing consumed) — stated.

## User Stories (each independently testable in the gate)

### US1 — Properties and appearance, not classes (P1)

Channel redesign: `pocket` (4: total, kinds, placeable, other — pure
aggregates), `hand` (6: present, placeable, count, sig0–2), `grid`
(7: staged, offer, offer_placeable, offer_count, offer_sig0–2),
`mining` (1: break progress). `blocks` stays 027-exact. Signatures:
sha256 of the item name, bytes 0–2, mapped to [−1, 1] — identical in
both bridges by construction. Placeable = the game's own fact (an item
that maps to a block — so logs, gravel, moss are placeable; sticks are
not — fixing my vanilla deviation too). `hold_next` cycles
nothing → the pocket's distinct kinds sorted by name; `place_ahead`
and `grid_put` act on the held kind. The world's pocket-craft rules
(any log alone → 4 planks of its species; two same planks → 4 sticks)
are world mechanics, stated in the contract, never sensed as names.

**Acceptance**: the full chain runs in the fake gate with every rung
sensed via properties/signatures only; a pale-moss-like item (any name)
counts in the pocket the moment it exists; log-staging offers a
*placeable* result, planks-staging a *non-placeable* one, and the brain
can tell logs from planks only by signature — as designed.

### US2 — Digging is persistence, and persistence is sensed (P1)

The fake gains per-material dig durations (mineral ~3 ticks, wood ~12
at the 250 ms posture — vanilla-proportioned); `mining` rises with
each continued dig, resets on cancel, and the block breaks at 1.0,
yielding its item. The live bridge starts/continues/cancels
`bot.dig` the same way, computes progress from the game's own dig
time, and caps a no-progress dig at 10 s.

**Acceptance**: fake — wood requires exactly its duration of repeated
digs, an interruption resets progress, `mining` is monotone within an
attempt; state seam carries mid-dig progress byte-exactly. Live smoke —
a real log placed ahead breaks under repeated digs with progress
visibly rising, and the drop lands in the pocket aggregates.

### US3 — Named channels and ground truth (P2)

Every sensor declares per-channel labels (contract table = the labels);
`anatomy_meta` carries them; charts/log/schematic show them with zero
dashboard changes (the 029 path). The bridge's tick response gains a
compact `view` (position, held item name, real inventory names+counts);
the transport forwards it to the world-view channel when telemetry is
attached; the dashboard renders a Ground Truth panel for kind
"minecraft" (and the rover keeps its map).

**Acceptance**: metadata for the builder body carries labels for all
32 dims; the dash state endpoint shows view.live with real item names
during a fake-transport run; unit-labeled charts need no dash edits
beyond the one new view renderer.

## Requirements (the load-bearing subset)

- **FR-001**: No channel may encode a material category chosen by the
  implementation; identity reaches the brain only as properties +
  signatures. (The audit: grep the bridges for item-name conditionals
  outside the world-rule table.)
- **FR-002**: Signature function identical across bridges:
  sha256(name-utf8) bytes 0..2, each byte/127.5 − 1.
- **FR-003**: Dig progress is world state: continued digs accumulate,
  cancellation resets, completion yields the item; no flat action
  timeout; 10 s no-progress safety cap, live only.
- **FR-004**: Labels are part of the contract table and travel in
  `anatomy_meta`; the ground-truth view travels the 015 world-view
  channel (humans-only — the brain never senses it).
- **FR-005**: Fake-mode byte-identity + exact resume incl. mid-dig and
  mid-staging; reference suite untouched; zero core edits.
- **FR-006**: Pre-registered pilot re-baseline (the body changed):
  8 paired seeds, bar (a) improvement > 0 in ≥6/8 at 32/12; context —
  chance rates for pocket-change/planks/sticks under the persistence
  cliff (expected ≈ 0: consecutive-dig requirements make chance
  material acquisition collapse), dig-persistence statistics, paired
  tax vs legacy. Published verbatim.
- **FR-007**: Fresh run: new world, new snapshot dir, run id `c1b`
  (never mix telemetry prefixes with the v3 burn-in — the join-pollution
  lesson), amended pre-registration before boot.

## Success Criteria

- **SC-001**: gate green; the full property-sensed chain and the
  persistence mechanics proven deterministically; labels on all dims.
- **SC-002**: live smoke on the node: signature/property channels match
  the real inventory; a real log broken by held-intention digging.
- **SC-003**: dashboard shows named channels + ground truth with real
  item names, zero body-specific channel code.
- **SC-004**: pilot bar decided, context published, run plan amended,
  run `c1b` live on a fresh world.

## Assumptions

- The two pocket recipes as world rules (stated in the contract) are
  the v1 craft surface; general recipe matching is a later rung.
- The chance-level material cliff is accepted knowingly: with
  persistence required, *any* sustained crafting in the long run is
  emergence; a never-climbed ladder remains a publishable null
  (the 031 posture, sharpened).
- Reversal condition: unchanged from 031 (fall back to the 14/8 flag),
  with the added note that the legacy body on the v4 bridge cannot
  place (nothing held) — the reversal is about learning viability, not
  building.
