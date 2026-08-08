# PRA Vision

## What PRA is

PRA — **Pose Resolution Architecture** — is an alternative approach to machine
intelligence: a brain that learns a world by *living in it*, not by being
trained on it. No labels, no dataset, no task you hand it. You give it a way
to sense, a way to act, and one built-in urge to make sense of what it meets —
and it builds its own model of that world from scratch, keeping only the
structure that earns its place. Three moves, over and over: **act and
predict** (a wrong guess is the lesson), **grow small maps** (many rival
models, each explaining a slice), **keep what pays for itself** (predict well
or be pruned).

The long-range claim is against *frozen* intelligence — the
trained-then-deployed model — on the axis where that paradigm is structurally
weak: continual learning, online restructuring, adaptation without
retraining. A PRA brain is never "finished"; it keeps learning as long as it
runs.

## The founding bet

One machinery for physical objects **and** abstract concepts
(`../02-DESIGN/validate/pose-resolution-architecture.md`). To PRA, everything
is signals coming in and actions going out; meaning is learned, never wired
in. A hand exploring an object and attention moving through a space of ideas
are, to this architecture, the same problem. Everything on the horizon below
leans on this bet.

## Who it is for

Hobbyists and makers — people who want to point a learning system at a world
(a simulation, a game, a robot) and *experiment* with it. Fair-code (the
Sustainable Use License — free for personal and internal use, source always
open to read; [journey 0067](../04-JOURNEY/0067-fair-code-license.md)),
runs on a laptop: install in one command, mount a world through the Body API,
watch it learn live, keep what it learned, share it. Putting it in people's
hands is the whole bet: the discoveries that matter will come from worlds we
would never think of (decided in [journey 0010](../04-JOURNEY/0010-the-product-thesis.md)).

## Where it is pointed

The horizon ambitions, restated and re-broadened on 2026-07-19
([journey 0042](../04-JOURNEY/0042-the-vision-re-broadened.md)). None is a
schedulable milestone; all shape design decisions today. The concrete next
experiment each ambition is gated behind is tracked in
`../03-IMPLEMENTATION/roadmap.md` (Research candidates).

- **Compounding intelligence.** A brain can be snapshotted and cloned as a
  *seed* for the next, so knowledge compounds across brains — **measured**:
  the head start is real, it is relevant transfer rather than mere maturity,
  and it survives chaining across a body-growing resize
  ([journey 0044](../04-JOURNEY/0044-brain-seeding.md)).
- **Huge worlds.** The architecture is meant to grow into worlds far larger
  than its validation suite — including distributed operation, a single brain
  across machines, which the bus seam was designed for from the start.
- **Language as a learnable world.** Under the founding bet, language is a
  world to learn, not a rival's turf. Gated behind the teacher-world
  experiment and three prerequisite decisions, with a pre-registered
  prediction that the current kernel plateaus short of syntax — if that
  prediction is wrong, the vision gets much cheaper; if right, hierarchical
  frames become the next named gate.
- **Tool self-invention, richer senses.** Open problems named honestly: the
  registration seam exists, the inventing mechanism is unsolved research;
  vision/high-dimensional input waits until the research earns it.

## What we refuse to become

- **Benchmark theater.** No chasing leaderboard SOTA for its own sake; honest
  comparative evaluation against continual-learning and RL baselines, run
  with the same spread-and-horizons discipline as everything else, is the
  substitute.
- **A hosted service.** This is OSS you run yourself.
- **A frozen-LLM competitor on encyclopedic recall.** That is a
  stored-knowledge property, not a learning property. Whether a PRA brain can
  *learn* language from lived interaction is a horizon question; *being* a
  language model is not the axis.

## How ambition stays honest

Every ambition above sits behind a named, pre-registered gate, and no demo
outruns measured capability — a claim without telemetry behind it does not
ship. Direction decisions record what would change our minds when they are
made, so a future reversal is a clean, anticipated turn instead of drift.
The full discipline lives in [`constitution.md`](constitution.md) and
[`how-we-work.md`](how-we-work.md).
