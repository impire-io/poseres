# Does the brain set goals for itself, or only follow a drive?

**State:** draft — bars OPEN, held for the Fable 5 adversarial pass (2026-07-23)
**Started:** 2026-07-22
**Origin:** a friend (ex-Willow Garage) asked what the brain has *as goals* —
curiosity is an inner drive, but does the brain ever set itself a target and
pursue it? Humans do. This topic is that question, held against the code.

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

### Teacher invariant (owner's principle, 2026-07-22)

A teacher teaches **mechanisms**, never **purposes**. "How to craft" is
knowledge (world-model + reusable skill); "*what* to craft, when, to what end"
stays the learner's own goal-setting. Candidate hard rule, parallel to the
constitution's "the system cannot modify its own drive":

> **A teacher may write to the knowledge layer (world-model, skills) — never to
> the goal/value layer.**

This preserves autonomy-of-purpose *mechanically*: a teacher can only expand
what the brain **can** do, never what it **wants**. It is the online, interactive
cousin of **seeding** (feature 028), which already transfers mechanisms offline
— measured as *relevant transfer, not maturity*, and it never dictates goals.
Lineage: Willow-Garage learning-from-demonstration = imitate the *how*, not the
*what*.

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
   experiment, or do we lean on Minecraft's forgivingness and defer it?
5. **The bar** — crafting-chain completion rate vs. the reactive policy on the
   FakeBridge testbed? At what margin, how many seeds, what horizon?
6. **Is this even the next frontier?** — steelman the null: curiosity-alone at
   C1 scale might yet produce directed chains; goals might add nothing. What
   would show that *before* we build?

## Pre-registered bars

**OPEN.** To be set with Fable 5 tomorrow, then this graduates to a real
pre-registration via `/research-start` (or stays a topic here).

## Reversal condition

**Draft:** if the C1 curiosity-alone run begins producing multi-step crafting
chains on its own, the premise ("goals are the missing ingredient for directed
multi-step behavior") weakens and this topic should pause, not build.
