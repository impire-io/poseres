# Chapter 9 — The proposal diagnosis: the ladder was never the bottleneck (2026-07-08)

Took up SCALE-DIAGNOSIS's successor problem (a): can the [O] proposal seam
make rung *count*, not rung patience, the thing that shrinks? A jump-size
dose–response in the live engine (td=20, fixed 500-cycle budget, 8 seeds, six
arms) answered the question asked: selection at scale is **waste-limited, not
reach-limited** — wider explore bands (+8→+32) move nothing (far candidates
die on their transient), while forbidding proposals at or below the incumbent
doubles the fixed-budget median (13.0 vs 6.5, better in 7/8 paired seeds).
The winner, `ClimbingProposalPolicy` (every proposal in `(best, best+4]`),
climbs ~1 rung per maturation window.

Then the full-length confirmation caught the screen being flattering: at 2000
cycles the climbers ride past the truth to `best_dim` 62–74 ≈ `obs_dim` —
the 500-cycle "four seeds at 18–20" was a **lucky-horizon snapshot**, the v3
failure mode, caught this time by the protocol built after v3. Three
mechanism hunts followed, two refuted with data (post-learning EMA grading:
real but flat ~0.02; end-of-episode EMA sampling: flatters everyone, inverts
nothing — the extended scan to dim 80 shows a *healthy* score surface,
minimum at dim 12–16). What stood was arithmetic plus a census (the Doc 06
persistence seam as instrument): every scaled run is a **two-caste ecology**
— a standing conveyor of exactly `spawn_per_cycle × patience` protected
juveniles, plus a mature niche that only dims ≲ 12 can enter, because the
absolute survival bar sits below the achievable at-maturity score of
everything larger. The control's scaled medians (8/10.5/9.5) were never the
score-surface elbow: they are the **maturation filter** — which dims can
train under the bar within one protection window. Under the climbing policy
the niche is empty (census: 29/29 juveniles, zero mature) and `best_dim`
ratchets with the proposals themselves, decoupled from the world.
**`survive_threshold_base` is the seventh scale-variant constant**, named and
open (a reference-preserving effective rule is the candidate); the climbing
policy ships opt-in, correct-once-the-bar-scales; the scan instrument now
trains at the effective learning rate (it probed the divergent regime at
scale). Chapter lesson, again from a new direction: a faster search is also a
sharper instrument — the slow ladder wasn't finding the truth, it was too
slow to reveal that nothing was. Full-scale confirmation across all three
scales: one rate (~0.8–1 rung per maturation window) explains all 24 runs —
best_dim 62–74 / 26–34 / 12–25 at td 20/35/50 (69/29/17 windows), overshooting
a truth of 20 threefold and falling far short of a truth of 50; the td=35
median of 28.5 would have read as a breakthrough in isolation, which is the
whole argument for the multi-scale protocol. Trail:
`hq/02-DESIGN/validate/PROPOSAL-DIAGNOSIS.md`; committed together with this chapter.
