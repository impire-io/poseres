"""Rover integration (feature 006) — byte-reproducibility, viewer-on ≡
viewer-off under live HTTP polling, endpoint shapes, pacing byte-identity,
and the `pra-rover` command. No browser anywhere (FR-012).

Small budgets throughout: these tests check the instrument, never the
science.
"""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

import pytest

from pra.config import Config
from pra.core.engine import Engine
from pra.examples.rover.cli import main
from pra.examples.rover.viewer import RoverTelemetry, start_viewer
from pra.examples.rover.world import make_rover_body

SMALL = dict(
    warmup_episodes=2,
    n_cycles=2,
    episodes_per_cycle=1,
    steps_per_episode=10,
    horizon_checkpoints=(1, 2),
)


def _run(cfg: Config, seed: int = 1, *, tap=None, step_delay: float = 0.0) -> str:
    def factory(config, rng):
        return make_rover_body(config, rng, telemetry=tap, step_delay=step_delay)

    kwargs = {"bus_factory": tap.bus_factory} if tap is not None else {}
    return Engine(cfg, world_factory=factory, **kwargs).run(seed).serialize()


def _get(url: str, timeout: float = 5.0) -> bytes:
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return response.read()


# --- US1: byte-reproducibility on the unchanged engine (SC-002, FR-009) --------


def test_rover_run_is_byte_reproducible():
    cfg = Config(**SMALL)
    first = Engine(cfg, world_factory=make_rover_body).run(1).serialize()
    second = Engine(cfg, world_factory=make_rover_body).run(1).serialize()
    assert first == second
    summary = json.loads(first)
    assert summary["seed"] == 1
    assert summary["observation_steps"] == 40  # (2 warmup + 2 cycles x 1 episode) x 10


def test_pacing_changes_wall_clock_only():
    cfg = Config(**SMALL)
    assert _run(cfg, step_delay=0.001) == _run(cfg, step_delay=0.0)


# --- US2: the viewer observes without perturbing (SC-003, FR-007) ---------------


def test_viewer_on_equals_viewer_off_under_live_polling():
    cfg = Config(**SMALL)
    bare = _run(cfg, step_delay=0.002)

    tap = RoverTelemetry(cfg)
    server, url = start_viewer(tap, port=0)
    stop = threading.Event()
    polls = {"count": 0}

    def hammer():
        while not stop.is_set():
            try:
                _get(url + "state")
                _get(url + "layout")
                polls["count"] += 1
            except (urllib.error.URLError, ConnectionError, TimeoutError):
                if stop.is_set():
                    break

    poller = threading.Thread(target=hammer, daemon=True)
    try:
        poller.start()
        watched = _run(cfg, tap=tap, step_delay=0.002)
    finally:
        stop.set()
        poller.join(timeout=10)
        server.shutdown()
        server.server_close()

    assert watched == bare
    assert polls["count"] > 0  # the run really was observed while it happened
    assert tap.step == 40 and tap.episode == 4  # the tap saw every step and reset


def test_state_endpoint_shapes_across_the_run_lifecycle():
    cfg = Config(**SMALL)
    tap = RoverTelemetry(cfg)
    server, url = start_viewer(tap, port=0)
    try:
        # before any run: coherent empty state (spec edge case)
        state = json.loads(_get(url + "state"))
        assert state["step"] == 0 and state["pose"] is None and state["trail"] == []
        assert state["learning"] is None and state["done"] is False
        assert json.loads(_get(url + "layout")) == {}

        def factory(config, rng):
            return make_rover_body(config, rng, telemetry=tap)

        summary = Engine(cfg, world_factory=factory, bus_factory=tap.bus_factory).run(1)
        tap.finish(summary)

        page = _get(url)
        assert b"<canvas" in page
        assert b'src="http' not in page and b'href="http' not in page  # self-contained
        assert b"random" in page  # the honesty note ships with the page

        layout = json.loads(_get(url + "layout"))
        assert layout["arena_half"] == 1.0 and len(layout["obstacles"]) == 5
        assert layout["actions"] == ["forward", "reverse", "turn_left", "turn_right"]
        assert layout["sensors"] == ["rays", "compass", "gps", "bump"]

        state = json.loads(_get(url + "state"))
        assert state["step"] == 40 and state["episode"] == 4
        assert len(state["pose"]) == 3 and len(state["trail"]) >= 1
        learning = state["learning"]
        assert learning["population"] >= 1
        assert isinstance(learning["best_dim"], int)
        assert learning["pred_err_ema"] >= 0.0
        assert sum(learning["dims"].values()) == learning["population"]
        assert state["done"] is True
        assert state["final"]["best_dim"] == summary.best_dim

        with pytest.raises(urllib.error.HTTPError) as excinfo:
            _get(url + "nothing-here")
        assert excinfo.value.code == 404
        excinfo.value.close()  # the HTTPError owns the response body
    finally:
        server.shutdown()
        server.server_close()


def test_busy_port_raises_a_naming_error():
    blocker = socket.socket()
    try:
        blocker.bind(("127.0.0.1", 0))
        blocker.listen(1)
        port = blocker.getsockname()[1]
        with pytest.raises(OSError, match=str(port)):
            start_viewer(RoverTelemetry(Config()), port=port)
    finally:
        blocker.close()


# --- US3: the command (FR-008/009/012) -------------------------------------------


def _write_small_config(tmp_path) -> str:
    cfg = tmp_path / "cfg.json"
    cfg.write_text(
        json.dumps(
            {
                **{k: v for k, v in SMALL.items() if k != "horizon_checkpoints"},
                "horizon_checkpoints": [1, 2],
            }
        )
    )
    return str(cfg)


def test_cli_runs_headless_and_writes_the_byte_stable_artifact(tmp_path, capsys):
    cfg_path = _write_small_config(tmp_path)
    out_a = tmp_path / "a" / "rover.json"
    out_b = tmp_path / "b" / "rover.json"
    argv = [
        "--config",
        cfg_path,
        "--seed",
        "1",
        "--fps",
        "0",
        "--port",
        "0",
        "--no-open",
        "--exit-when-done",
    ]

    assert main([*argv, "--json", str(out_a)]) == 0
    output = capsys.readouterr().out
    assert output.index("viewer: http://127.0.0.1:") < output.index("run complete")
    assert "single seed" in output  # the demo caveat is always printed
    assert main([*argv, "--json", str(out_b)]) == 0

    assert out_a.read_bytes() == out_b.read_bytes()  # SC-002: the example artifact
    summary = json.loads(out_a.read_text())
    assert summary["seed"] == 1 and summary["observation_steps"] == 40


def test_cli_exits_2_on_a_busy_port(capsys):
    blocker = socket.socket()
    try:
        blocker.bind(("127.0.0.1", 0))
        blocker.listen(1)
        port = blocker.getsockname()[1]
        code = main(["--port", str(port), "--fps", "0", "--no-open", "--exit-when-done"])
    finally:
        blocker.close()
    assert code == 2
    assert str(port) in capsys.readouterr().err
