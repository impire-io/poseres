# Contracts: Learned Channel Weighting

## C1 — Off-path identity (the byte-frozen contract)

With `channel_weight_floor == 0.0` (the default):
- no estimator arrays are allocated, updated, or serialized;
- every `FrameGroup` method executes the textually-current expressions —
  zero additional float operations, zero RNG;
- the pinned seed-1 baseline values, the determinism check, the ladder
  degenerate-dial streams, and snapshot blob bytes reproduce exactly;
- a config that sets the feature fields to their inert values explicitly
  serializes byte-equal to a default `Config()` run.

## C2 — Weighted-math contract (one `w`, both legs)

When on, with `w` the store's current weight vector:
- `fit = ‖(recon − obs)⊙w‖₂ / (‖obs⊙w‖₂ + 1e−6)` (numerator AND
  denominator; same form for `honest_pred_err`);
- `encode` consumes `w⊙obs`; `learn_placement` uses `e = (recon − obs)⊙w`
  and `gW1 = clip(ghe ⊗ (w⊙obs))`; `learn_transition` inherits through its
  `encode` calls; `effort` and all pose-space math unchanged;
- an all-ones `w` is bit-equal to the unweighted path; a zero entry
  removes that channel from numerator and denominator exactly;
- `w` changes only at episode boundaries (real or virtual): every
  within-episode judgment happens in one norm.

## C3 — No-RNG contract (exact pairing)

The feature consumes no random draws when on: twin runs (same seed, ON vs
OFF) see identical world observation streams and identical frame-birth
weight draws for the run's whole life. This is load-bearing for E4's
paired reads and is asserted by a twin-engine test.

## C4 — Snapshot contract (Doc 06 §2)

- ON: the five arrays are captured in `state_dict()["channel_stats"]` /
  `chanw__*` keys; a resumed run continues byte-identically to the
  uninterrupted one.
- OFF: blobs are bit-identical to the pre-016 format.
- Pre-016 blob: decodes and resumes byte-identically under its recorded
  config; enabling the feature on such a resume starts the estimator
  fresh (stated, tested).

## C5 — Telemetry contract

`pred_error_early` / `pred_error_late` / `improvement` keep their
unweighted all-channel definitions in every mode. The survival EMAs
(`recon_err_ema` / `pred_err_ema`) accumulate weighted fits when on — they
are what the ecology judges. Summary fields for the feature appear only
when on (agency-fields precedent); the OFF summary serialization is
byte-identical to pre-016.

## C6 — Resize contract

On anatomy growth the estimator extends: new channels get zero stats and
weight 1 (full voice until `ready`); on shrink it truncates. The resize
draw order and existing tensors' bit-identity (feature 004 contract) are
untouched.
