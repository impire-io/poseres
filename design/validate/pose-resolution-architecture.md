# The Pose Resolution Architecture

*A reference-frame model of perception and learning, developed as a structured alternative to the Thousand Brains Theory.*

---

## Status of this document

This is a **theory sketch**, not an established result. It was developed in dialogue as a response to specific gaps in the Thousand Brains Theory (TBT) of Hawkins et al. Where it overlaps with TBT, that is noted. Where it departs, that is noted too. The name "Pose Resolution Architecture" (PRA) is a working label; nothing rides on it.

Confidence is tagged throughout:

- **[Grounded]** — established neuroscience or a direct consequence of definitions.
- **[Inferred]** — a strong argument, not yet demonstrated.
- **[Open]** — a deliberate design choice whose correctness is unproven, or an unsolved problem honestly flagged as such.

---

## 1. The problem PRA is trying to solve

TBT proposes that every cortical column builds models of objects using reference frames implemented by grid-cell-like neurons, and that the same machinery handles physical objects and abstract concepts alike. **[Grounded]** that grid cells exist and support path integration in physical space; **[Inferred]** that the cortex reuses this for objects; **[Open]** — TBT's own papers state there is no direct evidence that every column contains grid-cell-like functionality.

Two things TBT leaves underspecified, which PRA tries to make concrete:

1. **A metric for comparing interpretations.** TBT says relationships are "properties of learned transitions" but gives no clean operator for scoring one candidate interpretation against another.
2. **Structural learning.** TBT has almost no account of how the set of reference frames is *learned* — how frames come into being, how their structure changes, how bad ones are removed.

PRA's contribution is to make both of these explicit. It does **not** claim to solve the hard core of structure learning analytically; it reorganizes the problem so the hard part is approached by selection rather than search (Section 6).

---

## 2. Core objects

### 2.1 Reference frame

A reference frame is a **dimensioned coordinate space**, not a slot for a single object. **[Open]** This is a deliberate departure from the one-frame-one-object reading. A single frame can host many objects and concepts at different coordinates, the way one environment hosts many landmarks. This is closer to the grid-cell substrate than a one-object-per-frame view: entorhinal grid cells represent many environments by remapping, so "frame as reusable space" is the better analogy than "frame as object record."

Each frame has its own dimensionality. Frames need not agree on dimensionality with each other.

### 2.2 Observation

An incoming sensory (or internally generated) event, broadcast to all frames (Section 3).

### 2.3 Local-pose

The coordinate vector an observation receives **within a single frame**. It is the answer to "where, in this frame's space, does this observation sit?" A local-pose only exists if the frame elected to map the observation.

### 2.4 Global-pose

The structured collection of all local-poses an observation receives across the frames that mapped it — a **vector of vectors**. This is the full interpretation of an observation: not one position, but its position in every frame that found it relevant. The global-pose is explicit and inspectable, unlike TBT's emergent voting consensus.

### 2.5 Transition

Within a frame, the learned mapping `(current_pose, action) -> predicted_next_pose`. **This is the load-bearing object.** A static frame predicts nothing; a frame *with transitions* predicts the consequence of an action. Transitions are where both prediction and effort-scoring live (Sections 4 and 5).

---

## 3. The message bus: sparsity by pull, not by push

TBT pushes a location signal *into* columns. PRA inverts this.

An observation is **broadcast on a bus**. Every frame is subscribed. Each frame independently decides whether to map the observation or drop it. A frame may decide by checking whether the observation fits its dimensions, or by consulting its current pose to judge whether mapping makes sense.

This produces **sparsity at the level of frame participation**: most frames drop most observations; only the relevant few map any given one. This is a different locus of sparsity than TBT's sparse cell activation, achieved by selective listening rather than a designed activation threshold.

**Constraint:** at least one frame must map an observation, or it is lost. **[Open / defensible]** Losing observations is acceptable and expected — humans do not track most of what they sense; relevance is situational. Loss is a feature of attention, not a bug, *provided* the system does not systematically lose observations it later needs. (This is a place the model could fail and must be watched in simulation.)

---

## 4. Prediction lives in transitions, driven by action

A frame at rest has nothing to predict — a coordinate does not forecast anything. Prediction is therefore **not** a property of a frame. It is a property of a frame's **transitions**, and its input is the **action / motor efference copy**.

The prediction step:

1. Take the current local-pose in frame F.
2. Take the action about to be performed (the efference copy of a movement, attention shift, or manipulation).
3. Apply the frame's transition structure: `predict(pose, action) -> predicted_next_pose`.
4. Execute the action; obtain the actual next observation and its actual local-pose.
5. **Prediction error** = discrepancy between predicted-next-pose and actual-next-pose.

This is the one place PRA adopts TBT wholesale: **perception is sensorimotor**. The input to prediction is the motor command, and prediction is over the next pose given that command. A frame that cannot predict the consequence of an action is a filing cabinet, not a model.

---

## 5. Scoring: three readings, not two (corrected by simulation)

> **Note (validation finding):** This section originally specified a two-term score — effort + prediction error. A simulation of the architecture (zero-start, nonlinear, multi-seed) showed that two terms are **insufficient**: scoring frames on prediction error alone is gameable, because a low-dimensional frame has a trivially small prediction problem and scores well regardless of whether it can model the world. Under two-term scoring, frame dimensionality collapsed toward 1 instead of growing toward the truth. Adding a third, **explanatory** term fixed it and structure then grew to the correct dimensionality across seeds. The three-term version below is the corrected claim.

Candidate interpretations and the frames that produce them are scored on **three** criteria. The distinction between them is structural, not stylistic:

- **Explanation (how much of the observation the frame accounts for).** Reconstruction error: does this frame's space actually capture what was sensed? A 1D frame can predict its own trivial pose easily but reconstructs a rich observation poorly. **This term is what prevents collapse to degenerate low-dimensional frames.**
- **Prediction error (external / anchor).** How well the frame's transition predicted the observation actually obtained after acting. Grounded in the world, not in current belief.
- **Effort (internal / regularizer).** The transformation distance required to reach a candidate pose. Cheaper transitions are favored. A least-action-style prior.

**Why all three are required.**

- *Prediction without explanation* collapses to degenerate frames that predict an impoverished pose well but capture nothing (the simulation's failure mode). A good reference frame must explain what you sense, not just predict cheaply.
- *Effort without prediction* has an inertial confirmation bias: the cheapest pose to reach is the one nearest current belief, so effort alone resists revising a wrong interpretation and converges to stable-but-wrong. Prediction error is the external teacher that breaks this, because the world delivers the next sensation regardless of what was cheap to believe.
- *Explanation without prediction* would give you a good static autoencoder with no model of consequences — a filing cabinet, not a model of how the world behaves under action.

The structure is a loss with a **fit term** (explanation), a **data term** (prediction), and a **regularizer** (effort). The first two are the load-bearing pair the simulation validated; effort refines economy on top. **[Inferred]** the weighting between terms is itself learnable.

A reference frame, then, earns its keep by simultaneously **explaining what is sensed and predicting what happens when you act** — and the simulation showed that dropping either of the first two breaks structural learning.

---

## 6. Learning: two timescales, and selection instead of search

### 6.1 Online learning — fixed structure, place and resolve

While awake, the frame structure is **fixed**. Online learning is the placing and resolving of observations: each observation is broadcast, mapped by whichever frames elect to, scored, and a winning global-pose is selected. New observations are placed directly into existing frames where they find grounding.

Online learning does **not** change frame structure. It is inference under a fixed model.

### 6.2 Offline learning — questioning structure by copy-and-select

Offline (the consolidation phase, suggestively "sleep"), the **structure itself** is put into question: should a frame split? merge with another? acquire a new dimension?

PRA's central claim about structural learning: **frames are never edited in place. New frames are created as candidates and selected by use.**

- A structural operation (split, merge, re-dimension) produces a **new candidate frame** alongside the original. The original is not destroyed.
- Only a **limited number** of candidates are spawned per offline cycle.
- Candidates run in parallel during subsequent waking cycles and accumulate a performance record.
- **Survival is earned, not default.** A frame that fails to demonstrate useful performance **decays toward non-existence** over time. Persistence must be actively earned; loss is the default fate.
- A split that turns out useless simply decays — and because the original was never destroyed, nothing is lost by trying.

**Why this is the right move:**

- It is **variation + selection**, not directed search. The combinatorial space of possible structures is never optimized over; it is sampled cheaply and pruned by use. This sidesteps the brutal search problem that makes structure learning hard everywhere.
- It is **reversible by default.** In-place mutation cannot undo a bad edit; copy-and-select can, because the predecessor survives. This is why robust biological systems (immune repertoire, synaptic overproduction-then-pruning) use overproduce-then-select rather than directed editing.
- The **rate limit is principled.** Too many candidates per cycle creates a credit-assignment problem — none gets enough exposure to prove itself. Limiting variants-per-cycle guarantees each candidate earns enough waking experience to be evaluated fairly.
- **Decay-as-default** is garbage collection for free and the correct asymmetry: earning persistence is harder than losing it, which prevents the frame population from growing without bound.

### 6.3 The performance signal

The quantity that decides survival combines the explanatory and predictive terms from Section 5: **a frame survives if it both reconstructs what it senses and predicts well under action, accumulated across the day.** A frame that fails either decays. (Validation finding: using prediction alone here was the bug that caused collapse to degenerate frames; the survival score must include the explanatory term.)

Online scoring and offline selection are driven by this same combined signal.

---

## 7. What PRA does and does not settle

### Settled well (stronger than TBT on these axes)

- **Sparsity by pull.** The bus-and-subscribe model gives sparsity at frame-participation level, cleanly.
- **Frame as vector space.** Better grounded in grid-cell remapping than a one-object-per-frame view.
- **Explicit global-pose.** An inspectable, scorable interpretation object, versus emergent voting.
- **Structural learning by selection.** Copy-and-select with earned persistence sidesteps the combinatorial search that TBT has no account of at all.
- **Unified signal.** Prediction error over transitions drives scoring and selection both.

### Honestly open

- **Re-dimensioning is the hard problem.** Splitting and merging frames is tractable discrete operation. Introducing a *new dimension* to a frame is genuine representation learning — a new axis only earns its place if it separates observations that previously collided. Offline scheduling decides *when* this is confronted, not *how* it is done. This remains unsolved; PRA organizes it but does not crack it.
- **Sample efficiency.** Selection-based structural learning spends many cycles on candidates that decay. Biology pays this happily; an engineered version likely wants a *biased proposal distribution* — use waking poor-fit statistics to decide *where* to try a split, rather than proposing blindly. Variation need not be blind to remain selection-based.
- **Cross-frame comparability.** Frames of different dimensionality produce local-poses in incommensurable spaces. PRA's position is that you compare **transition efforts and prediction errors** (both scalars) rather than poses across frames — sidestepping the incommensurability. Whether this is always sufficient is untested.
- **Observation loss.** "At least one frame must map an observation" plus "loss is acceptable" needs a guarantee that the system does not systematically discard observations it will later need.

---

## 7. Validation status (what a simulation actually showed)

A minimal testbed simulated the architecture in a synthetic sensorimotor world (hidden latent space, lawful action-driven motion, nonlinear emission). It began with **zero frames** and grew structure by the spawn-and-select rule, run across multiple random seeds. This is a coherence test of the mechanism, not a claim about real sensory data. Results:

| Claim tested | Result | Notes |
|---|---|---|
| Sparsity by pull (frames drop, don't all listen) | **Holds** | ~75% map fraction, all seeds |
| Prediction error falls as the system learns | **Holds** | fell in every seed |
| Effort-only scoring fails to learn the world | **Holds** | combined improved ~14× more than effort-only, every seed |
| Structure grows from zero to the right dimensionality | **Holds (after fix)** | best-frame dim clustered around the true value across seeds — *only once the explanatory scoring term was added*; with prediction alone it collapsed to degenerate low dimensions |
| Decay removes useless frames | **Partial** | selection picks the right structure, but eviction is too gentle and the frame population grows larger than it should — a decay-rate calibration issue, not a conceptual hole |
| Observations aren't systematically lost | **Holds** | <0.2% loss post-warmup |

**The most important finding** is the one that failed first: two-term scoring (effort + prediction) was insufficient, and the simulation caught it. The fix — a third explanatory term — is now part of the theory (Section 5). This is the simulation doing its job: turning an assertion worked out in conversation into something a run could falsify, and falsifying part of it.

**The honest open items remain open.** Re-dimensioning still only works here because the search space is small (dims ~1–8); scaling to high dimensionality and to real sensory streams is untested. The decay-rate calibration is best tuned against the real substrate (where memory pressure is real) rather than against the toy.

---

## 8. One-paragraph summary

Perception broadcasts each observation on a bus; reference frames — each a dimensioned space hosting many concepts — independently elect to map it, yielding a local-pose per frame and a global-pose (vector of local-poses) as the full interpretation. Frames carry action-driven transitions, and prediction is the application of a transition to a pose given a motor command. Interpretations and frames are scored by three terms — explanation (does the frame account for what was sensed), prediction error (the external anchor that prevents confident-but-wrong convergence), and effort (a parsimony regularizer); a simulation showed the first two are jointly necessary and that dropping explanation collapses structure to degenerate low dimensions. Learning runs at two timescales: online placement under fixed structure while awake, and offline structural learning that never edits frames in place but spawns rate-limited candidate frames and lets differential performance decide, by earned persistence and default decay, which survive. A single combined quantity — explanatory-plus-predictive performance over action-driven transitions — drives both online scoring and offline selection.

---

## 9. Relationship to the Thousand Brains Theory, at a glance

| Aspect | TBT | PRA |
|---|---|---|
| Reference frame | Grid-cell code per column, dimensionless | Dimensioned space, many concepts per frame |
| Frame ↔ object | Tends toward per-object models | Many objects per frame (vector space) |
| Location signal | Pushed into columns | Pulled by frames off a bus |
| Sparsity | Sparse cell activation | Sparse frame participation |
| Interpretation | Emergent voting consensus | Explicit global-pose (vector of vectors) |
| Scoring metric | Underspecified | Effort + prediction error |
| Prediction | Sensorimotor (over next sensation) | Sensorimotor (over next pose) — adopted from TBT |
| Structural learning | Largely absent | Copy-and-select, earned persistence, default decay |
| Hard open problem | Whole cortical-grid hypothesis unverified | Re-dimensioning of frames unsolved |

PRA is best read as TBT's representational and sparsity choices **reformulated for explicitness**, plus a structural-learning mechanism TBT lacks, with the sensorimotor-prediction core kept intact because that is the part of TBT that does the real work.
