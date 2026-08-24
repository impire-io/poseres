# Journey — compositional-frames (started 2026-08-24)

## 2026-08-24 — rig recovered; the tower and the arms registered before any run

The whose-envelope rig is recovered from git history (commit 99b30e0:
frozen `seq.py`, the plain and stack-nc rows) into the session
scratchpad. The kernel stays untouched in git: the composition
prototype patches `pra.core.engine.FrameStore` with a rig-level
subclass; principled kernel changes land only if the topic graduates.

**The scaffolding, shared by the tower and every reference arm — so
each pair of arms differs by exactly one variable:**

- Base tier: the kernel FrameStore exactly, on the engine's own rng
  stream (tier-2 draws from a separate spawn-keyed generator,
  spawn_key 7000 — the base tier stays byte-equivalent to the flat
  arm's).
- Tier-2: a second frame population reading `aug_obs = [obs, z]`,
  where `z` (width Z = 8, zero-padded/truncated pose — births draw
  dims in [2,6), exploration reaches best+4; truncation is a
  registered cost if it bites) is the composition carrier — the one
  thing that differs between arms.
- Tier-2 lifecycle mirrors the engine's exactly: on-demand birth when
  no tier-2 frame maps, aging/eviction/spawn once per offline cycle,
  own DecayPolicy/ProposalPolicy instances at the same config. The
  event head is not duplicated (tier-2 runs with η = 0; the base
  store's head at η = 0.5 is the arm's only head).
- Cross-tier arbiter (registered): the policy's lookahead predictor
  comes from the tier whose best frame carries the lower honest
  obs-space one-step prediction-error EMA — tier-2's trimmed to the
  first obs_dim channels over ‖obs‖, decay 0.9, the same norm shape
  as the base `pred_err_ema` it is compared against. The maturity
  gate applies to the winning frame's own age. Tier-2 decoded
  predictions are trimmed to obs space before the policy sees them;
  progress/pulse indices unchanged.
- Step order (registered): base `online_step` first; `z_now` computed
  from post-step base weights; tier-2 steps on `[obs, z_now]` with
  `prev_aug = [prev_obs, z_prev]` exactly as stored last step — what
  tier-1 actually said at t−1, never recomputed.

**The tower (Bar T0's arm):** `z_now` = the current best base frame's
pose at the *current* observation. Same-step, slot semantics — "the
layer below," no identity, no memory. This is hierarchy-as-built:
strictly a function of obs; it adds representation and no
information.

**The reference arms (Phase A), registered now so the tower is not
shaped to lose later:** identical scaffolding, `z` carried across the
step boundary — *ref-pose*: base best's pose at obs(t−1); *ref-pred*:
base best's predicted next pose from (obs(t−1), a(t−1)). Tower →
ref-pose differs by exactly one variable: same-step vs carried.
Phase A uses slot semantics in every arm; identity-bound references
(a frame owning its referent — the 0117 primitive proper, and the
only form whose eviction lifecycle Bar L0 can measure) are Phase B
for the winning content, measured against its slot twin. The
learned-binding content joins only if pose vs pred is inconclusive:
its simplest learning rule is itself a design variable, and we vary
one thing at a time.

**Protocol for every arm:** stack-nc policy exactly (κ = 0.25,
commitment off, event head η = 0.5 on the base store), W2 on R / DK
on C, 13,000 steps, 24 seeds, continuous mode, the frozen acceptance
rule and conformity meters. Instrument-first: a 3-seed pilot reads
the tier-2 instrument bars (map rate, recon/pred EMAs, arbiter share)
before any 24-seed run; degeneracies are amended openly here first.

**The mechanism hypothesis, stated before the numbers:** the tower
cannot add information (pose = f(obs)); a carried reference widens
the effective window by chaining state across steps — if the wall is
information-starved, carried beats same-step; if it is
representation-starved, the tower suffices and 0117's reversal
fires.
