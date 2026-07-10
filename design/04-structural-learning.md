# 04 — Structural Learning

This document specifies how the frame population changes over time: how frames are born, spawned, evaluated for survival, and evicted. Online weight learning (within fixed structure) is in Doc 03; this document covers structural change.

---

## 1. Two timescales

- **Online (fast loop).** Structure is fixed. Frames place observations and learn weights (Doc 03). The only structural event permitted online is **birth on demand** (Section 2). **[V]**
- **Offline (slow loop / consolidation).** Structure changes: candidates are spawned, frames are evicted, the population ages. **[V]** mechanism; **[D]** scheduling.

The slow loop runs while the fast loop is paused, on a consistent state.

---

## 2. Birth on demand (zero-start, no-loss rule) — **[V]**

During the fast loop, when an observation is mapped by **no** frame:
- if the population is empty: birth a frame with `dim` drawn uniformly from `[initial_dim_min, initial_dim_max]` (Doc 07);
- otherwise: let `best_dim` be the `dim` of the frame with the lowest survival score; birth a frame with `dim = max(1, best_dim + uniform_choice({−1, 0, +1}))`.

A born frame is initialized per Doc 03 §3.2 and registered on the bus immediately. This rule guarantees every observation is captured by at least one frame, and lets the population grow from zero.

---

## 3. Copy-don't-mutate — **[V]**

Structural change **MUST NOT** edit an existing frame's `dim` in place. A change of dimensionality is performed by **spawning a new candidate frame** of the new `dim` (Section 4) alongside the original. The original is unaffected. Survival selection (Section 5) then decides, over subsequent cycles, which frames persist. This makes every structural change reversible by default: a bad spawn simply fails to earn its place and is evicted, while the frames it was derived from remain.

---

## 4. Spawning candidates — **[V]** mechanism, **[O]** proposal policy

Each slow-loop cycle spawns `spawn_per_cycle` candidate frames (default 1).

For each spawn:
1. Determine `best_dim` (the `dim` of the lowest-survival-score frame; or the initial range if the population is empty).
2. `new_dim = ProposalPolicy.propose_dimension(best_dim, population_dims, rng)`.
3. Birth a candidate frame of `new_dim`, initialized per Doc 03 §3.2 except its EMAs start at `0.9` (a small head-start). Set `is_candidate = true`. Register on the bus.

### 4.1 Proposal policy interface
```
ProposalPolicy:
  propose_dimension(best_dim, population_dims, rng) -> new_dim
```

### 4.2 Default proposal policy (biased) — **[D]**
```
if rng.uniform() < exploit_prob:                 # exploit near the current best
    new_dim = max(1, best_dim + rng.choice({−1, +1}))
else:                                            # occasional exploration jump
    new_dim = rng.uniform_int(1, best_dim + explore_dim_max_offset)
```
Defaults (Doc 07): `exploit_prob = 0.75`, `explore_dim_max_offset = 4`.

**[O] note:** the proposal policy is the component expected to change for large dimensionality. A near-random proposal cannot cover a large `dim` range fast enough; a high-dimensionality deployment supplies a different policy. The interface **MUST** allow this without touching any other component.

**Measured variant (PROPOSAL-DIAGNOSIS, 2026-07-08):** `ClimbingProposalPolicy` — every proposal in `(best_dim, best_dim + explore_dim_max_offset]` (exploit `+{1,2}`, else explore uniform in the band). Selection at scale is waste-limited, not reach-limited: proposals at or below the incumbent burn a maturation window, far jumps die on their transient; the tight upward band climbs ~1 rung per maturation window (2× the wide-band fixed-budget median). **Opt-in** until the Section 5 threshold scales (see below): under the current absolute bar, un-throttled climbing empties the mature niche and `best_dim` ratchets with the proposals themselves.

---

## 5. Survival and eviction — **[V]** mechanism (parameters **[D]**, expected to be tuned)

Run once per slow-loop cycle, after spawning is decided but applied as below (aging first, then eviction, then spawn — see Section 6 ordering).

### 5.1 Survival score
A frame's survival score is `Scorer.combine(recon_err_ema, pred_err_ema, effort_ema, dim)` (Doc 03 §6). Lower is better. The EMAs are **coverage-fair** (updated over every event the frame is exposed to, not only the ones it maps — Doc 03 §4) and prediction error is measured in **observation** space (Doc 03 §3.1); the score includes the **parsimony** term `w_complexity·dim` so selection lands on the true dimensionality rather than over-dimensioning. These three properties together are what make spawn-and-select grow to the right `dim` (Doc 02 validation T4).

### 5.2 Young-frame protection
A frame with `age_cycles < min_age_cycles` (Doc 07) is **protected**: it is exempt from all eviction this cycle. This guarantees a freshly spawned candidate (including a new-dimensionality one) gets at least `min_age_cycles` cycles of exposure before it can be removed.

### 5.3 Population-scaled threshold
```
threshold = survive_threshold_base / (1 + survive_threshold_pop_coeff · max(0, population_size − survive_threshold_pop_baseline))
```
Defaults in Doc 07. The threshold **falls** as the population grows: since a frame is evicted when its survival score *exceeds* the threshold (lower score = better), a falling threshold **tightens** the tolerated-error bar under crowding, so eviction pressure rises with the population. This is what lets soft eviction pace the one-spawn-per-cycle and makes the population self-limit rather than only being held by the hard cap.

**MUST:** the scaling divides (crowding tightens the bar). A threshold that *rises* with population — `base · (1 + coeff·…)` — makes eviction *vanish* as the population grows (everything falls under the rising bar), so the population grows at the spawn rate until it slams into the hard cap. That direction fails T5's "self-limits, not merely capped" criterion.

**Open scale problem (PROPOSAL-DIAGNOSIS, 2026-07-08):** `survive_threshold_base` is an *absolute* bar validated at the reference scale, where mature scores sit far beneath it. At `obs_dim = 60` the achievable at-maturity score of every dim past ~12 sits **above** the bar, so the mature niche is marginal-to-empty and selection is governed by the maturation filter (score at `age = min_age_cycles` vs the bar), not by the Section 5.1 score surface. A reference-preserving `effective_survive_threshold_base` rule (PRA-01 §8.8 pattern) is the named successor problem; the population census instrument (Doc 06 snapshot of per-frame dim/age/score) is how to verify it.

### 5.4 Soft eviction
Remove **every** unprotected frame whose survival score exceeds `threshold`, worst first, but never reduce the population below `min_frames`.

### 5.5 Hard cap
If, after soft eviction, the population still exceeds `max_frames`, remove the worst **unprotected** frames (highest survival score) until the population is at `max_frames`. If every frame over the cap is protected, the population **MAY** temporarily exceed `max_frames` until those frames age past protection.

**MUST:** soft eviction (5.4) plus the hard cap (5.5) keep the population bounded over time. (This is the mechanism that ensures earned persistence and prevents unbounded growth. The threshold and cap parameters are the values most likely to require tuning; tuning them is expected. Changing the *mechanism* is not.)

---

## 6. The slow-loop cycle — exact order — **[V]**

```
cycle += 1

# 1. Age; mature candidates.
for f in frames:
    f.age_cycles += 1
    if f.is_candidate and f.age_cycles >= min_age_cycles:
        f.is_candidate = false

# 2. Apply any pending tool / anatomy changes (Doc 02 §5; frame resize Doc 03 §7).

# 3. Eviction (Section 5): compute threshold; soft-evict; enforce hard cap; respect protection and min_frames.

# 4. Spawn (Section 4): spawn `spawn_per_cycle` candidates.

# 5. Snapshot (Doc 06).
```

Tie-breaking, wherever "the lowest/highest survival score" is needed and two are equal: break by ascending `frame_id`.

---

## 7. Action-space change (when `n_actions` changes via tools) — **[D]**

When tool registration changes `n_actions` (Doc 02 §5):
- every frame's transition tensors are resized per Doc 03 §7 (new per-action slices initialized, removed slices discarded);
- this occurs in slow-loop step 2 (Section 6), on a consistent state;
- learned transitions for surviving actions are preserved.

---

## 8. Definition of done (this document)
1. Birth-on-demand works during the fast loop, growing the population from zero and guaranteeing no observation is lost.
2. Structural change is copy-don't-mutate: dimensionality changes spawn candidates, never edit in place.
3. The slow-loop cycle runs in the exact order of Section 6.
4. Spawning uses a replaceable proposal policy with the biased default.
5. Survival/eviction uses young-frame protection, the population-scaled threshold, soft eviction, and the hard cap, and keeps the population bounded.
6. Action-space and observation-space changes resize frames during the slow loop without losing surviving learned weights.
