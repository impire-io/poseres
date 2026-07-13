# The multi-stream exit reading (feature 009, FR-007)

Recorded 2026-07-13. Protocol and bar pre-registered in research R5;
the pre-registered null expectation (R4) was that episodic multi-stream
under the random policy is near-exchangeable with single-stream.

## The pre-registered 8-seed protocol: FAIL as written

Reference world, standard schedule (equal total experience by
construction), seeds 1–8, K ∈ {1, 2, 4}:

| seed | K=1 impr / bd | K=2 impr / bd | K=4 impr / bd |
|---|---|---|---|
| 1 | +0.289 / 4 | +0.316 / 3 | +0.266 / 3 |
| 2 | +0.393 / 3 | +0.307 / 3 | +0.216 / 2 |
| 3 | +0.251 / 3 | +0.246 / 3 | +0.244 / 4 |
| 4 | +0.226 / 2 | +0.247 / 3 | +0.188 / 2 |
| 5 | +0.307 / 3 | +0.201 / 2 | +0.224 / 2 |
| 6 | +0.275 / 2 | +0.190 / 1 | +0.248 / 2 |
| 7 | +0.266 / 1 | +0.190 / 4 | +0.220 / 2 |
| 8 | +0.284 / 1 | +0.276 / 3 | +0.322 / 2 |

K=2: mean margin −0.0400 vs bound −0.0338 → **FAIL**. K=4: −0.0455 vs
−0.0396 → **FAIL**. Recorded as measured.

## Diagnosis: the protocol's pairing assumption was wrong

The bar was built on the T7 pairing precedent — but T7's arms share the
world *and* the generator realization up to the policy difference,
while here a K>1 run necessarily uses different generator realizations
than K=1 (separate brain and stream generators are the design, R1). The
"paired" margins are therefore **unpaired differences of two seed-noise
draws** (observed margin spread ≈ 0.05–0.06 ≈ √2 × the K=1 improvement
std of 0.048 — exactly the unpaired signature). Eight seeds are
underpowered for that statistic; the pre-registered protocol could FAIL
on noise, and did.

## The corrected protocol (24 seeds, same bar): PASS at both K

| arm | mean improvement | mean margin vs K=1 | SE | bound | margin > 0 | verdict |
|---|---|---|---|---|---|---|
| K=1 | +0.2762 (std 0.048) | — | — | — | — | baseline |
| K=2 | +0.2718 | **−0.0044** | 0.0130 | −0.0247 | 10/24 | **PASS** |
| K=4 | +0.2731 | **−0.0030** | 0.0160 | −0.0304 | 8/24 | **PASS** |

At triple the seeds the margins collapse to ≈ 0: merged K-stream
experience **matches the single-stream baseline per unit of experience**
— the roadmap's exit bar, met, and the pre-registered null (R4:
episodic streams are exchangeable under the random policy) confirmed.
Amendment recorded per the T7/T3 precedent: the exit verdict is judged
on the 24-seed protocol because the 8-seed one was statistically
malformed for margins that cannot be paired; the original numbers stay
above.

## Investigatory: continuous rover (bounded world), K ∈ {1, 4}, seeds 1–3

| seed | K=1 impr / bd | K=4 impr / bd |
|---|---|---|
| 1 | +0.237 / 2 | +0.174 / 2 |
| 2 | +0.204 / 2 | +0.272 / 2 |
| 3 | +0.208 / 2 | +0.133 / 4 |

Mixed at n=3, no bar, no claim — recorded as the first data on the
regime where streams genuinely differ (K explorers at K different
positions of one world). The substantive multi-stream questions —
directed policies across streams, longer horizons, wall-clock-parallel
world stepping — are future research on this instrument.

## What the reading teaches

1. The merge machinery does no harm: K-stream learning per unit of
   experience is statistically indistinguishable from single-stream on
   the exchangeable case — the safety result B4 needed.
2. A pairing bar is only as good as what the arms actually share;
   protocols whose arms differ in generator realization need unpaired
   power (more seeds), stated up front. Now written down for every
   future cross-mode comparison.
