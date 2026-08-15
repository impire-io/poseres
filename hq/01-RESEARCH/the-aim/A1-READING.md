# Bar A1 — the aim is real (live instrument reading, 2026-08-15)

**Verdict: MET, both forms — 11/11 checks PASS on the first run.**
Protocol and rows: [`a1_reading.py`](a1_reading.py),
[`a1-rows.json`](a1-rows.json). World: the native-survival probe world
(n1-minecraft, tick rate 100 — the arms' 5× fabric), V0 stand; scene =
classroom melon one block ahead (glance sector 0), an unpriced stone
one block behind (sector 4), summoned far drops 4 blocks out.

## Phase W — the worth form (`AIM=worth`, born naive)

| Check | Measured |
|---|---|
| W0 handshake | `aim` width 9 beside the survival channels |
| W1 naive book | melon SEEN (dist 0.0625, sig ≠ 0) yet `aim` all zeros |
| W-meal | one scripted meal (food 8 → 16, 4 chained slices) prices the chain: melon 0.068, melon_slice 0.068 — exactly the EMA's own arithmetic, 0.1·(1−0.75⁴) = 0.0684 |
| W-guard | the saturation refill paid nothing (no held use) — book unchanged |
| W2 | priced vs unpriced in ONE sample: `aim` = [1.0, 0, 0, 0, **0**, …] — melon sector 1.0 relative worth, stone sector 0 |
| W3 | plain and ungained: worth identical hungry (Δ = 0 at food 8), senses unfaded (stone drift 0.0) |
| W4 | the drop slot prices: summoned stick 0, summoned melon_slice 1.0 |

## Phase S — the salience form (`AIM=salience`, the SAME book, no new meal)

| Check | Measured |
|---|---|
| S0 persistence | no `aim` channel in the handshake; the book survived the bridge restart via PALATE_FILE (melon 0.068) — the tongue is body state |
| S1 sated plain | f = 0: melon AND stone fully visible (dist 0.0625, sigs full) |
| S2 hungry | food 8 → f = 0.2178: the priced melon sector byte-identical (drift 0.0); the unpriced stone fades exactly by g = 1−f — dist 0.0625 → 0.2667, dist_err 0.0, sig_err 0.0 — the instrument obeys its own formula to the float |
| S3 drops | stick presence 0.7822 = 1−f exactly; melon_slice presence 1.0 |

## Notes carried forward

- The relative book reads 1.0 for BOTH melon and melon_slice — they are
  paid by the same meals, so their prices are equal by construction.
  The whole taught chain lights up, block and item alike: the glance
  leg and the drops leg are both armed by one meal.
- Both forms read correctly through a book written by the OTHER form's
  process — the palate is genuinely form-independent body state.
- Limits (registered at build): the drops sense still selects the
  nearest item, faded or not; an rcon dose landing mid-chew would pay
  the trace (all doses in this reading landed outside a held use, and
  the W-guard check measured exactly that).
