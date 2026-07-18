# Contracts: The Web Dashboard (One Face for Any Brain)

Phase 1 of `plan.md`. Every clause maps to a test in the plan's suites;
the fake transport and urllib are the instruments (FR-008); the worked
example is the real-stack proof (FR-009).

## §1 View-channel contract (tap side)

1. `NatsTap.world_view(kind)` returns an adapter exposing exactly
   `attach_layout` / `record_reset` / `record_step`; the rover mounts via
   `make_rover_body(..., telemetry=adapter)` with zero rover-file edits.
2. Journal shape: `tele.view.static` appears on the first drain after
   `attach_layout` and re-appears at the heartbeat cadence; `tele.view.live`
   carries one payload per recorded reset/step, in mirror order, in the
   tap's seq family (drop derivation applies).
3. Byte-identity: rover run with the view channel on ≡ off ≡ bare (same
   seed, serialized summaries), and the engine generator's bit-state is
   untouched.
4. No world offering a view ⇒ the subjects never appear; the adapter is
   created only when requested (absent unless offered).
5. Run-path budget unchanged: adapter records are plain-value copies into
   the existing bounded buffer — no locks, no RNG, no floats beyond the
   copies.

## §2 Model contract (`DashboardModel` / `RunModel`)

1. Runs materialize from any observed run-scoped message AND from
   discover replies; a run appearing after the model started is listed
   without restart; two runs never cross-talk in any field.
2. Liveness ages monotonically from last received message; the
   dashboard's own control requests do not reset it.
3. Census history is bounded and ordered by seq; `seq_gaps` counts
   observed discontinuities; nothing is interpolated.
4. Malformed payloads on subscribed subjects increment `wire_errors` and
   are skipped — never an exception on the delivery thread.
5. `completed` status stores the summary and is terminal; payloads remain
   the authority over control-reply hints.

## §3 Endpoint contract (`server.py`)

1. `/runs` lists all known runs with state, age, and view presence;
   `/run/<id>/state` serves the full both-modes payload (data-model §3);
   unknown run → 404 with an error body.
2. `/run/<id>/ctrl` forwards the posted command verbatim and returns the
   run's reply verbatim — success and every B6 error reply pass through
   unsoftened; transport failure or timeout returns `{ok: false, error}`
   naming the failure; snapshot uses the long timeout.
3. The page endpoint serves the self-contained HTML (no external assets);
   every quantity the page renders is present in `/state` (asserted
   structurally: the gate reads endpoints, never pixels).
4. The server binds 127.0.0.1, ephemeral port supported, clean shutdown;
   serving beyond localhost requires the operator's explicit flag.

## §4 Observer-safety contract (the roadmap exit)

1. A seeded engine run (tap + view channel) with a live `DashboardModel`
   subscribed and the HTTP server polled by a hammer thread completes
   byte-identical to the bare run — reference world, rover-with-view, and
   a multi-stream continuous config.
2. Attaching and detaching the dashboard mid-run (subscribe, poll, shut
   down while the run continues) changes nothing.
3. A control round-trip through the dashboard's own ctrl endpoint during
   a live run: pause reply surfaced with position, mirrored steps freeze,
   resume continues, snapshot returns the id on a configured run — and
   the paused-and-resumed run is byte-identical to a never-paused one.

## §5 Regression & scope contract

1. Zero engine edits; every existing test (including all B6 suites)
   passes untouched with recorded reference values byte-identical; core
   install unchanged; `dev` unchanged.
2. The gate needs no NATS library, no server, no browser; zero skips.
3. `pra.dash` imports from B6 only `subjects` (names) and the transport
   protocol — asserted structurally (no other `pra.nats` imports).
4. Advanced-mode data completeness holds for a scaled config over the
   fake transport (SC-003's gate half).

## §6 Worked-example contract (outside the gate)

1. `examples/nats/dashboard_demo.py` exits zero only if: the model
   consumed live rover telemetry including the world view; `/runs` and
   `/run/<id>/state` served it; and a pause → frozen → resume → snapshot
   round-trip succeeded through the dashboard's ctrl endpoint — all
   against a real server; the browsable URL is printed for the human.
2. Without the extra or a server: the B6 error grammar, never a
   traceback.
