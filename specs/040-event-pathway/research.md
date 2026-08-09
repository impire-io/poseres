# Research: The Event Pathway (feature 040)

No open unknowns remain — every choice below was either measured in the G3
gate (`hq/01-RESEARCH/motivation-stack/README.md`, episode 0071) or follows a
recorded house precedent. This file records the load-bearing decisions with
their alternatives, per Phase 0.

## D1 — Where the event head lives: FrameStore

**Decision**: The head is owned by `FrameStore`, beside the frames and the
channel-weighting estimator.

**Rationale**: The store is the brain's learning-state owner — the feature-016
precedent put the channel estimator there for the same reason ("channel
quality is a world property, not a frame property; one estimator"). Ownership
there gives snapshot persistence (the store's `state_dict` already travels),
resize colocation (the store's `resize` is the single anatomy-change site),
and zero new SystemState fields.

**Alternatives considered**: (a) an engine-level `_EventHeadState` like
`_AgencyState` — more plumbing (new SystemState field, encode/decode paths,
separate resize hook) for no benefit; (b) policy-owned (the prototype's
shape) — rejected: policies are injected and never persisted, so the head
would forget on every resume, breaking the continuously-learning premise.

## D2 — The learning call site: end of the engine step-loop iteration

**Decision**: The engine calls the head once per executed transition, at the
end of each step-loop iteration, with the loop-local
`(prev_obs, prev_a, obs)` triple — guarded by a store flag so the off path
does no work.

**Rationale**: This is the only site that sees exactly the stream the
measured instrument learned from. The G3 prototype learned policy-side from
consecutive `select_action` observations; the engine's continuous mode
carries the trailing observation into the next virtual episode, so the
boundary transition is a real executed transition. `online_step`'s
`prev_obs` is deliberately `None` at every episode start (chain-break
semantics for frames), so hooking the head there would silently drop ~1/22 of
the measured stream. In episodic mode the loop-local triple never spans a
world reset, so no invalid pair can form — the same one-line site is correct
in both modes (spec FR-004, edge cases).

**Alternatives considered**: (a) inside `store.online_step` — loses the
boundary transitions vs the measured instrument (and in episodic mode the
restriction is right for *frames* because their transition targets are pose
chains, but the head's delta pairs are formed per-iteration and never cross a
reset either way); (b) policy-side like the prototype — see D1(b).

## D3 — Head form: per-action NLMS linear delta models, one dial

**Decision**: Per action `a`: `Δ̂_a(obs) = W_a · [obs, 1]`, update
`W_a += η · (Δ − Δ̂) · x / ‖x‖²`, cold start `W = 0`, no RNG. Config field
`event_head_eta`, default 0.0 (off), validated `0 ≤ η < 2`.

**Rationale**: Exactly the measured G3 instrument — Bar P passed at 0.0081
with this form and η = 0.5; NLMS is provably stable for η < 2 regardless of
input scale; the bias feature makes `‖x‖² ≥ 1` (no epsilon needed, but the
implementation keeps the exact prototype expression). One dial honors the
registration ("a single step-size dial") and the house preference for few
knobs.

**Alternatives considered**: surprise-gated learning-rate scaling (relevant
for G5's rare pulses) — deliberately out of scope; episode 0071's reversal
condition already names the sparse-event regime as the thing that may split
the design later. Ship what was measured.

## D4 — Policy seam: a defaulted `predict_event_delta` on PolicyContext

**Decision**: `PolicyContext` gains
`predict_event_delta: Callable[[int], np.ndarray | None]` with a module-level
no-op default returning `None`. The engine wires a closure over the current
observation when the head is on; the pinned random-baseline path keeps the
inert default (zero work).

**Rationale**: Mirrors `predict_decoded` exactly (per-action, closure over
`obs`); a defaulted field is a keyword-only addition — legal in a minor
release under the feature-035 surface policy; `None`-when-off lets any policy
degrade gracefully (spec FR-005).

**Alternatives considered**: passing the store or head object into the
context — rejected: the context is a read-only *view*, and handing policies a
mutable brain object breaks the seam's discipline.

## D5 — The shipped policy: constructor-parameterized, potential injectable

**Decision**: `CompletionItchPolicy(params, *, kappa, progress_index,
pocket_index, completion_threshold=1/128, potential_of=None)` in
`pra.action.policy`. Value: `drive + (potential_of(a) if given else 0) +
kappa · (progress_after − progress_now)`; completion rule: predicted pocket
delta > threshold → progress_after = 1.0, else
`clip(obs[progress] + Δ̂[progress], 0, 1)`. Draw order, ε/maturity gates,
frames candidate-skip, and lowest-index tie-break identical to
`CuriosityLookaheadPolicy`. Watch counters: `completions_fired`,
`false_completions` (checked against the next observation's realized pocket
delta), `progress_pred_error_ema` (decay 0.99) — bounded, no per-step lists.
Channel indices are validated against the first observation's width (fail
loudly, spec edge case).

**Rationale**: Channel indices and κ are anatomy-specific runtime knowledge —
config would hard-wire one anatomy's layout into the global schema. The
potential term stays caller-injected because the measured hold (clone-step Φ)
is research instrumentation the brain cannot have; product users may inject
an obs-based potential; `None` is honest (G1 measured itch-only at 2/8 — the
docs say so).

**Alternatives considered**: a `policy_mode="itch"` config value — rejected:
it would demand channel indices in `Config`, and the engine cannot construct
the policy without them; the injection seam is the established way every
measured policy ran.

## D6 — Persistence: additive-optional snapshot key, cold-start on absence

**Decision**: The store's `state_dict()` gains an `event_head` entry only
when on (`{"W": ndarray, "updates": int}`); `encode` writes `eh__W` plus a
meta flag; `decode` restores when present. Absent key (old blobs, feature-off
blobs) → cold start on load. Feature-off blobs remain bit-identical to the
pre-040 format.

**Rationale**: The exact `channel_stats` precedent (feature 016), including
the stated-refill rule for enabling the feature on an old blob.

**Alternatives considered**: bumping FORMAT_VERSION — unnecessary; the format
grows additively and old readers are not a supported direction (Doc 0006).

## D7 — Resize: zero-init growth, truncate shrink, no RNG

**Decision**: On anatomy resize the head preserves existing entries
bit-for-bit, appends zero rows/columns for new observation channels and zero
per-action blocks for new actions, truncates on shrink, draws nothing.

**Rationale**: Zero-init means "predicts no change" — the safe cold-start
semantics the head already has; frames must draw growth weights (their
representation needs symmetry breaking), a linear delta head does not, and
not drawing keeps the run's RNG stream untouched by the feature (Article I).

## D8 — Surface & version: additive entries, 1.1.0 → 1.2.0

**Decision**: New inventory entries: `pra.action.policy.CompletionItchPolicy`
(class, drive), `pra.anatomy.minecraft.C1_MINING_INDEX` and
`pra.anatomy.minecraft.C1_POCKET_TOTAL_INDEX` (constants, world-body).
`Config` and `PolicyContext` rows already exist (dataclasses; field additions
are keyword-only-legal). Docs 0005/0007/0008 updated; `pyproject.toml` and
`pra.__version__` to 1.2.0.

**Rationale**: Feature 035's policy: keyword-only additions are legal in
minor releases; everything new is listed or stays internal-by-default. The
engine summary schema is deliberately untouched (spec assumption) — policy
counters are read from the injected policy object, the established telemetry
pattern (`last_was_directed`).

## D9 — Research closure: the G3 rerun on shipped components

**Decision**: After implementation, rerun the G3 confirmatory protocol
(24 seeds, κ = 0.25, H = 5,000) with a scratchpad runner that uses the
shipped `event_head_eta=0.5` engine path and shipped `CompletionItchPolicy`
(clone-step potential injected via `potential_of`, as the gate's hold), and
record all three bars in the topic README the same day.

**Rationale**: Episode 0071's reversal condition names exactly this reading:
"the src-built event head fails to reproduce Bar A at its own gate" reopens
the result. Bar-level reproduction (not byte-level) is the house replication
standard (P0 precedent). The runner stays in the scratchpad per Article III;
only the recorded conclusion lands.
