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

**2026-08-09 13:11 — G5 registered before any run: approval,
revisited.** The owner's "open G5." E3.0's instrument rebuilt from its
committed record (verdict = channel 33, judge on stick-crafts, the 034
tape, 45 snapshot-bridged demos, fresh 33-dim cohort) with one
addition: `event_head_eta = 0.5` from the cohort's first step, the
shipped head learning through the demonstrations, its state riding the
feature-040 snapshot persistence between segments. Binding bars are
July's own two, statistics unchanged, predictor swapped: rising
≥ 18/24 and specific ≥ 18/24 on the head's predicted verdict at the
completion tick (July measured 18/24 and 14/24 on the frames). No
behavior bar — E3.0's rule already named the one-step-reach wall, so
the wanting side runs as context rows at power (V0 = the shipped G3
composition with approval merely present; V+ = plus κ₅·Δ̂[verdict],
pilot before arm) with the charter's sycophancy watch pre-registered
(stick/firing inflation against logs and unique positions). Frozen
prediction: P5-a 22–24, P5-b 19–23; the sparse 1-in-22 pulse is
exactly episode 0072's named risk — a P5-b FAIL splits
"event-sensitive" into dense/sparse regimes and makes the head's
architecture the next question, before any want.

**2026-08-09 afternoon — G5 lands: the brain learns to expect the
well-done perfectly, and wanting it backfires.** The binding bars:
**24/24 and 24/24** (bars 18) — every seed's completion-tick
expectation at exactly 1.000 with off-tick 0.000, all rows identical
(the head's cold-start-zero determinism ends the frames' expectation
lottery), half-formed within five approvals. The frames' context row
reproduced July to the digit (18/24, 14/24) — instrument proven in
the act of being overturned. Then the context rows delivered two
findings bigger than their status: **V0** — the shipped composition
with approval merely present — chains **24/24** (G3's cohort: 13/24)
because this cohort's head learned through the demonstrations and
entered free-run pre-trained: teaching the predictor erased the
cold-start barrier. And **V+** — the approval-anticipation term —
*hurts at every dose*: firings 572 vs 1,888 at κ₅ = 0.25 (23/24
chains — capability intact, praise-earning taxed 70%), log-hoarding
with zero sticks at κ₅ ≥ 1. Mechanism reading: the post-approval
hangover — the verdict's decay is learned online per action, so the
praised loop's familiar continuations all predict approval-loss and
get taxed the moment praise lands, while the untried stays untaxed.
Not sycophancy: avoidance. E3.1 reopens as the successor with a
measured hazard list (reach, hangover, avoidant collapse) and one
gift (demonstrations now transmit expectations, and expectation
alone carries election to ceiling). Prediction ledger: P5-a in range
at the top; P5-b **above** its range — the seventh under-prediction;
the V+ "within ±2 chains" call was wrong in the informative
direction.

**2026-08-09 — E3.1 and G4 registered before any run, in parallel**
(owner's "can we do all in parallel and autonomous?"; E3.1's design
from the owner's label-not-fuel conversation). E3.1: the parent
applauds cobblestone — a preference the bots demonstrably do not
have — and praise enters only as a completion label
(progress_after = 1 + β·clip(Δ̂[verdict],0,1) inside fired
completions; no level valuing, no decay tax possible). Bars: T1
transmission ≥ 12/24 seeds gain cobble (floor arm measured), T2 own
chains preserved ≥ 18/24; the farming row (gain events vs net) is
the real sycophancy channel this world finally has. G4: the meter —
energy decays 0.0005/tick, +0.1 per pocket gain, death at zero;
bars: frontier-alone starves (median < 3,000) while the composition
feeds itself (≥ 18/24 survive AND work); the miser watched. H1 (the
brain-side hold) runs in its own topic the same afternoon.

**2026-08-09 evening — the parallel afternoon lands: three gates,
three different verdicts.** H1 (own topic): both bars PASS — the
brain-side hold works (98.22% dwell, 23/24 chains, no clone
anywhere); the composition is deployable and c1d registrable. E3.1:
T1 FAIL 0/24 at every dose with T2 PASS 22/24 — the label is
perfectly safe and perfectly inert; one-step reach blocks the walk
to the applauded context, so E2.1 upgrades from refinement to
layer-5 prerequisite. The ledger's first over-prediction of a
composed mechanism (T1 predicted 14–20, measured 0): composition
keeps beating predictions, reach keeps losing to them. G4: M1 PASS
(frontier starves at median 2,001 — E0's null has a body count),
M2 FAIL-informative (10/24 alive but 24/24 working — the runway is
shorter than time-to-first-chain; stakes race learning, and the gap
is what provisioning exists for). Episodes 0074 (H1 graduation) and
0075 record the afternoon.

**2026-08-09 night — G4b registered: the tapered childhood.** The
owner's dose: full parental coverage to tick 1,500, weaning to zero at
3,000, stakes thereafter. Bars M1b (frontier still dies in-window,
predicted ≈ 4,250) and M2b (≥ 18/24 alive AND working); the weaning
window becomes an observable row. Runs in parallel with the
recipe-reach gate (own topic) — the owner's purist road.
