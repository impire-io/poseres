# motivation-stack — investigation journal (started 2026-08-08)

**2026-08-08 — the topic opens as goal-homing's successor.** Born the
same evening goal-homing graduated (episode 0069: presence solved,
election isolated): the owner's conversation — Fry's calorie for the
bottom layer, the parent for transmission, option-counting for the
middle — assembled into the stack hypothesis, first written as a loose
note and re-homed here on the owner's structural call ("shouldn't
that research be in a research folder?"). The charter holds the
layers, their ugly twins, the five measured nulls mapped, and a
five-gate ladder (completion-pull first, cheapest and sharpest).
Nothing is registered yet; each gate's bars land in the README before
its run, on the owner's sign-off, per the house method.

**2026-08-08 — G1 registered before any run.** The completion-pull
gate: the homing hold retained at its measured λ*, plus one oracle
term valuing sensed-progress advance (completion counted as full — the
channel zeroes on the completing tick, a trap caught at registration
time by reading the world's source). Bars A (≥ 18/24 seeds gain a log)
and B (≥ 6/24 full chains) frozen under the owner's delegated
autonomy; itch-only context arm pre-named to separate the itch from
the hold. Frozen prediction on record: A 20–23, B 4–9.

**2026-08-08 — G1 lands: both bars PASS, and the stack's claim is
measured from the passing side.** Pilot first (published): every seed
digs at every κ, planks in the hundreds, chains in 3–4 of 8;
κ 1.0/4.0 seed-identical (the term saturates the argmax past κ ≈ 1);
κ* = 0.25 by the rule. Confirmatory: Bar A 24/24 (286 logs; the same
graduates under the same hold dug zero without the itch), Bar B 6/24 —
exactly at the bar, the first bar-level chains in the record. The
itch-only arm seals the reading: without the hold, 2/8 dig and none
chain. Neither term alone; the composition. Ugly-twin rows live as
predicted: target-agnostic digging (cobblestone in the hundreds for
some seeds at κ ≥ 1) — the perseveration watch carries forward into
the learnable-itch registration. Episode 0070 records the landmark;
the topic stays active with the learnable-itch and E2.1-shaping
registrations next in the queue.

**2026-08-08 21:55 — G1L registered before any run: the learnable
itch.** One change from G1: the itch reads the brain's own decoded
one-step prediction of the mining channel instead of the clone oracle
(the hold's Φ keeps its scaffold — one variable). No completion
special-case: whether the model has learned the channel's zeroing
cliff is part of the measurement, with the completion-stall and
noise-election pathologies pre-named as ground-truth rows. Bars
identical to G1 on purpose — 0070's reversal condition makes Bar A
here the composition claim's own test. Frozen prediction: A 18–23,
B 3–7.

**2026-08-08 late — G1L lands: both bars FAIL, and the failure is a
measurement, not a mess.** The de-scaffolded itch elects 11/24 (34
logs) against the oracle's 24/24 (286) and the no-itch floor's 0/24;
chains 5/24, one short of the bar — and 5 of the 11 logging seeds
chained, so once logs exist the taught knowledge converts *better*
than in the oracle arm. The pre-named noise row carries the reading:
median prediction error on the mining channel 0.0612 vs the 0.083
one-tick signal — the term ranks on a quantity the model can barely
see. Dose-response across the three arms (0 → 11 → 24 as signal
fidelity rises) says the mechanism is real and starved. Per the frozen
rule, 0070's reversal condition fires as written and G3 — the
event-sensitive predictor — jumps the queue: progress perception is
the arc's load-bearing build, exactly where 0058's parking left it.
Prediction ledger: fifth under/over-miss on A (18–23 vs 11), second
hit on B (3–7 vs 5).

**2026-08-08 22:49 — G3 registered before any run: the event
pathway.** The owner's word — "start with G3" — and the queue-jump
G1L's decision rule ordered. The design meets the charter's question
(can the brain learn to *expect* a discrete event? gate on
prediction) and G1L's inherited one (does sharp perception restore
the pass?) in a single gate: a prototype *event head* — per-action
normalized-LMS delta models over all 32 channels, cold-started,
learning only from the stream the policy witnesses — feeds the same
itch term, with G1's completion rule restored in learnable form (the
head's own predicted pocket gain stands where the oracle's
inventory peek stood). Three frozen bars: P (median mining-channel
prediction error ≤ half a tick — the frames measured 0.0612 against
the 0.083 signal), A and B identical to G1/G1L. The engine's
continuous-mode guarantee (trailing observation carries into the
next episode's first policy call, gap-free) makes the training
stream exact — checked against `core/engine.py` before freezing.
Frozen prediction: P PASS at 0.01–0.03; A 14–20; B 4–8. The src
build stays unlicensed until the bars speak.

**2026-08-08 late — G3 lands: ALL THREE BARS PASS, and the student
beats its scaffold.** Pilot first (published): every seed digs at
every κ, chains above the oracle pilot's, the noise row collapses
0.0612 → ~0.008, κ\* = 0.25 by the rule. Confirmatory: Bar P 0.0081
(bar 0.0417), Bar A 24/24 with 303 logs (the oracle arm: 286), Bar B
13/24 — double the bar, double the oracle. The dose-response closes
end to end: 0 → 11 → 24 as the progress signal sharpens, and the
sharpest signal is the learned one. The mechanism surprise: the
learnable completion rule generalized to crafting gains (the oracle's
hand-built rule never covered them), which is where the doubled
chains come from — wanting follows expecting, and learning to expect
reaches further than any scaffold that stands in for it. Pathology
watch: no stall (20 high abandons / 120k steps), no cobblestone at
κ\*, false completions noisy-but-harmless. Per the frozen rule the
composition claim is restored, the src build is the owner's call,
and G5 unblocks. Prediction ledger: sixth A-side under-prediction;
B under-predicted too. Episode 0071 records the landmark.

**2026-08-09 — the build lands and the closure is exact.** The owner's
"build it for real": feature 040 through spec-kit (spec → plan → tasks →
implementation, branch `040-event-pathway`, v1.2.0) ships the event head
as brain state and the completion itch as a shipped policy — off by
default and byte-identical, on by one config dial. The G3 confirmatory
rerun on shipped components reproduced the prototype's rows **exactly**
(every seed: same logs, same chain ticks, same MAE, same counters —
identical floats), closing 0071's reversal condition at behavioral
identity rather than bar level. The head now persists in snapshots: the
next long run's brain keeps its learned expectations across restarts —
the prototype relearned from zero each session. Queue standing: G5
(approval revisited) is the unblocked next gate; G2/G4 behind it;
E2.1 refinements now compete on top of a shipped mechanism.
