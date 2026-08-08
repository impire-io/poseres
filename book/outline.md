# Working outline

Parts follow the argument; chapters follow events. Each chapter lists its
beats and the real material it draws on (hq/04-JOURNEY episode numbers — episode 00NN = old chapter N — trail
docs). Beats are prompts, not sentences — the prose decides.

Status: working draft, 2026-07-18. Chapter count will move as drafting
reveals what merges and what splits.

## Part 1 — The problem

**01 · The brain in the freezer** *(drafted — calibration chapter)*
A robot vacuum that never learns the chair leg. How machine brains are made
today: study, then freeze. Why frozen
mostly works, and exactly when it breaks (world changes, task changes, body
changes). Why "just retrain" isn't learning. What I actually want: every
moment a lesson. The honesty promise of the book. Hook: ask for a brain that
never stops learning and two ugly failures appear.
Draws on: journey 0010 (positioning vs frozen intelligence).

**02 · Forget everything, or remember everything**
The two classic failures of continual learning. Catastrophic forgetting
explained with a kid-checkable example (cramming Spanish until French falls
out). Unbounded growth as the opposite disease. The afternoon my own
prototype demonstrated growth-without-bound — v3's population explosion —
and, worse, how it cheated its own report card so the numbers looked fine.
Draws on: journey 0002 (v3 caught red-handed; the four score exploits).

**03 · The question nobody answers**
Even if you fix forgetting and bloat, the hard question remains: how much
machinery does a brain need for *this* world? Nobody knows in advance — so
almost everyone pre-specifies it, and pre-specifying is quiet freezing. What
"structure" means, concretely (how many knobs describe your world). The
promise: a brain that discovers its own size. And the early result that made
this a real question: the first honest measurement said the system preferred
size 1 — for everything.
Draws on: journey 0003 (T-SCALE best_dim≈1, formally open).

## Part 2 — The triplet

**04 · Before, action, after**
The sensorimotor triplet: (what I sensed, what I did, what I sensed next).
Touching a radiator once. Why this is the only record of cause and effect a
body ever gets. Prediction as the test of understanding: you know what your
actions do when you can say what happens next. Everything the system will
ever learn arrives in this one shape.
Draws on: design docs 01/03; PRA-01.

**05 · Not words, not pictures**
Why this book barely mentions language models. A brain that reads every book
about swimming still can't swim. Causal understanding comes from acting and
being answered — the world grades you instantly and never flatters you.
Where language will re-enter later (Part 5 hook: a teacher is a world too).
Draws on: journey 0010 (non-goals: no language competition).

## Part 3 — The mechanism

**06 · A head full of rival guessers**
Frames: many small world-models, each betting the world can be described
with a different number of knobs. Spawn-and-select: keep making new
guessers, keep the ones whose predictions hold up. Evolution inside one
head, on a timescale of minutes. Why competition beats designing the one
right model (you'd have to know the answer to design it).
Draws on: design docs 03/04; journey 0001.

**07 · Never let it grade its own homework**
The chapter about cheating. All four ways v3's frames gamed their scores —
predicting in their own pet coordinates, grading only what they chose to
map, no price on complexity, an eviction bar that bent the wrong way — and
the v4 fixes. Then the later, subtler cheats: the training-stream EMA
(scoring yourself *while* practicing), caught by the fair judge. The
constitution that fell out: read the spread, not the mean; judge across
horizons; never self-graded homework.
Draws on: journey 0002, 0011 (fair judge); trail: THRESHOLD-DIAGNOSIS.

**08 · The price of a dimension**
Does the brain find the world's "true size"? The honest answer: no — and
that's the finding. The scale story compressed for the main text: collapse
at scale, six invisible constants, the climb back. Parsimony as a *price*:
selection buys dimensions while they pay for themselves. The measured
landing: price-optimal, stable, at every scale. The rover coda: a world
that's honestly 3–4 knobs, and the brain buys 2, because 2 is what the
error market will bear.
Draws on: journey 0004, 0009, 0011, 0014, 0020; trails: SCALE-, PROPOSAL-,
THRESHOLD-, SCORER-DIAGNOSIS.

**09 · Wanting things**
Drives. The system can't rewrite its own wanting (and why that's a design
choice, not a limitation). The curiosity story told straight: novelty-seeking
measured *worse* than random wandering; four wrong explanations refuted;
the inverted preference winning; competence (practice what you're getting
good at) as the first measured net-positive drive. The frontier drive as
the current edge. Kids will recognize all of this from their own practice
habits.
Draws on: journey 0005, 0007, 0018, 0024; trails: AGENCY-, BLEND-,
PREDLP-DIAGNOSIS.

## Part 4 — The continuity guarantee

**10 · The brain that almost stopped learning anyway**
The rot story — the best chapter-length argument that continuity is hard
even after you've designed for it. Frames that learned forever slowly
poisoned themselves (weight growth), the ecology started selecting for
rot-resistance instead of quality, and every earlier number was downstream
of it. The cap that fixed it without freezing anything. Why "never frozen"
has to be defended, not declared.
Draws on: journey 0013, 0014; trails: SCORER-, LONGEVITY-DIAGNOSIS.

**11 · No scrapbook required**
Versus replay-based continual learning: no stored past, no rehearsal
budget. What the system keeps instead (running structure, not episodes) and
what that buys: memory that doesn't grow with lifetime. Honest limits
stated: what is lost without a scrapbook, and where snapshots (a different
thing: pausing, not remembering) fit in — including the one-ULP resume bug
as a story about what "exactly the same" costs.
Draws on: journey 0006, 0023.

**12 · Watching it learn**
The proof of life a reader can run: `pra-rover`, install to watching in
five minutes. What the falling error curve and the breathing population
mean. Mounting other worlds: CartPole through one seam, a Gazebo rover
over ROS2, worlds that can never restart. The honest boundary: where
determinism ends (free-running robots) and why the project says so out
loud.
Draws on: journey 0019, 0020, 0021, 0026.

## Part 5 — The long run

**13 · The log it put back** *(drafted 2026-08-08)*
The multi-week Minecraft run (`c1c`), pre-registered and read: the setup
and the bar (chance ≈ 0, any craft = emergence), the week-1 material era
(449 digs, one mined oak log held four minutes and placed back), the
clean null on the headline (zero offers in 5.67M steps), why the frontier
drive abandons what it masters, the disk-full incident on the observer's
side, and the three lessons (detectors not visits; exploration is not
accumulation; pre-registration makes a null publishable).
Draws on: journey 0068 (plus 0050–0054); C1-RUN-PLAN.md; C1C-JOURNAL.md.

## Part 6 — Teachers (parked — premise re-arbitration pending, see REVISIT.md)

The self-set-goals topic was probed and parked with an existence proof
(journey 0054–0058); these chapters stay design until that re-arbitration.

**14 · A teacher is a world**
The reframe: feedback from a mentor is a triplet too (my attempt, their
response, my updated state). Multiple teachers as multiple streams into one
brain — and the measured foundation that makes this more than a metaphor:
N worlds already feed one brain safely (merged experience matches focused
experience). What is validated ends exactly there; the rest of this part is
design.
Draws on: journey 0022 (multi-stream measured); design horizon notes.

**15 · What would make it true**
The claims — pre-train on language, specialize to a profession, keep
improving — stated as hypotheses with their falsification conditions, the
way this project states everything. What experiments come first, what
failure would look like, and why the book ends on an open question on
purpose. This project's record says directional bets sometimes lose to
random; Part 5 gets no exemption.
Draws on: the recurring principles (hq/00-GENESIS/how-we-work.md); the vision's horizon ambitions (hq/00-GENESIS/vision.md).

## Not scheduled yet, parked

- Appendix candidates: the eight scale rules as a reference table; the
  T1–T7 acceptance suite in plain words; a reading guide to the trail docs.
- A possible interlude between Parts 3 and 4: "How I work" — spec-first,
  pre-registered criteria, amend-openly — if it earns its place.
