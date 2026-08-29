"""Feature 041 — recipe memory + recipe policy (measured gate semantics).
Feature 045 — place-keyed futility (episode 0120 measured semantics)."""

from __future__ import annotations

import numpy as np
import pytest

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


# --- futility (feature 045) --------------------------------------------------
# A static body at obs() points every step at place (0, 1) — each selection
# is a no-advance followed step there.

ZERO = lambda a: np.zeros(D)  # noqa: E731


def _stall_policy(params=NEVER_EXPLORE, **kw):
    m = RecipeMemory(pocket_index=3, label_index=4)
    m.add_demonstration(demo(with_label_at=3))
    defaults = dict(
        kappa=0.25, progress_index=2, pocket_index=3, lambda_r=0.25, label_index=4, label_beta=0.5
    )
    defaults.update(kw)
    return RecipePolicy(params, m, **defaults)


def test_futility_validation():
    for bad in (-1, 0.5, float("nan"), float("inf")):
        with pytest.raises(ValueError):
            _stall_policy(futility_k=bad)
    for bad in (0, -3, 2.5, float("inf")):
        with pytest.raises(ValueError):
            _stall_policy(futility_k=1, futility_w=bad)
    assert _stall_policy(futility_k=3.0).futility_k == 3  # int-valued float ok


def test_futility_off_is_off():
    # default == explicit off == armed-but-never-firing: identical action
    # streams and RNG consumption (the 042/043 parity idiom).
    eps = PolicyParams(exploration_epsilon=0.3, lookahead_min_age_cycles=2)
    arms = [
        _stall_policy(params=eps),
        _stall_policy(params=eps, futility_k=0),
        _stall_policy(params=eps, futility_k=10_000),
    ]
    rngs = [np.random.default_rng(7) for _ in arms]
    streams = [
        [p.select_action(_ctx(obs(), event=ZERO), r) for _ in range(30)]
        for p, r in zip(arms, rngs, strict=True)
    ]
    assert streams[0] == streams[1] == streams[2]
    assert rngs[0].bit_generator.state == rngs[1].bit_generator.state
    assert rngs[1].bit_generator.state == rngs[2].bit_generator.state
    off = arms[0]
    assert off.fatigue_events == 0 and off.revive_events == 0
    assert off._poisons == {} and off._futility_step == 0 and off._stall is None


def test_futility_poison_at_k_then_clean_peek():
    p = _stall_policy(futility_k=3, futility_w=4)
    step = lambda: p.select_action(_ctx(obs(), event=ZERO), np.random.default_rng(0))  # noqa: E731
    for _ in range(2):
        step()
    assert p.fatigue_events == 0 and p._subgoal is not None
    step()  # the K-th no-advance step poisons place (0, 1)
    assert p.fatigue_events == 1 and p._poisons == {(0, 1): 7}
    for _ in range(4):  # dead for exactly W selection steps
        step()
        assert p._subgoal is None and p.revive_events == 0
    step()  # the peek: revived, pointing again
    assert p.revive_events == 1 and p._poisons == {} and p._subgoal is not None
    step()
    assert p.fatigue_events == 1  # clean peek: re-poisoning takes K fresh steps
    step()
    assert p.fatigue_events == 2  # ...and lands exactly at K again


def test_futility_advance_resets_stall():
    p = _stall_policy(futility_k=2, futility_w=10)
    for i in range(10):  # alternate: stall at (0,1), then the pointer advances
        o = obs() if i % 2 == 0 else obs(z=1)
        p.select_action(_ctx(o, event=ZERO), np.random.default_rng(0))
    assert p.fatigue_events == 0 and p._poisons == {}


def test_futility_all_poisoned_degrades_to_parent():
    p = _stall_policy(futility_k=1, futility_w=100)
    p.select_action(_ctx(obs(), event=ZERO), np.random.default_rng(0))  # poisons
    base = CompletionItchPolicy(
        NEVER_EXPLORE, kappa=0.25, progress_index=2, pocket_index=3, label_index=4, label_beta=0.5
    )
    o = obs(prog=0.3)
    ev = lambda a: np.array([0, 0, 0.1 * a, 0, 0, 0])  # noqa: E731
    ra, rb = np.random.default_rng(1), np.random.default_rng(1)
    assert p.select_action(_ctx(o, event=ev), ra) == base.select_action(_ctx(o, event=ev), rb)
    assert ra.bit_generator.state == rb.bit_generator.state


def _demo_at(x0):
    seq = [obs(x=x0), obs(x=x0, z=1), obs(x=x0, z=2), obs(x=x0, z=2, pocket=0.1)]
    return seq + [seq[-1]]


def test_futility_cohort_dies_together_place_stays_poisoned():
    # three labeled recipes point through (0, 1); one unlabeled points at
    # (40, 1). Poisoning the shared place must kill the whole cohort in one
    # step (no fallback press — the refuted per-recipe forms) and leave the
    # elsewhere recipe untouched.
    m = RecipeMemory(pocket_index=3, label_index=4)
    for _ in range(3):
        m.add_demonstration(demo(with_label_at=3))
    m.add_demonstration(_demo_at(40))
    p = _policy(m, futility_k=2, futility_w=50)
    step = lambda: p.select_action(_ctx(obs(), event=ZERO), np.random.default_rng(0))  # noqa: E731
    step()
    assert p._subgoal == (0.0, 1.0)  # the labeled cohort wins selection
    step()  # K-th stalled step: (0, 1) poisoned
    assert p.fatigue_events == 1 and (0, 1) in p._poisons
    assert all(isinstance(c, int) for c in next(iter(p._poisons)))  # place-keyed, no recipe state
    step()
    assert p._subgoal == (40.0, 1.0)  # eligibility falls to the elsewhere recipe, unchanged


def test_futility_poison_sticks_to_place_not_recipe():
    p = _stall_policy(futility_k=2, futility_w=50)
    step = lambda o: p.select_action(_ctx(o, event=ZERO), np.random.default_rng(0))  # noqa: E731
    step(obs())
    step(obs())  # poisons (0, 1)
    assert p.fatigue_events == 1
    step(obs())
    assert p._subgoal is None  # its pointer still resolves to the poisoned place
    step(obs(z=2))  # the body moved on: the pointer resolves to (0, 2)
    assert p._subgoal == (0.0, 2.0) and p.fatigue_events == 1  # eligible again


def test_futility_state_stays_bounded():
    p = _stall_policy(futility_k=1, futility_w=1)
    for _ in range(100):  # poison/revive churn at one place
        p.select_action(_ctx(obs(), event=ZERO), np.random.default_rng(0))
        assert len(p._poisons) <= 1 and (p._stall is None or len(p._stall) == 2)
    assert p.fatigue_events > 10 and p.fatigue_events - p.revive_events in (0, 1)
