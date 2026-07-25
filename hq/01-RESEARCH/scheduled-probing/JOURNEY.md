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
