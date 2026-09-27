"""Stage-aware pointing — a rig-level prototype (topic the-arena-revival,
2026-09-27), NOT part of the registered R1 rounds.

Measured at the sibling's round-1 parked state (JOURNEY.md): the shipped
RecipePolicy pointer picks the nearest stored step by POSITION alone, and
on a loop the start and the end are the same corner — so at the lap line
every eligible lap recipe, the next stage's included, points at its own
last step, and the hold keeps the body where it stands. Two rig-level
changes, kernel untouched:

1. The nearest-step search runs over the recipe's STAGE-MATCHED steps only
   (those within `stage_tolerance` of the current observation on every
   declared stage channel) — the same arithmetic the eligibility filter
   already computes, applied to the pointer. With no stage channels the
   class is the parent exactly.
2. The pointer index is tracked PER RECIPE, so a selection flip between
   recipes of unequal length is not an "advance" — the artifact that reset
   the place-keyed stall 430 times in one parked life.

Verify offline:  python sap_policy.py   (reads mc/sib-demos.json + mc/sib-life1.npz)
"""

from __future__ import annotations

import numpy as np
from pra.action.recipe import Recipe, RecipePolicy


class StageAwareRecipePolicy(RecipePolicy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ptr_by_recipe: dict[int, int] = {}

    def _matched_steps(self, ctx, recipe: Recipe) -> list[int]:
        if not self.stage_indices:
            return list(range(len(recipe.steps)))
        obs, tol = ctx.observation, self.stage_tolerance
        idx = [
            i
            for i, step in enumerate(recipe.steps)
            if all(abs(float(step[c]) - float(obs[c])) <= tol for c in self.stage_indices)
        ]
        return idx or list(range(len(recipe.steps)))  # unreachable for an eligible recipe

    def _nearest(self, ctx, recipe: Recipe) -> tuple[int, float]:
        cur = self._pos(ctx.observation)
        cand = self._matched_steps(ctx, recipe)
        dists = [
            max(
                abs(self._pos(recipe.steps[i])[0] - cur[0]),
                abs(self._pos(recipe.steps[i])[1] - cur[1]),
            )
            for i in cand
        ]
        j = int(np.argmin(dists))
        return cand[j], dists[j]

    def _pointed_place(self, ctx, recipe: Recipe):
        n, _ = self._nearest(ctx, recipe)
        ptr = min(n + 1, len(recipe.steps) - 1)
        return self._place_key(self._pos(recipe.steps[ptr]))

    def _point_subgoal(self, ctx, recipe: Recipe):
        n, dist = self._nearest(ctx, recipe)
        if dist > 2.0:
            self.out_of_context += 1
        ptr = min(n + 1, len(recipe.steps) - 1)
        key = id(recipe)
        prev = self._ptr_by_recipe.get(key, -1)
        if ptr > prev and prev >= 0:
            self.advance_events += 1
        self._ptr_by_recipe[key] = ptr
        self._prev_ptr = ptr
        return self._pos(recipe.steps[ptr])


if __name__ == "__main__":
    import dataclasses
    import sys

    sys.argv = ["x"]
    import lc_runner as L
    from pra.action.policy import PolicyParams

    obs_dim = L.set_arm_body("sib")
    stage = L.stage_indices_for("sib", obs_dim)
    mem = L.build_memory("sib")
    cfg = dataclasses.replace(L.R.BASE, obs_dim=obs_dim)
    kw = dict(
        kappa=L.R.KAP,
        progress_index=L.C1_MINING_INDEX,
        pocket_index=L.C1_POCKET_TOTAL_INDEX,
        lambda_r=L.R.LAM,
        label_index=L.R.FOOD,
        futility_k=200,
        futility_w=800,
        stage_indices=stage,
        stage_tolerance=L.STAGE_TOL,
    )
    shipped = L.RecipePolicy(PolicyParams.from_config(cfg), mem, **kw)
    sap = StageAwareRecipePolicy(PolicyParams.from_config(cfg), mem, **kw)

    class Ctx:
        def __init__(s, o):
            s.observation = o

    d = np.load("mc/sib-life1.npz")
    obs, pos = d["obs"], d["pos"]
    parked = [
        i
        for i in range(min(len(obs), len(pos)))
        if abs(obs[i][73] - 1 / 3) < 1e-3
        and int(np.floor(pos[i][0])) == 0
        and int(np.floor(pos[i][2])) == 0
    ]
    ctx = Ctx(obs[parked[len(parked) // 2]])
    o = ctx.observation
    print(f"parked state: laps={o[73]:.3f} pos=({o[0] * 64:.2f},{o[1] * 64:.2f})")
    print("recipe  stages            shipped->place   stage-aware->place")
    for k, r in enumerate(mem.recipes):
        if not shipped._stage_matched(ctx, r):
            continue
        st = sorted({round(float(s[73]), 3) for s in r.steps})
        a, b = shipped._pointed_place(ctx, r), sap._pointed_place(ctx, r)
        print(f"  {k:>3}   {str(st):<18} {str(a):<16} {b}")
    # birth state: laps 0 at the birth stand — both pointers should agree (lap start)
    ctx0 = Ctx(obs[0])
    fwd = [
        sap._pointed_place(ctx0, r)
        for r in mem.recipes
        if r.process and shipped._stage_matched(ctx0, r)
    ]
    print("at birth (laps 0), stage-aware lap pointers ->", fwd)
