<!-- Draws on: journey 0072 (the event pathway ships), 0073 (the
     hangover), 0057 (July's approval gate);
     hq/01-RESEARCH/motivation-stack/README.md (G3 src closure, G5
     registration, outcome, context rows). Numbers as of 2026-08-09;
     feature 040, specs/040-event-pathway/, v1.2.0. -->

# A label, not fuel

The morning after the night of gates, the prototype went through the
front door. The instruction in the record is four words: "build it
for real." Everything else about August 9 follows from taking those
words literally.

## The head becomes brain state

The event head moved from the scratchpad into the brain itself. It
lives beside the frames now, owned by the same store, and it learns
in exactly one place: once per executed step, from the transition
the bot actually lived. It ships off by default, and off means off:
with the head disabled, the brain's bytes are identical to what
shipped before, proven by test, so every validated result in this
book stands untouched.

The part that matters most took one line to say and carries the rest
of this chapter: the head's learned state goes into snapshots.
Chapter 11's promise, pausing without forgetting, now covers
expectations. The prototype relearned its world from zero every run.
A shipped brain that has learned to expect something still expects
it after a restart.

The night's result had a condition attached, and I wrote it down
before shipping anything: if the shipped build failed to reproduce
the gate, then the scratchpad instrument, not the mechanism, had
carried the pass. The rerun on shipped components answered at a
stronger standard than the condition asked for. Row for row, every
pupil's logs, chain ticks, dwell, completion counters, and
prediction errors came out identical to the prototype's
confirmatory. Same verdict line: prediction error 0.0081, election
24 of 24 with 303 logs, chains 13 of 24, false completions 812 of
1,957, 159 seconds. Not replication at the level of bars, which is
the house standard, but behavioral identity: the shipped pathway
computes the measured instrument's numbers in its order. There is
nothing left for the instrument-versus-mechanism question to attach
to.

> **Under the hood: feature 040.** `specs/040-event-pathway/`,
> v1.1.0 → v1.2.0, additive only, 25 new tests. The head is
> FrameStore-owned state, config-gated by `event_head_eta` (0.0 =
> off: no state, no float work, no RNG; byte-identity proven by
> test against the pinned baseline). Snapshots carry it as an
> additive-optional key: head-off blobs are bit-identical, pre-040
> blobs cold-start it, and anatomy resizes zero-initialize the new
> channels, drawing nothing. `CompletionItchPolicy` ships the
> measured gate arithmetic with derived channel indices. The hold
> stays caller-injected: the clone-step potential is research
> instrumentation, not brain, so the shipped product still contains
> nothing that holds position. Closure runner: `src_closure.py`,
> shipped components only.

## July's question, asked again

At 13:11 the same day the record says "open G5," and the July gate
this book has now mentioned twice got its rematch.

The July result: a judge watching ground truth pulsed 1.0
onto a sensor channel on the exact tick a stick-craft landed,
forty-five approvals per pupil, and the brain's predictions never
reliably formed around it. Rising expectation, 18 of 24, met the bar
exactly; specific expectation, 14 of 24 against a bar of 18, failed
it, with five pupils anti-predictive at the very tick the praise
always arrived. But July's write-up carried a scope note that turned
out to be load-bearing: the refutation is predictor-shaped, not
concept-shaped. An event-sensitive predictor could reopen the
question. That predictor now shipped in the product.

The instrument was rebuilt faithfully from the committed record with
one addition: the head learns from the first step of the first
lesson, and its learned state rides the new snapshots from segment
to segment of the teaching tape. Same judge, same channel, same 45
approvals, same two bars with the same statistics. Only the
predictor changed.

Rising: 24 of 24. Specific: 24 of 24. And not narrowly. Every pupil
ended with a completion-tick expectation of 1.000 and an off-tick
expectation of 0.000. The brain expects the well-done exactly when
it always arrives and never otherwise, and the expectation was
already half-formed within the first five approvals: the first-five
mean was 0.450. The frames never got that far in forty-five.

Two readings sit inside the result. First, all 24 rows are identical
to three decimals. The frames' expectation had been a lottery,
because their random starting weights shape what their bottleneck
can carry; the head starts at zero and learns a deterministic stream
deterministically. Expecting stopped depending on luck. Second, the
frames' own predictions were measured in the same run, as a context
row: rising 18 of 24, specific 14 of 24. July's exact digits. The
rebuilt instrument reproduced the old result in the act of
overturning it, which is as close as an experiment comes to proving
it was fair both times.

I had also named a risk out loud the night before: approval is rare,
one guided step in 22, and the head had only been proven on dense
events like dig ticks. The worry dissolved on a distinction worth
keeping. Rare in time is not rare in structure. The tick before a
stick lands looks different on the sensors, because the crafting
grid is showing the stick offer, and a per-action model of changes
reads that precondition directly. The claim stays scoped: a rare
event whose precondition is invisible to the senses is still
untested ground.

> **Under the hood: the G5 gate.** E3.0's instrument rebuilt from
> its committed record: verdict channel 33 (index 32), harness-side
> wrapper, judge on ground-truth stick-crafts, the 034 tape, 45
> snapshot-bridged demonstrations per pupil, fresh 33-dim cohort,
> `event_head_eta = 0.5` from the first step. Instrument green:
> 45/45 crafts per seed, the pulse tick-stable in all 1,080
> demonstrations, mute arm's channel never left zero. Bars, July's
> own statistics with the predictor swapped: P5-a rising PASS 24/24
> (July 18/24), P5-b specific PASS 24/24 (July 14/24); last-5
> completion-tick mean 1.000, off-tick 0.000, first-5 mean 0.450.
> Ledger: P5-a predicted 22–24, measured 24; P5-b predicted 19–23,
> measured 24, the seventh consecutive under-prediction and the
> first measurement above its range's top.

## What a teacher transmits

No behavior bar was registered for G5, and the registration says why:
July had already measured that one-step anticipation cannot
start a twenty-step chain, so a want-bar would have been theater.
Instead the part of the brain that wants ran as context rows at full
power, to feed
the next design. The first row produced the finding I did not see
coming.

V0 is the shipped composition from chapter 14, hold plus itch, with
approval merely present in the world and no term reading it. On
chapter 14's cohort, that composition chained 13 of 24. On this
cohort: 24 of 24, with 1,888 approvals earned and 2,473 sticks.

One variable separates the cohorts. This cohort's event head learned
through the 45 demonstrations, its state riding the snapshots from
lesson to lesson, so it entered free-run already knowing the dig and
craft dynamics. The cold-start cost chapter 14's gate paid, the
early stretch where the itch points nowhere because the head knows
nothing yet, was simply gone, and with it the last barrier to
chaining.

Teaching the predictor was worth more than eleven chains. That
rewrites what teaching is in this architecture. In July,
demonstrations transmitted frames: knowledge of what the world does.
Through the event pathway, demonstrations now also transmit
expectations: knowledge of what comes next, sharp enough to act on.
And expectation alone, never wired to any reward, carried election
to ceiling.

## The hangover

Then the tempting step. The brain can now expect the well-done
perfectly, so make it want the well-done: one new term, weighted by
a dose, valuing each candidate action by the head's own predicted
change in the approval channel. Wanting praise, in the most literal
sense this architecture can express.

The pilot, published before the main arm, said something was wrong
at every dose. At the three doses tried, the same eight pupils
earned 179, 117, and 77 approvals, against 659 with the term off.
More dose earned less praise. At the higher doses behavior collapsed
into log-hoarding with zero sticks (one pupil stacked 100 logs;
another, at the highest dose, 156). The bot stopped doing the thing
that earns praise.

The 24-pupil arm at the smallest dose confirmed the shape. Chains 23
of 24, so capability survived. But approvals earned came to 572
against V0's 1,888, and sticks to 863 against 2,473. Valuing the
expectation of praise taxed the earning of it by about 70%, at the
smallest dose tried.
<!-- V+/V0 numbers: motivation-stack README, G5 context rows;
     journey 0073. -->

The rows support a mechanism, and it is uncomfortably clean. Praise
here is a pulse: 1.0 on the tick, 0.0 after. The head learns that
decay the way it learns everything, online, per action. So every
familiar continuation of the praised loop, the very actions that
lead back toward the next craft, comes to predict approval falling,
and the new term taxes them for it, while actions the bot has never
tried predict nothing and go untaxed. The moment praise lands, the
term pushes the bot away from its own praised loop. I call this the
*post-approval hangover*: the measured backfire of making expected
praise valuable, where the praised loop's own next steps all predict
praise going away, so the bot avoids the loop that earned it.

The watch I had pre-registered was for the opposite disease.
Sycophancy: praise-farming, the approval signal gamed, sticks
inflated while real capability stalls. The rows show none of it, in
either arm. No stick inflation, exploration flat, the hold intact.
The watch closed with its question inverted. The measured failure
mode of wiring approval into value is not sycophancy. It is
avoidance.

> **Under the hood: the V+ arm.** V+ = V0 plus κ₅ · Δ̂_a[verdict]
> through the shipped policy seam. Pilot seeds 1–8 ×
> κ₅ ∈ {0.25, 1, 4}: firings 179 / 117 / 77 vs 659 at κ₅ = 0; at
> κ₅ ≥ 1, log-hoarding with zero sticks (seed 2: 100 logs; seed 6
> at κ₅ = 4: 156). Arm, 24 seeds at κ₅\* = 0.25: chains 23/24
> (seed 12 the miss), firings 572 vs V0's 1,888, sticks 863 vs
> 2,473, median dwell 100.0%, unique positions median 22 vs V0's
> ~20. Mechanism reading: the verdict's 1 → 0 post-firing decay is
> learned per action, so familiar continuations accumulate
> Δ̂[verdict] ≈ −1 and are taxed −κ₅ every post-firing tick. The
> hangover reading reopens if a replication with the decay excluded
> from learning, or the term gated off post-firing ticks, fails to
> restore V0's earning rate; the tax would then live elsewhere.

## The open question

The successor gate has a name, E3.1: the anticipated verdict wired
into a want, properly designed this time. It reopens behind a design
conversation, not a build, and its registration owes answers to a
measured hazard list. One-step anticipation cannot start a
twenty-step chain. A value term on a still-learning expectation
repels the learner from its own praised loop. And at higher doses
the repulsion collapses the behavior entirely.

On the other side of the ledger sits the day's gift. In every
measured row of this arc, praise worked when it told the brain what
to expect, and hurt when it was made worth something. The teacher's
well-done turned out to be for information, not for payment: my
pupil learns most from praise when the praise is a label on the
moment, not fuel for reaching it.

Whether a mind can want its teacher's approval without the wanting
eating the earning is, as I write this, an open question with a
measured hazard list and no design. That is the current edge of the
record. The bar gets written before the mechanism does.
