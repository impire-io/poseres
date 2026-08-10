"""C1D-LAB — the provisioned life (run plan: hq/02-DESIGN/validate/
C1D-LAB-RUN-PLAN.md, registered before launch).

One brain (G4 graduate seed 1), one continuous world (state persists across
segments), the tapered childhood, 2,000-tick regrowth, the full brain-side
composition. Segmented resume-chain with disk snapshots; stop rules frozen
in the plan; rows to c1d-status.jsonl; stop file c1d-STOP.
"""

from __future__ import annotations

import dataclasses
import json
import time
from pathlib import Path

import numpy as np

import sys

sys.path.insert(0, str(Path(__file__).parent))
import p0_runner as p  # noqa: E402
import parallel_gates as pg  # noqa: E402

from pra.action.policy import PolicyParams  # noqa: E402
from pra.anatomy.minecraft import C1_MINING_INDEX, C1_POCKET_TOTAL_INDEX  # noqa: E402
from pra.persistence.snapshot import decode, encode  # noqa: E402
from pra.persistence.store import InMemorySnapshotStore  # noqa: E402

OUT = Path(__file__).parent
STATUS = OUT / "c1d-status.jsonl"
LATEST = OUT / "c1d-latest.json"
SNAP = OUT / "c1d-snapshot.bin"
STOPFILE = OUT / "c1d-STOP"

SEED = 1
SEG_CYCLES = 2_273  # ~50k steps per segment
TARGET_STEPS = 50_000_000
GOAL_CHAINS = 2_000
FUTILITY_WINDOW = 10_000_000
CHILDHOOD_END = 3_000
REGROW = 2_000
LAM = 0.25
KAP = 0.25


class LifeWorld(pg.MeterWorld):
    """The c1d world rules: tapered childhood + 2,000-tick regrowth."""

    def __init__(self, inner, bridge):
        super().__init__(inner, bridge)
        self._dug_at: dict = {}  # column -> tick it was dug

    def step(self, action):
        obs = self.inner.step(action)
        self.tick += 1
        w = self.bridge.world
        # regrowth: new dug columns get a clock; expired clocks regrow
        for col in list(w.dug):
            if col not in self._dug_at:
                self._dug_at[col] = self.tick
        for col, t0 in list(self._dug_at.items()):
            if self.tick - t0 >= REGROW:
                w.dug.discard(col)
                del self._dug_at[col]
        # the tapered childhood (G4b's dose), one childhood per life
        total = self._total()
        ramp = min(1.0, max(0.0, (self.tick - 1500) / 1500.0))
        self.energy -= self.DECAY * ramp
        if total > self._prev_total:
            self.energy = min(1.0, self.energy + self.FEED)
        self._prev_total = total
        if self.energy <= 0.0:
            self.energy = 0.0
            if self.death_tick is None:
                self.death_tick = self.tick
        return np.append(obs, self.energy)

    def state_dict(self):
        s = super().state_dict()
        s["__regrow"] = [[c[0], c[1], t] for c, t in self._dug_at.items()]
        return s

    def load_state_dict(self, s):
        s = dict(s)
        self._dug_at = {(int(a), int(b)): int(t) for a, b, t in s.pop("__regrow")}
        super().load_state_dict(s)


def make_policy(cfg, goal_xz):
    pol_box: list = []
    policy = pg.CtxItch(
        PolicyParams.from_config(cfg),
        kappa=KAP,
        progress_index=C1_MINING_INDEX,
        pocket_index=C1_POCKET_TOTAL_INDEX,
        potential_of=pg.head_potential(pol_box, goal_xz),
    )
    pol_box.append(policy)
    return policy


def trim(state):
    """Accumulator hygiene at 50M-step scale (recorded in the run plan)."""
    agency = state.agency
    if agency is not None:
        agency = dict(agency)
        for key in ("values", "lp_terms", "novelty_terms"):
            agency[key] = agency[key][-5000:]
    return dataclasses.replace(
        state,
        agency=agency,
        map_fractions=state.map_fractions[-5000:],
        pred_errors=state.pred_errors[-5000:],
        population_by_cycle=state.population_by_cycle[-5000:],
    )


def main():
    goal = np.load(OUT / "p0-graduates" / "goal_obs.npy")
    goal_xz = (float(goal[0]), float(goal[1]))

    if SNAP.exists():  # crash/stop resume
        state = decode(SNAP.read_bytes())
        prior = [json.loads(x) for x in STATUS.read_text().splitlines()] if STATUS.exists() else []
        cum = prior[-1] if prior else {}
        print(f"resuming at cycles_done={state.cycles_done}", flush=True)
    else:
        state = trim(decode((OUT / "g4-graduates" / "seed01.bin").read_bytes()))
        cum = {}
        # the life's world boots fresh ONCE, at birth
        state = dataclasses.replace(state, world_state=None)

    chains_cum = int(cum.get("chains_cum", 0))
    steps_cum = int(cum.get("steps_cum", 0))
    last_chain_step = int(cum.get("last_chain_step", 0))
    seg = int(cum.get("seg", 0))
    stop_reason = None
    seg_in_proc = 0  # process recycling: a ~145MB/segment leak (measured at
    # 5.8GB RSS by segment 40) throttled the run 501->59 steps/s; the
    # snapshot chain makes restarts free, so the wrapper relaunches us

    while stop_reason is None:
        if seg_in_proc >= 20:
            print("RECYCLE after 20 segments", flush=True)
            return 0
        seg_in_proc += 1
        seg += 1
        t0 = time.monotonic()
        cfg = dataclasses.replace(
            state.config,
            n_cycles=state.cycles_done + SEG_CYCLES,
            # ONE snapshot per segment: the teaching config's every-cycle
            # cadence made the in-memory store hold 2,273 growing blobs per
            # segment (measured 13GB RSS, the 501->57 steps/s decline)
            snapshot_every_n_cycles=SEG_CYCLES,
        )
        state = dataclasses.replace(state, config=cfg)
        policy = make_policy(cfg, goal_xz)
        views: list = []
        boxes: list = []
        store = InMemorySnapshotStore()
        pg.run_hop_wrapped(
            SEED, cfg, policy, LifeWorld, resume_state=state, store=store, views=views, boxes=boxes
        )
        world = boxes[-1]
        state = trim(decode(store.read(store.list()[0][0])))

        # per-segment rows (the readings' source of truth)
        n = len(views)
        steps_cum += n
        chains_seg = 0
        log_at = planks_at = None
        counts: dict = {}
        for i, name, delta in p.inv_events(views):
            counts[name] = counts.get(name, 0) + delta
            if name == "oak_log":
                log_at = i
            elif name == "oak_planks" and log_at is not None:
                planks_at = i
            elif name == "stick" and planks_at is not None:
                chains_seg += 1
                last_chain_step = steps_cum - n + i
                log_at = planks_at = None
        chains_cum += chains_seg
        dwell, _, unique = p.dwell_stats(views, window=n)
        row = {
            "seg": seg,
            "steps_cum": steps_cum,
            "chains_seg": chains_seg,
            "chains_cum": chains_cum,
            "last_chain_step": last_chain_step,
            "logs": counts.get("oak_log", 0),
            "sticks": counts.get("stick", 0),
            "cobble": counts.get("cobblestone", 0),
            "dwell_pct": round(dwell, 2),
            "unique": unique,
            "energy": round(world.energy, 3),
            "death_tick": world.death_tick,
            "pred_ema": round(policy.progress_pred_error_ema, 4),
            "steps_per_s": round(n / max(time.monotonic() - t0, 1e-9)),
            "wall": round(time.monotonic() - t0, 1),
        }

        # stop rules, in the registered order
        if world.death_tick is not None:
            stop_reason = f"DEATH at life-tick {world.death_tick}"
        elif chains_cum >= GOAL_CHAINS and steps_cum >= TARGET_STEPS // 2:
            # amended 2026-08-09 pre-fire (seg-1 raw: 131 chains/50k steps —
            # regrowth makes the bare chain count degenerate as a success
            # stop; endurance deciles are the run's registered purpose)
            stop_reason = f"GOAL {chains_cum} chains at {steps_cum} steps"
        elif steps_cum - last_chain_step >= FUTILITY_WINDOW and steps_cum > CHILDHOOD_END:
            stop_reason = "FUTILITY 10M steps without a chain"
        elif STOPFILE.exists():
            stop_reason = "MANUAL stop file"
        elif steps_cum >= TARGET_STEPS:
            stop_reason = "TARGET 50M steps"
        if stop_reason:
            row["stop"] = stop_reason

        with STATUS.open("a") as f:
            f.write(json.dumps(row) + "\n")
        LATEST.write_text(json.dumps(row, indent=1))
        SNAP.write_bytes(encode(state))
        if seg % 20 == 0 or stop_reason or steps_cum % 5_000_000 < 51_000:
            print(f"MILESTONE {json.dumps(row)}", flush=True)

    print(f"C1D_STOPPED {stop_reason} after {steps_cum} steps, {chains_cum} chains", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
