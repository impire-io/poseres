<!-- Draws on: PRA-01 §3.1 (SensorimotorEvent, event-ordering requirement);
     design docs 01/03; journey 0019 (reward never crosses the seam).
     No empirical numbers in this chapter.
     Rewritten 2026-07-18: flow pass (fewer asides, near-zero em dashes). -->

# Before, action, after

Watch a baby in a high chair with a spoon. The spoon gets lifted, studied,
and dropped over the side. Clatter. An adult picks it up and returns it.
It gets dropped again. Clatter. By the fifth drop the adult has theories
about the baby's motives, and none of them are charitable.

Here's what the baby actually has after five drops: five records that all
share the same three parts. What things were like. What I did. What things
were like next. The spoon was in my hand, I opened my fingers, and then my
hand was empty and a bang came from below. Before, action, after. The baby
is running experiments, and every experiment produces a record of exactly
this shape.

That shape is the foundation this entire book rests on, so let me give it
its name. A *triplet* is one recorded moment of experience: what I sensed,
what I did, and what I sensed next. Everything PRA will ever learn, it
learns from a stream of triplets. There is no other input. No textbook, no
labels, no instructions. Those would be someone else's knowledge. The
triplet stream is the machine's own life, and my claim is that it's
enough.

## One triplet, in numbers

Before going further I want to pin these words down, because the whole
book stands on them and "sensed" is doing a lot of work.

An *observation* is one simultaneous reading of every sensor the body
has, packed into a fixed-order list of numbers. Nothing more. The rover
you'll meet in Part 4 has five distance rays, a two-number compass, a
two-number position beacon, and a bump detector, so one of its
observations is ten numbers, always in that order. And the "before" and
"after" of a triplet are both simply observations: the same ten slots,
read at two consecutive steps. The triplet is the package of three
things: the reading before, the action taken, the reading after.

Here is one, from the rover, with the noise stripped for readability:

```
before:  rays 0.61 0.44 0.30 0.51 0.72   compass 0.00 1.00   position 0.05 -0.32   bump 0
action:  forward
after:   rays 0.54 0.37 0.22 0.44 0.65   compass 0.00 1.00   position 0.05 -0.24   bump 0
```

The labels are for you. The brain receives ten unlabeled numbers, then
an action, then ten more. Look at what moving forward did: the five ray
numbers all shrank (something ahead is getting closer), the compass
numbers held still (no turning happened), one position number grew by
the size of a step, and the bump flag stayed quiet. One triplet like
this proves nothing. But collect thousands, and the regularity is
sitting there in plain arithmetic: whenever the action was "forward",
the rays shrink together and the compass holds; whenever it was
"turn_left", the rays reshuffle and the compass moves instead. Nobody
tells the brain that the first five slots are distances, or that walls
exist. Cause and effect is lying in the differences between before and
after, waiting to be mined. That mining is Part 3's job.

## Why the middle part changes everything

Strike out the middle of the triplet and you're left with: what I sensed,
then what I sensed next. Just watching. A lot can be learned by watching.
You notice which sights tend to follow which. But there's a wall that
watching can never get through.

Every morning the rooster crows, and then the sun comes up. A pure
watcher sees these two events go together thousands of times without a
single exception. Does the crowing pull the sun up? To a watcher, "the
crow causes the dawn" and "the crow merely comes first" look identical.
They are identical in the watching. The only way to tell them apart is to
reach into the world and meddle. Keep the rooster quiet for one morning
and see whether the sun still rises.

That's what the middle of the triplet is. An action is a deliberate poke
at the world, and the "after" is the world's reply to your poke rather
than to the general flow of events. I did this, and then that happened,
and I know the "this" was mine. Stack up enough of those records and you
learn something that watching can't deliver at any volume: what your
actions actually do. Cause and effect can only be observed from one
vantage point, and that's the inside of something that acts.

This is why I keep insisting the book isn't about language or vision.
Those are kinds of content, and the triplet is about the structure of
experience: it comes as before, act, after, and the middle belongs to
you. Any content fits the shape. A rover's triplet holds laser ranges and
wheel commands. A robot hand's holds finger pressures and motor currents.
As promised in chapter 1, a conversation fits too: what I heard, what I
said, what came back. The shape doesn't care what flows through it, and
that indifference is what will let one mechanism serve every body in this
book.

## The test that needs no teacher

So a brain eats triplets. How do we know whether it's learning anything?
The shape carries its own test, and the test is cheap: prediction. If you
understand what your actions do, you can say the "after" before it
arrives. My fingers are about to open. What happens next?

The world then does something no teacher could be paid enough to do. It
grades every prediction instantly, and it has no interest in your
feelings. The spoon lands where it lands. The gap between what you
predicted and what arrived is your surprise, and it comes delivered fresh
with every triplet, thousands of times a day, for free. A big surprise
means your model of the world is wrong right here. No surprise means
there's nothing left to learn in this corner today.

When chapter 3 said PRA's models compete to predict well, this is the
game they're competing at: smallest surprise on the next triplet. Every
mechanism in Part 3 runs on prediction error as its fuel. Survival,
eviction, even the discovery of size.

> **Under the hood: the event contract.** In PRA-01 the triplet is the
> `SensorimotorEvent(previous_observation, action, observation)`, and its
> §3.1 ordering requirement is load-bearing: `previous_observation` is
> always the true observation from the immediately preceding step,
> regardless of what any frame chose to attend to or map. A frame that
> ignored the last step still receives the real history in its next
> event. The rule exists because the alternative is chapter 2's disease
> in a new organ: a model allowed to curate its own experience record is
> grading its own homework. History is written by the world, once, for
> everyone.

## What's *not* in a triplet

Look once more at the shape: sensed, did, sensed. Now notice what's
missing. I left it out on purpose, and it's the most opinionated design
choice in the book so far.

There is no score in it. No "that was good." No reward.

Most learning machines that act are built around a reward signal.
Game-playing systems are the famous example: a number arrives with each
step, the number says how well you're doing, and the machine exists to
make the number big. PRA's triplets carry no such number. When a game
world is plugged into PRA, the game's built-in reward is deliberately
left at the door. The brain receives sights and sends actions, and that
is the whole interface.

Why refuse free information? Because a reward is somebody's opinion
baked into a number. The game says the score is what matters. A
warehouse robot's designers say boxes per hour is what matters. Whoever
picks the reward has decided, in advance, what the machine is for, and
that decision rides along inside every step of training. Chapter 1 all
over again, one level deeper.

So PRA splits the job in two. The triplet stream teaches the brain how
the world works: do this, and that happens. Motivation, the business of
deciding which action is worth taking, is a separate component with its
own chapter (chapter 9). Keeping the two apart has a practical payoff:
you can change the machine's job without touching its understanding of
the world. What a motor command does stays true whether this week's
task is sorting packages or stacking shelves. A brain that mixed the
two would have to relearn its world every time its job changed, and a
brain that learns forever will change jobs many times.

One spoon-drop proves nothing, of course. Maybe the clatter was a
coincidence. Maybe the floor won't be there next time. A single triplet
is one data point from one poke at an enormous world. The power was
never in the triplet. It's in the stream, millions of triplets over a
lifetime, and in the kind of machinery that can eat that stream and come
out understanding. Before we open that machine, though, there's an
objection standing in the doorway: machines that seem to understand
already exist, and you can talk to one today. The next chapter is about
why this book isn't about them.
