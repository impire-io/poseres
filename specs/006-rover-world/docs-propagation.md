# Proposed docs propagation — feature 006 (merge-time integration)

Feature 006 was built in an isolated worktree; GETTING-STARTED.md,
README.md, and ROADMAP.md are owned by the main session during this
window. **At merge time**: apply the edits below, then delete this file.

## ROADMAP.md

In "B1. The watchable world (`examples/` + live viewer)": mark shipped —
suggested status note (match the house style used when A1/A3 closed):

> *Shipped (feature 006):* `pra-rover` — a 2D rover world (5-ray
> rangefinder / compass / gps / bumper anatomy at the validated reference
> widths) through the Body seam on the unchanged engine, with a stdlib
> live viewer. Exit met: install → watching in under five minutes
> (default paced run ≈ 4.3 min end to end); example run byte-reproducible
> (tested, including viewer-on ≡ viewer-off under live polling).

## GETTING-STARTED.md

1. In **§1 "Install and prove it works"**, after the `pra-validate`
   command list, add the demo as the first thing to *see*:

   ```markdown
   And to *watch* it learn instead of reading numbers:

   ```bash
   pra-rover        # a browser tab opens: a 2D rover world, live learning telemetry
   ```

   One command starts a paced run and serves a built-in viewer
   (stdlib-only, nothing to install): the rover wanders its arena under
   the pinned random policy while the brain's own quantities move —
   prediction error falling, the frame population breathing, best_dim
   settling. `--fps 0` runs unthrottled; `--seed N` is a fresh map and
   run; the run is byte-reproducible per seed. The rover does not
   navigate (the policy is random — directed behavior is the drive
   research's job); what you are watching improve is the brain.
   ```

2. In **§4 "Hook things up: the Body"**, after the `WorldSensor` 1:1
   example, add one sentence pointing at the richer real example:

   ```markdown
   For a full worked example of a multi-part body — four named sensors
   and an actuator around a real environment — read
   `src/pra/examples/rover/world.py` (the `pra-rover` demo): it is the
   integration surface this section describes, in ~340 lines.
   ```

3. In **§8 "Where to go next"**, mention the demo alongside the suite:

   ```markdown
   `pra-rover` is the watchable proof; the acceptance suite is the
   contract.
   ```

## README.md

If the README carries a quick-start block, add `pra-rover` next to
`pra-validate suite` with the one-line description:

> `pra-rover` — watch a PRA brain learn a 2D rover world, live in your
> browser (one command, zero extra dependencies, byte-reproducible).

## CLAUDE.md (SPECKIT pointer)

If the current-plan pointer is updated on merge, it should point at
`specs/006-rover-world/plan.md` only while 006 is the active feature;
otherwise leave as the main session has it.
