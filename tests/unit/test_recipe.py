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


# --- process recipes (feature 046) -------------------------------------------
# A walked loop with no acquisition; the teacher may applaud the ending.


def lap_demo(applause=True):
    seq = [obs(), obs(z=1), obs(z=2), obs(z=1), obs()]
    if applause:
        seq[-1] = seq[-1].copy()
        seq[-1][4] = 1.0
    return seq


def test_process_off_is_off():
    m = RecipeMemory(pocket_index=3, label_index=4)  # default: the pre-046 rule
    assert m.add_demonstration(lap_demo()) is None and m.recipes == []
    on = RecipeMemory(pocket_index=3, label_index=4, process=True)
    r_off = m.add_demonstration(demo(with_label_at=3))
    r_on = on.add_demonstration(demo(with_label_at=3))
    assert r_off is not None and not r_off.process and not r_on.process
    assert all(np.array_equal(a, b) for a, b in zip(r_on.steps, r_off.steps, strict=True))
    assert np.array_equal(r_on.terminal, r_off.terminal)


def test_process_requires_label_index():
    with pytest.raises(ValueError):
        RecipeMemory(pocket_index=3, process=True)


def test_process_door_stores_the_walked_path():
    m = RecipeMemory(pocket_index=3, label_index=4, process=True)
    r = m.add_demonstration(lap_demo())
    assert r is not None and r.process
    assert float(r.terminal[4]) == 1.0 and len(r.steps) == 5  # through the applause
    # the 0-of-15 closure: episode 0120's unstorable class now stores
    m15 = RecipeMemory(pocket_index=3, label_index=4, process=True)
    assert sum(m15.add_demonstration(lap_demo()) is not None for _ in range(15)) == 15


def test_process_no_applause_no_recipe():
    m = RecipeMemory(pocket_index=3, label_index=4, process=True)
    assert m.add_demonstration(lap_demo(applause=False)) is None and m.recipes == []


def test_process_applause_at_first_observation():
    m = RecipeMemory(pocket_index=3, label_index=4, process=True)
    seq = lap_demo(applause=False)
    seq[0] = seq[0].copy()
    seq[0][4] = 1.0
    r = m.add_demonstration(seq)
    assert r is not None and r.process and len(r.steps) == 1


def test_process_worth_is_the_label_grammar():
    m = RecipeMemory(pocket_index=3, label_index=4, process=True)
    acq = m.add_demonstration(demo())  # unlabeled acquisition, stored first
    proc = m.add_demonstration(lap_demo())
    silent = _policy(m, label_beta=0.0)
    assert silent._select_recipe(_ctx(obs())) is acq  # drive order: first wins
    voiced = _policy(m, label_beta=0.5)
    assert voiced._select_recipe(_ctx(obs())) is proc  # the teacher's voice elects it
    gated = _policy(m, label_beta=0.0, deficit_index=5, deficit_kappa=0.5)
    sated = obs()
    sated[5] = 1.0
    assert gated._select_recipe(_ctx(sated)) is acq
    assert gated._select_recipe(_ctx(obs())) is proc  # the 042 deficit amplifies


def test_process_walks_like_acquisition():
    # identical positions through each door: subgoal series, hold behavior,
    # and a full stall-poison-revive futility cycle must be twins.
    proc_seq = [obs(), obs(z=1), obs(z=2), obs(z=2)]
    proc_seq[3] = proc_seq[3].copy()
    proc_seq[3][4] = 1.0
    m_acq = RecipeMemory(pocket_index=3, label_index=4)
    m_acq.add_demonstration(demo(with_label_at=3))
    m_proc = RecipeMemory(pocket_index=3, label_index=4, process=True)
    m_proc.add_demonstration(proc_seq)
    assert not m_acq.recipes[0].process and m_proc.recipes[0].process
    pa = _policy(m_acq, futility_k=2, futility_w=3)
    pp = _policy(m_proc, futility_k=2, futility_w=3)
    series_a, series_p = [], []
    for _ in range(8):  # stall -> poison -> dead -> peek -> re-poison
        for p, log in ((pa, series_a), (pp, series_p)):
            p.select_action(_ctx(obs(), event=ZERO), np.random.default_rng(0))
            log.append(p._subgoal)
    assert series_a == series_p
    assert pa.fatigue_events == pp.fatigue_events == 2
    assert pa.revive_events == pp.revive_events == 1
    assert pa.advance_events == pp.advance_events


def test_futility_state_stays_bounded():
    p = _stall_policy(futility_k=1, futility_w=1)
    for _ in range(100):  # poison/revive churn at one place
        p.select_action(_ctx(obs(), event=ZERO), np.random.default_rng(0))
        assert len(p._poisons) <= 1 and (p._stall is None or len(p._stall) == 2)
    assert p.fatigue_events > 10 and p.fatigue_events - p.revive_events in (0, 1)


# --- stage-conditional selection (feature 047) -------------------------------
# Channel 5 doubles as the declared stage sense; process demonstrations carry
# their stage trajectory in their stored steps.


def stage_demo(stages, x0=0.0, label=1.0):
    seq = []
    for i, s in enumerate(stages):
        o = obs(x=x0, z=float(i))
        o[5] = s
        seq.append(o)
    seq[-1] = seq[-1].copy()
    seq[-1][4] = label  # the applause: a process demonstration
    return seq


def _stage_obs(s):
    o = obs()
    o[5] = s
    return o


def test_stage_validation():
    for bad in ((-1,), (1.5,), (float("nan"),)):
        with pytest.raises(ValueError):
            _stall_policy(stage_indices=bad)
    for bad in (-0.1, float("nan"), float("inf")):
        with pytest.raises(ValueError):
            _stall_policy(stage_indices=(5,), stage_tolerance=bad)


def test_stage_off_is_off():
    # default == explicit empty == armed-but-always-matching (pad channel is
    # 0.0 in every step and observation): the 045/046 parity idiom.
    eps = PolicyParams(exploration_epsilon=0.3, lookahead_min_age_cycles=2)
    arms = [
        _stall_policy(params=eps),
        _stall_policy(params=eps, stage_indices=()),
        _stall_policy(params=eps, stage_indices=(5,)),
    ]
    rngs = [np.random.default_rng(7) for _ in arms]
    streams = [
        [p.select_action(_ctx(obs(), event=ZERO), r) for _ in range(30)]
        for p, r in zip(arms, rngs, strict=True)
    ]
    assert streams[0] == streams[1] == streams[2]
    assert rngs[0].bit_generator.state == rngs[1].bit_generator.state
    assert rngs[1].bit_generator.state == rngs[2].bit_generator.state
    assert arms[0].stage_filtered_events == 0 and arms[2].stage_filtered_events == 0


def test_stage_partition_follows_the_demonstration():
    # the 0120 shape: a lap path demonstrated across stages 0-0.5 and a
    # HIGHER-WORTH gate entry demonstrated at 0.75 only. Hard eligibility:
    # the gate's worth never buys it selection out of context.
    m = RecipeMemory(pocket_index=3, label_index=4, process=True)
    lap = m.add_demonstration(stage_demo([0.0, 0.25, 0.5], label=0.5))
    gate = m.add_demonstration(stage_demo([0.75], label=1.0))
    p = _policy(m, stage_indices=(5,))
    for s in (0.0, 0.25, 0.5):  # eligible at every demonstrated span point
        assert p._select_recipe(_ctx(_stage_obs(s))) is lap
    assert p._select_recipe(_ctx(_stage_obs(0.75))) is gate
    assert p._select_recipe(_ctx(_stage_obs(0.4))) is None  # never demonstrated
    assert p.stage_filtered_events > 0


def test_stage_tolerance_boundary():
    m = RecipeMemory(pocket_index=3, label_index=4, process=True)
    m.add_demonstration(stage_demo([0.5]))
    p = _policy(m, stage_indices=(5,), stage_tolerance=0.125)
    assert p._select_recipe(_ctx(_stage_obs(0.625))) is not None  # exactly at
    assert p._select_recipe(_ctx(_stage_obs(0.65))) is None  # just beyond


def test_stage_no_context_degrades_to_parent_no_stall():
    m = RecipeMemory(pocket_index=3, label_index=4, process=True)
    m.add_demonstration(stage_demo([0.5]))
    p = _policy(m, stage_indices=(5,), futility_k=1, futility_w=100)
    base = CompletionItchPolicy(
        NEVER_EXPLORE, kappa=0.25, progress_index=2, pocket_index=3, label_index=4, label_beta=0.5
    )
    o = _stage_obs(0.0)  # a context nobody demonstrated
    for _ in range(5):
        ra, rb = np.random.default_rng(1), np.random.default_rng(1)
        assert p.select_action(_ctx(o, event=ZERO), ra) == base.select_action(
            _ctx(o, event=ZERO), rb
        )
        assert ra.bit_generator.state == rb.bit_generator.state
    assert p.fatigue_events == 0 and p._poisons == {}  # no followed step, no stall


def test_stage_composes_with_futility():
    # eligible = stage-matched AND unpoisoned, each filter removing only its
    # own recipes; expiry does not readmit a recipe the stage excludes.
    m = RecipeMemory(pocket_index=3, label_index=4, process=True)
    m.add_demonstration(stage_demo([0.0, 0.0, 0.0]))  # course at x=0
    m.add_demonstration(stage_demo([0.0], x0=40.0))  # elsewhere, same stage
    p = _policy(m, stage_indices=(5,), futility_k=2, futility_w=3)
    step = lambda o: p.select_action(_ctx(o, event=ZERO), np.random.default_rng(0))  # noqa: E731
    here = _stage_obs(0.0)
    step(here)
    step(here)  # stall budget exhausted at (0, 1)
    assert p.fatigue_events == 1
    step(here)
    assert p._subgoal == (40.0, 0.0)  # stage-matched AND unpoisoned wins
    away = _stage_obs(0.75)
    for _ in range(3):  # nobody demonstrated this stage; the poison expires meanwhile
        step(away)
        assert p._subgoal is None
    assert p.revive_events == 1 and p.fatigue_events == 1
    step(away)
    assert p._subgoal is None  # expired, but still out on stage grounds
    step(here)
    assert p._subgoal == (0.0, 1.0)  # both filters pass again; first-stored wins


def test_stage_process_acquisition_twins():
    # identical positions and stage trajectories through each storage door:
    # stage eligibility must be indistinguishable.
    acq_seq = [obs(), obs(z=1), obs(z=2), obs(z=2, pocket=0.1)]
    proc_seq = [obs(), obs(z=1), obs(z=2), obs(z=2)]
    for o in acq_seq + proc_seq:
        o[5] = 0.5
    proc_seq[3] = proc_seq[3].copy()
    proc_seq[3][4] = 1.0
    m_a = RecipeMemory(pocket_index=3, label_index=4)
    m_a.add_demonstration(acq_seq)
    m_p = RecipeMemory(pocket_index=3, label_index=4, process=True)
    m_p.add_demonstration(proc_seq)
    pa = _policy(m_a, stage_indices=(5,))
    pp = _policy(m_p, stage_indices=(5,))
    for s in (0.0, 0.5, 1.0):
        matched = pa._stage_matched(_ctx(_stage_obs(s)), m_a.recipes[0])
        assert matched == pp._stage_matched(_ctx(_stage_obs(s)), m_p.recipes[0])
        assert (pa._select_recipe(_ctx(_stage_obs(s))) is None) == (
            pp._select_recipe(_ctx(_stage_obs(s))) is None
        )


def test_stage_filtered_counter():
    m = RecipeMemory(pocket_index=3, label_index=4, process=True)
    m.add_demonstration(stage_demo([0.5]))
    p = _policy(m, stage_indices=(5,))
    p._select_recipe(_ctx(_stage_obs(0.5)))
    assert p.stage_filtered_events == 0  # matched: nothing removed
    p._select_recipe(_ctx(_stage_obs(0.0)))
    assert p.stage_filtered_events == 1  # the only unpoisoned recipe, removed
