<!-- Draws on: journey 0006 (feature 003: versioned pickle-free blob, resume
     byte-identical to uninterrupted), journey 0023 (feature 010: code from the
     caller, state from the blob; per-world-class guarantees Doc 06 §5b;
     the one-ULP group-order bug). No new empirical numbers beyond those. -->

# No scrapbook required

Here's a question with a revealing answer: after ten thousand episodes of
life, what does this brain contain?

For most continual-learning systems the answer includes an archive. The
replay approach from chapter 2, the field's workhorse, has to keep a
store of lived moments and re-study them forever. The honest inventory
of such a system: the model, plus a curated scrapbook of its past, plus
a policy for what to paste in and what to tear out. The scrapbook is
load-bearing. Lose it and the next lesson starts destroying old
competence again.

PRA's inventory is shorter. The population of frames: their sizes, their
weights, their running scores. That's the whole estate. Not one triplet
is retained; every observation is used in the moment, shapes whatever it
shapes, and is gone. The brain's memory footprint on day one thousand is
the same as on day one, bounded by the population cap, not by the length
of the life. Ask it about a specific afternoon last month and there is
nothing there to answer with. It keeps what ten thousand hours of
practice leaves in a person: not a recording of the hours, the shape they
built.

## Why losing the past is affordable

Throwing away experience sounds reckless, so it's worth being precise
about which jobs the scrapbook was doing in other systems, and what does
those jobs here.

Replay's first job is protecting old skills from new lessons. In a
single shared network, the only way to keep yesterday's competence from
being overwritten by today's gradient is to keep re-presenting
yesterday. PRA doesn't share one network; chapter 6's rule (nothing is
ever edited, rivals are spawned instead) means old competence is never
exposed to new gradients in the first place. Structural protection where
replay uses rehearsal.

Replay's second job is remembering rare-but-important situations.
Here the honest answer is: PRA handles this differently, and less
completely. A situation matters to this brain exactly as long as the
structure it shaped keeps earning its place in prediction. A one-time
event whose lesson stops paying rent will eventually be competed away.
That's a real limitation, stated plainly: this is a brain, not a log. If
your application needs an archive (an incident record, an audit trail),
keep one; the claim of this chapter is only that *learning continually*
doesn't require it, not that archives are useless.

What the no-scrapbook design buys in exchange is everything chapter 2
priced out: no growing storage, no growing rehearsal cost, no curator
deciding in advance what future-you will need, and no quiet dependence
on the archive's quality. The system's past is present only as the
structure it managed to build. That is also the only form of the past
that was ever going to keep up with a world that changes.

## Pausing is not remembering

There is one thing in PRA that looks like memory-of-everything and needs
to be carefully distinguished from it: the snapshot.

At any consolidation boundary, the complete learned state (every
frame's weights, every score, every counter, down to the exact state of
the random number generator) can be written to a file. Load that file
and the run *continues*. Here the project's standard is absolute: a run
resumed from a snapshot is byte-for-byte identical to the run that
never stopped. Not similar. Identical, to the last bit of every
number, provable by re-running both.

A snapshot isn't the brain remembering; it's the brain *paused*. But the
consequence is worth a moment of awe, because it's something biological
brains flatly cannot do: this brain is a file. It can be stopped,
copied, moved to another machine, resumed mid-thought. Two people can
run the same mind forward from the same moment and compare what happens.
A learned lifetime can be handed to someone else. That is the seed of
something Part 5 will want: if a brain is a file, a *trained* brain is a
shareable artifact.

> **Under the hood: the snapshot contract.** Feature 003: the full
> learned state (frame tensors, drive bookkeeping, counters, summary
> accumulators, RNG state, config in force) serializes to a versioned,
> pickle-free blob through an atomic store. Worlds that are derivable
> from the seed are re-derived on resume; worlds with their own state
> declare `snapshot_needs_state` and travel in the blob (feature 010).
> Doc 06 §5b records the guarantee per world class, including the
> honest fourth class, where live services and free-running hardware
> get *no* world-state guarantee: the brain persists, the world
> re-attaches.
> Snapshots are opt-in; validated modes stay byte-frozen and file-free.

## One bit, five features, and what "identical" costs

I want to tell you about the smallest bug I have ever hunted, because
nothing else in the project says as much about what the byte-identity
standard actually demands.

Five features after snapshots shipped, a test in a later feature caught
a resumed run differing from its uninterrupted twin in one telemetry
number: by one ULP. A ULP is the smallest step a computer's numbers can
take; this was a disagreement in the very last bit of one
floating-point value. Every earlier schedule, every mode, every test
across five features had shown perfect equality. One new test
configuration, and there it was: the tiniest representable crack in the
guarantee.

The diagnosis ran the usual ladder (capture doesn't perturb; plain
worlds diverge too; the bug predates the current feature) and landed
somewhere almost embarrassing. The snapshot wrote the frame groups
*sorted by size*, for tidiness. The live engine holds them in birth
order. Computers add floating-point numbers in sequence, and addition
order changes the rounding in the last bit. So a restored population,
identical in every value but iterated in a different order, summed its
per-step arithmetic infinitesimally differently. The fix records the
order as lived. The lesson earned a place next to chapter 7's rules:
*sorting is a mutation.* A byte-identity claim is only as strong as the
orders it preserves, and "the same numbers" is not the same as "the
same computation".

Why does a last-bit crack deserve a hunt at all? Because the guarantee
is the instrument. Every result in this book (every refuted
hypothesis, every dose–response, every "moved only this and the landing
rose") rests on runs being *exactly* reproducible, so that any
difference between two runs is caused by the one thing deliberately
changed. A standard of "close enough" would have dissolved chapter 10's
lockstep turns and chapter 9's paired margins into plausible noise. One
ULP today is an unexplained mechanism tomorrow. The project pays for
its certainties in this currency, and I've come to think the price is
the whole reason there's anything in this book worth telling.

The guarantee, then, in one sentence: nothing of the past is kept, and
nothing of the present is lost. The next chapter is where you stop
taking my word for any of it: the part of the book you can run.
