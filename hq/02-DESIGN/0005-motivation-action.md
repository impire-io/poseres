# 05 — Motivation and Action

This document specifies the system's motivation (its innate drive and the value signal) and its action layer (how it selects actions). These together make the system act; without them it is a passive world-model.

This is the least mature part of the system. The interfaces and a working default are specified unambiguously. Several internals are **[O]** — known open problems — and are flagged as such.

> **Build status (2026-07-07, feature `002-motivation-action`):** implemented and
> validated at the reference scale. The Drive/Policy seams, the curiosity default
> (windowed learning progress + min-distance novelty), the one-step lookahead
> policy, the multi-drive mechanism, and the immutability rule (§6) are built and
> test-locked; the validated T1–T6 core is byte-identical under the pinned random
> baseline. Acceptance: **T7** (PRA-02 §4) — curious vs random, noninferiority —
> **PASS** at the reference (arms statistically equivalent; directed exploration
> neither helps nor hurts in the small reference world). The [O] internals (§3.1,
> §3.2, §4.2) remain open exactly as flagged.
>
> **Research update (2026-07-08, `AGENCY-DIAGNOSIS.md`):** at scale
> (`true_dim=20`) novelty-directed curiosity is *worse* than random (T7 FAIL,
> margin −0.062), and a five-experiment diagnosis located the cause in the
> **content** of the preference, not the directedness: a content-free
> state-coupled policy is neutral (+0.014) and the inverted, familiarity-seeking
> preference **beats random** (+0.067, better in 6/8 seeds). The §5
> counter-drive concept is therefore validated in its strongest form: a
> **competence drive** (mastery + familiarity) is now shipped in the drive
> registry and is the recommended configuration for uniformly-learnable worlds
> at scale (`drive_weights = {competence: 1.0}`); the base default remains
> curiosity-only. The blend question closed in two acts (JOURNEY ch. 18 + 24):
> the curiosity/competence pair shares one per-candidate novelty statistic, so
> no blend surface existed — until the **frontier drive** (`"frontier"`,
> PREDLP-DIAGNOSIS) supplied the missing per-candidate *learnability* signal:
> realized local learning progress over the remembered neighborhood of each
> lookahead candidate. Measured at 24-seed power on the non-uniform ladder
> worlds: competence and the frontier+competence blend both beat random in a
> strict majority at every horizon and both noise dials (the A4 exit);
> frontier neither stares at noise nor camps, and matches — does not beat —
> competence where avoidance is optimal. The camping-costs worlds
> (feature 017, CAMPING-DIAGNOSIS) then measured the drive on its own
> turf: **camping does cost** (post-shift, competence recovers worst of
> all arms — even random beats it), but realized LP does not collect the
> prize — its post-shift edge over competence equals random's, and on
> multi-region worlds it steers to the harder region exactly as designed
> while *paying* for the visits (noninferiority FAIL). Guidance stands:
> **competence** is the recommended drive. Realized LP is a lagging
> indicator — progress already banked is not progress still available —
> so fully *predictive* LP (a per-candidate error model) remains [O],
> sharpened, with two ready-made testbeds and recorded baselines.

---

## 1. Principles

- The system has **one or more fixed innate (terminal) drives**, set at configuration. These are the system's only source of "better." **[D]**
- The innate drive **MUST NOT** be modifiable by the running system (cross-cutting requirement C3). If the drive could rewrite itself, the system could trivially maximize it by redefining it; this is prohibited.
- The system has **no pre-loaded instrumental goals.** Instrumental goals (learned, revisable sub-goals) emerge at runtime as the system discovers what serves its drive. The base build ships with the drive only. **[D]**
- The default drive is **curiosity** (Section 3). It is chosen because it produces a non-trivial value signal that pulls the system toward learnable experience and has no degenerate maximum reachable by inaction. **[D]**

---

## 2. The value signal

```
ValueSignal: float        # scalar; higher = more desirable, per the drive(s)
```

The motivation layer produces a value signal each fast-loop step from the system's own state and recent experience. The action layer (Section 4) uses it to choose actions. The value signal is internal; it is **not** supplied by the environment, the actuators, or any external reward.

### 2.1 Drive interface — **[D]**
```
Drive:
  id()    -> drive_id
  value(context) -> float        # the drive's contribution to the value signal
```
`context` provides the drive with read access to: the current and recent global poses, the frames' recent measurement EMAs (recon/pred/effort), the recent observation stream, and the system's running drive-state (Section 3.3). A drive **MUST** be a pure function of `context` and its own fixed parameters; it **MUST NOT** hold hidden mutable policy state beyond the bookkeeping in 3.3.

### 2.2 Combining multiple drives — **[D]**
If more than one drive is configured, the value signal is a fixed weighted sum:
```
ValueSignal = Σ_d  drive_weight[d] · Drive_d.value(context)
```
Drive weights are fixed at configuration (Doc 07). The base build configures exactly one drive (curiosity); the multi-drive mechanism exists so a counter-drive can be added (Section 5) without code change.

---

## 3. The curiosity drive (default) — **[D]**, with **[O]** internals noted

Curiosity rewards **learning progress** — the system reducing its own prediction error over time — with a **novelty** component that operates before a world-model exists. This two-part definition addresses the cold-start problem (no model ⇒ no prediction error ⇒ no signal) and the wandering problem (raw unpredictability traps the system on noise).

### 3.1 Learning-progress term — **[O]**
Reward is proportional to the **recent decrease** in the system's prediction error, not to the prediction error itself.
```
learning_progress = max(0,  pred_err_baseline − pred_err_recent)
```
where `pred_err_recent` is a short-window average of the system's prediction error (e.g. the mean `pred_err` over mapping frames, averaged over a recent window) and `pred_err_baseline` is a longer-window average. A region the system is *learning* yields positive learning progress; a region it has *mastered* (low, flat error) yields ~0; a region of *noise* (high, flat error) also yields ~0. This is what prevents the system from getting stuck on unlearnable noise.

**[O] note:** the exact windows, the precise statistic, and the normalization are open and expected to be tuned. The requirement is that the term reward *reduction* in prediction error, not raw prediction error.

### 3.2 Novelty term (cold-start) — **[O]**
Before a usable world-model exists, prediction error is meaningless, so learning progress is undefined. The novelty term provides a signal from the **raw observation stream**, which exists from the first step:
```
novelty = unfamiliarity(observation, recent_observation_memory)
```
where `unfamiliarity` is high for observations dissimilar to those recently seen and low for familiar ones. `recent_observation_memory` is a bounded store of recent observations (Section 3.3).

### 3.3 Combination and cold-start handover — **[D]/[O]**
```
curiosity_value = w_progress · learning_progress + w_novelty · novelty
```
At cold-start, `learning_progress ≈ 0` (no model), so `novelty` dominates and drives the system to gather varied experience, which lets frames form. As frames learn, `learning_progress` becomes informative and takes over. The handover is automatic (no phase switch); the weights `w_progress`, `w_novelty` are fixed (Doc 07).

The drive maintains, as bookkeeping (not policy): the recent and baseline prediction-error windows, and `recent_observation_memory`. This bookkeeping is part of system state (Doc 06).

---

## 4. The action layer (policy)

The policy selects, each fast-loop step, the `Action` to send to the actuators. Its objective is to **increase the value signal**.

### 4.1 Policy interface — **[D]**
```
Policy:
  select_action(context) -> Action
```
`context` provides read access to the current global pose, the frames' transition models (to predict consequences of candidate actions), the Drive(s) (to value predicted consequences), and the action space `[0, n_actions)`.

### 4.2 Default policy — one-step curiosity lookahead — **[O]**
For the discrete action space:
1. For each candidate action `a` in `[0, n_actions)` (or a sampled subset if `n_actions` is large):
   - use the frames' transition models to predict the next pose(s) for `a` (Doc 03 §3);
   - estimate the value signal that the predicted outcome would yield, via the Drive(s) over the predicted context;
2. Select the action with the highest estimated value. Break ties by lowest action index.
3. With probability `exploration_epsilon` (Doc 07), select a uniformly random action instead (to retain exploration when lookahead is confident).

### 4.3 Cold-start behavior — **[D]**
When frames are empty or too immature for their transition predictions to be meaningful, the lookahead in 4.2 is uninformative; the policy therefore selects **uniformly random actions**. This is by design: at cold-start the system cannot direct action toward novelty (it has no model of what action leads where), so it acts randomly while the novelty drive (3.2) values the resulting experience, bootstrapping the world-model. As transition models improve, the lookahead automatically becomes meaningful and action becomes directed. No explicit phase switch is required; an implementation **MAY** gate lookahead on a configured minimum frame maturity (Doc 07) to avoid acting on noise.

**[O] note:** one-step lookahead is myopic. Multi-step planning is a permitted, expected future replacement behind the same `Policy` interface; it is **out of scope** for the base build.

### 4.4 The event pathway and the completion itch — **[O]** (feature 040, opt-in)

Measured provenance: motivation-stack G3, episode 0071 — the one-step frame
prediction reads fast, discrete channels too coarsely to rank actions on
(pred error 0.0612 against a 0.083 one-tick signal), and election scales
with progress-signal fidelity and nothing else (0/24 → 11/24 → 24/24 across
the three measured arms).

**The event head** (`Config.event_head_eta > 0`; Doc 07): a second,
bottleneck-free prediction pathway beside the frames — per action, a linear
model of the next-observation *delta* over all sensed channels, learned by
normalized LMS (cold start zero, no RNG, one update per executed transition,
including continuous-mode virtual episode boundaries). It is brain state: it
lives with the frame store, travels in snapshots, and resizes with the
anatomy (growth zero-initialized — "predicts no change"). The policy context
exposes it as `predict_event_delta(action)`, `None` when off.

**The completion itch** (`CompletionItchPolicy`): the 4.2 lookahead plus an
optional caller-injected per-action term plus one new term,
`κ · (progress_after − progress_now)`, where `progress_after` reads the event
head with the learnable completion rule — a predicted pocket gain above the
threshold counts progress as full, else clipped sensed progress + predicted
delta. Same draw order, gates, candidate-skip, and tie-breaking as 4.2; the
itch is inert when the head is off. Channel indices are anatomy knowledge
(constructor parameters; the Minecraft anatomy exports
`C1_MINING_INDEX`/`C1_POCKET_TOTAL_INDEX`). The measured operating point:
η = 0.5, κ = 0.25, threshold half an item. The itch **composes** — itch
without a hold measured 2/8 digging and 0/8 chains (G1's control arm) — and
the policy ships bounded honesty counters (completions fired, false
completions, progress prediction-error EMA) because the completion rule
generalizes to any predicted acquisition (crafting became itchy in G3
without being designed to). This section stays within §6's rule: the drive
set is untouched — the itch is a policy-term reading of a *sensed* channel,
never a modified drive.

---

## 5. Stability: counter-drives — **[D]** (optional, not in base build)

A single curiosity drive **MAY** wander (perpetually chasing novelty without consolidating). The specified remedy, **if** wandering is observed, is to add another **fixed terminal drive in tension** (e.g. a competence drive that rewards *mastering* — driving prediction error low and keeping it low — or a safety drive that penalizes states the system cannot predict at all). Such a drive is added via the multi-drive mechanism (Section 2.2) at configuration. It is **fixed and terminal**, exactly like curiosity.

**MUST NOT:** the remedy for wandering is never a pre-loaded *instrumental* goal. Instrumental goals are always learned at runtime, never configured.

The base build ships with curiosity only; counter-drives are a configuration option, not a code change.

---

## 6. The "no self-modification of the drive" rule — **[D]**, mandatory

- Drive identities, drive parameters, and drive weights are **read-only** to the running system. They are set at boot (Doc 07) or restored from a snapshot (Doc 06) and never written by any runtime process.
- Structural learning (Doc 04), online learning (Doc 03), and the policy (Section 4) **MUST NOT** alter any drive parameter.
- **Optional / future:** drive parameters **MAY** be varied *between* snapshots by an external process (an outer selection across runs), never by the running instance. This is noted only so the snapshot format (Doc 06) records drive parameters explicitly; the base build does not implement drive evolution.

---

## 7. Data flow summary (for integration)

Per fast-loop step:
- Frames → produce global pose and measurement EMAs (Doc 03).
- Drive(s) → read those plus the observation stream → produce the value signal (Sections 2–3).
- Policy → read the global pose, the frames' transition models, and the Drive(s) → select an action (Section 4).
- Action → actuators → world → next observation (Doc 02).

---

## 8. Definition of done (this document)
1. One or more fixed drives produce a value signal; drive parameters are read-only at runtime (Section 6).
2. The default curiosity drive implements a learning-progress term and a novelty term with automatic cold-start handover (Section 3).
3. The policy selects actions to increase the value signal, with the one-step curiosity-lookahead default and random cold-start behavior (Section 4).
4. The multi-drive mechanism exists so a fixed counter-drive can be configured without code change (Sections 2.2, 5).
5. No runtime process modifies any drive parameter.
6. The data flow in Section 7 is wired: frames feed the drive and the policy; the policy's action returns to the body.
