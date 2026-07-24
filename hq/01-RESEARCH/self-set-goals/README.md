# Does the brain set goals for itself, or only follow a drive?

**State:** active
**Where it stands (2026-07-24):** E1 MEASURED at full power — taught 0/24,
blank 0/24, registered bar FAIL: demonstration alone does not reproduce
chains; the graduate leaves the workshop *because* the teaching worked
(frontier scores mastered ground at ~0). **E2 authorized; E2.0 (the dwell
gate) is REGISTERED** — a bare λ-bias must hold the policy near the
workshop before any goal machinery is built; the E2.1 mechanism choice is
its own registered decision, gated behind E2.0. E0/E0b (2026-07-23):
premise + frontier anti-idle both confirmed.
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

## Reversal condition

**Draft:** if the C1 curiosity-alone run begins producing multi-step crafting
chains on its own, the premise ("goals are the missing ingredient for directed
multi-step behavior") weakens and this topic should pause, not build.
