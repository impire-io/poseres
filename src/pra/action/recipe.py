"""Recipe memory and the recipe-following policy (feature 041).

Measured provenance — the recipe-reach gate (episode 0076): reach is
*taught*. A demonstration carries the steps, not just the ingredients; a
recipe is the remembered observation sequence of a demonstrated success,
its ending optionally marked by the parent's sensed applause (the label).
The shipped policy walks the most-valued recipe's stepping stones with the
event head's own predicted positions (the Doc-0009 hold form, chained) and
lets the completion itch do the work at each station. Measured at 24-seed
power: transmission 24/24 against a 0/24 label-alone floor, own chains
held at bar, 20/24 provably recipe-led.

Recipes are policy-side state, deliberately not snapshot state in v1: they
are reconstructible from kept demonstrations (the feature-041 spec records
the assumption).

Place-keyed futility (feature 045; the-long-carry, episode 0120): without
a disconfirmation pathway the selection argmax is stateless and the body
pressed a closed gate for 4,672 of 6,000 life-steps. The measured repair
(rig prototype K=200/W=800: parking abolished, the revive-peek-wander
loop emerged, first brain-driven lap crossings) ships here keyed to the
PLACE — a stalled pointer poisons the quantized subgoal it points at, and
every recipe currently pointing there is ineligible together until the
poison expires. Both refuted forms carried numbers: per-recipe erosion
thrashed at the poison boundary (556 die/revive events in one life) and
per-recipe hysteresis fell back through the cohort of near-identical
recipes. Futility state follows the recipe rule above: policy-side, not
snapshot state.

Process recipes (feature 046; episode 0120, design 0021 rung 2): the
gain requirement made a taught PATH unstorable as behavior — the larder
arena's fifteen lap demonstrations stored nothing. ``RecipeMemory``
grows a second, opt-in door (see its docstring): an applauded gainless
demonstration stores marked ``process``, worth spoken through the
shipped label/deficit grammar, the policy unchanged — one vocabulary,
two ways in.

Stage-conditional selection (feature 047; episode 0120, design 0021
rung 3 — the ladder's last): a declared stage sense was structurally
inert because a sense reached selection only through the terminal's
drive value, and the world's own reset zeroed it there (the sibling
arm: zero-zero at n = 8). Shipped as hard eligibility on the
demonstrated trajectory (see ``RecipePolicy``): the teacher's
demonstrations partition behavior by context with no new storage, and
a composed tier can speak through the same pathway by writing carried
stage into observation. With this the 0021 ladder is complete; whether
the stack walks the larder loop is the arena revival's question.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from pra.action.policy import CompletionItchPolicy, PolicyContext, PolicyParams

__all__ = ["Recipe", "RecipeMemory", "RecipePolicy"]


@dataclass(frozen=True)
class Recipe:
    """One demonstrated success: the observation steps through its terminal."""

    steps: tuple  # tuple[np.ndarray, ...] — the witnessed sequence
    terminal: np.ndarray  # the ending that gets valued (max-label or last gain)
    process: bool = False  # feature 046: an applauded ending, nothing acquired


class RecipeMemory:
    """Extracts and holds recipes from demonstration observation sequences.

    ``pocket_index`` is the sensed acquisition channel (a gain marks a
    success); ``label_index``, when given, is the sensed approval channel —
    the terminal becomes the max-label observation (the applauded ending),
    else the final pocket-gain observation.

    Process recipes (feature 046; the-long-carry episode 0120, design 0021
    rung 2): with ``process=True`` (requires ``label_index``) a gainless
    demonstration whose sequence carries a strictly positive label stores
    as a PROCESS recipe — terminal = the applauded observation (the same
    max-label/latest-tie rule), steps = the walked path through it, the
    record marked ``process``. Gainless without applause still stores
    nothing: a recipe remains a demonstrated something — an acquisition or
    an applauded ending. ``process=False`` (default) is the exact pre-046
    rule; the acquisition door is untouched either way. Worth needs no new
    arithmetic: a process terminal speaks through the shipped label/deficit
    grammar (features 041/042), and episode 0120's fifteen unstorable lap
    demonstrations are the measured absence this closes.
    """

    def __init__(self, pocket_index: int, label_index: int | None = None, *, process: bool = False):
        self.pocket_index = int(pocket_index)
        self.label_index = None if label_index is None else int(label_index)
        self.process = bool(process)
        if self.process and self.label_index is None:
            raise ValueError("RecipeMemory: process=True requires label_index")
        self.recipes: list[Recipe] = []

    def add_demonstration(self, observations) -> Recipe | None:
        """Extract one recipe; ``None`` (and nothing stored) if the sequence
        contains no pocket gain — unless ``process`` is on and an applauded
        ending marks the walked path as a demonstration."""
        seq = [np.asarray(o, dtype=float) for o in observations]
        gains = [
            i
            for i in range(1, len(seq))
            if seq[i][self.pocket_index] > seq[i - 1][self.pocket_index]
        ]
        process = False
        if not gains:
            if not self.process:
                return None
            li = self.label_index
            if not seq or max(float(o[li]) for o in seq) <= 0.0:
                return None
            process = True
        if self.label_index is not None:
            li = self.label_index
            end = max(range(len(seq)), key=lambda i: (float(seq[i][li]), i))
        else:
            end = gains[-1]
        recipe = Recipe(steps=tuple(seq[: end + 1]), terminal=seq[end], process=process)
        self.recipes.append(recipe)
        return recipe


class RecipePolicy(CompletionItchPolicy):
    """The completion itch walking taught paths (the measured gate policy).

    Adds, per directed step: recipe selection — argmax over stored recipes
    of ``drive_value_of(terminal) + label_beta · terminal[label_index]`` —
    then a subgoal at the recipe's nearest-step-plus-one position, held via
    the event head's predicted positions:
    ``lambda_r · (−scale · Chebyshev(pos + Δ̂ₐ[pos], subgoal))``. Position
    indices and scale are anatomy knowledge (constructor parameters; at C1:
    channels (0, 1), scale 64). With an empty memory or the head off the
    added terms are inert and the policy degrades to its parent. Bounded
    watch counters: ``advance_events`` (subgoal pointer progress) and
    ``out_of_context`` (no recipe step within 2 blocks — the parrot watch).

    Place-keyed futility (feature 045; episode 0120 measured, module
    docstring): with ``futility_k > 0``, ``futility_k`` consecutive
    followed steps without pointer advance poison the pointed place —
    the subgoal position rounded to the block grid — for ``futility_w``
    selection steps; recipes whose pointer currently resolves to a
    poisoned place are ineligible, and with none eligible the policy is
    exactly its parent (the wander phase). Expiry is a clean peek: the
    stall count restarts, so re-poisoning takes ``futility_k`` fresh
    steps — the re-check cadence comes from the constants alone. The
    ONLY futility state is per-place (both per-recipe forms are the
    measured failure modes); ``futility_k = 0`` (default) is bit-exact
    pre-045 behavior, RNG stream included. Watch counters:
    ``fatigue_events`` (poisons created), ``revive_events`` (expired).

    Stage-conditional selection (feature 047; episode 0120 measured,
    module docstring): with ``stage_indices`` declared (anatomy
    knowledge — a world's sensed counter or a composed tier's carried
    context), a recipe is eligible only where its demonstrated stage
    trajectory stood: some stored step within ``stage_tolerance`` of the
    current observation on EVERY declared channel. Eligibility is HARD —
    an out-of-context recipe is excluded regardless of worth (the soft,
    value-mediated pathway is the one 0120 proved inert) — and composes
    with futility as one law: eligible = stage-matched AND unpoisoned.
    No eligible recipe degrades to the parent exactly as everywhere
    else, accruing no stall. ``stage_indices = ()`` (default) is
    bit-exact pre-047 behavior, RNG stream included. Watch counter:
    ``stage_filtered_events`` (selection steps where the filter removed
    an otherwise-eligible recipe; measurement-only).
    """

    def __init__(
        self,
        params: PolicyParams,
        memory: RecipeMemory,
        *,
        kappa: float,
        progress_index: int,
        pocket_index: int,
        lambda_r: float,
        position_indices: tuple[int, int] = (0, 1),
        position_scale: float = 64.0,
        completion_threshold: float = 1.0 / 128.0,
        label_index: int | None = None,
        label_beta: float = 0.0,
        deficit_index: int | None = None,
        deficit_kappa: float = 0.0,
        commit_kappa: float = 0.0,
        explore_defers_holds: bool = False,
        futility_k: int = 0,
        futility_w: int = 800,
        stage_indices: tuple[int, ...] = (),
        stage_tolerance: float = 1.0 / 128.0,
    ):
        super().__init__(
            params,
            kappa=kappa,
            progress_index=progress_index,
            pocket_index=pocket_index,
            completion_threshold=completion_threshold,
            potential_of=None,
            label_index=label_index,
            label_beta=label_beta,
            deficit_index=deficit_index,
            deficit_kappa=deficit_kappa,
            commit_kappa=commit_kappa,
            explore_defers_holds=explore_defers_holds,
        )
        self.memory = memory
        self.lambda_r = float(lambda_r)
        self.position_indices = (int(position_indices[0]), int(position_indices[1]))
        self.position_scale = float(position_scale)
        fk, fw = float(futility_k), float(futility_w)
        if not np.isfinite(fk) or fk < 0.0 or fk != int(fk):
            raise ValueError(f"RecipePolicy: futility_k {futility_k} must be a finite integer >= 0")
        if not np.isfinite(fw) or fw <= 0.0 or fw != int(fw):
            raise ValueError(f"RecipePolicy: futility_w {futility_w} must be a finite integer > 0")
        self.futility_k = int(fk)
        self.futility_w = int(fw)
        for c in stage_indices:
            fc = float(c)
            if not np.isfinite(fc) or fc != int(fc) or fc < 0.0:
                raise ValueError(f"RecipePolicy: stage index {c} must be an integer >= 0")
        st = float(stage_tolerance)
        if not np.isfinite(st) or st < 0.0:
            raise ValueError(
                f"RecipePolicy: stage_tolerance {stage_tolerance} must be finite and >= 0"
            )
        self.stage_indices = tuple(int(c) for c in stage_indices)
        self.stage_tolerance = st
        self.advance_events = 0
        self.out_of_context = 0
        self.fatigue_events = 0
        self.revive_events = 0
        self.stage_filtered_events = 0
        self._prev_ptr = -1
        self._futility_step = 0
        self._poisons: dict[tuple[int, int], int] = {}  # place -> last poisoned step
        self._stall: tuple[tuple[int, int], int] | None = None  # (place, count)
        self._ctx: PolicyContext | None = None
        self._subgoal: tuple[float, float] | None = None
        self.potential_of = self._recipe_hold

    def _pos(self, obs) -> tuple[float, float]:
        ix, iz = self.position_indices
        return float(obs[ix]) * self.position_scale, float(obs[iz]) * self.position_scale

    def _place_key(self, pos: tuple[float, float]) -> tuple[int, int]:
        return int(round(pos[0])), int(round(pos[1]))

    def _pointed_place(self, ctx: PolicyContext, recipe: Recipe) -> tuple[int, int]:
        """Where this recipe's pointer currently resolves — the
        side-effect-free twin of :meth:`_point_subgoal`'s arithmetic."""
        cur = self._pos(ctx.observation)
        dists = [
            max(abs(self._pos(o)[0] - cur[0]), abs(self._pos(o)[1] - cur[1])) for o in recipe.steps
        ]
        ptr = min(int(np.argmin(dists)) + 1, len(recipe.steps) - 1)
        return self._place_key(self._pos(recipe.steps[ptr]))

    def _expire_poisons(self) -> None:
        for place in [p for p, last in self._poisons.items() if last < self._futility_step]:
            del self._poisons[place]
            self.revive_events += 1

    def _track_stall(self, place: tuple[int, int], advanced: bool) -> None:
        if advanced:
            self._stall = None
            return
        count = self._stall[1] + 1 if self._stall is not None and self._stall[0] == place else 1
        if count >= self.futility_k:
            # dead through step + futility_w inclusive: exactly futility_w
            # ineligible selection steps, then the peek
            self._poisons[place] = self._futility_step + self.futility_w
            self._stall = None
            self.fatigue_events += 1
        else:
            self._stall = (place, count)

    def _stage_matched(self, ctx: PolicyContext, recipe: Recipe) -> bool:
        """Whether the recipe's demonstrated stage trajectory includes NOW:
        some stored step within tolerance of the current observation on
        every declared stage channel."""
        obs, tol = ctx.observation, self.stage_tolerance
        return any(
            all(abs(float(step[c]) - float(obs[c])) <= tol for c in self.stage_indices)
            for step in recipe.steps
        )

    def _select_recipe(self, ctx: PolicyContext) -> Recipe | None:
        best, best_v = None, -np.inf
        weight = 0.0 if self.label_index is None else self._label_weight(ctx.observation)
        poisons = self._poisons if self.futility_k else None
        stage_removed = False
        for r in self.memory.recipes:
            if poisons and self._pointed_place(ctx, r) in poisons:
                continue
            if self.stage_indices and not self._stage_matched(ctx, r):
                stage_removed = True  # an otherwise-eligible recipe, out of context
                continue
            v = ctx.drive_value_of(r.terminal)
            if self.label_index is not None:
                v += weight * float(r.terminal[self.label_index])
            if v > best_v:
                best, best_v = r, v
        if stage_removed:
            self.stage_filtered_events += 1
        return best

    def _point_subgoal(self, ctx: PolicyContext, recipe: Recipe) -> tuple[float, float]:
        cur = self._pos(ctx.observation)
        dists = [
            max(abs(self._pos(o)[0] - cur[0]), abs(self._pos(o)[1] - cur[1])) for o in recipe.steps
        ]
        n = int(np.argmin(dists))
        if dists[n] > 2.0:
            self.out_of_context += 1
        ptr = min(n + 1, len(recipe.steps) - 1)
        if ptr > self._prev_ptr and self._prev_ptr >= 0:
            self.advance_events += 1
        self._prev_ptr = ptr
        return self._pos(recipe.steps[ptr])

    def _recipe_hold(self, action: int) -> float:
        ctx, goal = self._ctx, self._subgoal
        if ctx is None or goal is None:
            return 0.0
        delta = ctx.predict_event_delta(action)
        if delta is None:
            return 0.0
        ix, iz = self.position_indices
        x = (float(ctx.observation[ix]) + float(delta[ix])) * self.position_scale
        z = (float(ctx.observation[iz]) + float(delta[iz])) * self.position_scale
        return self.lambda_r * -max(abs(x - goal[0]), abs(z - goal[1]))

    def select_action(self, context: PolicyContext, rng) -> int:
        self._ctx = context
        if self.futility_k:
            self._futility_step += 1
            self._expire_poisons()
        adv_before = self.advance_events
        recipe = self._select_recipe(context)
        self._subgoal = None if recipe is None else self._point_subgoal(context, recipe)
        if self.futility_k and self._subgoal is not None:
            self._track_stall(self._place_key(self._subgoal), self.advance_events > adv_before)
        return super().select_action(context, rng)
