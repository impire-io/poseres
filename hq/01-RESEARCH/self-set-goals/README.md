# Does the brain set goals for itself, or only follow a drive?

**State:** active
**Where it stands (2026-07-24, night):** E2.0h REGISTERED — the owner
picked fork option (ii), the horizon read: is the 2-in-42 chain rate at
H = 5,000 a floor that climbs with an 8× window? Frozen: PASS iff
≥ 6/24 graduates chain by H = 40,000 (E1's own k) with growth beyond
C(5,000); FAIL iff ≤ 2. The instrument must first re-prove itself (P0:
the rebuilt runner reproduces E2.0's recorded confirmatory — the
originals were scratchpad-only per convention). Earlier same day: E2.0
MEASURED — the dwell gate **FAILs at power** (0/24 at 20%; λ-bias
orbits, doesn't hold) so the goal-object-via-λ approach paused per its
own reversal — **and the gate's context rows hold the project's first
deliberate crafting chains** (2 full log→planks→sticks across 42
goal-biased runs; frontier-alone: zero in the entire measured record).
E1 FAIL at power (teaching alone doesn't move the hands). E0/E0b
(2026-07-23): premise + frontier anti-idle confirmed.
**Started:** 2026-07-22
**Origin:** a friend (ex-Willow Garage) asked what the brain has *as goals* —
curiosity is an inner drive, but does the brain ever set itself a target and
pursue it? Humans do. This topic is that question, held against the code.

## Abstract

Drives are innate and frozen; a goal is transient and self-set. The code
today has only drives — every deliberate step is a one-step greedy
hill-climb with no held target. This topic asks whether goal-setting
machinery (and the teacher model it drags in) is the missing ingredient for
directed multi-step behavior — held against the measured fact that the C1
crafting chain's chance floor is ≈ 0, so any deliberate chain is
unmistakable. A decisive answer either authorizes the goal build (E2),
shows taught knowledge + intrinsic drives suffice (E1), or — should the
live null arm ever craft on its own — dissolves the premise entirely.

> This is a **capture for review**, not a pre-registration. The two
> load-bearing decisions — *what a goal is made of* and *the pass/fail bars* —
> are deliberately left open per the working agreement (no locking a
> direction-setting call with one model before an adversarial pass).

## What the code says today

Every deliberate step is a **one-step greedy hill-climb** on the drive
landscape (`src/pra/action/policy.py:88`, `CuriosityLookaheadPolicy`):

```
for each possible action:
    predict the ONE observation it leads to   (best-frame transition model)
    score that observation with the drive set (engine.py:357, _value_of)
pick the argmax
```

Horizon = **exactly one step**. There is no object anywhere representing a
target the brain isn't already next to, no commitment held across steps, no
distance-to-goal. **Drives, yes; goals, no.** The brain re-decides from scratch
every tick and walks toward whatever looks most interesting *right now*.

**Goals are not a drive.** Drives are innate and constitutionally
un-self-modifiable (`drive.py:1-9`, Doc 05 §6). A goal is the opposite kind of
object: transient, self-set, meant to change. It belongs at the **Policy seam**
— the same swappable slot that let competence and frontier ship without frozen-
core edits. A `GoalDirectedPolicy` sits beside the lookahead policy; no core
edits. This keeps the whole idea inside the constitution.

## The core idea (the mature loop)

Curiosity isn't *replaced* by goals — it becomes the thing that **generates and
grades** them. Drive → proposes candidate targets → commit to one → pursue it
across many steps → outcome (did I get better at reaching targets like this?)
feeds back into which targets are worth setting. This is the
"intrinsically-motivated goal exploration" line (Oudeyer/Forestier) — worth
naming for the friend.

The frontier drive is already most of the grading machinery: "reward where
error is *falling*; go silent where it's flat (mastered **or** impossible)."
Lift it from observations to goals and you get **goal selection *and*
abandonment from one principle** — no special-case give-up timer.

## Hard problem 1 — what a goal is made of (the shift-invariance landmine)

If a goal is "make the senses read *these exact numbers*," a world **shift**
(same meaning, moved/relabeled — see the shifting/multiregion worlds) makes it
unreachable or a lie: those numbers now name a different situation. Six
consecutive arcs (place-memory 019 → election-stream 025) died on exactly this
— raw-observation anchors are not shift-invariant. **A goal defined on raw
observations most likely inherits that death.** Defining a goal representation
that survives the world moving is the crux and the first place this dies.

## Hard problem 2 — deadlocks in a non-resetting world (the spoon)

A baby wants to eat with a spoon, drops it; the world does **not** reset. Three
*distinct* problems people usually blur:

1. **Abandonment** (internal, cheap) — stop pursuing a goal whose
   progress-signal is flat. Falls out of the frontier principle lifted to goals.
2. **The deadlock** (external, hard) — the spoon is on the floor and the world
   is in a worse, un-undoable state. Abandonment stops the *wanting*; it doesn't
   *recover the spoon*. Routes: (a) learn **reversibility** (model what can be
   undone, treat irreversible actions with caution); (b) the world is forgiving
   (fetch another log — Minecraft usually lets you). The forgivingness may be
   doing quiet load-bearing work.
3. **The teacher** (the reframe) — a baby never learns the spoon alone in a
   never-resetting universe; a parent resets it a hundred times. That external
   reset is a *feature of the learning environment*, not proof of failure.
   "Fully autonomous learner in a world that never resets" may be the wrong
   model. The vision already reserves a gated **teacher-world**
   (`hq/00-GENESIS/vision.md:56`) — this spoon question may be what makes
   "what minimal teacher does the brain need?" a concrete fork.

### Teacher model (owner's principle, 2026-07-22, rev. 2)

> Rev. 1 said "a teacher writes to knowledge, never to goals." The owner
> corrected it: a real teacher *does* set goals ("using logs, make a stick")
> and follows up. What a teacher must never touch is the **drive**, not goals.
> This rev. supersedes it.

**The teacher's job is twofold:** (1) show the mechanism through concrete
examples (demonstration → knowledge), and (2) set a goal and follow up on it
(a transient suggested goal + a completion signal).

**Corrected invariant:**

> A teacher may **suggest** a transient goal and **give feedback** on it —
> writing to the goal-suggestion and completion-signal channels — but may
> **never** write the intrinsic drive.

Why it stays coherent with autonomy:

- **No privilege.** A teacher-suggested goal is a *candidate*, valued by the
  same intrinsic machinery as self-generated goals, and just as **abandonable**
  — flat frontier progress drops it even though the teacher set it. Teacher
  proposes; the drive disposes.
- **Landscape, not drive.** The learner elects the taught goal for its *own*
  reasons: the demonstration makes the goal *learnable*, which makes it the
  highest-frontier option. Good teaching arranges the world so curiosity flows
  to the lesson — it does not coerce interest. The two halves reinforce.
  > **Refuted for realized-progress drives [measured, E1 2026-07-24]:** the
  > frontier goes silent on mastered ground, so demonstration makes the
  > lesson the *least* interesting region after the guided phase — the
  > graduate flees the workshop. The claim survives, if at all, only for a
  > drive that values *prospective* reachable progress. See *E1 outcome*.
- **Follow-up patches the graveyard.** A teacher's "that's a stick — yes" is an
  external, *un-confounded* completion signal — exactly the "did I succeed / am
  I stuck?" detector the seven arcs could not build from inside (the confound).
  The teacher bootstraps it; the learner learns to *predict* the verdict and
  internalizes it. **Outgrowing a teacher = knowing you succeeded without being
  told.**

**Outgrowing the teacher is the success criterion, not a complication.**
- *Weak (tractable):* recombine taught mechanisms into goals no teacher assigned.
- *Strong (holy grail):* discover a mechanism no teacher had.
- Possible **only because the drive is intrinsic and frozen** — a purely
  externally-rewarded agent can never outgrow its teacher (no reason to go where
  the teacher didn't point). The founding bet *is* the outgrowing engine; the
  teacher idea depends on it rather than fighting it. Cousin of **seeding**
  (028: measured relevant transfer, never dictates goals); lineage =
  Willow-Garage learning-from-demonstration (imitate the *how*, not the *what*).

**Failure mode to design against — dependence.** Training wheels that never come
off: if teacher-goals/feedback dominate, self-generation atrophies and the
learner never outgrows. The scaffold must **fade** (Vygotsky's zone of proximal
development). Concretely a knob: weight on teacher-suggestions, and whether it
decays.

> **Owner confirmed (2026-07-23):** the adversarial pass's λ reframe stands —
> teacher privilege exists, *bounded and fading*, rather than "no privilege."

### The two doors (owner's distinction, 2026-07-23)

The owner: guiding the **body** and guiding the **brain** are two different
things a teacher can do — body-guidance for physical skill, brain-guidance for
abstract/conceptual content (math, language). Architecturally this maps onto
the only two ways into a brain — there is no third door:

1. **The senses** (door 1): experience through the body's channels.
   Body-guidance teaches here — the teacher drives experience, the brain learns
   it the way it learns everything. *Apprenticeship.*
2. **Birth** (door 2): **seeding** (028) — the one legal direct brain-write,
   measured (relevant transfer, not maturity, survives resize), never touching
   the drive. Brain-guidance teaches here — knowledge arrives as inherited
   structure, without the lived fumbling. *Book-learning.* For abstract content
   (where even human demonstration is already symbolic), donated structure is
   the honest current analog — until language-as-a-world (the vision's gated
   horizon) gives teachers a symbol channel through door 1.

**The invariant holds at both doors: either door writes knowledge; neither
writes the drive.**

Consequences for the ladder — E1 splits into paired arms:
- **E1a — guided body** (apprenticeship): scripted teacher drives the body
  through the chain; brain untouched.
- **E1b — donated brain** (book-learning): learner seeded at birth from a donor
  that lived the chain (existing 028 machinery; same anatomy, no resize).
- **Blank control.**

**Frozen prediction (owner's hypothesis, registered before any run):** for this
*physical* chain, E1a ≥ E1b, both > blank. If E1b matches E1a, inherited
knowledge equals lived experience even for physical skill — surprising, and
the number decides.

**Teacher lineage:** E1a's graduate is E1b's donor — the guided apprentice
becomes the master whose brain seeds the next learner. Compounding
intelligence (the vision ambition) appearing as teaching, unprompted.

**Honest caveat:** *detecting* deadlock ("the world stopped responding to me")
is exactly the stasis-detection this project keeps finding HARD — election-
stream's killer was that the drive's own stillness looks like real signal.
"Am I stuck?" is not a cheap sensor.

## Do we need to solve the shift-invariance graveyard first? No — goals are its cure

Read `hq/02-DESIGN/validate/ELECTSTREAM-DIAGNOSIS.md` (the last of seven arcs).
The documented root cause is **not** "too few knobs," "misread raw signal," or
"too few event sources" — it is a **confound** [documented, ELECTSTREAM
Outcome §1–2]:

> "the detector's background is the brain itself… Every family failed on
> confounded evidence — 'the world changed' vs 'I changed where I go / who I
> am.'"

The train illusion: you can't tell if the next train or *you* are moving by
looking harder out the window — the view is identical. Every *passive* signal
mixes "world shifted" with "I moved / my frames aged," and no statistic un-mixes
it after the fact (robust across 4 statistic families, 3 representation spaces,
3 shift worlds). Mapped to the three hypotheses: (a) NO — robust to world dials;
(b) partial, not root — any passive read is confounded; (c) closest, but the
issue is *contamination by self-motion*, not source count.

**The successor the numbers name is active probing** — "deliberately re-visit
mastered ground under a held policy and re-test." *That is a goal.* So the
graveyard didn't die pointing nowhere; it died pointing at goal-directed active
probing. **Goals are not blocked by the shift problem; goals are the tool it
concluded it needed.**

Sequencing that falls out:
1. **Experiment #1 = crafting on the stable FakeBridge world** — no
   shift-detection involved; sidesteps the whole graveyard.
2. Shift-detection returns later as a *downstream application* of goals (active
   probing), never a prerequisite.
3. The only graveyard reach into goal work is **representation** (Hard Problem
   1): a goal that must *survive a shift* needs a shift-robust anchor — but a
   crafting goal in a stable world does not. Stable-world crafting first;
   shift-durable goals much later.

## The testbed already exists

The FakeBridge Minecraft world has the crafting chain (wood → planks → sticks)
and a **measured chance baseline ≈ 0** — a reactive one-step walker almost never
assembles the chain by accident. So the natural offline gate is: **does a
goal-setting agent hold the multi-step chain together where the one-step
hill-climber can't?** This also speaks directly to C1's emergence bet.

## Open questions for the Fable 5 adversarial pass

1. **Goal representation** — raw obs (dead on arrival?), a learned latent, a
   *relational/feature* target, or a predicted-error target? What survives a shift?
2. **Commitment vs. re-decision** — does a goal bias the existing one-step
   lookahead toward a target, or drive a real multi-step plan (compounding
   model error is a known risk)?
3. **Goal generation** — where do candidate goals come from? Sampled from
   memory? From frontier regions? Imagined by the world model?
4. **Deadlock/teacher scope** — is a teacher/reset in scope for the first
   experiment, or do we lean on Minecraft's forgivingness and defer it? (See
   *Teacher model rev. 2*.) Sub-questions: how does a teacher-suggested goal get
   *represented* alongside self-generated ones; does the fade-knob decay, and by
   what rule; and what is the concrete **test for outgrowing** (weak =
   self-generated goal past the taught set; strong = self-discovered mechanism)?
5. **The bar** — crafting-chain completion rate vs. the reactive policy on the
   FakeBridge testbed? At what margin, how many seeds, what horizon?
6. **Is this even the next frontier?** — steelman the null: curiosity-alone at
   C1 scale might yet produce directed chains; goals might add nothing. What
   would show that *before* we build?

## Adversarial pass (Fable 5, 2026-07-23)

Verdicts on the draft's load-bearing claims, argued against the code and the
measured record — not against the draft's own summary of them.

### BREAKS — "goals slot into the policy seam" hides the real wall

The seam is swappable [documented: `policy.py`], but the shipped lookahead
values exactly ONE predicted next observation (`engine.py:357`). A goal object
plus a one-step bias is *greedy descent on distance-to-goal* — and the
honest-primitives chain is (deliberately, 031/033) gradient-free at one step:
~10+ ordered actions (dig as held intention → `hold_next` → `grid_put` exactly
one log → offer → `take_result` → re-stage two planks adjacent →
`take_result`), most changing nothing any goal-distance metric can see, with
traps (a second log kills the offer) [documented: 0050 + `anatomy.py`].
**A goal object without multi-step machinery is decorative.** The real build is
one of: (a) multi-step rollouts over frame models (compounding error), (b)
means-ends/backward chaining over learned action effects, (c) learned skills.
Each is a Doc-05-level design; none is "nearly free." Likewise "abandonment
falls out free" overstates: goal-progress needs *per-goal-attempt* bookkeeping
— a NEW state surface with Doc 06 snapshot obligations, not the existing
per-visit error history [mechanism-argument].

### BREAKS (internal contradiction) — "no privilege" vs "the goal changes behavior"

If a suggested goal enters with zero weight and only intrinsic valuation
counts, the goal object is **inert** — that's just the frontier drive again; no
machinery needed. For a goal to matter it must carry weight (λ) beyond
intrinsic value — **which is privilege**. The honest version: goals are
privileged by a *bounded, fading* λ; the design question is λ's size and decay
rule, never whether privilege exists. Rev. 2's elegance ("demonstration makes
the goal highest-frontier, so the learner elects it") actually describes
teaching **without any goal channel** — pure landscape-shaping. The draft
conflates two separable mechanisms: **(A) demonstration → knowledge** (needs no
goal object at all) and **(B) suggestion + λ** (needs everything). (A) is
testable first and alone.

### TENSION RESOLVED — the completion signal's only legal consumer is a *sensor*

Where does "that's a stick — yes" GO? Wired into valuation it is external
reward — the founding bet forbids it; the drive is frozen. The resolution that
survives: **the teacher's verdict is an observation channel** — part of the
world, predicted by the frames like any other channel. Then internalization
falls out of existing machinery: when the brain predicts the verdict before it
arrives, it knows it succeeded without being told — **outgrowing, mechanized,
at zero new cost**. "Teacher as channels in the world" is literally the
vision's gated teacher-world. Caveat: prediction ≠ pursuit; *caring* still
requires λ (previous item) [mechanism-argument].

### OVERSTATED — "goals are the graveyard's cure"

Active probing needs a policy **held fixed** through the probe window —
commitment strong enough to temporarily override the drive: the *strongest,
riskiest* form of goal machinery (the dependence knob at maximum). A λ-biased
valuation does not give held-policy probes. Goals are a *prerequisite* of the
cure, not the cure. Sequencing unchanged; claim softened.

### SURVIVES (stronger) — the testbed choice

Pocket/hand/grid channels are cumulative and semantic-by-label; "offer
present," "count > 0" are directly observable and **un-confounded by
self-motion** — goal-completion here does NOT inherit the graveyard confound
[mechanism-argument over `anatomy.py`]. And the bar is measured and brutal:
one accidental planks in 8×275 undirected steps, **zero sticks** [measured,
0050]. Any deliberate chain is unmistakable.

### SURVIVES (stronger) — the teacher model fits the body better than the draft noticed

The property body (033) has **no material classifiers** — a teacher goal "make
a stick" cannot even be *expressed* as a category to this body. A teacher goal
must be **ostensive**: shown, not named — a demonstrated chain, a target
signature. The classifier-free body *forces* teaching toward
learning-from-demonstration, which is exactly the owner's two-job teacher
model. The body decision and the teacher model were made independently and
agree [mechanism-argument].

### FOUND — the null arm is already running (open question #6)

c1c is frontier-alone in the live world [documented: 056af43]. **The null
experiment costs nothing — it is the current run.** Discipline: pre-register
the prediction BEFORE peeking at crafting telemetry. Prediction (frozen now):
frontier-alone produces stick-family crafting at ≈ the measured accident rate
— i.e. ~zero deliberate chains — over the run's horizon. If c1c *does* craft
chains, the premise weakens and this topic pauses (the standing reversal
condition, now with a concrete read).

## The ladder (PROPOSED — bars open until the owner sets thresholds)

Cheapest falsification first; each rung builds only if the one below
fails/underdelivers; X0 at any rung is data.

- **E0 — the free experiment.** Pre-registered read of c1c crafting telemetry
  vs the 0050 chance rate. No build. (Prediction frozen above.)
- **E1 — demonstration only, no goal object** (two-door form, see *The two
  doors*): paired arms **E1a** guided body (scripted teacher drives the body;
  brain untouched) vs **E1b** donated brain (seeded at birth from a donor that
  lived the chain; 028 machinery) vs **blank**; then intrinsic drives run
  alone. Question: does taught knowledge + existing drives reproduce chains?
  Candidate bar: ≥1 full log→stick chain in ≥ k/24 seeds within horizon H, vs
  0 in blank paired arms. Frozen prediction: E1a ≥ E1b > blank.

  > **Arm dissolution (owner's call, 2026-07-24, before any run):** at plan
  > time the mechanism argument showed E1a/E1b collapse — 028 seeding is a
  > full-state resume and E1b's donor IS E1a's graduate, so both arms hold
  > byte-identical brains at the free-run boundary; only the world could
  > differ, making the comparison either empty (fresh world = identical
  > runs) or confounded (teacher-depleted world = material handicap). E1
  > runs **two arms: taught vs blank**. The E1a ≥ E1b half of the frozen
  > prediction is recorded as **untestable with current machinery** (not
  > wrong, not dropped); partial/structural transfer — inherited structure
  > without the lived episode — is the named successor that would make the
  > two-doors contrast testable. Taught > blank stands as the primary and
  > is what E1 decides. Dose (owner-set, same day): **45 demonstrations /
  > ~1,012 guided steps** as 45 fresh-world single-chain segments (the
  > 15×3 sketch traded for tape determinism, dose unchanged). Spec:
  > `specs/034-two-doors/spec.md`.
- **E2 — goal object + bounded fading λ** (only if E1 fails): suggestion
  channel + λ + ONE of the multi-step mechanisms (a)/(b)/(c) — that choice is
  its own registered decision.
- **E3 — teacher loop:** verdict-as-sensor + follow-up; internalization test =
  verdict-prediction accuracy rising while verdict-delivery fades (the
  outgrowing measurement, weak form).

Evidence-class audit of this whole topic: [measured] = the 0050 chance
baseline, the 028 seeding transfer; everything else here is
[mechanism-argument] or [judgment]. Per the working agreement, only the ladder
turns the arguments into numbers.

## Pre-registered bars (REGISTERED 2026-07-23, before any c1c telemetry read)

> Numbers proposed by Fable 5 at the owner's explicit delegation ("your
> guess is better than mine when it comes to setting k and H") and
> registered/committed **before** opening the S3 archive. The only c1c
> facts known at registration: step count ~340k (owner-reported) and the
> boot-time observations already in ep. 0053.

### E0 — the free experiment (c1c read)

**Body correction that sharpens the read:** the "1 accidental planks per
~2,200 steps" rate is the *031* body's [measured, 0050]. c1c runs the
**033 property body**, whose measured chance floor is ≈ 0 — 0/8 pilot
seeds completed even one *dig* by chance (max 1 of 3 ticks) [measured,
0052]. Under the frozen prediction we therefore expect **zero planks and
zero sticks** at ~340k steps — not "some planks." Any crafting at all is
above chance; under this body planks is already a multi-step chain (held
dig → hold_next → grid_put → take_result).

- **Window:** the full c1c run, step 0 through the latest archived step at
  read time (must be ≥ 300,000 steps; it is).
- **Primary counts:** (a) planks-creation events (planks signature count
  rises in the pocket/ground-truth view), (b) stick-creation events,
  (c) full log→planks→sticks chains.
- **Decision rule:**
  - 0 sticks AND ≤ 1 planks event → prediction holds; premise stands;
    **build E1**.
  - ≥ 1 stick, OR ≥ 2 planks events, OR ≥ 1 full chain → the reversal
    condition fires: frontier-alone is producing directed multi-step
    crafting; topic **pauses**, no build.
  - Exactly 1 planks event → fluke-consistent (0050's one-in-2,200
    spirit); premise stands *flagged*; re-read at +250k steps.
- **Context rows (no bar):** dig successes / log acquisitions,
  offer-present events. The drive may legitimately elect digs — material
  acquisition is not crafting and does not fire the reversal.

### E0b — the 0053 anti-idle read (same telemetry pull, separate question)

Ep. 0053 froze this reversal before c1c matured; folded in here so one S3
pull answers both. Over the **last 10,000 steps** of the window:

- idle share **< 20%** (prediction: well below competence's 26.7%);
- no single action ≥ 50% of steps (the frontier-degeneracy clause);
- otherwise the 0053 reversal fires: frontier-alone refuted for Minecraft
  → escalate per 0053 (curiosity+frontier blend, or scheduled probing).

### E1 — k and H (built only if E0 upholds the premise)

- **Seeds:** 24 per arm (project-standard power); arms E1a / E1b / blank.
- **Horizon H = 5,000 free-run steps** per seed on the FakeBridge world
  (E1a: after the guided phase ends; E1b and blank: from birth).
  Rationale: a directed chain is ~10–20 steps, so H gives ~250× slack for
  election and fumbling; the ≈0 chance floor means a generous H cannot
  inflate a false PASS, while a stingy H risks a false FAIL that sends us
  into E2's heavy build — the expensive error.
- **PASS bar k = 6: ≥ 6/24 seeds** complete ≥ 1 full log→planks→sticks
  chain, AND blank = 0/24. (Any nonzero blank re-opens the 0052 baseline
  and voids the read.) Rationale: with chance ≈ 0 any nonzero count is
  statistically unambiguous; 6/24 separates "taught knowledge reliably
  re-elects the chain" from a single-seed fluke, without a bar so high
  that noisy-but-real teaching fails us into building E2 unnecessarily.
- **Ordering read (frozen prediction E1a ≥ E1b > blank):** judged on
  per-arm seed counts; descriptive unless both taught arms clear k.

## E0 + E0b outcome [measured, 2026-07-23]

Read executed the same day the bars were registered (commit 11725f1), against
the full S3 archive `pra/v1/c1c/` (first archive-read tooling; gzip-JSONL,
deduped by seq). Window: the whole run, **328,560 archived steps** (one boot,
zero restarts, run live since 2026-07-22 17:23 UTC).

**E0 — crafting (ground-truth `tele.view.live`):**

- planks events: **0**. stick events: **0**. full chains: **0**.
- Deeper than predicted: **not one log ever entered the inventory.** Items
  ever held in ~328k steps: dirt ×1, leaf_litter ×22, wheat_seeds ×1.
- The drive *does* dig — 6,548 records with digging>0, dig_ahead 4.7% of all
  steps — but digs ground cover, never completes a tree. A sensed crafting
  offer was present on **0 steps** of the entire run.
- **Decision rule: 0 sticks AND ≤1 planks → prediction holds; premise
  stands; build E1.** The 0052 chance floor is honest at scale: 328k
  frontier-driven steps produced zero material-chain progress. Whatever E1's
  taught arms produce sits on a measured floor of zero.

**E0b — anti-idle (tele.step, last 10,000 steps):**

- idle share **3.1%** (bar < 20%; competence camped at 26.7%) — an ~8.6×
  drop, below even the uniform 8.3% cold-start share: frontier actively
  disfavors stasis.
- top action `forward` **35.7%** (bar < 50%) — no degeneracy; the remaining
  mass is spread near-uniformly across all 11 other actions.
- **The 0053 reversal does NOT fire.** Frontier-alone stands for Minecraft;
  no escalation to blends or scheduled probing. This closes ep. 0053's
  "anti-idle effect not yet measured" caveat.

One honest asymmetry to carry: E0b's action spread (3–9% each for the grid
actions) looks *exploratory*, not *directed* — the brain pulls crafting
levers ~22% of all steps (hold_next + grid_put + grid_take + take_result)
yet never once assembled the preconditions for an offer. Busy hands, no
chain. That is precisely the premise's shape: drives generate contact with
the mechanism, not sequences through it.

## E1 outcome [measured, 2026-07-24] — FAIL; E2 authorized

Feature 034 (`specs/034-two-doors/`), run same-day: P0 tape gate 45/45,
8-seed pilot published first (`pilot-results.md`), then the registered
24-seed read.

- **Taught: 0/24** seeds with a full chain (bar was ≥ 6/24), despite every
  seed receiving all **45/45 demonstrations** and provably carrying them —
  graduates enter the free-run with ~19 frames where blanks build ~13.
- **Blank: 0/24** (bar required 0 — the 0052 floor holds; the read is
  valid).
- Sharper than the bar: **zero dig attempts in 240,000 taught free-run
  steps.** Both arms drift off the feature cluster (~2,000–2,700 unique
  positions per 5,000-step window) and never return. The arms are
  behaviorally indistinguishable: teaching changed the brain, not the
  behavior.

**Reading [mechanism-argument]:** the frontier drive rewards error
*falling* and scores mastered ground at ~0. Forty-five identical
demonstrations make the workshop the best-learned region the brain knows;
by graduation the progress is already collected, so the drive goes silent
exactly there. **A well-taught lesson is exhausted territory — the
graduate leaves because the teaching worked.** This refutes, for
realized-progress drives, rev.2's landscape claim ("demonstration makes
the goal learnable, hence the highest-frontier option"): demonstration
lights the frontier *during* the guided phase and silences it after.
Knowledge without wanting is not behavior — which is the topic's thesis,
now measured from the teaching side too.

**Consequence:** the ladder's condition "E2 only if E1 fails" is met at
full power. **E2 — goal object + bounded fading λ + ONE multi-step
mechanism ((a) rollouts / (b) means-ends / (c) skills) — is authorized**;
the mechanism choice is its own registered decision, per the ladder.

## E2.0 pre-registration — the dwell gate (REGISTERED 2026-07-24, before any run)

The cheapest falsification of the goal-object idea, run at the policy
seam with **zero src edits** (arc convention; runner scratchpad-only).
Episode 0054's reversal condition, operationalized: before any goal
machinery is built, a bare λ-bias must at least **hold the policy near
the workshop** where frontier-alone provably leaves (E1: every graduate
walked off and never dug).

**The gate policy.** `GoalBiasPolicy` mirrors `CuriosityLookaheadPolicy`
exactly (same ε-gate at 0.1, same maturity gate, same fixed draw order,
ties to lowest index) with one added term per candidate action:
`value = drive_value(pred) + λ · (−‖pred − goal_obs‖₂)` over the full
32-channel predicted observation. The goal is **teacher-given and
ostensive**: the observation captured at tape step 2 of the E1
demonstration — standing at the workshop, facing the wood — identical
across seeds (the world is deterministic). v1 uses the full observation;
a labeled-channel mask is the single pre-named amendment if the pilot
shows the time-of-day channels swamping the spatial ones (raw numbers
reported either way).

**Subjects and arms, seed-paired on the E1 graduates** (the brain that
lived the 45 demonstrations, resumed into a fresh world exactly as in
E1): **G-λ** = goal-biased free-run at λ; **F** = frontier-alone free-run
(the E1 taught arm, replicated). Window H = 5,000 free-run steps.

**Dwell metric [ground truth]:** fraction of window steps within
Chebyshev distance ≤ 2 of the wood column (−1, 0). The run *starts
inside* this region — **the gate tests HOLDING, not homing.** Homing
from the featureless plain is explicitly out of scope for E2.0: a
one-step distance-to-goal has no gradient out there; returning from afar
is exactly the multi-step mechanism's job (E2.1), not the λ-bias's.

**Protocol and frozen bars:**

- Pilot: 8 seeds × (λ ∈ {0.25, 1.0, 4.0} + F), full grid published;
  **λ\*** = the smallest λ whose pilot median dwell ≥ 20%.
- Confirmatory: 24 seeds at λ\* + F. **PASS iff ≥ 18/24 G-λ\* seeds have
  dwell ≥ 20% AND the F arm's median dwell < 5%.** The demanding k
  (18/24, vs E1's 6/24) is deliberate: this gate tests a mechanism
  *directly* biased toward the goal — if it barely works, E2 proper has
  no chance, and a weak pass must not launder the rung.
- Context rows (no bar): digs/planks/sticks during goal-biased runs
  (workshop re-contact is the point of dwell), unique positions, mean
  distance-to-goal per arm.

**Frozen prediction:** PASS at λ ≥ 1 — near the workshop the one-step
goal-distance gradient is real (stepping away increases predicted
distance), so λ should hold what frontier abandons. The named doubt is ε
and drive noise slowly leaking the runner off the plateau edge; that is
what the 20% dwell floor and 18/24 measure.

**Decision rule:** PASS → E2.1 unblocks: the multi-step mechanism choice
((a) rollouts / (b) means-ends / (c) skills) goes to the owner as its own
registered decision before any build. FAIL → per episode 0054's reversal,
**the goal-object approach pauses before any src build** — the topic
returns to the drawing board with the dwell numbers as the diagnosis.

## E2.0 outcome [measured, 2026-07-24] — gate FAIL; and the first deliberate chains

- **The registered bar FAILs at power: 0/24 seeds reach 20% dwell**
  (λ\* = 4.0, the pilot's best; no λ cleared the pilot floor — grid
  medians 4.6% / 4.2% / 5.6% for λ 0.25 / 1 / 4). Confirmatory G4.0
  median dwell **3.8%** vs frontier's **0.3%**; F sanity bar met. The
  pull is real — mean Chebyshev distance to the workshop roughly halves
  (~50–150 vs ~100–420), unique positions halve (~1,000 vs ~2,300) — but
  it is **orbit, not hold**: the pre-named failure mode (no obs-distance
  gradient out on the plain) dominates once ε and drive noise leak the
  runner off the plateau. Per the decision rule and 0054's reversal,
  **the λ-on-one-step-lookahead form is refuted as the holding mechanism
  and the goal-object approach pauses before any src build.**
- **The context rows carry the discovery: the first deliberate crafting
  chains in the project's history.** Across all 42 goal-biased runs
  (8 seeds × 3 λ pilot + 24-seed confirmatory + 2 probe): **2 full
  log→planks→sticks chains** (seed 6 at λ 0.25; seed 7 at λ 4.0,
  deterministic across pilot and confirmatory) and ≥1 dug log in ~10
  runs — each log 12 consecutive deliberate dig ticks, planks and sticks
  vanilla-exact grid crafts, with post-craft grid churn (dozens of
  stage/unstage cycles) showing sustained engagement with the mechanism.
  Frontier-alone across the entire measured record — 328k live steps
  (E0), 24 E1 free-runs, 26 F arms today — has never produced one log.
  **E1's knowledge was deployable all along; it needed pull, not push.**
  Wanting-without-holding touches the workshop rarely; when it touches,
  the taught chain executes. The chains live at the intersection of E1's
  knowledge and E2.0's (weak) wanting — an existence proof that a goal
  signal converts taught knowledge into directed sequences, delivered by
  the very gate that failed its bar.
- **Instrument correction, recorded openly:** the FakeBridge ground-truth
  view carries no `digging` field (only the live bridge does), so the
  `digging_records = 0` context rows in E1/E2.0 measured nothing;
  episode 0054's phrase "zero dig attempts" overstated — the measured
  fact is zero dig *completions* (inventory-based, unaffected). The E1
  verdict stands unchanged.

**Where this leaves the ladder:** E2 as specified (λ + ONE multi-step
mechanism) is paused by its own gate. The drawing-board fork is the
owner's: (i) a homing-capable goal term (e.g. potential-shaped distance
or goal-conditioned frames) re-registered as E2.0b; (ii) accept
orbit-and-touch and measure whether λ-orbiting yields chains reliably at
longer horizons (the 2/42 existence rate vs H); or (iii) reread the
teacher model — the completion-signal/verdict channel (E3 machinery) as
the thing that holds attention, not distance. No option builds src
before its own registered gate.

## E2.0h pre-registration — the horizon read (REGISTERED 2026-07-24, before any run)

**The owner picked fork option (ii)** (2026-07-24, evening): accept
orbit-and-touch as measured and ask whether the chain rate climbs with
horizon. Options (i) E2.0b homing term and (iii) E3 verdict-channel
reread stay on the drawing board, unregistered.

**Question.** E2.0 produced 2 full chains in 42 goal-biased runs at
H = 5,000 (1/24 in the λ = 4 confirmatory). Floor or rate? If
wanting-without-holding accumulates chains as the window grows, λ-orbit
plus patience already converts taught knowledge into directed behavior —
a holding mechanism would buy speed, not existence. If the count
freezes, the λ-on-one-step-lookahead form is exhausted for rate as it
already is for holding.

**Instrument rebuild, declared before any run.** The E1/E2.0 runners
were scratchpad-only per the arc convention and did not survive the
session; the committed record plus the deterministic world make them
reconstructible, and the rebuild must prove itself before any horizon
step is read:

- **P0 (rebuild gate):** regenerate the 24 graduates (seeds 1–24, 45
  snapshot-bridged single-chain segments each, every segment asserting
  its stick-craft — 034's tape gate inherited), then re-run G-λ4 at
  H = 5,000. **HARD criterion:** the full-chain set is exactly
  {seed 7} — E2.0 recorded it deterministic across pilot and
  confirmatory. **SOFT criterion:** 0/24 seeds ≥ 20% dwell and median
  dwell in 3.3–4.3% (recorded: 3.8%) under the declared
  operationalization — Chebyshev distance ≤ 2 from the raw float (x, z)
  of the ground-truth view position to the wood column (−1, 0). If the
  recorded dwell cannot be recovered under this rule, nearby
  operationalizations (floor/round of position) may be tried with every
  attempt reported — instrument reconstruction, not bar-tuning; the
  chain-set criterion admits no variant. If the full-observation goal
  term fails the HARD criterion, E2.0's single pre-named amendment (the
  labeled-channel mask) is the first diagnosis candidate. HARD mismatch
  → instrument diagnosis; nothing downstream is read.
- **Prefix invariance (validity):** the first 5,000 steps of every
  40,000-step run must reproduce the P0 run's per-seed rows (the
  horizon must not leak into the stream); divergence voids the read
  pending diagnosis.

**Subjects and arms.** G-λ4 = `GoalBiasPolicy` exactly as E2.0
registered it — mirrors the curiosity lookahead (single ε draw at 0.1
first, maturity gate, ascending candidate scan, ties to lowest index)
plus λ·(−‖pred − goal_obs‖₂) over the full 32-channel decoded
prediction; goal obs = the observation at tape step 2 (standing at the
workshop, facing the wood, captured when the teacher emits its first
`dig_ahead`); λ = 4.0 (the registered λ\*); subjects = the 24 E1
graduates resumed into a fresh world. **H_max = 40,000** free-run steps
(8× the E2.0 window; throughput probe 2026-07-24, calibration only:
942 steps/s single-process, so the whole protocol is minutes-to-tens-of-
minutes). Nested read points H ∈ {5,000, 10,000, 20,000, 40,000}.
**F control:** frontier-alone graduates (no injected policy), seeds
1–8, H = 40,000. **λ0.25 context arm (no bar):** seeds 1–8,
H = 40,000 — the second recorded chain (seed 6) lived at this λ.

**Primary metric.** C(H) = how many of the 24 G-λ4 seeds have ≥ 1 full
log→planks→sticks chain within their first H steps. Detector: the
causal triple over bare inventory increases in the ground-truth view
(log-up → planks-up → stick-up, in order), exactly as operationalized
for 034 — the window starts in a fresh world with an empty pocket, and
the only mechanical path to a stick is the full chain.

**Named cap (no silent caps):** the fake world holds exactly three wood
columns — the starter (−1, 0) plus (−2, 3) and (5, −1) — so one world
caps *recurrence* at ≤ 3 chains per seed. First-chain incidence, the
primary, is uncapped by this. Recurrence is a context row, read against
that ceiling.

**Context rows (no bar):** per-seed first-chain step; chains per seed
(ceiling 3, named above); dwell per 5,000-step block across the window
(does the orbit persist or decay?); digs / logs / planks / sticks;
unique positions and mean Chebyshev distance per block; the same rows
for the λ0.25 and F arms.

**Protocol.** P0 → pilot (seeds 1–8 at H_max, numbers published in this
README before the confirmatory) → confirmatory (seeds 1–24 G-λ4 + the
F and λ0.25 arms at H_max).

**Frozen bars.**

- **PASS iff C(40,000) ≥ 6 AND C(40,000) > C(5,000).** k = 6/24 is
  deliberately E1's own bar: if weak wanting plus 8× patience reaches
  the count that "taught knowledge reliably re-elects the chain"
  demanded at H = 5,000, orbit-and-touch is a usable mechanism, not a
  fluke. The second clause demands growth beyond the seeds already
  known by 5,000 — accumulation, not replay.
- **FAIL iff C(40,000) ≤ 2** — the count freezes at or below the known
  chainers: a floor.
- **C(40,000) ∈ {3, 4, 5} is a gray zone, reported as such** — no
  laundering either way; the growth curve goes to the owner against the
  memoryless reference, fork re-opened.
- **Validity:** F chains = 0 (any nonzero re-opens the 0052 floor and
  voids the read); P0 and prefix invariance as above.

**Memoryless reference (frozen).** If chaining-on-touch were a
constant-rate process at the confirmatory's observed p = 1/24 per
5,000-step window, expected C(40,000) = 24·(1 − (23/24)⁸) ≈ 6.9. The
PASS bar sits just under this line: a roughly-memoryless process should
PASS; a strongly sub-memoryless one should not.

**Frozen prediction.** C(40,000) ∈ [4, 10] — the orbit comes from a
stationary policy with no decay mechanism, so touches should recur and
chains accumulate near the memoryless line; PASS judged marginally more
likely than not. Named doubt: seed heterogeneity — if chaining needs an
atypically-structured brain rather than RNG luck, the curve plateaus at
≤ 3 and the read FAILs. (E2.0's frozen prediction was wrong; this one
is offered with that humility.)

### E2.0h P0 + pilot [measured, 2026-07-24] — published before the confirmatory

- **P0 rebuild gate GREEN.** The reconstructed instrument reproduces the
  recorded E2.0 confirmatory from the committed record alone: chain set
  exactly {seed 7} (first chain at tick 427), 0/24 seeds ≥ 20% dwell,
  median dwell **3.76%** against the recorded 3.8% — under the declared
  raw-float Chebyshev operationalization, no variants needed. The lost
  runner is rebuilt and proven; every downstream number stands on this.
- **Pilot (seeds 1–8, λ = 4, 40,018 steps): the dwell after the first
  5,000-step block is exactly 0.0 in every seed.** No seed re-enters
  Chebyshev ≤ 2 of the workshop in 35,000 further steps; per-block mean
  distance wanders 100–1,300 blocks out. Chains: seed 7's early one
  (tick 427) and nothing after, anywhere. Prefix invariance green (the
  40k runs' first 5,016 steps reproduce P0 per-seed exactly).
- **Reading:** not orbit-and-touch — **leave-and-never-return**. The λ
  pull is local: within its capture radius it halves distance (E2.0),
  but past that radius the one-step obs-distance is flat and the walk
  never re-crosses. The pilot predicts the confirmatory reads
  C(40,000) = C(5,000) = 1 → registered FAIL (floor). Confirmatory
  proceeds per protocol.

**Decision rule.**

- **PASS** → orbit-and-touch stands as the topic's measured mechanism:
  a taught goal observation plus a λ-bias at the policy seam converts
  taught knowledge into directed chains at a usable, accumulating rate.
  The next registered decision is the owner's: graduate the topic on
  this result, or continue to E2.0b/E3 for speed and holding. No src
  build is authorized by this gate alone.
- **FAIL** → the λ-form is exhausted (holding *and* rate); the fork
  narrows to (i) E2.0b homing or (iii) E3 verdict-channel — or park,
  with the existence proof standing and the c1c run as the watch.
- **Gray** → the owner decides with the curve on the table.

## Reversal condition

**Draft:** if the C1 curiosity-alone run begins producing multi-step crafting
chains on its own, the premise ("goals are the missing ingredient for directed
multi-step behavior") weakens and this topic should pause, not build.
