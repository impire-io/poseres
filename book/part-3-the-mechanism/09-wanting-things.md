<!-- Draws on: journey 0005 (feature 002: drive seam, immutable drive params,
     T7 criterion amended openly, curious ≈ random at reference), journey 0007
     (agency diagnosis: novelty worse than random at scale, four refuted
     hypotheses, content-free control, inverted preference, CompetenceDrive
     PASS), journey 0018 (blend dissolves — one novelty statistic), journey 0024 (frontier
     drive, A4 closed at 24-seed power). Trails: AGENCY-, BLEND-,
     PREDLP-DIAGNOSIS. Numbers as of 2026-07 measurements. -->

# Wanting things

There's something I've put off telling you for three chapters. Every
result so far (the discovered dimensions, the anchored ecologies, the
price-optimal landings) was produced by a brain that wanders at random.
Every action it took, through all of it, was a coin flip. The frames, the
judge, and the price never needed anything better, and random has a
virtue nothing else has: it can't fool you. It has no preferences to
bias what the brain gets to see.

But a real agent can't stay a coin flip. A brain that learns from its own
actions gets to *choose* its experience, and choosing well ought to beat
drifting. This chapter is about making the system want things, and it contains
the project's most instructive failure, so I'll say the conclusion up
front: the obvious thing to make it want, the one half the field and I
both reached for first, measurably hurt.

## The one part that doesn't learn

First, a design constraint that surprises people. In PRA, the drive, the
rule that scores which action looks worth taking, is the one component
that cannot learn. Its parameters are structurally immutable; there is no
code path by which experience modifies them. In a book that has spent
eight chapters replacing frozen things with learning things, the part
that does the wanting is deliberately frozen.

Remember the law: never, ever let the system grade its own
homework.[^homework-law] This is the same law, applied one level up. A drive defines what
counts as a good experience. If the system could learn its own drive, it
would be choosing its own exam one final time. And the gradient points
somewhere predictable: toward wanting something that is easy to satisfy.
A system that can edit what it wants will drift toward wanting what it
already has. So what the system wants is fixed, small, and outside the
market. Everything else competes; the thing that defines winning does
not.

What a drive gets to work with is the machinery already built. When an
action is considered, the frames predict where the world would land
(one step of lookahead through the transition models) and the drive
scores those predicted outcomes. Understanding proposes; wanting
disposes. The two stay in the separate rooms chapter 4 promised.

## Curiosity, measured

The default drive I built first was curiosity. Not a straw man set up to
fail: it's the respectable choice, with a long research pedigree. Prefer
novelty, weighted by learning progress.
Seek out what you haven't seen, especially where your predictions have
been improving. It's also what I would have bet on.

The acceptance test for the drive layer, T7, was written with deliberate
modesty: directedness must not *hurt*. Beat the random baseline or tie
it. At the reference scale, curiosity tied: statistically
indistinguishable from random. Fine; the reference world is small, maybe
there's nothing to be clever about. Then the scaled measurement, the one
with room for cleverness, came back: the curious brain was *worse* than
the coin flip. Not subtly: worse in seven of eight seeds, while its
policy was measurably doing what it was designed to do. Eighty-seven
percent of its actions were directed, all that direction was real, and
the sum of it was negative. The system that wanted interesting things
learned less than the system that wanted nothing.

I couldn't leave it there. A policy doing exactly what it was designed
to do, and learning less for it, either meant the measurement was lying
or something real was hiding underneath, and I needed to know which. So
I went hunting: five controlled experiments. Four hypotheses died in
order: not the world's geometry saturating; not
starvation of the mapping gate (the curious arm actually mapped
*more*); not the mathematical shape of the preference; not a skew in
the action distribution. The experiment that settled it was a control
I'd recommend to anyone measuring exploration: a *content-free*
directed policy (the same statistical structure of directedness,
coupled to nothing about novelty). It scored neutral. Directedness
itself was harmless. The harm was the content: preferring novelty, as
such, was the mistake. And the mirror-image control drove it home: the
*inverted* preference (seek the familiar) beat random cleanly.

The interpretation isn't mysterious once the data forces it on you. In
a world where everything is learnable, novelty-seeking spreads your
finite experience as thinly as possible across the state space:
maximum coverage, minimum depth, a policy of guaranteed shallowness.
Concentrated practice, the thing novelty-seeking structurally prevents,
was the actual asset. Every hour of a finite life spent somewhere new
is an hour not spent getting good at something.

So the shipped drive became *competence*: prefer the familiar and the
mastered, weighted by how well prediction is going there. Practice
what you're getting good at. It passed T7 at both scales, the
project's first measured case of directed exploration beating random,
and it held up later on worlds built specifically to punish it.

> **Under the hood: the T7 record.** Reference scale, feature 002:
> curious vs random margin −0.006 ± 0.036, equivalence, PASS under the
> noninferiority criterion (which itself has a story: the planned
> sign-majority bar measured 3/8 and was found degenerate for
> continuous margins near zero, so it was replaced openly, raw numbers
> kept). Scaled (AGENCY-DIAGNOSIS): novelty-curiosity margin −0.062,
> better in 1/8, 87% directed actions. Content-free state-coupled
> control: +0.014. Inverted (familiarity) preference: +0.067, better
> in 6/8. CompetenceDrive (mastery + familiarity): +0.064 scaled,
> +0.027 reference, better in 6/8 at each: T7 PASS both scales.

## Two wrinkles, and the current edge

I could stop the chapter here and it would read like a clean win. It
would also be handwaving, and handwaving is the thing this whole project
exists to refuse. So, two wrinkles.

First: on worlds with mild non-uniformity, at these budgets, *nothing*
directed beats random by a detectable margin. Resolving that took real
statistical power: twenty-four seeds per configuration, where the
original protocol had eight. Directed exploration
pays where the world is sharply uneven (there, competence wins in a
strict majority of seeds at every horizon measured). Where the world is
gentle, the coin flip remains embarrassingly hard to beat, and anyone
selling exploration bonuses without saying so hasn't measured at power.

Second: curiosity didn't die; it got a successor. The deep problem with
novelty-seeking is that it can't tell "new because I haven't learned it
yet" from "new because it's unlearnable noise": both look novel, and a
TV of static is endlessly novel. The current edge is the *frontier*
drive: score places by whether prediction error there has been
*falling*. Is this somewhere I'm actively getting better? Unlearnable
regions read flat and score zero; mastered regions read flat and score
zero; the frontier of improvement scores high. Measured at full power
it works exactly as designed and, on worlds whose difficult regions are
best simply avoided, it wins nothing over competence. The worlds where
it should pay, worlds that change under a mastered policy, are named and
instrumented but not yet measured: a loose end I'll come back to rather
than a detour worth taking now. That's the frontier in both senses.

I'll resist drawing life lessons from a pile of simulation runs,
except to note the shape of the result, because it will be familiar:
chasing whatever glitters measured worse than doing nothing, and
deliberate practice at the edge of what's working measured best. Make
of that what you will, and hold it loosely: a far richer world is
waiting a few chapters ahead, and what happens there will force me to
take back part of this chapter's verdict. Chapter 13 is that story.

Part 3 is complete: triplets in, a tournament of frames over them, a
judge that can't be gamed, a price that sizes the structure, and a
fixed drive that aims the whole thing. What remains is the question the
book opened with: whether this actually buys learning that *lasts*.
Part 4 begins with the discovery that, for a while, it quietly didn't:
the frames that lived longest were rotting from the inside, and every
number in this part of the book was downstream of it before the fix.

[^homework-law]: Chapter 7, where the law earned its name.
