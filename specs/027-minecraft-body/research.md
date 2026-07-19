# Feature 027 — research decisions (frozen before code)

- **R1 — reuse the 013 seam whole.** `Ros2Body` is transport-generic in
  fact (declarative specs, control tick, staleness, startup gate,
  telemetry — none of it touches rclpy); the Minecraft adapter is a
  *transport*, not a body. Rejected: a parallel MinecraftBody (code
  duplication of validated semantics); renaming/moving the 013 module
  (churn in validated code for cosmetics — recorded as a possible
  Phase-D cleanup instead).
- **R2 — wire protocol: newline-delimited JSON over TCP,** versioned
  `"pra-mc/1"`. Ops: `hello` (→ channel table name→width, spawn
  confirmation), `tick` (commands + tick_ms → per-channel float
  vectors + tick index), `state` / `load_state` (snapshot seam;
  FakeBridge answers with full world state, the live bridge with a
  stated live-world marker), `bye`. Rejected: WebSocket (adds a
  Python dependency for no gain over a socket), stdio subprocess
  (couples the brain's lifetime to the bridge's; TCP lets either side
  restart independently, which is the C1 restart story).
- **R3 — the channel contract is the observation semantics** (Doc 02
  §3.3: order and meaning are load-bearing), implemented identically
  by both bridges and pinned in `contracts/minecraft-adapter.md`:
  `pose`[5] = (Δx/64, Δz/64, (y−64)/64, sin yaw, cos yaw — Δ from
  spawn, clipped ±1), `vitals`[2] = (health/20, food/20), `env`[4] =
  (light/15, sin ϑ_day, cos ϑ_day, rain), `blocks`[3] = (solid at
  feet-level ahead, solid at eye-level ahead, air below front) —
  **obs_dim 14**, inside the validated envelope (C2 sizing, arc 026).
- **R4 — one actuator, eight commands** (`n_actions` 8): forward,
  back, turn_left(45°), turn_right(45°), jump_forward, dig_ahead,
  place_ahead, idle. Presets are plain mappings (`{"forward": 1.0}`),
  carried verbatim to the bridge — declaration stays data (013
  SC-006). Dig/place act on the block the contract's `blocks` channel
  reads — act and sense line up by construction.
- **R5 — continuous-only against the live world.** The real bridge
  declares `can_reset = False`; episodic mounting fails loudly at the
  factory (the 013 message). FakeBridge is optionally resettable for
  tests. Live mode is Doc 06 §5b class 4 (openly non-reproducible),
  fake mode class 1 — both stated where they hold.
- **R6 — mineflayer for the real bridge,** confined to
  `examples/minecraft/`. Rejected: Python protocol libraries (pyCraft/
  quarry — protocol support lags modern servers), MineRL/Malmo
  (episodic pixel RL platforms; wrong scale envelope and wrong
  lifetime semantics for a continuous deployment). The Node dependency
  is example-only, exactly like Gazebo/Docker in 013.
- **R7 — C1 run configuration (arc 026 applied):** `episode_mode=
  "continuous"`, `weight_norm_cap=1.2` (measured behaviorally free),
  snapshot cadence sized to the ~8 B/step blob growth, population
  expected at the ceiling, resume-from-latest as the restart path.
