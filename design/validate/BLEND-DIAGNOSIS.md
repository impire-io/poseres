# Blend diagnosis — curiosity, competence, and the noisy region

Date: 2026-07-13. Question under test (ROADMAP A4, the last open Phase-A
item): **what drive configuration survives a world that is not uniformly
learnable?** AGENCY-DIAGNOSIS measured, on uniformly-learnable worlds,
that novelty-seeking curiosity is *worse* than random and
familiarity-seeking competence *beats* random — and both it and Doc 05 §5
name the untested risk: in worlds with unlearnable regions, curiosity's
novelty pole should be *attracted* to the noise (the noisy-TV failure —
prediction error there never falls, novelty never fades), while
competence's familiarity pole risks the camping degeneracy (park where
error is already low, never explore). The L1 ladder rung (feature 005)
exists to make both measurable: a half-space region of latent space with
irreducibly random transitions, an agent whose actions carry it into and
out of the region, and per-seed random-policy occupancy baselines
already recorded (LADDER-CRITERIA.md, L1 result).

## Hypotheses (pre-registered)

- **H-stare:** curiosity-directed runs have *higher* region occupancy
  than the same-seed random baseline, and their improvement margin vs
  random is negative on L1 worlds — worse where the noise is stronger
  (σ=0.8 worse than σ=0.2).
- **H-camp:** competence-directed runs have *lower* occupancy than
  random, and their improvement margin vs random is non-negative
  (extending the uniform-world result to non-uniform worlds) — the open
  risk being that avoidance costs structure (best_dim degradation vs
  random) rather than improvement.
- **H-blend (the open §5 question):** whether any curiosity/competence
  blend beats *pure competence* on L1 is genuinely uncertain — a blend
  buys exploration breadth at the price of some noise-staring. No
  directional prediction is registered; whatever lands is the finding.

## Protocol (pre-registered)

Arms per (world, horizon, seed), all through the unchanged engine on the
L1 world (`world="nonuniform"`, reference dials `true_dim=3,
obs_dim=10`), seeds 1–8:

| arm | `policy_mode` | `drive_weights` |
|---|---|---|
| random | `random` | — (pinned baseline) |
| curiosity | `curiosity` | curiosity 1.0 |
| competence | `curiosity` | competence 1.0 |
| blend-25 | `curiosity` | curiosity 0.25, competence 0.75 |
| blend-50 | `curiosity` | curiosity 0.5, competence 0.5 |
| blend-75 | `curiosity` | curiosity 0.75, competence 0.25 |

Dials: σ ∈ {0.2, 0.8}. Horizons: the ROADMAP A4 exit demands "majority of
seeds at **every checkpoint**", so each arm runs at three schedule
lengths, `n_cycles = horizon ∈ {18, 30, 50}` (separate runs — the
early/late improvement windows must belong to the horizon being judged).
Measures per run: `improvement`, region occupancy (world-side counters,
the feature-005 capture instrument), `best_dim`. Comparisons: per-seed
paired margins vs the same-seed random arm at the same (σ, horizon);
sign counts and spreads always reported, means never alone.

**Exit criterion under test (ROADMAP A4, verbatim):** a drive
configuration that beats random exploration on non-uniform ladder worlds
in the majority of seeds at every checkpoint, with the spread reported.
Judged per (σ, horizon): margin > 0 in a strict majority of the 8 seeds,
at all three horizons, at both σ dials.

## E1 — the arms grid (recorded 2026-07-13; 288 runs)

Margins are paired vs the same-seed random arm; Δocc = mean occupancy
delta vs random; sign counts over 8 seeds.

| arm | σ | margin>0 @18/@30/@50 | mean margin @18/@30/@50 | mean Δocc @18/@30/@50 |
|---|---|---|---|---|
| curiosity | 0.2 | 2/8, 2/8, 5/8 | +0.002, −0.007, −0.008 | −0.016, −0.014, −0.010 |
| curiosity | 0.8 | 4/8, 5/8, 4/8 | +0.023, +0.056, +0.011 | **+0.019, +0.013, +0.009** |
| competence | 0.2 | 6/8, 5/8, **4/8** | +0.047, +0.040, +0.037 | −0.093, −0.100, −0.093 |
| competence | 0.8 | 7/8, 5/8, 7/8 | **+0.133, +0.089, +0.101** | −0.043, −0.061, −0.072 |
| blend-25 | 0.2 | 7/8, **3/8**, 6/8 | +0.042, +0.022, +0.037 | −0.086, −0.100, −0.091 |
| blend-25 | 0.8 | 8/8, 7/8, 6/8 | +0.108, +0.093, +0.062 | −0.032, −0.057, −0.068 |
| blend-50 | 0.2 | 5/8, **4/8**, 6/8 | +0.049, +0.044, +0.040 | −0.103, −0.112, −0.123 |
| blend-50 | 0.8 | 8/8, 7/8, 6/8 | +0.114, +0.135, +0.083 | −0.054, −0.079, −0.089 |
| blend-75 | — | *bit-identical to curiosity, all 48 runs* | | |

`best_dim` spreads stay reference-healthy (~3 ± 1) in every arm — no
structural cost of avoidance at these dials.

## The anomaly that became the finding: the blend axis is degenerate

blend-75 reproduced pure curiosity **bit-for-bit across all 48 runs**.
The mechanism is in the drive forms plus one policy line, and it closes
H-blend by dissolution:

Per lookahead candidate, the *only* term that varies is the same novelty
statistic ν: curiosity's per-candidate part is `+ν` (its LP term is
history-shaped, candidate-constant), competence's is `max(0, 1 − ν)`
(its mastery term likewise constant). A weighted sum's candidate
ordering is therefore `(w_cur − w_comp)·ν` wherever ν ≤ 1 — **only the
sign of the weight difference can matter**:

- `w_cur > w_comp` → argmax ν ≡ pure curiosity. Bit-identical
  trajectories (measured: blend-75 ≡ curiosity, 48/48).
- `w_cur < w_comp` → argmin ν ≡ competence's ordering, up to clip ties
  (candidates with ν ≥ 1 all score 0 familiarity; the blend's unclipped
  ν still ranks them) — blend-25 tracks competence closely but not
  bit-identically (measured: margins within ~0.01–0.03).
- `w_cur = w_comp` → every candidate with ν ≤ 1 scores the same;
  `select_action` scans ascending with strict `>`, so **ties collapse to
  action 0**. blend-50 is not a blend: it is mostly-fixed-action drift
  (+ε exploration, + novelty-chasing only when some candidate's ν > 1).

blend-50's strong-noise numbers (8/8, 7/8, 6/8 — the best in the grid)
are therefore a **degenerate-policy artifact worth understanding, not a
blend result**: a repeated single displacement is maximally predictable
experience (concentrated practice in its purest form) and its drift
walks straight out of the region for most worlds (Δocc the most negative
in the grid). A useful warning: never read a blend grid without a
mechanism check.

## Outcome

1. **H-stare: attraction confirmed, harm refuted.** Curiosity is
   measurably pulled toward the noisy region exactly where the noise is
   strong (Δocc +0.9 to +1.9 points at σ=0.8; *negative* at σ=0.2 —
   mild noise doesn't make the region novel enough to attract), but its
   margins never go meaningfully negative: the LP term's
   `max(0, baseline − recent)` flatness in unlearnable regions caps the
   noisy-TV damage, exactly as Doc 05 §3.1 designed. The trap exists;
   the guard works; pure curiosity still doesn't *beat* random here.
2. **H-camp: confirmed in curiosity's favor-reversed form — competence
   avoids and wins where the noise bites.** Occupancy −4 to −10 points
   vs random at every dial; margins strongly positive at σ=0.8
   (+0.09 to +0.13, signs 7/8, 5/8, 7/8) with **no structural cost**
   (best_dim spreads healthy). The camping degeneracy did not
   materialize at these dials — avoidance of the unlearnable half is
   exactly the right policy there.
3. **H-blend: dissolved, not answered.** With the current drive forms
   there is no blend surface to tune — the weight simplex collapses to
   {curiosity, competence, a degenerate tie-corner}. The §5 tuning
   question is closed by mechanism: a *real* blend requires functionally
   independent per-candidate terms, i.e. the predicted-LP /
   per-candidate-learnability signal already tagged [O] in Doc 05 — now
   the only live path to A4's original ambition.
4. **A4 exit criterion, as pre-registered: no configuration passes.**
   At σ=0.8, competence, blend-25, and (degenerately) blend-50 clear
   every horizon; at σ=0.2 every arm misses at least one horizon
   (competence 4/8 @50, blend-25 3/8 @30, blend-50 4/8 @30) — at mild
   non-uniformity the directed-vs-random effect sits inside seed noise
   at reference budgets. Recorded as measured, not amended: the
   criterion demanded both dials, and the honest summary is
   **directedness pays in proportion to how much the world punishes
   indiscriminate experience**.
5. **Practical guidance (for showcases and A4's successor):** on
   strongly non-uniform worlds, `competence` is the measured
   recommendation (19/24 seed-horizon wins, margins ~+0.1); on mildly
   non-uniform worlds no directed policy demonstrably beats random at
   these budgets; the predicted-LP lookahead is the named successor for
   a genuine blend.
