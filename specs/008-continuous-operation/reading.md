# The episodic-vs-continuous reading (feature 008, FR-008)

Recorded 2026-07-13. **Investigatory** — judged by nothing, recorded
whichever way it landed (and it landed against half the pre-registered
guess). Protocol per research R9: same world, same seeds, standard
schedule, pinned random policy; the only change is
`episode_mode="continuous"`.

## Reference world (unbounded latent walk): the world drifts, learning collapses

| seed | episodic impr | continuous impr | Δ | episodic best_dim | continuous best_dim |
|---|---|---|---|---|---|
| 1 | +0.289 | +0.151 | −0.138 | 4 | 1 |
| 2 | +0.393 | +0.152 | −0.242 | 3 | 1 |
| 3 | +0.251 | +0.116 | −0.136 | 3 | 1 |
| 4 | +0.226 | +0.084 | −0.142 | 2 | 1 |
| 5 | +0.307 | +0.100 | −0.207 | 3 | 1 |
| 6 | +0.275 | +0.173 | −0.101 | 2 | 1 |
| 7 | +0.266 | +0.079 | −0.188 | 1 | 1 |
| 8 | +0.284 | +0.111 | −0.173 | 1 | 1 |

Improvement degrades in **8/8 seeds** (mean Δ ≈ −0.166); `best_dim`
collapses to 1 in **8/8** (episodic spread 1–4). Populations stay in the
normal band (24–31 vs 18–42) — the ecology is alive; the world it is
modeling has changed character.

**Mechanism (the R9 pre-registration, half right and half wrong).** As
pre-registered: without per-episode restarts the reference world's latent
is an unbounded random walk — variance grows with every step, `‖latent‖`
grows ~√t, and the tanh emission saturates toward ±1. What the guess got
*wrong*, recorded as required: structure size was predicted to be "less
affected" — instead it collapsed hardest, because near-saturated,
slowly-flipping observations make dim-1 structure price-optimal (the
parsimony machinery working correctly on a world that has genuinely
degenerated).

## Bounded world (the rover arena): the mode is healthy

The discriminator — is the collapse the *mode* or the *world*? The rover
world is bounded (walled arena, feature 006); seeds 1–3, same protocol:

| seed | episodic impr | continuous impr | episodic best_dim | continuous best_dim |
|---|---|---|---|---|
| 1 | +0.190 | +0.237 | 2 | 2 |
| 2 | +0.280 | +0.204 | 2 | 2 |
| 3 | +0.203 | +0.208 | 2 | 2 |

Same improvement band, mixed signs, `best_dim` identical — **no
collapse**. The reference-world result is attributable to unbounded drift
plus emission saturation, not to continuous operation.

## What this reading teaches (guidance for C1/C2 and B4)

1. **The mode works**: deterministic, single-boot, every mechanism in
   place (the contract tests), and healthy learning on a world whose
   dynamics are recurrent.
2. **Continuous deployments need recurrent worlds.** A world whose state
   wanders unboundedly stops being learnable — by anything — when run
   forever. Real deployment targets (game worlds, rooms, arenas) are
   bounded by construction; the reference world was designed as an
   *episodic instrument* and should be read as one.
3. **A drifting world is a new ladder axis if ever needed**: the
   collapse signature (improvement down, best_dim → 1, population
   normal) is now recorded and reproducible in one config change.
