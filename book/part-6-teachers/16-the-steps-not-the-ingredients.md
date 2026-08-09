<!-- Draws on: journey 0074 (the hold goes brain-side), 0075 (the label
     and the meter), 0076 (the steps, not just the ingredients);
     hq/01-RESEARCH/motivation-stack/README.md (E3.1 and G4
     registrations and outcomes, G4b registration, G5 context rows);
     hq/01-RESEARCH/recipe-reach/README.md; hq/02-DESIGN/0009-brain-side-hold.md;
     hq/02-DESIGN/validate/C1D-LAB-RUN-PLAN.md (stop rules and the
     open amendment); hq/01-RESEARCH/fast-real-bridge/README.md.
     Numbers as of the 2026-08-09 night gates; c1d rows through the
     first million steps. -->

# The steps, not the ingredients

The open question at the end of the last chapter did not stay open for
an afternoon.

Praise as a label rather than fuel was a sentence in a conversation.
Turning it into a mechanism was almost free, because the shipped
completion rule already had the right shape. It counts a finished
thing as done, and a label only has to say which finished things
count for more. By the time that gate was registered, two unrelated
questions were also ready to run. Could the bot hold its position
without peeking at the world's own bookkeeping? And would any of this
look different in a world where standing still costs something?

So I asked whether all three could run at once, autonomously, while I
was doing something else. Three gates, three sets of bars, every bar
frozen before any of the runners existed, all three decided before
the end of the day.

One passed. Two failed in the most useful way a gate can fail: each
named its own successor, and by midnight both successors had been
designed, run, and measured.

## The last crutch

The composition from chapter 14 still carried one piece of laboratory
equipment. To decide whether stepping north takes it nearer the
workshop, the bot copied the whole world, took the step in the copy,
and read the true distance out of the game's bookkeeping. A brain
that ships inside a robot cannot copy the world it lives in. As long
as that term stayed, the whole staying-and-finishing life was a
demonstration rather than something a body could do.

The replacement was already in the product. The event head predicts,
for each of the twelve actions, how every sensed number will change
if that action is taken next. Two of those numbers are the bot's own
position. So stop asking the world and ask the head: if I step this
way, what will my position readings say? Measure the distance from
that predicted position to the position it was taught to work at.

Two channels out of thirty-two. That is the entire difference between
this and the July failure the book keeps returning to. July's pull
measured distance over the whole observation, all thirty-two numbers
at once, and bought 3.8% dwell. The wall was never that observations
cannot carry a hold. It was that one number cannot summarize
thirty-two channels, and I had been blaming the wrong half of that
sentence since July.

Median dwell, 24 pupils: 98.22%, against the clone oracle's 99.98%.
The bar was 20%. And the whole composition survived the swap: 23 of
24 pupils ran the full chain, 647 logs, 1,919 sticks, with the drive
coming from the frames, the hold from the head's predicted positions,
and the itch from the head's predicted progress. No ground truth
anywhere in the loop.

The registered context row is the part I like. The teaching tape
holds only turns, so these graduates had watched themselves pivot
forty-five times and had never once watched themselves walk. They
entered their first free run with no model of what walking does to
their own position, holding station by predicting a motion they had
never seen. Median dwell over the first thousand steps: 91.5%. Over
the last thousand: 100.0%. In between, from nothing but its own
random exploration steps, the bot learned its legs, inside the first
fifth of the run.

> **Under the hood: the brain-side hold.**
> Φ̂(a) = 64 · Chebyshev(obs[x,z] + Δ̂ₐ[x,z], goal[x,z]), the goal being
> the position channels of the taught goal observation;
> hold(a) = λ · (−Φ̂(a)), λ = 0.25; Δ̂ₐ from the head, the term
> contributing 0 when the head is off. Subjects: the 24 G5 graduates,
> H = 5,000, 308 s for both arms. H1a, hold alone, bar ≥ 20% dwell:
> PASS, median 98.22% (clone reference 99.98%); context row, median
> dwell 91.5% over the first 1,000 steps rising to 100.0% over the
> last 1,000, movement models cold at the start because the tape
> holds only turns. H1b, full composition, bar ≥ 6/24 chains: PASS
> 23/24, 647 logs, 1,919 sticks (clone reference 24/24). Graduated as
> design Doc 0009: shipped components plus about fifteen lines of
> caller-side composition, so a `src` build is licensed and not
> demanded. Standing reversal watch: a long run whose head-derived
> hold drifts off the goal after long homeostasis reopens this as a
> memory question rather than a prediction one.

## A label with nowhere to walk

The label gate needed a world where the parent wants something the
pupil does not. That was easy to arrange, because at the measured
operating point these bots do the wood chain and mine exactly zero
cobblestone. So the parent applauds cobblestone. Never sticks.

The teaching tape grew twelve stone lessons beside its forty-five
wood ones: walk to the wall, dig for three ticks, one cobblestone in
the pocket, one round of applause at a fixed tick. Then the label
went into the completion rule and nowhere else. When the rule fires
for an action, an applauded completion counts fuller than a plain
one. The level of expected praise is never valued on any other tick,
which means the hangover from the last chapter cannot form. Not
unlikely to form. Mechanically excluded, because no tick after praise
ever reads the channel.

It worked exactly as designed and moved nothing at all.

Zero cobblestone in the pilot, at every dose. Zero in the 24-pupil
arm. Not one pupil, not one stone. Meanwhile the wood chain held at
22 of 24 with 1,492 sticks, so the label did no damage at any dose,
against the 70% tax the praise-as-fuel term charged. Perfectly safe
and perfectly inert.

I had also pre-registered the sycophancy row this world finally made
measurable: cobblestone gain events against net new cobblestone,
because a bot can place a stone and dig it again forever to farm
applause. The row had nothing to measure. The bot never went to the
wall.

The mechanism is the myopia the decision rule had named in advance.
The label pays one step away from a finished mineral dig. Nothing in
the composition values the walk to the mineral face, and the walk is
where all the cost is. Dwell 100%: the bot stands in the wood loop,
which pays on almost every tick, and the walk to the wall pays nothing
at all until its final step.

Twelve demonstrations of the walk to the wall. Applause at the end of
every one. A predictor that the same day's earlier gate had measured
expecting praise at ceiling. And no walking.

Because the frozen decision rule had already said what a transmission
failure would mean, the failure did the promoting instead of me: the
reach question, which had been sitting in the queue as a refinement,
became a prerequisite for the whole borrowed-goals layer. I had
predicted 14 to 20 pupils would reach the stone. Measured zero, the
first time in this arc I had over-predicted rather than
under-predicted, and the ledger's lesson sharpened into something I
can use. I under-predict what composed mechanisms do. I over-predict
how far a one-step term can reach.

> **Under the hood: the label gate (E3.1).** Fresh 33-dim cohort,
> `event_head_eta = 0.5`, 45 wood segments with the verdict silent
> plus 12 cobble segments (tape [3,3,0,0,5,5,5, idle×15]). Instrument
> gate green: 45/45 wood crafts per pupil, exactly one cobble gain
> and one firing per cobble segment, tick-stable, wood segments
> silent. The label: inside a fired completion,
> progress_after = 1.0 + β · clip(Δ̂ₐ[verdict], 0, 1), with
> Δ̂[verdict] read nowhere else, so no post-firing tick can be taxed.
> Clone hold λ = 0.25, κ = 0.25, H = 5,000. Pilot, seeds 1–8 ×
> β ∈ {0.5, 1, 2}: 0/8 cobble at every β, chains 8/8 everywhere;
> β\* = 0.5 by the registered tie-to-smallest rule. Arm: Bar T1 FAIL
> 0/24 (bar ≥ 12), Bar T2 PASS 22/24 chains with 1,492 sticks, median
> dwell 100.0%, farming row empty because the events never happened.
> Ledger: T1 predicted 14–20, measured 0.

## A world where standing still costs something

Both of this project's test worlds are paradise. Idling is free,
nothing decays, nothing is ever hungry, and every drive the brain has
ever had is an appetite for learning. That was the bottom of the map
in chapter 14, and the third gate of the afternoon put a floor under
it.

Life burns calories; acquiring things restores them. In mechanical
terms: one more sensed number, energy, starting at 1.0 and draining
0.0005 every tick, so a bot that does nothing dies in about two
thousand ticks. Every pocket gain adds 0.1, capped at full. Zero is
death.

The part I find elegant is that nothing in the brain was told about
any of this. The completion itch was built to finish begun things.
Finishing things is now also how the bot eats, so the itch became a
survival mechanism without survival ever being wired as a goal.

The first bar asked whether the meter has teeth. The frontier drive
on its own, the curious version of this brain with no hold and no
itch, died at a median of 2,001 ticks, with dwell under 1% and not a
single acquisition anywhere in 24 runs. The record's oldest null, a
brain that learns eagerly and picks nothing up, now has a body count.

The second bar asked whether the stack feeds itself, and it split in
half. All 24 pupils worked: every one gained logs, 1,905 sticks
across the arm, unique positions at a median of 22, so the miser twin
the registration was watching for never appeared. And 10 of 24 were
still alive at step 5,000, against a bar of 18.

The rows say why, and it is not a conflict between the layers. The
energy runway from a cold start is about 2,000 ticks. This cohort's
median time to its first completed chain is about 2,300. The floor
races learning and wins by three hundred ticks. The pupils that
chained early lived off their own work; the rest died in the middle
of it, having done everything right and slowly.

Which left two honest options. I could re-dose the decay until the
numbers passed, which is cheating with extra arithmetic. Or I could
look at the shape of the gap: a stretch of early life where the
creature is competent enough to learn and not yet competent enough to
eat. No animal is born into full stakes.

## What a demonstration carries

That evening I wrote the premise for the reach problem down in the
registration, in my own words, and the record kept them: *this is
what is being taught by the teachers as they teach the recipe. it
involves the steps, not just the ingredients.*

The two roads I could see were both expensive. I could hand the brain
a ladder of subgoals, which means declaring the order myself, which
is chapter 3's quiet freezing wearing a new hat. Or I could build
learned decomposition, planning over imagined rollouts, a research
program measured in months.

The third road only becomes visible once you notice what a
demonstration is. Forty-five times the bot's hands had been walked
through the wood chain, twelve times to the stone wall. Every one of
those was recorded in the same sensor readings the bot uses to think
with, in order, with the applause in the right place. The order was
in the teaching all along. Nothing in the brain was keeping it: the
frames learn what one step does, the head learns what one action
changes, and neither of them stores a sequence.

So the new machinery is a *recipe memory*: the remembered sequence of
observations from a demonstrated success, kept whole and in order, so
the steps that led to a result can be walked again. One recipe per
finished item, the last demonstration of it. This cohort had two.
Wood, ending in sticks, with no applause anywhere. Stone, ending in
cobblestone, with the parent's approval stored inside the remembered
ending.

Choosing between them is one line. At each step, score every stored
recipe by what its ending is worth to the bot's own drive, plus the
applause remembered at that ending. The parent's approval, recalled
rather than felt, marks which ending matters. Following one is the
hold from earlier in this chapter, pointed one step further along:
the subgoal is the next position in the recipe instead of the final
workshop, and the pointer advances when the bot gets within a block.
Transport only. Digging and crafting at each stop stay the itch's
job.

Against the label's floor of zero, on the same cohort, with the same
demonstrations: 24 of 24 pupils reached the stone. 3,129 cobblestone
gain events across the arm.

The wood chain survived at 18 of 24, exactly at its bar and two below
the label arm's 22, and the twin the registration had named in
advance is why. *The obsessive* is a bot whose borrowed goal eclipses
its own: dwell medians fell to somewhere between 55% and 72% as
pupils split their days between the tree and the wall. The dose is
visible in the rows, which is the useful part. At the pilot's highest
setting the wood chains sagged to 4 of 8, so 0.5 is the honest
operating point and I can see the cliff from there.

The third bar asked whether the walk was walked or stumbled into. Of
the pupils that mined stone, 20 of 24 made at least two pointer
advances along the taught path before their first cobblestone. *The
parrot*, the other named twin, is a bot performing recipe steps
somewhere they do not apply, and it stayed modest at about 2% of
steps.

One instrument failure belongs in the middle of this. The first pilot
ran with its applause marker inert: the code that picks the
remembered ending read the idle tail of the tape, so both recipes
recorded no applause at all. The bots pursued the stone anyway. With
approval invisible, the drive's own pull toward the newer of the two
recipes was enough at pilot scale. I fixed the marker, which is now
the highest-applause observation in the whole remembered sequence,
republished the pilot before the arm, and kept the broken row, because
it is the only measurement I have of what novelty alone would do.

E3.1 had said reach blocks the borrowed-goals layer. Reach was never
missing from the mechanism. It was sitting in the teaching, and the
only new machinery is a pointer.

> **Under the hood: recipe memory.** Extraction, from the witnessed
> teaching stream and nothing else: a recipe is the observation
> sequence of a demonstrated segment ending in a pocket-gain event,
> one canonical recipe per terminal item (the last demonstrated
> instance). Selection, each directed step: argmax over stored
> recipes of `drive_value_of(terminal_obs) + β · terminal_obs[verdict]`.
> Following: the pointer starts at the recipe step nearest the current
> position (position channels, world units), the subgoal is the next
> step's position, the added term is λ_r · (−Φ̂_subgoal(a)) with Φ̂
> from the head's predicted positions, advance within 1 block;
> transport only. Dials λ_r = 0.25, κ = 0.25, clone-free throughout;
> β piloted on {0.5, 1, 2}, β\* = 0.5. Arm: 24 seeds on the E3.1
> cohort, H = 5,000. Bar R1 transmission PASS 24/24 (bar ≥ 12; the
> label-alone floor 0/24), 3,129 cobblestone gain events. Bar R2 own
> goals PASS 18/24, at the bar; pilot β = 2.0 sagged chains to 4/8.
> Bar R3 recipe-led PASS 20/24 with ≥ 2 subgoal advances before first
> cobble; parrot row ~2% of steps out of context. Named successor:
> recombination, recipes composed across taught fragments, which is
> the real means-ends question.

## A childhood

The meter's gap wanted the oldest mechanism there is. *Provisioning*
is a parent covering a child's costs until the child's own competence
can pay them, and every creature that has to learn a living gets some
of it. So the dose I chose was not a smaller number for the drain. It
was a shape: the parent pays the whole metabolic bill through tick
1,500, then coverage fades in a straight line to nothing at 3,000,
and the bot lives at full stakes from there. One childhood, at the
start of one life. The record calls that particular dose *the
stipend*, and the way it fades is the first weaning this project has
been able to watch.

The bars went in before the run, and the first one carried a number I
was oddly pleased about. If a bot never feeds itself, the taper's
arithmetic says it should die at about tick 4,250. The frontier
drive's median survival, measured: 4,250. Nine predictions into this
arc's ledger, not one of them had landed on its number rather than
somewhere near it. This one did.

The provisioned composition went from 10 of 24 alive to 24 of 24
alive, with 24 of 24 still working, 2,304 sticks, unique positions at
a median of 20 and the miser still nowhere in the rows. The weaning
window shows the stipend fading and the work continuing through it.

The parent's first gift is not knowledge and not approval. It is
time. Provisioning turns the floor from a race against learning into
ground underneath it, and it does that without softening the stakes
for a bot that chooses to do nothing, which still dies on schedule.
Both of that evening's answers turned out to be teachers: steps for
reach, time for survival.

> **Under the hood: the meter, both doses.** The rig's world wrapper
> appends energy at channel index 32 (no verdict in this world):
> start 1.0, drain 0.0005/tick, +0.1 per pocket-gain tick capped at
> 1.0, death at 0 (first zero tick recorded; the run continues so the
> rest can be measured). G4, H = 5,000, 24 seeds per arm: Bar M1,
> frontier-alone median survival < 3,000, PASS at 2,001 with dwell
> < 1% and zero gains; Bar M2, ≥ 18/24 alive AND ≥ 18/24 gaining a
> log, FAIL 10/24 alive with 24/24 working, 1,905 sticks, unique
> positions median 22. Teaching itself never kills anyone: each
> segment's ~9 gain events dwarf its 0.011 of decay. G4b's stipend:
> effective drain = 0.0005 · clip((t − 1500)/1500, 0, 1), feeding
> unchanged. Bar M1b PASS, frontier median 4,250 against a
> registration that named that tick and a frozen range of 4,200–4,400;
> Bar M2b PASS 24/24 alive and 24/24 working, 2,304 sticks, unique
> positions median 20. Ledger: M2 predicted 22–24 alive, measured 10;
> M1b is the first exact hit the ledger has recorded.

## One brain, one world

By the end of that day every part of the measured life was either
shipped in the product or taught by a demonstration, and nothing in
the loop peeked at the world's bookkeeping. That licensed a run the
last long one could not be. Chapter 13 asked whether crafting would
emerge unaided in a real game at real speed, and got a clean null.
This one asks a different question: does the measured life endure?

The setup is one brain and one life. A taught graduate of the meter
cohort boots into a world that persists from that moment on, with no
resets and no fresh starts, its drive from the frames, its hold from
its own predicted positions, its itch at the same dose every gate
this month has used, and the tapered childhood at the front. One new
world rule was necessary and is recorded as such: a dug column grows
back two thousand ticks later, wood and stone alike, because a
three-tree world cannot feed a life of millions of steps.

The lab world runs at roughly five hundred brain steps a second. A
brain step is five game ticks and Minecraft's clock is twenty ticks a
second, which makes the run about 125 times faster than real time.
The target is fifty million steps, ten times what chapter 13's run
lived, in a weekend of wall clock.

Then the first segment came back and told me my own stop rule was
broken.

Five stop rules were frozen in the run plan, and one of them was the
early graduation I had asked for: stop at two thousand completed
chains. Segment one produced 131 chains in 50,007 steps. At that rate
the run would have declared victory at about one and a half percent
of its target, with none of the endurance readings it exists to
produce. The chain bar had been dosed against the old scarcity, back
when a dug tree stayed dug.

So the stop file went down at the next boundary, the amendment went
into the plan with segment one's raw numbers written into it, and the
run resumed from its snapshot. Graduation now needs two thousand
chains and twenty-five million steps. The whole correction cost two
segments, because the thing chapter 11 promised about snapshots is
also what makes an honest mid-flight amendment cheap: stop, write it
down, resume the same brain.

At step 1,000,121 the row reads 3,236 chains since birth, dwell
99.99%, energy 0.980 out of a possible 1.0, which is a bot feeding
itself without ever having been told to.

And one thing I did not design. For nine segments the pocket gained no
cobblestone whatsoever. In the segment ending at step 500,061 it
gained 691, and after that the stone never stopped: the segment that
crosses the millionth step counts 1,400 cobblestone beside 1,651 logs
and 5,544 sticks, each of those figures net of what crafting consumed.
There is no recipe memory in this run and no label. What there is, is
an itch that pays for finishing anything finishable and a meter that
counts any pocket gain as food. My reading, offered as a reading:
somewhere in the first half-million steps the bot found the stone face
and added it to the rotation, and chapter 14's grinding twin has
turned up here as a hobby that pays for itself.

The run is still going as I write this. The deciles that answer the
endurance questions are not in. What is in is the first fiftieth of a
planned life, with no death, no drift off the work position, and no
sign yet of the composition wearing out.

> **Under the hood: the c1d-lab run plan.** Brain: the G4 meter
> cohort's graduate seed 1 (33-dim, head trained through 45
> demonstrations, `event_head_eta = 0.5`); world state persisted in
> every snapshot, no resets after boot. Policy, all shipped seams and
> zero ground truth: the frames' drive + the Doc 0009 hold (goal = the
> taught work position, λ = 0.25) + `CompletionItchPolicy` at
> κ = 0.25. World renewal: a dug column regrows 2,000 ticks after it
> was dug, wood and mineral alike, placed blocks untouched. Execution:
> ~50,000-step segments (2,273 cycles), a disk snapshot at every
> boundary so the run is crash-resumable, per-segment rows appended to
> `c1d-status.jsonl`; engine telemetry accumulators are trimmed to a
> recent window between segments at 50M-step scale, so the readings
> come from the per-segment rows rather than the engine summary. Each
> row's item counts are that segment's net pocket change per item, so
> its log count is digs minus what crafting consumed. Pre-registered
> readings, by 5M-step decile: chains (endurance),
> dwell (episode 0074's drift watch), the policy's
> progress-prediction error EMA and the head's update count (NLMS
> wander at 50M steps is this run's novel exposure), the life itself,
> and unique positions (the miser). Stop rules: death; ≥ 2,000 chains
> AND ≥ 25M steps (the amendment; the original rule was the bare
> chain count); zero chains across any consecutive 10M steps after
> childhood; the `c1d-STOP` file; otherwise 50M. Measured segment
> rates fall from 501 steps/s at segment 1 to 80 by segment 28, which
> makes the weekend estimate optimistic; I have not diagnosed it.

## A time machine with unreliable hands

The other half of the plan was running the same night, and it is the
reason this chapter ends on a machine rather than a mind. Every number
in this chapter came out of the lab world, the faithful stand-in the
test rig can copy and restart at will. Chapter 13's null came out of
the real game, at real speed, over seventeen days. If the measured
life is ever going to be asked the endurance question in the full
game, the full game has to run faster than a life.

It turns out vanilla Minecraft has shipped that switch since version
1.20.3. A server console command sets the tick rate anywhere from 1
to 10,000 ticks a second, and the version this project already pins
has it. The pacing on our side was a single number: the bridge sleeps
a fixed slice of wall clock per brain step, so dividing that slice by
the speed multiplier keeps the posture chapter 13 ran at, about five
game ticks per brain step.

Two of the three bars passed everywhere. The server sustained every
speed asked of it: 19.9, 40.0, 100.0, and between 199.9 and 200.1
ticks per second against nominals of 20, 40, 100, and 200. At five
times speed it was spending about 1.6 milliseconds of a
10-millisecond tick budget, so ten times was nowhere near a ceiling.
And the posture held to the tick, between 5.02 and 5.29 game ticks
per brain step at every speed. The pacing law is real, and vanilla
Minecraft runs ten times fast with exact throughput.

The bar that failed was the bot's hands, and it failed at normal
speed.

Five attempts to dig an oak log at each of four speeds completed 3,
4, 2, and 4 times. There is no speed trend in those numbers. Normal
speed misses the bar by itself, which means the bar as I wrote it
could not measure what it was for: it conflated a flake the bridge
has always had with an effect of acceleration. The bridge's own logs
name the flake, digs aborting somewhere between 26 and 800
milliseconds into the break, and chapter 13's run lived with it
unmeasured because its 449 digs never needed any single attempt to
succeed.

Every dig that did complete crafted successfully, five out of five.
The pipeline is fine. The hands are not.

So that bar gets re-registered rather than quietly retried: a
relative bar, success at speed measured against the same bridge's own
normal-speed rate with at least twenty attempts per arm, and it goes
in after the dig question gets its own small investigation. On the way
through, four instrument bugs were found and fixed: the bridge died
when a vanished client handed it a broken pipe, the console tool
reads negative coordinates as command flags unless you warn it, the
game's rotation zero is the bridge library's yaw π so the two
conventions sit 180 degrees apart, and the registered distortion
finally showed itself in practice. The bot's body runs on wall clock
while the world runs on the accelerated tick, so at ten times speed
crossing a single block took 17 brain steps against 4 at normal
speed. The faster the world, the slower the bot inside it.

The time machine exists. At ten times speed, the seventeen days of
chapter 13 fit inside two, which is the difference between a run that
costs a fortnight and a run that costs a weekend. Whether anything
measured in there can be believed depends on a bot that misses two
digs in five, and that is where the next chapter starts.

> **Under the hood: the `/tick rate` calibration.** Local fresh flat
> vanilla 1.21.11 over RCON on an isolated volume, never c1c's data;
> the bridge patched only to report the server's game-tick clock in
> every view; a micro-arena (an oak column beside the bot) rebuilt per
> rep; per M ∈ {1, 2, 5, 10}: `/tick rate 20·M`, `tick_ms = 250/M`,
> five reps of dig-log-then-craft-planks, ≥ 3 wall-minutes of
> stepping. Bar B1, measured TPS ≥ 90% of nominal 20·M with the bot
> attached and working: PASS at every M (19.9 / 40.0 / 100.0 /
> 199.9–200.1; ~1.6 ms per tick against a 10 ms budget at M = 5).
> Bar B3, mean game ticks per brain step within 5 ± 1: PASS at every M
> (5.02–5.29). Bar B2, 5/5 digs and 5/5 crafts at each passing M:
> the M = 1 reference fails its own bar (3/5, 4/5, 2/5, 4/5 across
> M ∈ {1, 2, 5, 10}, no speed trend; 5/5 craft conversion on
> completed digs; bridge logs attribute it to mineflayer digs
> aborting mid-break, 26–800 ms in, a 1×-native behavior c1c lived
> with unmeasured), so the bar is unmeasurable as written and the raw
> numbers are recorded under the amendment protocol. Successor B2′, a
> re-registration: success rate at M within noise of the 1×
> reference, n ≥ 20 reps per arm, gated behind a fix-and-gate on dig
> reliability. Registered distortion, measured for the first time: the
> bot's physics are wall-clock, so at M = 10 a collect-walk took 17
> brain steps to cross a block against 4 at M = 1, and the bot slows
> by 1/M relative to mobs, crops, and daylight.
