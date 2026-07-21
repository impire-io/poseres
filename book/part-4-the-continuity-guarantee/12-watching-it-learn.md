<!-- Draws on: journey 0020 (pra-rover: viewer discipline, three-way
     byte-identity, improvements 0.190/0.280/0.203, best_dim 2, pops
     15/19/13), journey 0019 (Gymnasium: respawn semantics, 473 respawns/13k steps,
     ~3s/seed, best_dim 1 observation), journey 0021 (continuous mode: single boot,
     reference world drifts, bounded rover healthy), journey 0026 (ROS2: topics as
     tools, control tick, lidar NaN incident), journey 0027 (channel weighting as
     C2 gate). Numbers as of 2026-07. -->

# Watching it learn

A book about a machine that learns in front of you should let it learn
in front of you. This chapter is the part you can run.

Two commands, on any machine with Python:

```
pip install poseres
pra-rover
```

A browser page opens. In it, a small rover wanders a walled arena with
five obstacles, reading a five-beam rangefinder, a compass, a position
beacon, and a bumper. The rover's movements are, and remain, random.
Chapter 9 explained why the coin flip is the honest baseline. The point
of the demo isn't the driving. It's the three quantities moving beside
the arena, because by now you know what each one of them is.

The prediction error falls. That's chapter 4's free teacher being
satisfied: the brain is getting less surprised by the consequences of
its own actions, live, with no training phase and no labels.

The population breathes. Frames spawn, compete, and are evicted:
chapter 6 running in real time, holding around fifteen or so residents
without any line of code naming that number.

And best_dim settles, usually at 2, run after run. The rover's physical
state is three or four numbers (position, heading). Two is chapter 8's
price-optimal answer for what this sensor stream will pay for at this
budget. You are watching the book's central argument happen in about
four minutes.

One discipline behind the screen deserves its paragraph, because it's
chapter 7's law wearing its last disguise. The viewer *observes without
perturbing*: a run with the browser page open is byte-identical to the
same run with no one watching. A paced, watchable run is byte-identical
to an unthrottled one. That's tested, not assumed. An
instrument that changes the experiment can't be trusted about the
experiment. And a demo that secretly ran different code from the
validated engine wouldn't be a demo of anything.

## Other worlds, one seam

The rover is built on the same interface anything else can use, and by
now several very different kinds of world hang off it.

Any Gymnasium game (the standard library of reinforcement-learning
worlds, CartPole and its hundreds of cousins) mounts through an
adapter of about fifty lines. Chapter 4 told you the opinionated part:
the game's reward stays at the door. Run the CartPole example and the
summary says what the brain is actually doing (predicting its world,
not playing to win) and proves its own determinism by re-running its
seed.

One design choice there was a genuine fork. When the pole falls, the
game ends mid-episode, and the adapter respawns instantly rather than
pretending the fall didn't happen. The boundary moment is honestly
unpredictable (under a random policy, about 3.6% of transitions), and
that noise shrinks as competence grows: a brain that keeps the pole up
sees fewer deaths. The alternative designs quietly falsified the
action-consequence pairing, and falsifying triplets is the one sin this
architecture can't absorb.

Real robots mount through ROS2, the lingua franca of robotics: every
topic a robot publishes (lidar, odometry, a camera) becomes a sensor,
every command channel an actuator, on the same body interface. Anatomy
is changeable at runtime, by the same machinery as chapter 6's
spawning. You can snap a new sensor onto a *running* robot, and the
frames resize without forgetting what they knew.

Worlds that cannot be reset run in continuous mode: a robot can't
teleport to a starting pose between episodes. The engine boots the
world exactly once and learns from one unbroken stream, with every
mechanism from Parts 3 and 4 carried over.

Continuous mode also produced a finding I didn't ask for: run unbroken,
the *reference* world (the synthetic one every validated result was
measured on) drifts into a saturated corner and learning collapses.
The bounded rover arena stays healthy indefinitely. The
instrument-vs-world lesson again, from a new side: the reference world
is an episodic instrument, and continuous deployment needs worlds that
keep returning to familiar ground. That's now written down as deployment
guidance, with the drift signature recorded so the failure is
recognizable.

> **Under the hood: where determinism ends.** Doc 06 §5b classifies
> worlds by what snapshots and reproducibility can promise. Derivable
> worlds: everything, byte-exact. Capture-required worlds (Gymnasium):
> exact resume, conditional on the env's own seeded determinism.
> Multi-stream: exact, all stream state in the blob. Class 4 (live
> services and free-running hardware) gets no world-state guarantee
> and, when free-running, is the project's first openly non-reproducible
> mode: the brain's own updates stay deterministic, but wall-clock
> sensor timing is the world's to control. Stated up front rather than
> discovered by a disappointed user.

## The first real sensor drew blood

The Gazebo worked example (a simulated diff-drive rover with a real
lidar stack, the dress rehearsal for physical hardware) earned its
place in this book on its first run. The summary printed `nan early →
nan late` while the exit code reported success. A lidar reports
infinity for "no hit" and negative infinity for "below minimum range."
Those non-finite values marched straight through the pipeline and
poisoned every accumulated error statistic. The instrument smiled;
the numbers were garbage.

The fix was boring in the best way: the adapter now rejects non-finite
deliveries loudly, and the example clamps its lidar to the sensor's own
range bounds. But the incident is the right note to end Part 4 on,
because it's a preview with a warning label.

Chapter 8's worlds were clean. Real sensors are not: they saturate,
they drop out, they carry channels of pure noise. A measured result
from the complexity-ladder work says exactly where that bites: strong
static on half the channels collapses structure discovery. The named
remedy, learned channel weighting, is on the bench as I write this,
and it explicitly gates the physical-robot showcase. The continuity
guarantee of this part of the book holds where it has been measured.
Between here and a robot in your garage stands one named, sized, open
problem. That's the most honest sentence a systems book can end a part
on.

What's left is the frontier the whole book has been walking toward. The
worlds so far answer pokes with physics. There's one more kind of world:
one that answers with *intent*, that notices what you're trying to do
and replies in a way meant to change you. A teacher. Part 5 asks what
this architecture becomes when the world teaches back.
