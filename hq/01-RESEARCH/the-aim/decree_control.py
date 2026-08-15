"""The positive control — the hand-wired decree (the-aim README, reversal).

Runs ONLY on the measured double failure (salience below floor at
pilot, worth below floor at arms — A23-READING.md). The decree
replaces exactly the AIM and nothing else: when hungry and a priced
appearance is seen at distance, the wrapper emits turn/forward toward
the highest-priced sector (or the priced drop's bearing); every skill
— dig, collect, hold, eat — stays the taught brain's, which delegates
whenever the body is engaged (progress held, pocket non-empty) or
nothing priced is seen. Same lives protocol as the arms: 6 hungry-born
10,050-step lives, worth form (lookup LIVE), taught tongue restored
per life.

Decree clears A2 (>= 4/6 expressing, median first-eat <= 3,000,
drops leg) -> aiming is real but not learnable in the record's
grammar. Decree fails too -> the gap is not aim at all.

    python decree_control.py run
    python decree_control.py verdict
"""

from __future__ import annotations

import json
import os
import shutil
import statistics
import sys
from pathlib import Path

OUT = Path(__file__).parent
sys.path.insert(0, str(OUT))
sys.path.insert(0, str(OUT.parent / "native-survival" / "arms"))
sys.path.insert(0, str(OUT.parent / "distal-senses"))
import a23_arms as A  # noqa: E402 — indices, drops-leg/explore readers, life shape
import aim_pilot as AP  # noqa: E402
import d23_runner as D  # noqa: E402
import n23_runner as R  # noqa: E402

FOOD = A._index("vitals", "food")
MINING = A._index("mining", "progress")
POCKET = A._index("pocket", "total")
SOLID_AHEAD = A._index("blocks", "solid_ahead")
DROP_PRESENT = A.DROP_PRESENT
DROP_SIN = A._index("drops", "sin_b")
DROP_DIST = A.DROP_DIST
AIM_DROP = A._index("aim", "drop")
AIM_S = [A._index("aim", f"s{k}") for k in range(8)]
GLANCE_D = [A._index("glance", f"s{k}_dist") for k in range(8)]
FWD, TL, TR, JUMP = 0, 2, 3, 4

ARM_LIVES = 6
HUNGRY = 0.75  # food < 15/20 — the flood's own theta, the decree's trigger


HOLD_STEPS = 24  # ~5 blocks of pursuit on a lost ray before giving up
POCKET_GRACE = 400  # steps the taught chain gets to eat what it pocketed


class DecreePolicy:
    """The hand-wired aim over the taught skills. Records the drops
    slice (drops-leg detection) and how often the decree steered.

    Amendment 1 (JOURNEY.md): v1 acted only on frames where the single
    feet-level ray held the target — 45 of 10,050 steps steered. v2
    added the held heading. Amendment 2: v2 still steered only 14
    steps, because the blanket engagement guards gave the taught head
    the turn on nearly every frame — it holds digs most of a life
    (~100–200 completions), and one pickup silenced the decree
    forever. v3 delegates only when the engagement is FOOD-relevant:
    priced food adjacent (the taught dig/collect/eat takes it), or a
    bounded grace while the pocket is non-empty (the taught eat gets
    its window); pointless digs are the decree's to interrupt —
    contact with food is precisely what it exists to force."""

    def __init__(self, inner):
        self.inner = inner
        self.drops: list[tuple[float, float]] = []
        self.steered = 0
        self.delegated = 0
        self.heading = 0  # remaining held-pursuit steps
        self.pocket_grace = POCKET_GRACE

    def _steer(self, o) -> int | None:
        if o[FOOD] >= HUNGRY:
            self.heading = 0
            return None  # sated: the decree is silent
        if o[POCKET] > 0.001:
            self.pocket_grace -= 1
            if self.pocket_grace > 0:
                return None  # the taught chain gets its eating window
            # grace spent, still pocketed and still hungry: not food —
            # the decree resumes steering
        else:
            self.pocket_grace = POCKET_GRACE
        # arrived means ONE block (glance dist 1/16) — the dig's actual
        # reach; amendment 3: 0.13 (two blocks) stopped the walk one
        # block short and the head's dig hit the air cell between
        if o[AIM_S[0]] > 0 and o[GLANCE_D[0]] <= 0.07:
            self.heading = 0
            return None  # priced food adjacent: the taught dig takes it
        # a priced drop first (the collect leg), by its sensed bearing —
        # sin_b positive toward the body's turn_RIGHT side (measured, D1)
        if o[DROP_PRESENT] > 0.5 and o[AIM_DROP] > 0:
            self.heading = HOLD_STEPS
            if o[DROP_SIN] > 0.3:
                return TR
            if o[DROP_SIN] < -0.3:
                return TL
            return JUMP if o[SOLID_AHEAD] > 0.5 else FWD
        # else the highest-priced SEEN glance sector
        k = max(range(8), key=lambda i: o[AIM_S[i]])
        if o[AIM_S[k]] > 0 and o[GLANCE_D[k]] < 1.0:
            self.heading = HOLD_STEPS
            if k == 0:
                return JUMP if o[SOLID_AHEAD] > 0.5 else FWD
            return TR if k <= 4 else TL  # sectors count to the body's right
        if self.heading > 0:
            # blind but pursuing: the ray is single and quantized — keep
            # walking the held heading until it expires or a view returns
            self.heading -= 1
            return JUMP if o[SOLID_AHEAD] > 0.5 else FWD
        return None  # nothing priced in view, no pursuit: no opinion

    def select_action(self, context, rng) -> int:
        o = context.observation
        self.drops.append((float(o[DROP_PRESENT]), float(o[DROP_DIST])))
        action = self._steer(o)
        if action is not None:
            self.steered += 1
            return action
        self.delegated += 1
        return self.inner.select_action(context, rng)

    def __getattr__(self, name):
        return getattr(self.inner, name)


def run_life():
    import dataclasses

    from pra.persistence.snapshot import decode
    from pra.persistence.store import InMemorySnapshotStore

    state = decode(D.TAUGHT.read_bytes())
    cfg = dataclasses.replace(
        state.config,
        steps_per_episode=75,
        n_cycles=state.cycles_done + A.LIFE_CYCLES,
        snapshot_every_n_cycles=state.cycles_done + A.LIFE_CYCLES,
    )
    policy = DecreePolicy(D.make_policy(cfg, kd=R.KD))
    views: list[dict] = []
    store = InMemorySnapshotStore()
    R.run_engine(
        cfg, policy, dataclasses.replace(state, config=cfg), store, views, R.live_transport
    )
    return views, policy


def run() -> None:
    rows = []
    out = OUT / "decree-rows.json"
    if out.exists():
        rows = json.loads(out.read_text())
        print(f"decree: resuming at life {len(rows) + 1}", flush=True)
    for life in range(len(rows) + 1, ARM_LIVES + 1):
        shutil.copy(A.TAUGHT_PALATE, A.PALATE)
        os.environ["AIM_ABLATE"] = ""  # the lookup is LIVE — the decree reads it
        bridge = AP.start_bridge("worth")
        try:
            D.hungry_newborn()
            views, policy = run_life()
        finally:
            bridge.terminate()
            bridge.wait(timeout=10)
        chains = D.chains_of(views)
        row = {
            "arm": "decree",
            "life": life,
            **chains,
            "satiated": max((v.get("food", 0) for v in views), default=0) >= 17,
            "expressed": chains["chains"] >= 1
            and max((v.get("food", 0) for v in views), default=0) >= 17,
            "drops_leg": A.drops_leg(views, policy.drops),
            "steered": policy.steered,
            "delegated": policy.delegated,
            "food_min": min((v.get("food", 0) for v in views), default=None),
            "food_max": max((v.get("food", 0) for v in views), default=None),
            **A.explore(views),
        }
        rows.append(row)
        out.write_text(json.dumps(rows, indent=1))
        print(f"LIFE {json.dumps(row)}", flush=True)
    print("DECREE_ARM_COMPLETE", flush=True)


def verdict() -> None:
    rows = json.loads((OUT / "decree-rows.json").read_text())
    expressing = [r for r in rows if r["expressed"]]
    eats = [r["first_eat"] for r in expressing if r["first_eat"] is not None]
    med = statistics.median(eats) if eats else None
    clears = (
        len(expressing) >= 4
        and med is not None
        and med <= 3000
        and sum(1 for r in expressing if r["drops_leg"]) >= 1
    )
    print(
        json.dumps(
            {
                "expressing": len(expressing),
                "median_first_eat": med,
                "drops_leg_lives": sum(1 for r in expressing if r["drops_leg"]),
                "clears_A2": clears,
            },
            indent=1,
        )
    )


def main() -> int:
    phase = sys.argv[1] if len(sys.argv) > 1 else ""
    if phase == "verdict":
        verdict()
        return 0
    if phase != "run":
        raise SystemExit("usage: decree_control.py run|verdict")
    print("world:", R.rcon("tick", "rate", "100"), flush=True)
    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
