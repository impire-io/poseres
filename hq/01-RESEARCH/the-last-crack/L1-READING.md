# Bar L1 — the release attribution (2026-08-15)

**Verdict: neither registered pattern alone — the trace convicted a
third mechanism, sharper than both suspects: the vote is a knife-edge
and holds have no commitment.** Protocol: [`l1_trace.py`](l1_trace.py);
rows: [`l1-trace.json`](l1-trace.json), [`l1-releases.json`](l1-releases.json),
[`l1-summary.json`](l1-summary.json). 1,500 steps, parked-decree
geometry, the itch's value table replicated read-only per frame.

## The releases (7 total, threshold: a hold past progress 0.1)

| At | Kind | Progress | DIG value | Rival value | Rival |
|---|---|---|---|---|---|
| 251 | directed | 0.011 | −0.28552 | −0.21650 | use_held |
| 387 | directed | 0.546 | −0.95063 | −0.91089 | grid_take |
| 403 | directed | 0.387 | −0.92561 | −0.91929 | forward |
| 428 | directed | 0.227 | −0.97690 | **−0.97688** | grid_take |
| 451 | explore | 0.842 | −0.95842 | −0.97549 | grid_put |
| 479 | explore | **0.994** | −0.94560 | −0.96696 | jump |
| 491 | explore | 0.418 | −0.96917 | −0.98805 | grid_put |

## What the numbers convict

- **The clip: innocent.** 0 of 4 directed releases in the clip's
  predicted band; directed releases scatter at LOW progress
  (0.011–0.546). The clip only shaves the final frame's itch from
  0.008 to ~0.007 — irrelevant against these margins.
- **The knife-edge: convicted.** Directed release margins are 0.069,
  0.040, 0.0063, and **0.00002** — the vote between DIG and its rival
  is frame-to-frame noise (the intrusion flood varies every
  observation by design), and the hold's own per-step margin is only
  κ·Δ̂ ≈ 0.008. A 30-frame live dig must win ~30 consecutive
  near-coin-flips.
- **The ε-gate: convicted as accomplice.** At ALL THREE explore
  releases DIG was WINNING the directed vote — one killed at progress
  0.994, one frame from the world's own break. ε = 0.1 alone gives a
  30-frame hold ~4% survival.

## The convicted fix (both mechanisms, opt-in, constitution I)

`commit_kappa` — incumbency: repeating the previous action while
sensed progress advances earns a bonus set above the largest measured
flip margin (0.1 > 0.069) — hysteresis against the noise.
`explore_defers_holds` — the ε-gate defers while a hold advances.
Defaults 0.0/False are bit-exact shipped behavior, RNG stream
included (the full suite is the proof, run green). The L2 pair then
measured commitment's own degenerate twin — perseveration, a
517-frame DIG lock across breaks — closed by the intention boundary:
a progress collapse (the world's own completion/reset) clears the
incumbent, so incumbency dies with its intention. Unit-tested
(`test_completion_itch_policy.py`, 25 green).
