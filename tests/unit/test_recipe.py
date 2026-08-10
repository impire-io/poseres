"""Feature 041 — recipe memory + recipe policy (measured gate semantics)."""

from __future__ import annotations

import numpy as np

from pra.action.policy import CompletionItchPolicy, PolicyContext, PolicyParams
from pra.action.recipe import RecipeMemory, RecipePolicy

NEVER_EXPLORE = PolicyParams(exploration_epsilon=0.0, lookahead_min_age_cycles=2)
D = 6  # obs: [x, z, progress, pocket, label, pad]


def obs(x=0.0, z=0.0, prog=0.0, pocket=0.0, label=0.0):
    return np.array([x / 64.0, z / 64.0, prog, pocket, label, 0.0])


def demo(with_label_at=None):
    seq = [obs(), obs(z=1), obs(z=2), obs(z=2, pocket=0.1), obs(z=2, pocket=0.1)]
    if with_label_at is not None:
        seq[with_label_at] = seq[with_label_at].copy()
        seq[with_label_at][4] = 1.0
    return seq


def _ctx(o, event=None, drive=None):
    return PolicyContext(
        observation=o,
        n_actions=3,
        best_frame_age=10,
        predict_decoded=lambda a: o,
        drive_value_of=drive or (lambda x: 0.0),
        **({"predict_event_delta": event} if event else {}),
    )


def _policy(memory, **kw):
    defaults = dict(
        kappa=0.25, progress_index=2, pocket_index=3, lambda_r=0.25, label_index=4, label_beta=0.5
    )
    defaults.update(kw)
    return RecipePolicy(NEVER_EXPLORE, memory, **defaults)


# --- memory ------------------------------------------------------------------


def test_extraction_terminal_rules():
    m = RecipeMemory(pocket_index=3, label_index=4)
    r = m.add_demonstration(demo(with_label_at=3))
    assert r is not None and float(r.terminal[4]) == 1.0 and len(r.steps) == 4
    m2 = RecipeMemory(pocket_index=3)  # no label: last gain obs
    r2 = m2.add_demonstration(demo())
    assert float(r2.terminal[3]) == 0.1 and len(r2.steps) == 4


def test_no_gain_no_recipe():
    m = RecipeMemory(pocket_index=3)
    assert m.add_demonstration([obs(), obs(z=1)]) is None and m.recipes == []


# --- policy ------------------------------------------------------------------


def test_selection_prefers_labeled_terminal():
    m = RecipeMemory(pocket_index=3, label_index=4)
    m.add_demonstration(demo())  # unlabeled ending
    labeled = m.add_demonstration(demo(with_label_at=3))
    p = _policy(m)
    assert p._select_recipe(_ctx(obs())) is labeled


def test_pointer_advances_and_counts():
    m = RecipeMemory(pocket_index=3, label_index=4)
    m.add_demonstration(demo(with_label_at=3))
    p = _policy(m)
    zero = lambda a: np.zeros(D)  # noqa: E731
    p.select_action(_ctx(obs(), event=zero), np.random.default_rng(0))
    p.select_action(_ctx(obs(z=1), event=zero), np.random.default_rng(0))
    assert p.advance_events >= 1 and p.out_of_context == 0
    p.select_action(_ctx(obs(x=40, z=40), event=zero), np.random.default_rng(0))
    assert p.out_of_context == 1  # the parrot watch


def test_subgoal_hold_arithmetic():
    m = RecipeMemory(pocket_index=3, label_index=4)
    m.add_demonstration(demo(with_label_at=3))
    p = _policy(m)

    def event(a):
        d = np.zeros(D)
        d[1] = (1.0 / 64.0) if a == 1 else 0.0  # action 1 steps +z
        return d

    picks = {p.select_action(_ctx(obs(), event=event), np.random.default_rng(s)) for s in range(3)}
    assert picks == {1}  # the hold elects the step toward the next stone


def test_empty_memory_degrades_to_parent():
    p = _policy(RecipeMemory(pocket_index=3, label_index=4))
    base = CompletionItchPolicy(
        NEVER_EXPLORE, kappa=0.25, progress_index=2, pocket_index=3, label_index=4, label_beta=0.5
    )
    o = obs(prog=0.3)
    ev = lambda a: np.array([0, 0, 0.1 * a, 0, 0, 0])  # noqa: E731
    ra, rb = np.random.default_rng(1), np.random.default_rng(1)
    assert p.select_action(_ctx(o, event=ev), ra) == base.select_action(_ctx(o, event=ev), rb)
    assert ra.bit_generator.state == rb.bit_generator.state


def test_deficit_gates_recipe_selection():
    # feature 042: the pad channel doubles as the meter (index 5).
    m = RecipeMemory(pocket_index=3, label_index=4)
    first = m.add_demonstration(demo())
    labeled = m.add_demonstration(demo(with_label_at=3))
    p = _policy(m, label_beta=0.0, deficit_index=5, deficit_kappa=0.5)
    sated = obs()
    sated[5] = 1.0
    hungry = obs()  # meter at 0.0 -> full deficit
    assert p._select_recipe(_ctx(sated)) is first
    assert p._select_recipe(_ctx(hungry)) is labeled
