# Data Model: Multi-Stream Experience

Phase 1 of `plan.md`.

## Config additions (inert by default — SC-002)

| Field | Type / default | Meaning | Validation (FR-008) |
|---|---|---|---|
| `n_streams` | `int = 1` | number of world instances / explorers; 1 = the untouched validated path | `>= 1`; `> 1` rejects `snapshot_every_n_cycles > 0` (research R6 — multi-stream capture is B5) |

`n_streams` rides in snapshots via config-in-force (relevant only to K=1
blobs until B5).

## Engine state (K > 1 only)

- `stream_rngs: list[Generator]` — per-stream generators; stream `k`
  seeded from `SeedSequence(run_seed, spawn_key=(k,))` (uint32-safe, the
  feature-007 derivation pattern), assigned by overwriting the state of
  the generator each world was constructed with.
- `worlds: list[EventSource]` — K instances, each constructed from a
  generator seeded identically with the run seed (same construction draws
  → same structure), then reseeded per stream (research R2).
- `pending: list[np.ndarray | None]` — per-stream carried observation
  (continuous mode; each entry set once by that stream's single boot).
- Episode scheduler: merged episode counter `e`; the acting stream is
  `e mod K`; consolidation every `episodes_per_cycle` merged episodes;
  warmup counts merged episodes (research R3).

Within `online_episode(stream)`: the world, generator, and (continuous)
pending slot of the acting stream; `prev_obs`/`prev_a` are local to the
episode as today — chains cannot cross streams by construction. Births,
proposals, decay keep drawing from the shared brain generator in merge
order (research R1).

K = 1 allocates none of this; the single-stream path is byte-identical.

## Policy/drive wiring (K > 1)

- `policy.select_action(ctx, stream_rng)` — the acting stream's generator
  (ε-gate and random-arm draws are exploration, i.e. stream-owned).
- Agency/drive bookkeeping (`pred_error_history`, `observation_memory`)
  stays run-level (the brain's merged experience), exactly one instance.

## Test instruments

- **Structure-sharing probe**: two streams' worlds produce identical
  clean structure (compare `ladder_readings`/state via the capture
  protocol or first emissions under forced equal actions with aligned
  generator states).
- **Chain-locality probe**: a world wrapper recording `(stream, step)`
  provenance; asserts every transition trained pairs observations of one
  stream (via engine-visible behavior: per-episode locality is structural
  — the test asserts episode→stream assignment follows `e mod K` and no
  observation crosses episodes).
- **Cadence probe**: consolidation positions (in total observation count)
  identical for K=1 and K=4 on the same schedule (SC-003).

## Exit reading artifacts

`specs/009-multi-stream/reading.md`: per-seed table for K ∈ {1, 2, 4} —
improvement, best_dim, final population; paired margins vs K=1;
noninferiority verdict per K (bar pre-registered in research R5); plus
the investigatory continuous-rover table (K ∈ {1, 4}, seeds 1–3).
