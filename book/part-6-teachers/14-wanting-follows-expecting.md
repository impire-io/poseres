<!-- Draws on: journey 0069 (goal homing), 0070 (the first elected
     chains), 0071 (wanting follows expecting);
     hq/01-RESEARCH/motivation-stack/README.md (G1 / G1L / G3
     registrations, pilots, outcomes); July background from journey
     0054-0058. Numbers as of the 2026-08-08 confirmatories. -->

# Wanting follows expecting

The last chapter ended with a promise: the next arc of this project
would be about building the part of a mind that would have kept the
log. I did not know, writing the run's closing entry on the morning
of August 8, that the arc would run its first four experiments before
the day was out, or that by midnight the missing part would exist, in
prototype, and pass every bar set for it.

First, though, I owe the reader July.

## What July had already ruled out

While the seventeen-day run was ticking along on its server, a second
line of experiments had been asking the same question from the other
side: short pre-registered gates, each run the day it was registered,
on a faithful stand-in of the same Minecraft mechanics, one the test
rig can copy and restart at will. And, for the first time in this
book, a teacher.

The teaching works like this. There is a spot in the world I call
the workshop: standing room, a wood column in reach, the crafting
grid ready. Forty-five times, the bot's hands are driven through the
whole chain while its brain watches and learns exactly as it always
does. Dig the log, twelve committed ticks. Craft planks. Craft
sticks. Then the hands are given back.

What July measured, gate by gate, was a staircase of nothing. The
knowledge provably arrived: taught brains carry the chain, and every
later gate confirms it, because whenever anything persuades a taught
bot to start the chain, the whole chain runs. But knowledge alone
moved nothing: zero of 24 taught brains ever ran the chain on their
own, against a bar of six. A weak pull toward the workshop moved
almost nothing: two full chains across 42 runs, the first deliberate
chains in the project's history, from a gate that failed its own bar
(the pull produced orbiting, a median 3.8% of time near the
workshop, not holding). And approval moved nothing at all: a judge
pulsed "well done" onto a sensor channel at the exact tick a
stick-craft landed, forty-five times per pupil, and the brain never
reliably came to expect the pulse, let alone want it. Fourteen of 24
pupils ended with a specific expectation, against a bar of eighteen;
five ended anti-predictive at the exact tick the praise always
arrived.
<!-- July numbers: journey 0054 (E1 0/24 vs >=6/24), 0055 (2 chains /
     42 runs; dwell 3.8%), 0057 (specific 14/24, five anti-predictive). -->

The topic was parked on July 24 with one sentence standing: no cheap
mechanism converts taught knowledge into reliable directed behavior.
Then the big run closed, chapter 13's null said the missing thing is
chaining, and the parked question was suddenly the only question.

## A statue at the workshop

The July pull had a diagnosed flaw. Its sense of "toward the goal"
was the distance between what the bot sees now and what it saw at
the goal, and away from the workshop that signal is nearly flat: one
step toward and one step away look almost the same on a featureless
plain. So the reopened gate asked the cleanest version of the
question. What if the sense of direction were perfect?

Perfect meant cheating on purpose. For each action the bot
considers, the rig clones the world, takes that one step in the
copy, and reads the true distance to the workshop out of the game's
own bookkeeping. That is an *oracle*: a measurement taken by peeking
at the world's ground truth, which the brain itself could never
make, used to mark the ceiling of what any learnable version could
reach. If a brain with a perfect sense of direction still does not
chain, then direction was never the wall.

Getting the instrument right produced the day's first lesson before
any new result did. The gate runners live in a scratchpad and
get rebuilt from the committed record when a topic reopens. The
first rebuild matched every coarse anchor in the record and produced
zero chains where the record held two. One configuration number was
wrong: chapter 10's weight cap, 0.0 where the run posture said 1.2.
The registered criterion that caught it demanded identity, not
resemblance: the rebuilt instrument had to reproduce July's two
recorded chains at their exact recorded ticks, seed 6 at tick 706
and seed 7 at tick 427. After the fix, it did. Coarse anchors are
not identity; exact ticks are.

Then the gate ran, 24 pupils, and the holding problem died. Median
time at the workshop: 99.98%, against the July form's 3.8%.
Departures: zero, in 24 runs. The second bar had been written
expecting escapes and returns, and was amended openly, before the
confirmatory, to the never-leaves form the pilot revealed. Presence,
which two July gates had failed to buy at any price, was suddenly
free.

And the chains bar failed, zero of 24. One hundred twenty thousand
steps standing at the workshop, the taught chain provably in the
frames, and not one log dug. Three cobblestone, across the whole
arm, was the entire material record. About twenty-five times the
presence bought exactly zero chain gain.

I had predicted high return rates and a narrow pass on chains, my
third wrong frozen prediction at three consecutive gates. What stood
instead was a statue: a bot that stands where the log is, knowing
how to get it, and never starting.

The word the record settled on for what was missing is *election*:
choosing, on purpose, to begin a sequence you know, its first step
and all the steps after it. Knowing the chain was solved in July.
Standing at its start was solved the same day. Election was the
isolated wall.

> **Under the hood: the goal-homing gate.** Policy term
> λ · (−Φ(pos_after(a))), Φ the clone-step Chebyshev distance to the
> workshop; subjects the 24 taught graduates, H = 5,000, fresh
> worlds. Bar 1 (holding, ≥ 18/24 at ≥ 20% dwell): PASS 24/24,
> median dwell 99.98%. Bar 2, amended to never-leaves: 0 departures
> in 24 runs. Bar 3 (chains ≥ 6/24): FAIL 0/24; 3 cobblestone across
> the arm. Against the July floor of 2 chains in 42 runs, 0/24 alone
> is not significant (Fisher p ≈ 0.5); the finding is the direction,
> roughly 25× the presence for zero chain gain. Instrument identity
> was gated on the two recorded chains landing at ticks 706 and 427.

## The map

With the wall isolated, the question turned into why every gate kept
failing the same way, and that evening the project got its working
map. Every drive this brain has ever had is an appetite for
learning, and both of its test worlds are paradise: idling is free,
nothing decays, nothing is ever hungry. Animal motivation does not
look like one mechanism. It looks like a stack. At the bottom, a
budget, the calorie, life as optimization toward the calorie (an
idea I took from Stephen Fry's *Great Leap Years*). Above it,
deficits: the budget compiled into sensations like hunger, making
specific things valuable at specific times. Then option-value, where
a log is money, worth having for the doors it opens. Then a
completion itch that pulls begun sequences toward their ends. Then
goals borrowed from a parent. Then imagination.

Each layer exists to patch the failure of the one below. A pure
budget makes a miser; a pure deficit, a monomaniac; pure
option-value, a hoarder; a pure itch, a grinder who cannot quit;
borrowed goals, a sycophant; imagination, a dreamer. And the record's five
nulls lined up on the map as the same mistake repeated: a single
upper layer, tested in a creature and a world missing the floor
below it.

A map is a judgment, not a measurement. I let it order the queue,
cheapest first, and I did not let it win: each layer would get its
own gate, bars frozen before the runner existed.

## One term separates a statue from a woodcutter

The cheapest untested layer was the itch. Digging wood in this world
is twelve consecutive ticks of choosing "dig"; choose anything else
and the cracks vanish. The mechanics already charge for quitting.
All the brain lacked was caring.

So, one new term in the action choice, on top of the proven hold:
value each candidate action by how much dig progress it would add.
Starting a crack is worth a little. Continuing is worth more.
Abandoning charges you everything sunk, because the world's own
reset does the bookkeeping. That is the *completion itch*: a small
standing pull that makes begun things want finishing.

The bars were frozen first: at least 18 of 24 pupils gain a log, at
least 6 of 24 complete the full chain, log to planks to sticks. A
published pilot picked the smallest working dose. Then the
confirmatory.

Twenty-four of 24 gained a log, 286 logs across the arm. The same
graduates, under the same hold, without the itch: zero logs in 24
runs. One term separates a statue from a woodcutter.

And six of 24 ran the full chain. Exactly at the bar, not above it,
and I report it as what it is, a pass at the line. But the entire
prior record held two chains, both existence-level flukes from a
failing gate. These six were the first bar-level deliberate chains
in the project's history.

The control I care most about ran alongside: the itch without the
hold. Eight wandering pupils, itch on, hold off. Two of them dug
(ten logs and seven), none chained. Wanderers itch only where they
happen to stand. Neither term alone does anything; the pass belongs
to the composition. The map's core claim, that layers compose where
single layers fail, now had its first measurement from the passing
side.

The map's ugly-twin column earned its keep too. The itch is
target-agnostic: at higher doses, pilot seeds ground out 107 to 143
cobblestone apiece, finishing any crack in reach because finishing
is what the term pays for. Noted, watched, and carried forward by
name.

> **Under the hood: the G1 gate.** value(a) = drive_value(pred_a)
> + 0.25 · (−Φ(pos_after(a))) + κ · (progress_after(a) −
> progress_now), progress read from the clone-step oracle,
> completion counted as full; κ\* = 0.25 (smallest pilot κ with
> median logs ≥ 1), H = 5,000. Bar A PASS 24/24 (286 logs); Bar B
> PASS 6/24, at the bar (seeds 1, 3, 5, 11, 19, 20); median dwell
> 100.0%. Itch-only arm (λ = 0, seeds 1–8): 2/8 dig, 0/8 chain.
> Frozen-prediction ledger: Bar A predicted 20–23, measured 24, the
> fourth consecutive under-prediction; Bar B predicted 4–9, measured
> 6, the arc's first prediction inside its own range.

## Take away the crutch

The itch's progress signal was still the oracle's: the clone-step
peek knew the exact crack progress every candidate action would
produce, and knew a completed dig when it saw one. A mechanism that
only works while a ground-truth peek feeds it is not a mechanism, it
is a demo. So the next gate, registered at 21:55 the same evening,
kept the identical term and swapped its signal: the brain's own
one-step prediction of its sensed mining channel. No oracle in the
itch.

Both bars failed. Eleven of 24 pupils got a log, 34 logs against the
oracle arm's 286. Five of 24 chained, one pupil short of the bar.

A failure at power is only as good as its explanation, and this one
arrived with its explanation pre-named. The registration had
declared a noise row: how far off is the brain's predicted progress
from realized progress, on the actions it chooses? Measured: a
median gap of 0.0612, against a single dig tick worth 1/12 ≈ 0.083.
The brain's model of its own progress was barely finer than the
quantity the itch has to rank. The term was real; the signal feeding
it was fog.

Two details said the fog was the whole story. Five chains from just
34 logs is a better conversion rate than the oracle arm's six from
286: once a log existed, the taught chain ran, so neither knowledge
nor crafting was the bottleneck. And the three arms lined up into a
dose-response curve of signal quality. No itch: zero of 24 elect.
Itch on a foggy signal: eleven of 24. Itch on a perfect signal: 24
of 24. Same policy shape, same hold, same graduates. Election scaled
with progress-signal fidelity and with nothing else that varied.
<!-- G1L numbers: motivation-stack README, G1L outcome section. -->

One sentence closed the gate: the completion-pull works exactly as
far as the brain can perceive its own progress. Which turned the
arc's next question from a motivation question into a perception
question.

## The event head

Why is the brain's own progress signal fog? Because of what frames
are. A frame earns its living by squeezing everything the body
senses through a few knobs (that economy is the whole of Part 3),
and squeezing keeps the smooth shape of the world while blurring
spikes. A dig is eleven ticks of smoothly climbing cracks and then a
cliff: the cracks vanish, a log appears in the pocket. The cliff is
the event that matters, and the cliff is exactly what the squeeze
blurs.

So the last gate of the night, registered at 22:49, built a second
pathway that does not squeeze. For each of the twelve actions, a
small separate model predicts how each of the 32 sensed numbers will
change if that action is taken next. No shared knobs, no averaging
across actions, and it predicts changes, not scenes. It starts at
zero and learns online, one update per lived step, from exactly the
stream of experience the bot's own choices produce. I call it the
*event head*: a small second predictor beside the frames, one model
per action, built to be sharp about the moments when a number jumps.

The itch now reads the head. Even the notion of "done" became
learnable: an action counts as completing when the head predicts the
pocket is about to gain something.

Three bars, frozen first: the head's progress error at least twice
as fine as a dig tick, election at G1's bar, chains at G1's bar. The
head measured 0.0081 where the frames had measured 0.0612, the same
channel read ten times finer than a single tick after roughly 5,000
online updates from a cold start. Election: 24 of 24, 303 logs,
above the oracle's 286. Chains: 13 of 24. More than double the bar,
and more than double what the oracle arm itself had managed.

Sit with that last one. The student beat its oracle.

The pilot had already shown why. The learned completion rule fires
on any predicted pocket gain, and crafting produces pocket gains
too. So planks landing in the pocket itched the same way a finishing
dig did, and sticks after them. G1's hand-built rule only ever knew
about digs, because I was only thinking about digs when I wrote it.
Learning generalized where the scaffold couldn't, because the
scaffold could only contain what its author foresaw.

The roughness gets reported with the trophy. The learned rule is
noisy: 812 of its 1,957 completion firings came with no realized
gain, and that noisy rule still carried three passing bars. No
cobblestone appeared at the confirmed dose; the grinding twin stayed
asleep. And six pupils showed a new profile, the
woodcutter-hoarder: 21 to 61 logs each, zero chains, bots that never
enter the craft loop and so never learn that crafting completes.
What remains of the chain bottleneck lives at the entry to crafting,
not in the conversion.

My frozen predictions missed all three bars in the same direction,
the sixth consecutive gate where I under-predicted a composed
mechanism. I keep writing the predictions down precisely so that
pattern is measurable: my intuition is systematically pessimistic
about compositions, and the bars keep being the better judge.

> **Under the hood: the event head and the G3 gate.** Per action a,
> Δ̂_a(obs) = W_a · [obs, 1], cold start W = 0, updated by
> normalized LMS: W_a += η · (Δ − Δ̂_a) · x/‖x‖², η = 0.5, one
> update per executed transition. Completion rule:
> progress_after(a) = 1.0 if Δ̂_a[pocket_total] > 1/128, else
> clip(obs[mining] + Δ̂_a[mining], 0, 1). Bar P: median per-seed
> mean |Δ̂[mining] − realized| on chosen directed actions ≤ 1/24 ≈
> 0.0417; measured 0.0081 (frames: 0.0612). Bar A PASS 24/24, 303
> logs; Bar B PASS 13/24; median dwell 100.0%; 20 high-progress
> abandons in 120,000 steps; false completions 812/1,957.
> Confirmatory: 24 seeds at κ\* = 0.25, H = 5,000, 158 s. Ledger:
> P predicted 0.01–0.03, A predicted 14–20, B predicted 4–8.

Between the run's closing entry that morning and the last
confirmatory that night, the answer changed shape. The bot stays
where its goal is, wants what it has begun, and finishes to exactly
the degree it can expect what comes next. And expecting is now
something it learns. Wanting follows expecting.

The log from chapter 13 is still in its hillside. The machinery that
would have kept it now existed, passing every bar, as a scratchpad
prototype with one crutch left in it: the hold that keeps the bot at
the workshop still reads the position oracle, because nothing
brain-side holds position yet. A prototype is not a brain. The next
morning's work was making it one.
