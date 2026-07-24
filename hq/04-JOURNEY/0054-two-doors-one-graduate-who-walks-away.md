# Episode 0054 — Two doors, one graduate who walks away (2026-07-23 → 2026-07-24)

The self-set-goals topic (`hq/01-RESEARCH/self-set-goals/`) went from open
bars to two measured rungs in two days. First the free experiment: the
owner delegated the numbers, the bars were registered and committed
**before** the S3 archive was opened (E0: read c1c's crafting telemetry
against the 033 chance floor; E0b: fold in episode 0053's anti-idle
reversal; E1: 24 seeds/arm, H = 5,000 free-run steps, k = 6/24, blank must
be 0/24). The read took the project's first S3 archive-reader (MinIO is
loopback-only on beno4 — SSH tunnel, gzip-JSONL, dedupe by seq).

**E0 [measured]: the prediction confirmed exactly, and deeper.** In
328,560 archived c1c steps, frontier-alone crafted nothing — and never
held a single log. Items ever pocketed: dirt ×1, leaf_litter ×22,
wheat_seeds ×1. The drive digs (6,548 digging records, dig_ahead 4.7% of
steps) but never completes a tree; a crafting offer existed on **0
steps**. Premise stands; E1 authorized. **E0b [measured]: the 0053
reversal does not fire.** Idle over the last 10k steps: **3.1%** (bar
< 20%; competence camped at 26.7%); top action `forward` 35.7% (bar
< 50%), the rest near-uniform. Frontier-alone stands for Minecraft, and
0053's "anti-idle effect not yet measured" caveat closes.

**Then E1 — feature 034, `034-two-doors` — and an honest collapse before
any run.** The registered arms (E1a guided body vs E1b donated brain)
turned out mechanically identical: 028 seeding is a full-state resume and
E1b's donor *is* E1a's graduate, so both arms hold byte-identical brains
at the free-run boundary — only the world could differ, making the
comparison empty (fresh world) or material-confounded (teacher-depleted
world) [mechanism-argument]. The owner dissolved the split pre-run: two
arms, **taught vs blank**; the E1a ≥ E1b half of the frozen prediction is
recorded *untestable with current machinery*, and partial/structural
transfer (inheriting structure without the lived episode) is the named
successor. Dose owner-set: **45 demonstrations / ~1,012 guided steps**.

The teacher is a 22-action scripted Policy on the FakeBridge world —
turn, twelve dig ticks, hold, stage, take planks, hold, stage twice, take
sticks — with each demonstration in a fresh world via snapshot-bridged
resume with `world_state=None` (the teacher resetting the spoon). Zero
src edits: learning is policy-independent (the store learns before the
policy is consulted), so the brain learns the guided stream through door
1, the senses. P0 proved the tape: **45/45** chains. The 8-seed pilot was
published before the confirmatory run, as registered.

**The verdict [measured, 24 seeds]: taught 0/24, blank 0/24 — the
registered bar FAILs.** Every taught seed received all 45/45
demonstrations and provably carried them (graduates enter the free-run
with ~19 frames; blanks build ~13) — and then **not one of the 24
graduates attempted a single dig in 240,000 free-run steps**. Both arms
drift off the feature cluster (~1,800–2,700 unique positions per
5,000-step window) and never return. Teaching changed the brain, not the
behavior. Blank 0/24 keeps the 0052 floor honest, so the read is valid.

**What was refuted:** teacher-model rev.2's landscape claim —
"demonstration makes the goal *learnable*, which makes it the
highest-frontier option" — is refuted for realized-progress drives
[measured + mechanism-argument]: frontier rewards error *falling* and
scores mastered ground at ~0, so forty-five demonstrations make the
workshop the least interesting region the brain knows. **A well-taught
lesson is exhausted territory; the graduate leaves because the teaching
worked.** The claim survives, if at all, only for a drive valuing
*prospective* reachable progress.

**What it taught / opened:** the topic's thesis now has its second
measured leg — E0 showed drives make *contact* with the mechanism but no
sequences; E1 shows knowledge without wanting is not behavior, even when
the knowledge is provably in the frames. The ladder's condition "E2 only
if E1 fails" is met at full power: **E2 — a goal object with a bounded,
fading λ plus ONE multi-step mechanism (rollouts / means-ends / skills) —
is authorized**, with the mechanism choice its own registered decision.

Reversal condition: for the E2 direction — if E2's pre-registered offline
gate shows a goal-λ bias cannot hold the policy near the workshop any
better than frontier alone (no dwell-time separation at the registered
margin), the goal-object approach pauses before any src build; and the
standing topic reversal remains — if c1c ever produces deliberate chains
on its own, the premise weakens and the topic pauses.

Trail: `hq/01-RESEARCH/self-set-goals/README.md` (bars, E0/E0b/E1
outcomes, dissolution note); `specs/034-two-doors/` (spec +
pilot-results); registration commit 11725f1 (pre-peek), E0/E0b outcome
9d11d1a, spec 013fab4, pilot 29531fc; runner scratchpad-only per the arc
convention (FR-006); landing episodes 0053's branch and the research
branch onto main preceded this arc (main da218b6).
