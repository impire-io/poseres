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


class RecipeMemory:
    """Extracts and holds recipes from demonstration observation sequences.

    ``pocket_index`` is the sensed acquisition channel (a gain marks a
    success); ``label_index``, when given, is the sensed approval channel —
    the terminal becomes the max-label observation (the applauded ending),
    else the final pocket-gain observation.
    """

    def __init__(self, pocket_index: int, label_index: int | None = None):
        self.pocket_index = int(pocket_index)
        self.label_index = None if label_index is None else int(label_index)
        self.recipes: list[Recipe] = []

    def add_demonstration(self, observations) -> Recipe | None:
        """Extract one recipe; ``None`` (and nothing stored) if the sequence
        contains no pocket gain — an undemonstrated success is not a recipe."""
        seq = [np.asarray(o, dtype=float) for o in observations]
        gains = [
            i
            for i in range(1, len(seq))
            if seq[i][self.pocket_index] > seq[i - 1][self.pocket_index]
        ]
        if not gains:
            return None
        if self.label_index is not None:
            li = self.label_index
            end = max(range(len(seq)), key=lambda i: (float(seq[i][li]), i))
        else:
            end = gains[-1]
        recipe = Recipe(steps=tuple(seq[: end + 1]), terminal=seq[end])
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
        )
        self.memory = memory
        self.lambda_r = float(lambda_r)
        self.position_indices = (int(position_indices[0]), int(position_indices[1]))
        self.position_scale = float(position_scale)
        self.advance_events = 0
        self.out_of_context = 0
        self._prev_ptr = -1
        self._ctx: PolicyContext | None = None
        self._subgoal: tuple[float, float] | None = None
        self.potential_of = self._recipe_hold

    def _pos(self, obs) -> tuple[float, float]:
        ix, iz = self.position_indices
        return float(obs[ix]) * self.position_scale, float(obs[iz]) * self.position_scale

    def _select_recipe(self, ctx: PolicyContext) -> Recipe | None:
        best, best_v = None, -np.inf
        for r in self.memory.recipes:
            v = ctx.drive_value_of(r.terminal)
            if self.label_index is not None:
                v += self.label_beta * float(r.terminal[self.label_index])
            if v > best_v:
                best, best_v = r, v
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
        recipe = self._select_recipe(context)
        self._subgoal = None if recipe is None else self._point_subgoal(context, recipe)
        return super().select_action(context, rng)
