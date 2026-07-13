# Proposed JOURNEY.md chapter — feature 006 (merge-time integration)

This file exists because feature 006 was built in an isolated worktree in
parallel with other work; JOURNEY.md is owned by the main session during
this window. **At merge time**: append the chapter below to JOURNEY.md
(numbering it after whatever chapter is then last), and fold the "Where
things stand" delta into that section. Then delete this file.

---

## Chapter N — Feature 006: the watchable rover world — the product is the watching (2026-07-13)

ROADMAP B1, spec-kit flow in one arc (spec → plan → tasks → implement).
The first artifact whose product is a person standing in front of it: a
deterministic 2D rover world (arena, five seeded circular obstacles, a
rover with pose) built as a **body of named parts** — 5-ray rangefinder,
compass, position beacon, bumper, one drive actuator — composed by the
Doc 02 anatomy layer into exactly the validated reference widths
(obs_dim 10 / n_actions 4, where every scale-rule factor is 1, on
purpose), mounted on the unchanged engine through `world_factory`. One
command, `pra-rover`, serves a built-in live viewer (stdlib
`http.server` + one self-contained canvas page, zero new dependencies):
the rover wanders under the pinned random policy while the brain's own
quantities move on screen — best-frame prediction-error EMA falling,
population breathing, best_dim settling. B1 is the anatomy layer's first
real showcase beyond 1:1 delegation: a newcomer reading the rover source
reads the integration surface they would use for their own hardware.

The load-bearing design decision was **who is allowed to touch the run**.
The viewer observes without perturbing: the world records its own pose
stream (the L1 occupancy-counter precedent — plain value appends, no RNG,
no float work, no locks on the run path), the tap's `bus_factory` captures
the live FrameStore reference while returning the **stock** bus unchanged,
and every derived computation happens in the serving thread on copies,
with torn-read fallback instead of run-path locks. Pacing (`--fps`,
default 50 steps/s ≈ 4.3 min for the full reference schedule) lives in
the *world*, never the viewer — watchability is a property of the demo
run, not of being watched. Byte-identity is proven three ways in tests:
re-run ≡ re-run, viewer-on-under-live-HTTP-polling ≡ viewer-off, paced ≡
unpaced. 223 tests green (30 new), the byte-frozen baseline untouched,
nothing outside `pra.examples` edited but two inert pyproject lines.

Honest numbers from the shipped instrument (single seeds, labeled as
such, unthrottled full runs ≈ 4.6 s): seed 1/2/3 pred-error improvement
0.190/0.280/0.203, best_dim 2/2/2, final populations 15/19/13 — the
brain genuinely learns the rover's sensor stream, and the parsimony
finding recurs on a spatial world: the latent is (x, y, θ) ≈ 3–4
dimensional, and selection again lands at the price-optimal 2, not the
"true" size (SCORER-DIAGNOSIS, now seen on a world with real geometry).
Deliberately out of scope, stated in the spec: drive-directed rover
watching is A4's measured work (the demo claims *predicting*, never
*navigating*); rover-run snapshot/resume byte-identity is unclaimed and
untested; the anatomy is fixed at reference widths. What it opened: the
getting-started experience now exists (`pip install poseres && pra-rover`
— install to watching in well under five minutes), and the rover is a
ready-made testbed body for B2's adapter comparisons and A4's directed
policies. Trail: `specs/006-rover-world/` (spec, research R1–R10,
contracts); commits on branch `006-rover-world`.

---

## "Where things stand" delta (fold in at merge)

- **Phase B**: B1 shipped — `pra-rover` (in-repo 2D rover world through
  the anatomy seam + stdlib live viewer; viewer-on ≡ viewer-off in
  bytes; example run byte-reproducible). B2 (Gymnasium adapter) can
  reuse the rover's tap/viewer wiring for its own demo if wanted.
- The rover is deliberately **not** a `Config.world` member: examples
  mount through the library seam like user worlds; the validation-world
  enum keeps its byte-identity obligations to itself (research R9).
