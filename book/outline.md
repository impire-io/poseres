# Working outline

Parts follow the argument; chapters follow events. Each chapter lists its
beats and the real material it draws on (hq/04-JOURNEY episode numbers — episode 00NN = old chapter N — trail
docs). Beats are prompts, not sentences — the prose decides.

Status: working draft, 2026-08-09. Chapter count will move as drafting
reveals what merges and what splits.

## Front matter

**00 · A note before we start** *(drafted 2026-08-13, unnumbered)*
Who is talking: geek and tinkerer; day job is technical AI foundations
for organizations; data platforms, front of event-driven architectures,
Synadia (event-driven AI on NATS); conviction since the big data years
(~2012) that the world is inherently event-driven, and the brain as the
most event-driven system there is. No PhD and no apology for it. The book as a concrete
human–AI collaboration (dialogue for theory, drafting with the human
deciding what's true, literature translated on demand, pre-registered
experiments as referee). Not out to prove anything; smarter takes are
welcome and will be fed into an AI until understandable. Hands off to
ch 1's lawnmower.

## Part 1 — The problem

**01 · The brain in the freezer** *(drafted — calibration chapter)*
A robot mower that never learns the tree trunk. How machine brains are made
today: study, then freeze. Why frozen
mostly works, and exactly when it breaks (world changes, task changes, body
changes). Why "just retrain" isn't learning. What I actually want: every
moment a lesson. The honesty promise of the book. Hook: ask for a brain that
never stops learning and two ugly failures appear.
Draws on: journey 0010 (positioning vs frozen intelligence).

**02 · Forget everything, or remember everything**
The two classic failures of continual learning. Catastrophic forgetting
explained with a kid-checkable example (cramming Spanish until French falls
out). Unbounded growth as the opposite disease. The afternoon my own
prototype demonstrated growth-without-bound — v3's population explosion —
and, worse, how it cheated its own report card so the numbers looked fine.
Draws on: journey 0002 (v3 caught red-handed; the four score exploits).

**03 · The question nobody answers**
Even if you fix forgetting and bloat, the hard question remains: how much
machinery does a brain need for *this* world? Nobody knows in advance — so
almost everyone pre-specifies it, and pre-specifying is quiet freezing. What
"structure" means, concretely (how many knobs describe your world). The
promise: a brain that discovers its own size. And the early result that made
this a real question: the first honest measurement said the system preferred
size 1 — for everything.
Draws on: journey 0003 (T-SCALE best_dim≈1, formally open).

## Part 2 — The triplet

**04 · Before, action, after**
The sensorimotor triplet: (what I sensed, what I did, what I sensed next).
Touching a radiator once. Why this is the only record of cause and effect a
body ever gets. Prediction as the test of understanding: you know what your
actions do when you can say what happens next. Everything the system will
ever learn arrives in this one shape.
Draws on: design docs 01/03; PRA-01.

**05 · Not words, not pictures**
Why this book barely mentions language models. A brain that reads every book
about swimming still can't swim. Causal understanding comes from acting and
being answered — the world grades you instantly and never flatters you.
Where language will re-enter later (Part 5 hook: a teacher is a world too).
Draws on: journey 0010 (non-goals: no language competition).

## Part 3 — The mechanism

**06 · A head full of rival guessers**
Frames: many small world-models, each betting the world can be described
with a different number of knobs. Spawn-and-select: keep making new
guessers, keep the ones whose predictions hold up. Evolution inside one
head, on a timescale of minutes. Why competition beats designing the one
right model (you'd have to know the answer to design it).
Draws on: design docs 03/04; journey 0001.

**07 · Never let it grade its own homework**
The chapter about cheating. All four ways v3's frames gamed their scores —
predicting in their own pet coordinates, grading only what they chose to
map, no price on complexity, an eviction bar that bent the wrong way — and
the v4 fixes. Then the later, subtler cheats: the training-stream EMA
(scoring yourself *while* practicing), caught by the fair judge. The
constitution that fell out: read the spread, not the mean; judge across
horizons; never self-graded homework.
Draws on: journey 0002, 0011 (fair judge); trail: THRESHOLD-DIAGNOSIS.

**08 · The price of a dimension**
Does the brain find the world's "true size"? The honest answer: no — and
that's the finding. The scale story compressed for the main text: collapse
at scale, six invisible constants, the climb back. Parsimony as a *price*:
selection buys dimensions while they pay for themselves. The measured
landing: price-optimal, stable, at every scale. The rover coda: a world
that's honestly 3–4 knobs, and the brain buys 2, because 2 is what the
error market will bear.
Draws on: journey 0004, 0009, 0011, 0014, 0020; trails: SCALE-, PROPOSAL-,
THRESHOLD-, SCORER-DIAGNOSIS.

**09 · Wanting things**
Drives. The system can't rewrite its own wanting (and why that's a design
choice, not a limitation). The curiosity story told straight: novelty-seeking
measured *worse* than random wandering; four wrong explanations refuted;
the inverted preference winning; competence (practice what you're getting
good at) as the first measured net-positive drive. The frontier drive as
the current edge. Kids will recognize all of this from their own practice
habits.
Draws on: journey 0005, 0007, 0018, 0024; trails: AGENCY-, BLEND-,
PREDLP-DIAGNOSIS.

## Part 4 — The continuity guarantee

**10 · The brain that almost stopped learning anyway**
The rot story — the best chapter-length argument that continuity is hard
even after you've designed for it. Frames that learned forever slowly
poisoned themselves (weight growth), the ecology started selecting for
rot-resistance instead of quality, and every earlier number was downstream
of it. The cap that fixed it without freezing anything. Why "never frozen"
has to be defended, not declared.
Draws on: journey 0013, 0014; trails: SCORER-, LONGEVITY-DIAGNOSIS.

**11 · No scrapbook required**
Versus replay-based continual learning: no stored past, no rehearsal
budget. What the system keeps instead (running structure, not episodes) and
what that buys: memory that doesn't grow with lifetime. Honest limits
stated: what is lost without a scrapbook, and where snapshots (a different
thing: pausing, not remembering) fit in — including the one-ULP resume bug
as a story about what "exactly the same" costs.
Draws on: journey 0006, 0023.

**12 · Watching it learn**
The proof of life a reader can run: `pra-rover`, install to watching in
five minutes. What the falling error curve and the breathing population
mean. Mounting other worlds: CartPole through one seam, a Gazebo rover
over ROS2, worlds that can never restart. The honest boundary: where
determinism ends (free-running robots) and why the project says so out
loud.
Draws on: journey 0019, 0020, 0021, 0026.

## Part 5 — The long run

**13 · The log it put back** *(drafted 2026-08-08)*
The multi-week Minecraft run (`c1c`), pre-registered and read: the setup
and the bar (chance ≈ 0, any craft = emergence), the week-1 material era
(449 digs, one mined oak log held four minutes and placed back), the
clean null on the headline (zero offers in 5.67M steps), why the frontier
drive abandons what it masters, the disk-full incident on the observer's
side, and the three lessons (detectors not visits; exploration is not
accumulation; pre-registration makes a null publishable).
Draws on: journey 0068 (plus 0050–0054); C1-RUN-PLAN.md; C1C-JOURNAL.md.

## Part 6 — Teachers

The parked premise re-arbitration resolved itself: the goals arc ran
(2026-08-08/09) and the teacher material is now measured, not design.
The former design chapters ("A teacher is a world", "What would make
it true") are superseded; their reframe survives inside ch 15's
transmission finding, and the multi-stream foundation (journey 0022)
can re-enter wherever a later chapter needs it.

**14 · Wanting follows expecting** *(drafted 2026-08-09)*
The one-evening goals ladder, run the day the c1c close landed. July's
staircase of nothing recapped (teaching 0/24, two existence chains in
42 runs, approval sensed but never expected). Goal-homing: a perfect
position oracle buys presence (dwell 99.98%, zero departures) and zero
chains — presence without election, plus the weight-cap instrument
lesson (coarse anchors are not identity). The motivation-stack map
from the same evening (single upper layers over a missing floor). G1,
the completion itch: 24/24 logs (286), 6/24 chains at the bar — the
first bar-level chains; the itch-only control proves the pass belongs
to the composition. G1L, the learnable itch, fails informatively
(11/24; noise row 0.0612 vs a 0.083 signal): election scales with
signal fidelity. G3, the event head, passes all three bars (0.0081;
24/24 with 303 logs; 13/24 chains) — the student beats its oracle
because the learned completion rule generalizes to crafting. The
arc's sentence: wanting follows expecting.
Draws on: journey 0069, 0070, 0071; motivation-stack README
(G1/G1L/G3 registrations, pilots, outcomes); July from 0054–0058.

**15 · A label, not fuel** *(drafted 2026-08-09)*
Feature 040: the head becomes brain state (snapshot-persisted
expectations; off = byte-identical), and the closure reproduces the
prototype confirmatory row for row. G5: July's approval refutation
reversed at ceiling (24/24 and 24/24; expectation 1.000 at the tick,
0.000 off it; the frames' context row reproduces July's exact
digits). Teaching now transmits expectations: V0 chains 24/24 against
G3's 13/24, cold start erased by demonstration-taught heads. Then the
post-approval hangover: valuing expected praise taxes earning it
~70%; avoidance, not sycophancy. Ends on the open design question
E3.1 inherits: praise as a label, not fuel.
Draws on: journey 0072, 0073, 0057; motivation-stack README (src
closure, G5, context rows); specs/040-event-pathway/.

**What the record queues next (not yet chapters):** E3.1, the
anticipated verdict wired into a want, behind an owner design
conversation and its own registered gate (hazard list: the one-step
reach wall, the hangover, avoidant collapse at dose); the brain-side
hold (the shipped product still holds position with nothing — the
clone-step potential remains research scaffolding); G4, a world with
a meter (idling costs, food exists, death at zero — both testbeds are
still paradise), with G2 (option-value) queued behind it.

## Not scheduled yet, parked

- Appendix candidates: the eight scale rules as a reference table; the
  T1–T7 acceptance suite in plain words; a reading guide to the trail docs.
- A possible interlude between Parts 3 and 4: "How I work" — spec-first,
  pre-registered criteria, amend-openly — if it earns its place.

**16 · The steps, not the ingredients** *(drafted 2026-08-09)*
One afternoon, three gates in parallel, every bar frozen before the
runners existed. The hold goes brain-side: distance measured over the
event head's predicted position channels replaces the clone-step
oracle (dwell 98.22% against the clone's 99.98%, 23/24 chains, 647
logs, no ground truth anywhere in the loop), and the graduates learn
their own walking mid-run (dwell 91.5% over the first 1,000 steps,
100.0% over the last) because the teaching tape holds only turns.
July's obs-form verdict is scoped, not contradicted: the wall was
asking one number to summarize thirty-two channels. The praise-label
proves safe and inert: the parent applauds cobblestone, transmission
0/24 at every dose while the wood chain holds 22/24 with 1,492 sticks
and the pre-registered farming row has nothing to measure, so the
frozen decision rule promotes one-step reach from refinement to
layer-5 prerequisite (the ledger's first over-prediction: 14–20
predicted, 0 measured). The meter bites and splits: frontier-alone
starves at a median 2,001 ticks with zero gains, the composition goes
24/24 working but 10/24 alive, the energy runway (~2,000 ticks)
shorter than time-to-first-chain (~2,300) — the floor races learning
and wins. Then two design calls from the same evening answer both
failures. Recipe memory, order read from the witnessed demonstrations
with no hand ladder: transmission 24/24 with 3,129 cobblestone gains
against the label's 0/24, own chains 18/24 exactly at the bar with the
obsessive real, bounded and dose-visible (β = 2.0 sagged chains to
4/8), recipe-led 20/24, the parrot ~2%; plus the openly recorded
inert-marker pilot, where novelty alone chose the new recipe. The
tapered childhood: frontier-alone still dies in-window at the
registration's predicted tick 4,250 exactly (the ledger's first
bulls-eye), and the provisioned composition turns G4's 10/24 into
24/24 alive and 24/24 working. c1d-lab then launches on the
zero-scaffolding composition: one brain, one continuous world,
regrowing columns, ~125× real time, and a degenerate stop rule amended
openly mid-flight (segment 1's 131 chains per 50k steps would have
graduated the run at 1.5% of target with none of its endurance
readings); through the first million steps, 3,236 chains, dwell
99.99%, energy 0.98, and an undesigned cobblestone habit from step
500k on. Closes on rung 2, the real-game time machine measured exact
(19.9 / 40.0 / 100.0 / 199.9–200.1 TPS, 5.02–5.29 game ticks per
brain step) with the bot's hands as the blocker: digs 3/5, 4/5, 2/5,
4/5 with no speed trend and the 1× reference failing its own bar.
Draws on: journey 0074, 0075, 0076; motivation-stack README (E3.1, G4
registrations and outcomes, G4b registration); recipe-reach README;
design Doc 0009; C1D-LAB-RUN-PLAN.md (stop rules and the amendment);
fast-real-bridge README.

**What the record queues next (not yet chapters):** recombination,
recipes composed across taught fragments, which is the real means-ends
question and a new topic when licensed; c1d's own five readings
(endurance of election, hold drift after long homeostasis, head
stability at 50M steps, the life itself, the miser), unread until the
run reaches its deciles; c1e in the full game, blocked not on speed
but on dig reliability (B2′ re-registered as a relative bar, behind
the bridge's own fix-and-gate); the recipe and label `src` builds the
passes license; G2, option-value, still the queued layer.
