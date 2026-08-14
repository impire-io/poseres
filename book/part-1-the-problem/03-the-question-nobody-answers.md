<!-- Draws on: journey 0003 (feature 001: harness + batched core, ~40x, T1–T6
     PASS, T-SCALE best_dim≈1 at true_dim 20/35/50 — formally open);
     PRA-02 (world construction: reference true_dim=3/obs_dim=10, scaled
     20/35/50 with obs_dim 60/105/150). Commits 7387bd7 → d17354c. -->

# The question nobody answers

Suppose you fixed both cliffs from the last chapter. Your brain overwrites
nothing it still needs and hoards nothing it doesn't. Congratulations: you
now face the question that was hiding under both of them, the one this
project actually stands or falls on.

How much brain does a world need?

## The knob game

Let me make "how much" mean something. Play this game with anything that
moves: what's the smallest number of knobs you'd need on a control panel to
describe it completely?

A playground swing: one knob. Its angle. Turn the knob, the swing sweeps
back and forth. Everything else about it (the height of the seat, the
shadow on the ground) follows from that one number.

A boat on a lake: three knobs. Where it is (two knobs, like map
coordinates) and which way it's pointing. A drone adds height and tilt.
Your hand? Try counting: each finger bends in three places... you'll land
somewhere over twenty before you're done with one hand.

That number is the world's hidden size. I'll call the knobs *dimensions*:
the separate numbers you'd need to pin down what state a thing is in.

Now the strange part. What your senses receive is enormously bigger than
that. A camera watching the swing delivers a million pixels, sixty times a
second. A million numbers to describe a one-knob world. The pixels aren't
lying, but they're redundant: behind the million there is one. Finding the
few knobs behind the many numbers is, I'd argue, most of what
understanding a world *is*. And here's the question that matters: when a
brain does that, how does it know how many knobs to look for?

> **Under the hood: latent state and emission.** Formally: the world has a
> latent state `z ∈ R^d` and the senses receive `x = f(z)` with
> `dim(x) ≫ d`. The knob count is the latent dimensionality `d`; the
> million pixels are the observation. In PRA's validation worlds this is
> made literal so `d` is knowable to the harness: actions displace a
> hidden latent vector, and observations are a fixed nonlinear projection
> (`tanh` of a random linear map) into a larger observation space:
> `d = 3` with 10 observation channels in the reference world. The system
> under test never sees `d`, the latent, or the projection. That's the
> point: it must discover the size, and the harness can check its answer
> against ground truth.

## The field's answer: decide in the lab

Here is how the question gets answered today, almost everywhere: a person
picks. An engineer chooses the model's size and shape before training
starts: how many layers, how wide, what kind of internal state. The choice
gets tuned on benchmarks, and then it ships.

Notice what that is. It's freezing again, one level up. Chapter 1's brains
had their *knowledge* frozen at the factory; this freezes the *shape of
what can be known*. The engineer has decided, in the lab, what kind of
world the machine is allowed to find itself in. Too small for the world it
meets, and it physically cannot represent what's happening around it. Too
big, and there's room for every exception to be memorized instead of
understood: the hoarder's house again, pre-built with extra wings.

And when the world changes (chapter 1's whole complaint), the right size
changes with it. A brain committed to learning forever can't have its size
picked once by somebody else. It has to keep answering the question itself,
for whatever world it's actually in.

So that became PRA's defining requirement, the one everything in Part 3
serves: the brain must discover its own size, while running, with nobody
telling it.

## The measurement that said "one"

By early summer 2026 I thought I was close. The v4 prototype (the honest
one, after the cheating was fixed) had passed its tests in the toy world.
The most important of those, the one v3 had faked, checks exactly the
question of this chapter: the toy world's hidden size is three knobs, and
the brain, told nothing, grew models of size three. It worked. On eight
different random runs it worked almost every time.

So I built the real thing: the actual engine, engineered properly, about
forty times faster than the prototype. The speed mattered for one reason:
it made bigger worlds affordable. I could finally ask the question at
serious sizes: worlds with a hidden size of 20, 35, 50 knobs, their
observations three times wider. If the discovery mechanism was real, it
should find those numbers, or at least march toward them.

The engine's answer, at every one of those sizes, was: one.

One knob for a twenty-knob world. One knob for fifty. The same machinery
that reliably found "three" in the small world looked at every large world
I could build and confidently reported the smallest possible answer, as if
the entire world were a swing.

> **Under the hood: the T-SCALE reading.** Feature 001 (the `pra` package:
> batched dim-grouped kernel, deterministic telemetry, the `pra-validate`
> CLI) reproduced the v4 prototype's trajectory near bit-for-bit at ~40×
> speed, byte-identical on re-run. The acceptance suite T1–T6 passed at
> the reference scale (T4 within-one majority at every checkpoint). The
> investigatory T-SCALE run at `true_dim ∈ {20, 35, 50}`
> (`obs_dim` 60/105/150) reported `best_dim ≈ 1` across the board. The
> scale question was recorded as formally open rather than explained away.
> Commits `7387bd7` → `d17354c`.

This result shaped the next several weeks, so it matters what it was and
what it wasn't. It was not a bug, in the usual sense: the code did what it
was written to do, and did it reproducibly (the engine is deterministic: the
same run, re-run, produces the same bytes, which is what let me trust any
of these readings at all). And it was not the old cheating; v4's scoring
was honest. Something else was true: every part of the mechanism had been
tuned, tested, and validated in a three-knob world, and somewhere in the
climb from three to twenty, some assumption baked into it had quietly left
its comfort zone. The discovery machinery didn't crash at scale. It failed
*politely*, returning a clean, wrong, tiny answer.

Which meant the question of this chapter was still open, in the worst way.
It's easy to build a system that discovers structure in a world small
enough that you could have hand-picked the structure yourself. The entire
value of the promise is at the sizes where nobody can, and that's exactly
where mine had just shrugged. Finding out *which* assumption broke (it
turned out to be six of them, stacked) is a story for Part 3, and I'd
argue it's the best story in this book.

But before any of that can make sense, you need to know what this brain is
actually made of and what it eats. Not code, yet. Something simpler. Every
brain that learns from a body has exactly one kind of experience available
to it, one shape of raw material, and everything in Part 3 is built out of
it. Three things, in a row: what you sensed, what you did, what you sensed
next. That's Part 2.
