<!-- Draws on: hq/02-DESIGN/0003-sensorimotor-core.md (frame = place + predict,
     identical kernel, global pose); hq/02-DESIGN/0004-structural-learning.md
     (birth on demand, copy-don't-mutate, spawning, protection, threshold
     divides by crowding, slow-loop order); journey 0001–0002 background.
     Numbers: rover populations from journey 0020 (15/19/13, best_dim 2). -->

# A head full of rival guessers

Time to open the machine. You know what it eats (triplets), and you
know the question it has to answer while eating: how many knobs does
this world have? Here's the design decision everything else hangs on.

PRA does not contain a model of the world. It contains a *crowd* of them.

## One guesser

Let me introduce a single member of the crowd first. In PRA it's called a
*frame*, and a frame is a bet. Specifically: "this world can be described
with *D* knobs." Every frame picks its own D. A three-knob frame
and a fourteen-knob frame can live in the same head at the same time,
watching the same triplets, each insisting on its own answer to chapter
3's question.

A frame backs its bet by doing two jobs, over and over, on every triplet.

First job: *place*. A sight arrives. That means one step's worth of raw
numbers from the senses; for the rover you'll meet in Part 4 it's ten
numbers (five laser ranges, a compass, a position beacon, a bumper).
The frame's work is to re-express that sight as a setting of its own
knobs. It helps to keep the two ideas separate here. The frame is the
panel itself: the knobs, however many it bet on. The *pose* is where
those knobs point right now. A three-knob frame answers every sight
with three numbers, its best summary of the sight it was just handed.
So a pose is not the frame, and not the world either. It's the frame's
reading of one observation, expressed in the frame's own coordinates.
New sight, new pose, same frame.

Second job: *predict*. Told the action (motors forward!), the frame
predicts where its knobs will land next. Then the real next sight
arrives and does the grading itself, the free teacher chapter 4
promised. Surprise, measured, delivered, logged.

A frame with too few knobs can't help but blur things together. A
one-knob frame watching a boat can track it east-west or north-south, but
never both, so its predictions keep being wrong in ways it can't even
express. Too many knobs and the frame has room to fit its recent
experience like a glove, including the noise, which reads well today
and predicts poorly tomorrow. The bet is real, and the triplet stream
settles it.

## What a frame keeps

The word "space" invites vague readings, so here is the complete
inventory of one frame, the way a debugger would list it. Three small
networks: the *encoder* (observation in, pose out), the *decoder* (pose in,
reconstructed observation out, which is how the frame proves its knobs
can still express what it's looking at), and one transition model per
action (pose in, predicted next pose out). Plus some bookkeeping: its
dimension D, its age, whether it's still a protected newcomer, and
three running averages of its recent scores. That is everything a frame
is.

Notice what's not on the list. No observations. No triplets. No poses.
A pose exists for exactly one step: computed from the current
observation, used for prediction and learning, folded into the running
averages, discarded. Over a frame's life the stream of poses traces a
path through its space, and the path is stored nowhere. What the path
leaves behind is the shape it wore into the weights, the way a field
keeps no record of footsteps and still ends up with a trail. When
chapter 11 tells you the whole brain keeps no scrapbook, this is where
that starts: a single frame is already scrapbook-free.

> **Under the hood: what a frame is made of.** Three small tanh networks
> sharing one hidden width: an encoder (observation → pose, `dim = D`), a
> decoder (pose → reconstructed observation, which measures how well this
> frame's knobs can even express the current sight), and a per-action
> transition model (pose + action → predicted next pose). Every frame
> runs the *identical* kernel, with no per-frame branching anywhere, so
> frames differ only in `D` and learned weights, and the whole population
> batches on one code path. A frame is a coordinate space, not a slot for
> one object: one frame holds many concepts at once. The set of poses
> from every frame that mapped the current observation is the *global
> pose*: the system's full interpretation of the moment, handed to the
> motivation layer in chapter 9.

## The crowd

Why keep a crowd instead of building one excellent model? Because of
chapter 3. To build the one right model you'd have to already know the
right size, and nobody knows, not even the builder. The honest position
is ignorance, and the honest mechanism for ignorance is to let rival
answers *coexist* and make the world's own replies decide. If that sounds
like evolution, it should. PRA runs survival-of-the-fittest on world-
models, inside one head, with generations measured in minutes.

The life cycle has four rules, and by now you can guess the disease each
one exists to prevent.

New guessers keep arriving. On a schedule, the system spawns a fresh
candidate frame, usually betting a knob-count near the current best
performer's: a rival that says "close, but I think it's more like
eleven." And if ever a sight arrives that *no* frame can express, a new
frame is born on the spot, that instant, mid-life. The crowd can start
from literal zero this way: the first sight of the first day creates the
first frame.

Nobody ever gets edited. This one took me a while to appreciate. If the
system suspects a frame's size is wrong, it does not reach in and resize
it; it spawns a new candidate at the new size and lets the two fight it
out. The original keeps running, unharmed. Every structural change is
therefore reversible by default: a bad idea simply loses and gets evicted,
while what already worked was never touched. Chapter 2's first cliff,
destroying old competence while reaching for new, is fenced off by
construction. The system never rewrites what it knows; it out-competes it.

Children are protected. A newborn frame is hopeless at first, like all
newborns, so for a fixed window it cannot be evicted no matter how badly
it scores. It gets a childhood: guaranteed cycles of real experience
before judgment day. Without this, no new bet could ever survive long
enough to be tested fairly against seasoned rivals.

The losers are deleted. Past childhood, every frame is judged continually
on its record: the gap between what it predicted and what arrived, plus
a rent I'll come back to in chapter 8. Fall below the bar and you're
evicted. Permanently. And this bar is the one piece of v3 wreckage I most
needed to get right the second time: the more crowded the head gets, *the
harsher the bar becomes*. Growth itself raises the pressure to be worth
keeping. In v3 the bar bent the other way: crowding made survival
easier, and chapter 2 showed you the straight-line hoarding that
bought. Same mechanism, one sign flipped, opposite fate.

> **Under the hood: the life cycle, precisely.** Two timescales. The fast
> loop runs per-event: frames place, predict, and learn weights; the only
> structural event allowed is birth-on-demand when zero frames map an
> observation. The slow loop (consolidation) runs between episodes on a
> paused, consistent state, in fixed order: age everyone and mature
> candidates past `min_age_cycles`; apply pending anatomy changes; evict
> (soft eviction against the population-scaled threshold, then a hard
> cap, respecting protection and `min_frames`); spawn `spawn_per_cycle`
> candidates via the proposal policy (default: near `best_dim ± 1`, with
> occasional exploration jumps). The threshold *divides* by crowding:
> `base / (1 + coeff · excess_population)`. Doc 04 marks the dividing
> direction as a MUST, with v3's rising-bar failure documented as the
> reason. Copy-don't-mutate is likewise a MUST: dimensionality change
> only ever happens by spawning a rival.

## What the crowd looks like, alive

Run PRA on the little rover world from Part 4 and you can watch all of
this happen on one screen. The population "breathes": spawns push it up,
evictions pull it down, and it hovers in the teens (fifteen, nineteen,
thirteen frames on three different runs of the same world) while the
crowd's best answer for the world's size settles and steadies. No line in
the code says "keep about sixteen frames." That number is negotiated,
continuously, between the spawn rate and the bar, and it holds while
individual frames come and go.

That sentence is the quiet heart of this
book. The knowledge in PRA doesn't live in any frame. Frames are
disposable: hired, tested, fired. What persists is the *population*: a
shifting collection of coordinate systems whose current consensus
is the system's understanding of the world. Learning forever stops being
"one model, carefully revised forever," which chapter 2 showed is a walk
between two cliffs, and becomes something sturdier: a steady turnover of
mortal guesses under an immortal selection rule.

Which puts enormous weight on one question: is the judging fair? A
tournament is exactly as good as its scoring, and chapter 2 already
showed you what happens when it isn't: v3's contestants found four
separate ways to win without being right. The next chapter is about
those four cheats, how each got sealed, and the constitution that came
out of it. It's the most important chapter in the book.
