# scheduled-probing — investigation journey (started 2026-07-26)

**2026-07-26 — θ frozen before any run.** The P1 fire threshold is
frozen now — before the pilot, before any probe exists: **θ = 3.0**,
the midpoint of the registered P0 brackets (benign clause < 2×, shift
clause ≥ 4×), derived from the registration alone so a P0 pass implies
a P1-viable rule and no reading can tune it. Fire = probe contrast
C ≥ 3.0; cadence and detection window as registered in README.md.
Also recorded before any run: the passive arcs captured **frontier-arm**
traces (EMSHIFT-DIAGNOSIS P1), so every run in this topic holds the
drive arm at frontier for comparability.

**2026-07-26 — pilot settledness criterion, frozen before the pilot.**
The h100 config is now pinned from the record (TRANSFERSTALE-DIAGNOSIS):
`policy_mode="curiosity"`, `drive_weights=(("frontier", 1.0),)`,
`n_cycles=100` (625 episodes / 25,000 steps), 017 dials
(`world="shifting"`, `shift_after_steps=6760`, both modes;
`world="multiregion"`, `region_noise_levels=(0.0, 0.3)`); 40-step
episodes, shift boundary at episode 169. The pilot reads probe-free
runs (whose first 6,760 steps are by determinism the shared prefix of
every arm) and judges: **episode-130 mastery is *settled* iff
median electing error over episodes 121–130 ≤ 1.5× the median over
episodes 160–169**, per screening world. Unsettled ⇒ the mastery point
moves later along the measured trajectory (keeping ≥ 2 pre-shift
probes, i.e. no later than episode 150 at cadence 10), amended openly
with the raw numbers here before any shift-cell reading.

**2026-07-26 — instrument built and proven (I-gate) before any reading.**
The runner (scratchpad, zero `src/pra` edits) follows the arcs' own
instrument pattern: a world wrapper (counts resets; records the mastery
episode's start `{latent, obj}` and 40-action tape; at probe resets
restores the recorded start while **preserving** the world's
`steps_emitted` / region counters, so a post-shift probe stays
shifted), a probe policy (delegates to the exact
`CuriosityLookaheadPolicy(PolicyParams.from_config(cfg))` the engine
would build; plays the tape during probes; `last_was_directed=False`
during probes — scripted is not directed), and a class patch of
`FrameStore.online_step` (logs per-step mean electing error and elect
count; reads only, no RNG, no float-order change). Gates: **I1** probe
reset restores saved `{latent, obj}` and preserves `steps_emitted` —
PASS; **I2** probe actions reaching the world equal the tape — PASS;
**I3** a post-shift probe runs with the world reporting shifted=True —
PASS; **I4** two identical runs → identical row logs, tapes, and
engine summary hashes — PASS. Recorded instrument choices: a probe
reset performs the normal inner reset (same draws as any episode),
then restores state (no draws) and emits the restored state's first
observation (one extra obs-noise draw) — downstream RNG therefore
differs from a probe-free run; the run is deterministic and
self-consistent, which is all the protocol requires. Erratum to the
previous entry: probe-bearing arms share their prefix with probe-free
runs only through episode 139 (5,600 steps), not 6,760 — the mastery
recording at 130 is inside the shared prefix either way; the
settledness criterion reads probe-free runs as frozen.
