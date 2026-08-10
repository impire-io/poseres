# 11 — The dials: what they represent, how to tune them (episodes 0069–0085)

**Status:** reference. Every number here is a measured operating point
or a measured failure mode; nothing is folklore. General vocabulary
throughout (acquisition channel, felt/label channel, meter) — body
names like "pocket" or "praise" are one anatomy's dressing.

## The reference scale — read this first

Every preference dial in the motivation stack is implicitly measured
against **the drive's terminal-value band**: the range of values the
curiosity drive assigns to candidate endings. In the measured lab
cohorts this band is **≈ 0.06–0.15** (episode 0080's registered value
traces). This is the brain's natural enthusiasm range, and it is the
unit that makes the other dials meaningful:

- A preference term **below** the band *whispers* (it biases ties).
- **Within** the band it *contends* (a real preference, curiosity
  still alive).
- **Above** the band it *commands* (it overrides curiosity entirely).

The band is not a constant of nature — it is a property of the drive
and the world's novelty structure. **Tuning protocol:** measure your
band first (log `drive_value_of(terminal)` snapshots across candidate
endings, as the 0080 instrument did), then place the preference dials
relative to it. If a future drive or world shifts the band, every
"cliff" below moves with it (episode 0081's recorded reversal
condition).

## The brain-side dials (constructor / config)

| Dial | Where | Measured point | What it represents |
|---|---|---|---|
| `event_head_eta` | `Config` | **0.5** (0 = off; stable 0 ≤ η < 2) | How fast expectations track experience — the NLMS step size of the event head. 0 disables the pathway bit-exactly. |
| `kappa` | `CompletionItchPolicy` | **0.25** | The completion itch: how much *finishing what is started* weighs against curiosity. |
| `lambda_r` (and hold λ) | `RecipePolicy` / hold terms | **0.25** | The pull toward the current subgoal per unit of predicted distance — the transport strength. |
| `completion_threshold` | `CompletionItchPolicy` | **1/128** | The smallest predicted acquisition that counts as a real completion; below it is prediction noise. |
| `label_beta` | `CompletionItchPolicy` / `RecipePolicy` | **0.02** or **0.5** | The *social* weight: how loudly a teacher's label speaks. |
| `deficit_kappa` | `CompletionItchPolicy` / `RecipePolicy` | **0.1** | The *body's* weight: how strongly depletion amplifies remembered felt value. |
| `exploration_epsilon`, `lookahead_min_age_cycles` | `PolicyParams` | per-protocol | The undirected floor: how often the policy acts randomly, and how mature a frame must be before directed selection trusts it. |

### `kappa` — the itch (episodes 0070–0072)

κ = 0.25 elects work reliably (24/24 dig at G3) without
perseveration. **Failure mode at the high end, measured:** κ ≥ 1
produces target-agnostic compulsive digging (cobblestone in the
hundreds, G1's perseveration watch). Tune κ to be *comparable to* the
drive band — the itch should win ties on nearly-finished work, not
overrule curiosity outright.

### `label_beta` — the teacher's voice (episodes 0080, 0081)

The dose curve is measured end to end: **0.02 nudges** (the praised
ending becomes the favorite at ~half the work; the menu keeps
rotating; nothing else is lost), **0.05–0.1 is the cliff**, **0.5
commands** (selection monoculture; the obsessive twin costs own goals
— chains 18/24, dwell ~63%). The cliff sits where β crosses the drive
band, which is *why* it sits there. Choosing β is choosing between a
preference and an order; there is no "slightly commanding" setting —
the transition is a cliff, not a slope. **At β = 2.0 (measured
pilot): own chains sag further** — louder is strictly worse past the
cliff.

### `deficit_kappa` — the body's voice (episodes 0083–0085)

The effective label weight is
`label_beta + deficit_kappa · clip(1 − meter, 0, 1)` — the *only*
state-dependent dial in the stack, and the state-dependence is the
measured value: a constant taste at the nudge dose ate *more on
average* and still died as often as no coupling at all (timing beats
volume, 0083). Tune by where you want crisis behavior to land on the
β curve: with κ_d = 0.1, a mild deficit of 0.25 produces an effective
0.025 (a nudge), a crisis deficit of 0.75 produces 0.075 (at the
cliff) — hunger whispers early and insists near the edge, which is
the shape that halved (0083) and then zeroed (0084) mortality.
Requires a felt/label channel; the meter must be [0, 1]-normalized
(readings outside clip).

### `event_head_eta` — the speed of expectation

η = 0.5 is the measured point everywhere; the NLMS bound is 0 ≤ η <
2. Low η: expectations lag the world (the itch and the holds starve
for signal). High η (→ 2): weights chase noise. There has been no
measured reason to move it off 0.5; it is bounded, not fragile
(bounded error over ~25M updates, episode 0079).

## The world-side dials (the economy; harness/anatomy, not brain)

These live in the body or world, not the policy — but callers tune
them together with the brain dials, so they are recorded here.

| Dial | Measured points | What it represents |
|---|---|---|
| meter drain | 0.0005 (G4); 0.0015 (C1 crisis); 0.005 (sample field) | The cost of being alive per tick. **Calibrate against measured income**, not intuition: the same drain that bites one body never bites a richer one (0084's open recalibration — income was ~0.0066/tick). |
| the taper (childhood) | ramp 1,500 → full 3,000 | Provisioning: the stipend that covers the gap between birth and first self-earned income. Measured exactly (G4b: frontier death moved to the predicted tick; the composition's 10/24 → 24/24 survival). |
| pay table | e.g. 0.15 / 0.04 / 0.004 | What the world's metabolism rewards, per gain-tick per product. This is *world truth* (like block hardness) — the brain never sees the table, only its felt consequence. |
| felt normalization | `clip(pay / max_pay, 0, 1)` | The interoceptive label: the body grading its own meal on [0, 1]. |

**The economy's measured limits:** payments alone do not steer choice
(0082 — the drive cannot smell calories); praise does not steer diet
(0082 — the itch feeds opportunistically wherever the hands are).
Choice responds to novelty, the label, and — through `deficit_kappa`
— the meter. Survival responds to work rate and the economy. Keep
those channels straight when tuning.

## `pocket_index` — which sense defines wealth (episode 0088)

Not a scalar dial but the stack's most consequential wiring choice:
the completion itch and recipe extraction key on whatever channel
`pocket_index` names. Pointed at a **count** sense, the brain hoards
— and is provably blind to trades (a 3-for-1 exchange cannot even be
remembered as a lesson; 0/24 ever traded). Pointed at a sensed
**worth** channel (Σ count·price, the world's price truth felt
interoceptively), the identical machinery trades 24/24 and composes
count-losing journeys. Choose deliberately per body; economies
require the worth sense.

## What is deliberately NOT a dial

The drive itself (fixed and terminal, Doc 0005 §6 — no dial modulates
`drive_value_of`); the draw order and maturity gating (behavioral
contract, not tunable); the completion rule's read sites (the label
is read only inside fired completions — the measured hangover guard,
episode 0073).
