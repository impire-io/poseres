# Episode 0053 — The brain that preferred to stand still (2026-07-22)

A dashboard read of the live multi-week run turned into a drive-direction
call. Watching `c1b` (competence-alone, the arc-026 launch posture), the
owner flagged that the bot idles far more than a curious brain should.
The telemetry agreed: over the last 600 steps **idle was 26.7%** — the
single most-chosen action, ~3× uniform — and the four most no-op-like
actions (idle, `place_ahead`, `grid_put`, blocked `forward`) together took
**84%** of steps, while the world-changing ones (`dig_ahead` 7%, turns ~5%,
`jump_forward` 0.3%) were suppressed [measured, dashboard census/steps
window at step ~129k].

The run was **not broken** — it was learning well. A stable mature core
(frames aged ~850–1030 cycles holding prediction error **0.10–0.16**; best
frame pred 0.100), a clean age→error gradient (newborns ~1.0–1.5 → mature
~0.10, the signature of frames improving over their lifetime), healthy
turnover (~1,123 frames born, ~32 alive, ~8.3 spawn/evict per 1,000 steps),
dims 1–6 with no best-dim collapse, 0 seq gaps / 0 wire errors [measured].
It was learning its way into stasis.

**Why:** the C1 drive was competence-alone, and its *only* per-candidate
term in the one-step lookahead is **familiarity** — `mastery` depends only
on error history, so it is identical across all 12 candidate actions
(`engine.py:357-372` builds the drive context with only `observation`
varying; `drive.py` CompetenceDrive). The action the policy picks is
therefore the one whose predicted next observation is *most like recent
experience* — and the outcome most like now is the one that changes the
world least: **stand still**. Competence-as-familiarity degenerates toward
stasis in Minecraft — the competence-side analog of the noisy-TV trap, and
exactly the camping failure the frontier drive was built to avoid
[mechanism-argument, traced end to end in source].

**The call (owner's, accepted):** competence-alone will not reach
exploratory, emergent behavior no matter how long it runs; stop the run and
switch to the **FrontierDrive** — the project's own designed successor
(arc 024, A4 exit met). Frontier rewards moving toward regions where
prediction error is *falling* and scores both mastered (flat-low) and
no-change (stasis) outcomes at ~0, so it structurally cannot camp on idle.
Chosen alone (not blended) for the cleanest read; fresh brain (new run
`c1c`, empty snapshot dir) so the frames train on exploratory experience
from step 0 with no competence-shaped confound.

This **reverses the arc-031 "competence guidance stands" posture for the
Minecraft world** — competence won in *uniformly-learnable* toy worlds
(AGENCY-DIAGNOSIS E5) where practicing the familiar pays; a rich world with
many no-op actions inverts that verdict.

Shipped: a `--drive` selector on `run_c1.py` (default `frontier`) over a
small drive-set map, so the next switch is config not code; the shared
brain unit now passes `--drive ${DRIVE}` and the env files carry it.
Competence run `c1b` stopped at **step 137,103** (learning real to the end).
Fresh `c1c` verified live: stepping ~4/s, `--drive frontier` in the process
args, boot action mix uniform (**idle back to 8.3%**), pred err ~0.55 cold.
The anti-idle *effect* is **not yet measured** — frontier stays silent
until its memory holds ≥40 finite-error entries and the frames age past the
lookahead gate; the real steady-state read is hours out, not at boot
[the 8.3% is the uniform cold-start phase, not yet evidence frontier works].

Reversal condition: once the `c1c` brain matures (frames aged past the
lookahead gate, frontier memory warm — within the first ~day / tens of
thousands of steps), if steady-state **idle share does not fall well below
competence's ~27%** (stays ≥~20%), or frontier degenerates into a single
action (e.g. `forward`-locked >50% because its per-candidate signal is
silent everywhere in this world), or the population/prediction-error stops
improving for want of varied experience — then frontier-alone is refuted
for Minecraft and we escalate to `curiosity+frontier` (novelty as an
always-on anti-idle gradient) or scheduled active probing (Doc 05-level).

Trail: run_c1.py `--drive`, `deploy/units/pra-brain@.service` +
`deploy/experiments/c1*.env`; diagnosis mechanism in `core/engine.py`
(policy context) and `motivation/drive.py`; competence run `c1b` archived
under S3 `pra/v1/c1b/` (final step 137,103), fresh run `c1c` live under
`pra/v1/c1c/`; commit c3e83c1.
