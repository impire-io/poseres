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

## 2026-08-24 — the pilot kills scaffolding v1; v2 registered: the reference lives in the transition

The registered 3-seed instrument pilots did their job. **v1
(observation-augmentation, `aug_obs = [obs, z]`) is dead on its
instruments** [measured, rows in the scratchpad rig]: the arbiter
share never exceeded 0.005 in any arm (R2 tower 0.0005–0.0029; R4
tower 0.0002–0.0018; R4 ref-pose ≤ 0.0004 — even after amending the
arbiter to task-channel error, where tier-2 still read 3–5× worse
than base), so no mechanism could express itself and R0 would have
compared seed noise to seed noise. Matching tier-2's effective
learning rate to base's (the kernel's scale rule had slowed it 3.6×)
made it worse: populations ballooned 26–52 and churned, map rate
fell to 0.93, the best-by-scorer was perpetually a newborn.
Diagnosis: obs-augmentation makes tier-2 reconstruct and predict the
8-channel carrier block alongside the world — every loss diluted
14/6, the carrier's dynamics an unlearnable target, and the scale
rules treating carrier as world. No symmetric knob fixes a
wrong-shaped seam.

**v2, registered before any 24-seed run: the reference enters the
frame's TRANSITION, not its observation.** A tier-2 frame is a plain
obs-space frame — encoder, decoder, losses, channels, and effective
learning rate identical to base — and only its per-action transition
reads `[own pose, z]` (width D+8): another frame's state as a
constituent of this frame's dynamics. Sequence state is a dynamics
problem; appearance never needed the reference. This is 0112's rank
lesson relocated — the interaction between two factors made
explicit. The tower/reference split stays a one-variable switch
inside the transition: tower `z` = base best's pose at obs(t)
(same-step — representation, no information); ref-pose `z` = base
best's pose at obs(t−1) (carried); ref-pred `z` = base's expectation
of t made at t−1. Transition training uses the z the mode would have
had at the sample's origin; the z chain breaks at episode boundaries
exactly where the transition chain does. The cross-tier arbiter is
now the kernel's own survival score (both tiers' EMAs computed by
identical obs-space arithmetic); task-channel EMAs remain telemetry
only. Tier-2 keeps its own generator (spawn_key 7000) and mirrored
lifecycle.

**v2 pilot instruments (3 seeds, R4): healthy.** Map rate 0.9995,
populations 10–19 and stable, arbiter share 0.19–0.61 — the tiers
genuinely compete and a mechanism can now win or lose on its merits.
Scaffolding frozen.

Openness note for T0's verdict: 3-seed ref-pose instrument pilots
ran during scaffolding validation, before the tower's 24-seed
record. They were read for map rates, populations, and arbiter
shares — n=3 acceptance is noise and shaped nothing — but the order
is on the record.

A design lesson that stands whatever R0 says: in this kernel,
input-space composition fails on loss dilution and carrier-as-world
scale rules, not on capacity; the transition is the seam where a
reference enters without touching placement.

## 2026-08-24 — Bar T0 PASS: the tower's record lands first, and it is a real rival

The plain stacked-frame tower, 24 seeds, all five rungs, before any
reference arm's 24-seed measurement [measured; rig median = upper
middle of 24, the frozen rows' own convention]:

| rung | tower acc/1k back (min–med–max) | seeds | flat stack-nc med (seeds) |
|---|---|---|---|
| R(2) | 22.6 – 26.5 – 29.4 | 24/24 | 25.8 (24/24) |
| R(4) | 0.154 – 1.231 – 2.154 | 24/24 | 0.769 (22/24) |
| R(8) | 0 – 0 – 0 | 0/24 | 0.0 (0/24) |
| C(2) | 12.2 – 23.4 – 28.3 | 24/24 | 23.2 (24/24) |
| C(4) | 0.308 – 0.923 – 1.692 | 24/24 | 0.538 (23/24) |

Conformity medians (violations/step): R(2) 0.582, R(4) 0.480, R(8)
0.467, C(2) 0.499, C(4) 0.429 — inside a few thousandths of the flat
arm at every rung. Tier-2 instruments: map ≥ 0.9985, populations
7–17, arbiter share medians 0.33–0.70 — the tower's frames genuinely
hold the predictor a third to two-thirds of directed steps.

The honest headline: **same-step capacity alone already moves
R(4)** — median 0.769 → 1.231, every seed accepting (22→24), one
seed touching 2.154 — while the frozen 2.0 line stands unmet at the
median and R(8) stays at exactly zero. Hierarchy-as-built is not a
straw man on this world; R0 now asks whether carried state beats a
rival that visibly works. (Both arms sit fully inside 0116's
attribution: interior meters move, the wall stands.)
