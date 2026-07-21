<!-- Draws on: journey 0004 (six scale rules, patience dose–response, medians
     8/10.5/9.5), journey 0009 (climbing ratchet, two-caste census), journey 0011 (conveyor
     correction, 24/24 anchored 6/8/8.5), journey 0014 (weight cap lift → 10/9/9;
     parsimony-as-price retirement, 0.0067/dim crossing), journey 0020 (rover:
     3–4-dim latent, lands at 2). Trails: SCALE-, PROPOSAL-, THRESHOLD-,
     SCORER-, LONGEVITY-DIAGNOSIS. Numbers as of 2026-07 measurements. -->

# The price of a dimension

Chapter 3 ended with the engine reporting that every large world had one
dimension. This chapter is the account of what it took to get an honest
answer instead, and of the discovery at the end that the question I had
been asking was itself wrong.

## Nothing was broken

The natural assumption, staring at "best_dim ≈ 1" on a 20-dimensional
world, is that something is broken. Some component has a bug; find it, fix
it, done. Months of measurement said otherwise. Every component was doing
exactly what it was designed to do. The problem was that it had been
designed, tuned, and validated in a world of true dimensionality 3 with
ten observation channels. Half a dozen constants in the system were
quietly *about* that world without anyone having said so.

An example makes the pattern clear. Newly spawned frames get a protected
childhood of a fixed number of cycles before eviction can touch them. At
the reference scale, that window was long enough to train a candidate to a
fair reading. In a 60-channel world the same window ends long before a
large frame can converge, so candidates were being judged on their
half-trained transient and evicted. The filter this imposes is
dimension-dependent: small frames train fast enough to pass it; large
ones never get the chance. Lengthen the patience stepwise
(2, 12, 24, 29 cycles) and the discovered dimensionality climbs stepwise
with it (means 4.7, 5.7, 6.7, 10.7). A dose–response curve like that is
as close as this kind of work gets to proof of mechanism.

Six constants turned out to have the same disease: sensible at the
reference, silently wrong at scale, each one masking the next. The
learning rate diverged first and hid everything behind it. The world
itself was distorting: the emission function saturated at high
dimensionality, so a scaled run wasn't even testing the same kind of
world (that one was a bug in my measuring instrument, not in the system).
The initial weight scale saturated newborns. The linear complexity
penalty, tuned against reference-scale error spans, overwhelmed the
flattened spans at scale. And so on down the stack.

The repair discipline mattered more than any single fix. Every corrected
constant became a formula that evaluates to exactly the old value at the
reference scale (factor 1.0, bit-for-bit), so the validated behavior
could not regress while the scaled behavior was being repaired. After the
six: medians of 8, 10.5, and 9.5 discovered dimensions on worlds of true
size 20, 35, and 50, with one run climbing to 18. Not the right numbers
yet, but no collapse anywhere, and a conclusion worth stating carefully:
the structure-finding mechanism survives scale; what doesn't survive is
the *rate* at which it converges within a budget.

> **Under the hood: the six scale rules.** (1) Emission pre-activation
> normalized by `sqrt(true_dim/3)`: without it, 65% of channels saturate
> at td=20 vs 18% at reference. (2) Effective learning rate scaled to
> obs_dim (the binding constraint; divergent at obs=60). (3) Init scale
> normalized so newborn pre-activations stay in the linear regime.
> (4) Parsimony weight rescaled to the compressed error span.
> (5) Maturation patience scaled to convergence time. (6) Spawn/eviction
> pacing scaled with patience. Every rule is reference-preserving:
> factor exactly 1 at `true_dim=3, obs_dim=10`, verified byte-identical.
> Trail: `hq/02-DESIGN/validate/SCALE-DIAGNOSIS.md`.

## The system deceives me twice more

The remaining gap looked like a search-speed problem, and a measurement
confirmed it: selection at scale was wasting proposals, not failing to
reach. Forbid proposals at or below the current best (always climb) and
the fixed-budget result doubled. For a few days the climbing policy looked
like the answer. Four seeds reached 18–20 on a true-20 world in the short
protocol.

Then the full-length run, the protocol v3 forced on me, caught it: at
2000 cycles the climbers had ridden past 20 and up to 62–74: the
observation width, the ceiling of the representation, nothing to do with
the world. The short result had been another lucky horizon. The census
instrument explained the mechanism: the scaled ecology had split into two
castes. A standing conveyor of youth-protected juveniles, reborn faster
than they could mature, and a mature niche that only the smallest frames
could enter, because the survival bar sat below what any larger frame
could score at maturity. Under the climbing policy the mature niche was
simply empty (the census counted 29 juveniles, zero adults), and
"best_dim" was tracking the proposal generator, not the world.

The conveyor also explained a subtler wrong number. The survival
threshold scales with population size, and the population it was counting
included those unevictable juveniles: frames that tighten the bar for
everyone else while being untouchable themselves. Correcting the count to
exclude the conveyor is a one-line, constant-free change, and it was the
second half of the coupled pair from chapter 7: fair judge plus corrected
bar. With both in place, all twenty-four scaled runs (eight seeds at
each of the three sizes) anchored: a long-lived resident frame in every
single run, populations self-limited, and the discovered dimensionality
finally invariant to budget and to the proposal policy. One more fix
(a frame-aging problem that is chapter 10's story) lifted the final
landing to its measured value: medians of 10, 9, and 9.

## Ten is not twenty. The reason rewrote the question.

Ten, on a world whose true size is 20. Nine on 35, nine on 50. After a
year of removing every dishonesty I could find, the honest system lands
at half the truth or less. The *reason* turned out to be the most
useful thing this project has produced.

With every distortion gone, I could finally measure the thing directly:
train frames of every size for a long time, honestly, and plot error
against dimensionality. The plot has no elbow at 20. Error just falls,
smoothly, all the way to the capacity ceiling: each added dimension
buys a smaller improvement than the one before, with no feature marking
the "true" size at all. In hindsight the reason is geometric. This
world's observations are a *nonlinear* image of its 20-dimensional
latent, and under a nonlinear map that image is simply not a
20-dimensional object; there is no elbow for any analysis to find.
The truth I was asking selection to find leaves no signature in
the error surface. It cannot be found, by this system or any other,
because as a feature of the data it isn't there.

So what is the parsimony term actually doing? It's a price. Each
dimension costs a fixed fee, and selection keeps buying dimensions while
the marginal error improvement exceeds the fee, then stops. On the
scaled worlds the measured crossing point, where another dimension
stops paying for itself, sits at dimensions 8 to 12. The system lands
at 10. It isn't failing to find the truth. It is sitting exactly at the
optimum of the trade it was actually asked to make, and it holds that
optimum stably at every scale and every budget I've measured.

> **Under the hood: the price arithmetic.** Long-horizon honest error
> falls monotonically in dim (both components, both probe seeds; 4×
> training moves the honest minimum to dim 28 and deepens it: the
> surface is experience-limited, not structure-limited). The shipped
> parsimony weight prices a dimension at 0.0067 of normalized error;
> the measured marginal gain crosses that price at dims 8–12; the capped
> ecology's landing is 10. "Does best_dim track true_dim at scale" is
> closed by measurement: it cannot and should not. What T-SCALE
> certifies instead: selection lands at the price-optimal
> dimensionality, stably, at every scale and budget. Trails:
> `SCORER-DIAGNOSIS.md` (epilogue), `LONGEVITY-DIAGNOSIS.md`.

I resisted this conclusion for a while, because it sounds like moving the
goalposts after missing the shot. What convinced me is that the same
behavior shows up where I *can* check the intuition. The rover world of
Part 4 has a latent state of three or four dimensions: position and
heading, physically interpretable. The brain lands at two, run after
run. Two is wrong as an inventory of the rover's physics. Two is right
as an answer to the question the rover's sensor stream actually poses at
that budget: pay for a third dimension and it does not return its fee in
prediction.

And that, I now think, is the honest shape of the question this project
began with. Chapter 3 asked how a brain can discover its world's true
size. The measured answer is that "true size" is a property of worlds
seen from outside, by someone who built them. From inside, from a
stream of triplets and finite experience, there is only *worthwhile*
structure: the dimensions that pay their way. Every real learner,
including the reader, is in the same position. The map is not sized to
the territory. It's sized to the mapmaker's budget, and that isn't a
compromise; it's the only version of the question that was ever
answerable.

The tournament, the judge, and the price: the mechanism is now complete
except for one part. Nothing yet says why this brain does anything at
all: why it moves, what it practices, what it seeks out. That's the
drive layer, and its story includes the project's most instructive
failure: the day curiosity measured worse than doing nothing in
particular. Chapter 9.
