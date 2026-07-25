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

**2026-07-26 — pilot: mastery at 130 is settled in every screening
world (PASS, no amendment).** Probe-free h100 runs, pooled per-step
electing-error medians (n = 389–390 per block): dynamics s1/s2/s3
med(121–130) 0.162/0.119/0.188 vs med(160–169) 0.176/0.121/0.199 —
ratios 0.92/0.99/0.95; emission s1/s2/s3 0.170/0.173/0.193 vs
0.171/0.119/0.173 — ratios 0.99/**1.45**/1.12; multiregion s1 0.147 vs
0.131 — ratio 1.12. All ≤ 1.5: the episode-130 mastery point stands as
registered. The pre-shift plateau of the frontier arm sits at ~0.12–0.20
mean electing error (this run family's own scale; not comparable to the
old arcs' windowed cell statistics). Raw: scratchpad
`probing/data/pilot.json`; every run byte-deterministic (I4 machinery).

**2026-07-26 — P0 screening: FAIL on both clauses; the registered
reversal condition fires on both legs.** Ten probe-bearing h100 runs
(six shift cells + no-shift twins s1–3 + multiregion s1), read exactly
as registered.

*Clause (a) — first post-shift probe ≥ 4× (bar), per cell
[measured]:*

| cell | B | pre-probes C (140/150/160) | C at 170 (bar ≥ 4) | later posts (180/190/200) |
|---|---|---|---|---|
| dynamics s1 | 0.190 | 0.90 / 0.94 / 1.08 | **1.08 FAIL** | 0.82 / 0.75 / 0.57 |
| dynamics s2 | 0.148 | 0.59 / 0.95 / 0.60 | **0.87 FAIL** | 0.87 / 0.86 / 0.89 |
| dynamics s3 | 0.191 | 0.91 / 1.08 / 1.16 | **0.84 FAIL** | 1.19 / 1.09 / 1.33 |
| emission s1 | 0.179 | 0.93 / 1.22 / 0.89 | **1.33 FAIL** | 0.79 / 1.03 / 0.66 |
| emission s2 | 0.072 | 1.65 / 0.94 / 0.76 | **1.76 FAIL** | 1.24 / 1.14 / 1.12 |
| emission s3 | 0.170 | 1.05 / 0.84 / 0.76 | **0.92 FAIL** | 0.58 / 0.74 / 0.75 |

*Clause (b) — every pre-shift and benign probe < 2× (bar)
[measured]:* pre-shift probes all pass (max 1.65); the benign tier
does not — no-shift twin s3 reads **2.41** (ep 150) and 2.39 (ep 180);
multiregion s1 violates six times across its 49 probes, to **2.80**
(eps 180/220/230/410/460/600). With world, start state, and action
tape pinned, the brain's own churn alone moves the reading up to
2.8× — **the benign band (max 2.80) sits above the entire shift band
(max 1.76): no threshold separates, so the frozen θ = 3.0 was never
reached and no θ could be.** Confirmation tier not run (registered
read-only-on-pass); P1/P2 not run (conditional).

*The mechanism, from the same captures [measured]:*

1. **Relearning completes inside one episode.** In the first shifted
   episode (169, free-running), within-episode error medians collapse
   early→late: dynamics s1 0.21→0.06, s2 0.23→0.05 (whole-episode
   median 0.054 — at floor during the first 40 shifted steps),
   s3 0.40→0.08; emission s1 0.54→0.08, s2 0.46→0.16, s3 0.64→0.22.
   By probe 170 — the earliest revisit cadence 10 allows — the
   transient is gone.
2. **Election censoring survives the held policy** (mode-specific):
   emission arms halve their electing census on the probe route
   (s1: 14.0 → 6.5 mean electing frames, pre→post; s3: 10.5 → 7.0)
   while the surviving mean stays benign — the ch. 38 censor, intact
   under total route control. Dynamics arms keep electing (fit is
   appearance-based) and relearn instead.
3. **The raw one-step error has < 4× headroom.** Baselines B
   0.07–0.19 sit on the obs-noise floor; even the free-run first
   shifted episode peaks at 3.9× (emission s2, med 0.28 vs B 0.072) —
   the single reading anywhere in these runs that approaches the
   bracket, gone by the next episode.

*The sentence the numbers write [judgment]:* chapter 40 found the
detector's background is the brain itself; this gate adds the twin —
**the detector's window is the brain's own relearning speed.** The
staleness signal lives ~10–30 steps; the earliest scheduled revisit
arrives an episode late; there is nothing left to detect by the time
any probe can run. Active probing controlled everything it promised
to control (I1–I4) and the reading still cannot separate.

*Named, not licensed (the 0058 pattern — each needs its own
registered gate):* a first-transfer-steps statistic (the e = 1
purest-read lesson; context rows here show episode-start noise may
drown it — pre-probe early medians 0.12–0.32 vs post-probe 0.19–0.38,
no clean separation); a censorship-proof per-frame reference read
(record the mastery frames' ids and read those frames' errors on
revisit, electing or not); event-triggered probing (requires the
trigger chs. 39–40 already closed). None runs without fresh
registration; the reversal condition as registered has fired.

Trail: scratchpad `probing/` (runner.py, mechanics_check.py, pilot.py,
p0_screen.py, diag.py, analysis.py; data/p0-*.json.gz +
p0_screen_summary.json), all runs byte-deterministic; instruments stay
out of git per the arc convention — this record is the conclusion.
