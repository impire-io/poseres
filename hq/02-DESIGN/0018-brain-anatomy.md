# 0018 — Brain anatomy: the zones of the learner

**Status:** descriptive reference (2026-08-18). Doc
[0001](0001-system-overview.md) maps the system's seams (body, bus,
core, persistence); this document opens the brain box itself — what
parts exist inside a running pra-brain, what each part holds, and
**where knowledge lives**. Everything drawn here is shipped and
measured; each zone links the design doc that specifies it. Nothing
in this document adds requirements — it is the visual companion the
component docs never had.

## 1. The anatomy, visually

```
        world ──► BODY (sensors · actuators) ◄── acts on the world
                     │ observations                ▲ actions
─ body seam ─────────┼─────────────────────────────┼──────────────────
                     ▼                             │
  knowledge that ┌───────────────────────────┐     │
  lives at the   │        FRAME STORE        │     │
  seam, sensed   │  a population of frames — │     │
  back as        │  small predictive maps    │     │
  channels:      │  (encoder · decoder ·     │     │
  · palate /     │  per-action transition),  │     │
    price book   │  born on demand, kept     │     │
    (worth,      │  only while they pay      │     │
    learned by   │  ┌───────────────────────┐│     │
    eating)      │  │ EVENT HEAD — learned  ││     │
  · flood        │  │ per-action consequence││     │
    (deficits as │  │ model: what will this ││     │
    intrusion)   │  │ act change?           ││     │
  · vitals,      │  └───────────────────────┘│     │
    drops,       └───────────┬───────────────┘     │
    glance,          poses · predictions ·         │
    peers…           progress · errors             │
                             ▼                     │
                 ┌───────────────────────────┐     │
                 │    MOTIVATION & ACTION    ├─────┘
                 │  drive value (frontier)   │
                 │  + completion itch (κ)    │
                 │  + praise label (β)       │
                 │  × deficit coupling (κ_d) │
                 │  + commitment (κ_c)       │
                 │  ┌───────────────────────┐│
                 │  │ RECIPE MEMORY — taught││
                 │  │ step chains, held as  ││
                 │  │ their own structure   ││
                 │  └───────────────────────┘│
                 └───────────┬───────────────┘
                             │ every zone above, one blob
                             ▼
                 ┌───────────────────────────┐
                 │ PERSISTENCE — snapshot /  │
                 │ byte-identical restore;   │
                 │ the brain as an artifact  │
                 └───────────────────────────┘
```

Two reading rules make the picture honest:

- **Everything inside the box is plastic.** No zone is
  trained-then-frozen; every one keeps learning as long as the brain
  runs, and every one rides in the snapshot (Doc
  [0006](0006-state-persistence.md)).
- **Everything outside the box enters as a sense.** The brain never
  receives injected state — knowledge beyond its own structure lives
  in the world or at the body seam and is *sensed*, exactly like any
  other world fact (the senses-first rule,
  [how-we-work](../00-GENESIS/how-we-work.md)).

## 2. The zones

| Zone | Lives in | Holds | Kind of knowledge | Spec |
|---|---|---|---|---|
| **Frames** (`FrameStore`/`FrameGroup`) | kernel | how each slice of the world responds to each act: encoder, decoder, per-action transition per frame; born on demand, evicted unless they earn their keep | procedural, predictive — knowing-*how* the world behaves | [0003](0003-sensorimotor-core.md), [0004](0004-structural-learning.md) |
| **Event head** | kernel, `FrameStore`-owned | one learned map from (state, action) to expected observation delta — the consequence sense the itch and the hold read | consequence knowledge | [0009](0009-brain-side-hold.md); episode 0072 |
| **Recipe memory** (`RecipeMemory`) | action layer | taught step chains — the order of acts a demonstration carried, replayable and composable | skill sequences: the nearest thing to declarative memory inside the box | [0010](0010-recipes-and-the-label.md) |
| **Motivational state** (itch, live intention, deficit-scaled label weight) | action layer (`CompletionItchPolicy`/`RecipePolicy`) | the current posture: what is half-finished, what is committed, how loud the label is right now | dispositional, moment-to-moment | [0005](0005-motivation-action.md), [0016](0016-motivation-stack.md) |
| **Palate / price book** | **body seam** (`PALATE_FILE`), sensed back through the worth channel | what things are worth, eaten into existence — an EMA of felt meals that converges to the world's real prices | value knowledge as an **external artifact**: separable, inspectable, survives the brain | [0013](0013-the-aim.md); episodes 0089, 0100 |
| **The body itself** | anatomy (config) | which world facts are sensible at all — the channels decide what the brain *can* know (worth-not-count is the measured proof) | the epistemic frame | [0012](0012-anatomy-from-world.md), [0015](0015-native-survival.md) |

## 3. Where knowledge lives — the architectural stance

The brain deliberately does **not** hold fact-knowledge the way a
trained-then-frozen model does. What it accumulates is structure that
keeps paying: frames that predict, a head that anticipates
consequences, chains that finish, prices that match felt reality.
Fact-like knowledge splits two ways, and both patterns are shipped:

- **Internal zone** — recipe memory: knowledge held *beside* the
  general fabric in its own structure, learned by demonstration
  (transmission 24/24 where labels alone carried 0/24, episode 0076).
- **External artifact** — the palate: knowledge held *outside* the
  kernel at the body seam, written by living (eating), read back as a
  sense, portable between brains and outliving any one of them.

Any richer knowledge system couples the same way the palate does:
as part of the world, behind a sense, with consulting it a skill the
brain can be taught — never as injected state. The measured warning
that shapes this rule: *which sense defines wealth decides what the
brain can value* (episode 0088); the same holds for what it can know.

## 4. What this document is not

Not a requirements document — the linked docs carry the normative
spec, the dials live in [0011](0011-the-dials.md), and the measured
composition that runs by default is [0015](0015-native-survival.md).
When a new zone ships (a knowledge store, a consolidation mechanism
that survives its registered bars), this map gains a box in the same
commit.
