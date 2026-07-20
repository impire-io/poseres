# Chapter 34 — The repainted world: the testbed pair closes, and brackets the problem (2026-07-18)

Chapter 33's debt was a world, and it cost one dial: `shift_mode` on the
shifting world. `"dynamics"` stays the recorded 017 behavior
byte-identically; `"emission"` swaps the per-object emission matrices at
the boundary (drawn at construction after all other draws, zero RNG at
shift time) while displacements never change — appearance moves,
territory does not. Swap semantics, dynamics invariance, and state
capture across the shift are unit-tested; the whole gate stays green.

The arc's pre-registered first read completed the picture with a
baseline the next design must beat, and its prediction was honestly
left open between two mechanisms — both turned out true in parts. The
raw-observation place memory (the ch. 33 replay, revision-1 arithmetic,
recorded as such) reads the emission shift *directionally* — post-shift
staleness rises in 2/3 seeds (0.172/0.178 vs ~0.11 background), the
opposite sign from the dynamics shift's 3/3 post-below-pre — because a
repaint leaves every post-shift observation landing on *some* mastered
anchor, while a territory move leaves mastered anchors unvisited. But
sensing is not detecting: ~1.5× background against the 4× bar, one seed
flat. **The testbed pair now brackets the design space with numbers**:
a shift-invariant error memory must clear 4× separation on both modes,
from measured starting points of ~1.5× (emission) and < 1× (dynamics).
That — pose/encoding anchors with spike-robust per-cell statistics,
judged against this bracket — is the successor arc, unchanged in name,
now fully instrumented. Trail: `hq/02-DESIGN/validate/EMSHIFT-DIAGNOSIS.md`;
`specs/020-emission-shift/spec.md`; commit `3500576` and this close.
