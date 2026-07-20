# Chapter 23 — Feature 010: snapshot completeness — three debts, one principle, one caught bug (2026-07-13)

ROADMAP B5, the Phase B finisher. Three features had each left one named
hole in the persistence story; all three closed under one principle —
**code from the caller, state from the blob**: grown bodies record and
verify their *current* dimensions (the resuming factory supplies the
grown parts, because tools are code; wrong anatomy fails loudly);
capture-required worlds declare `snapshot_needs_state` and their state
travels in every snapshot (the Gymnasium adapter's reset counter — one
integer at a C4 boundary fully determines every future reseed, so
episodic Gymnasium resume went from silently-divergent to exact,
conditional on the env's own seeded determinism, stated); multi-stream
runs snapshot all stream positions (per-stream generators, world states
where the class requires them, carried observations, the merge
position). Every format addition is optional-with-absent-default —
unresized, K=1, derivable-world blobs are unchanged — and the
feature-009 config rejection is lifted. Doc 06 §5b is the exit's
documentation artifact: what snapshots guarantee per world class,
including the honest fourth class (live services, hardware: **no
world-state guarantee**; the brain persists, the world re-attaches at
boot).

The feature's tests then caught something older than the feature: a
plain-world resume on a fresh schedule diverged from its uninterrupted
run by **one ULP** in `pred_error_late`. The diagnosis walked the usual
ladder — capture doesn't perturb (control), plain worlds diverge too
(control), pre-010 code diverges too (stash control) — and landed on
group order: the blob recorded frame groups *sorted by dim* while the
live store holds them in *birth order*, and group iteration order feeds
per-step float accumulation, so restored runs summed in a different
order. Doc 06's core promise (resume ≡ uninterrupted, in bytes) had a
one-ULP hole since feature 003, invisible to every schedule tested until
now. Fixed by recording group order as lived; old blobs decode
unchanged (their order was lost at write time). The lesson joins the
collection: *byte-identity claims are only as strong as the orders they
preserve* — sorting is a mutation too. Gate: 285 tests green (8 net new).
Phase B closes: the platform the showcases need — watchable, mountable,
unbroken, parallel, persistent — exists end to end.
