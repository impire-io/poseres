# Implementation Plan: The Web Dashboard (One Face for Any Brain)

**Branch**: `015-web-dashboard` | **Date**: 2026-07-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/015-web-dashboard/spec.md`

## Summary

Build ROADMAP B7: one dashboard for any live PRA brain, as a pure consumer
of the B6 surface. A new subpackage `src/pra/dash/` holds the consumer
model (`model.py`: `pra.v1.>` subscription + discovery sweep → one
`RunModel` per run, built from received payloads only), the stdlib HTTP
server (`server.py`: `/`, `/runs`, `/run/<id>/state`, `/run/<id>/ctrl`
with verbatim control-reply forwarding), the single self-contained page
(`page.html`, simple + advanced modes as client tabs, SVG world view), and
the `pra-dash` entry point (real transport behind the existing lazy
import). The one gap the roadmap named is closed on the B6 side of the
fence: `NatsTap.world_view(kind)` returns an adapter with exactly the call
surface the rover world already speaks (`attach_layout` / `record_reset` /
`record_step` — verified at world.py:199-226, 339-340), mirroring a static
part (layout, published on first drain + slow heartbeat) and a live part
(pose/bump per step) through the tap's existing buffer, pump, and
drop-derivation machinery onto two new subjects (`…tele.view.static`,
`…tele.view.live`). The rover mounts unchanged:
`make_rover_body(cfg, rng, telemetry=tap.world_view("rover"))`.

The proofs keep the house discipline: observer safety re-proven at this
layer (a seeded run with tap + view channel + live model + hammered HTTP
server, byte-identical to the bare run, including attach/detach mid-run —
the B1 polling-hammer test, off-process), every endpoint and control path
(success and every error reply) asserted via urllib against scripted
traffic on the fake transport, and the worked example
(`examples/nats/dashboard_demo.py`) driving the real stack headlessly with
the browser URL as the human's reward. Gate: no NATS, no server, no
browser, zero skips, byte-frozen baseline untouched.

## Technical Context

**Language/Version**: Python ≥3.12 (repo `.venv` runs 3.14; unchanged).
**Primary Dependencies**: stdlib only for `pra.dash` (http.server, json,
threading); `pra.nats.subjects` for names and `BusTransport` for the seam;
the `nats` extra only inside `pra-dash`'s real-transport path (lazy, the
B6 error). No new dependencies; `dev` unchanged.
**Storage**: none — the dashboard holds bounded in-memory windows
(census history default 512 readings, trail cap 4000 points client-side);
durable history stays deferred (B6 assumption carried).
**Testing**: pytest — unit (RunModel from scripted payloads: two runs,
malformed frames, gaps, completion, liveness aging), contract (view
channel: journal shape, heartbeat, byte-identity on/off; endpoints via
urllib: `/runs`, state shape for both modes, every ctrl path incl. error
replies and unknown-run 404), integration (the polling-hammer observer
proof incl. rover + view channel and attach/detach; control round-trip
through the dashboard's own ctrl endpoint during a live run; scaled-config
advanced-mode data completeness).
**Project Type**: extends the `pra` package (one new subpackage, additive
tap/subjects extension, tests, example additions).
**Performance Goals**: poll-sized data (censuses, poses); the page polls
at ~4 Hz like the B1 viewer; the model's payload handlers are O(1) dict
updates on the delivery thread.
**Constraints**:
- **Pure consumer** (FR-001): `pra.dash` imports `pra.nats.subjects` and
  the transport protocol only; no B6 internals; no engine imports at all.
- **Byte-frozen reference** (SC-001/SC-006): zero engine edits; tap and
  subjects changes are additive (every existing B6 test passes
  untouched); no new `Config` fields.
- **Observer safety** (FR-007/SC-002): the polling-hammer byte-identity
  test, off-process, incl. rover-with-view vs rover-without vs bare, and
  attach/detach mid-run.
- **Honest rendering** (FR-010): liveness ages monotonically; gaps and
  drops surface in advanced mode; error replies forwarded verbatim;
  malformed wire data → counted `wire_errors`, never a crash.
- **No skipped tests** (FR-008): fake transport + urllib carry everything;
  browser and real server live in the worked example only.
**Scale/Scope**: censuses every ~500 ms and poses every paced step are the
wire volume; the scaled-run claim (SC-003) is data completeness in
advanced mode, not new visualization kinds.

## Constitution Check

Constitution file remains the unfilled template; gating against project
rules (AGENTS.md) and the spec:

| Gate | Requirement | Status |
|---|---|---|
| Regression (SC-001/SC-006) | validated modes byte-identical; core install unchanged | PASS — new leaf subpackage + additive tap/subjects extension; nothing imports `pra.dash` unless the user does |
| Pure consumer (FR-001) | documented B6 surface only; no second transport | PASS — model speaks subjects + the transport seam; control forwarded verbatim through the existing three commands + discover |
| Observer safety (FR-007/SC-002) | byte-identity with dashboard attached, polling, view channel on | PASS — the B1 hammer test off-process; view adapter reuses the tap's proven mirror path (research R2/R5) |
| Honest instrument (FR-010) | staleness, gaps, errors shown; nothing interpolated | PASS — liveness from message age, counters rendered, verbatim replies, `wire_errors` counted (R3/R4) |
| World-view additivity (FR-005/FR-006) | absent unless offered; rover unchanged; unknown kinds degrade | PASS — adapter created only on request; RoverTelemetry call surface reused verbatim; present-but-unrenderable fallback at the page |
| Gate stance (FR-008) | no NATS/server/browser; zero skips | PASS — fake transport + urllib endpoint tests; example carries the real stack (R5/R6) |
| Scope honesty | showcase half out; durable history deferred | PASS — stated in spec assumptions; nothing here renders beyond received payloads |
| Quality gate | ruff + pytest green, none skipped | PASS — gated in tasks |

## Project Structure

### Documentation (this feature)

```text
specs/015-web-dashboard/
├── spec.md, plan.md, research.md, data-model.md, quickstart.md
├── checklists/requirements.md
├── contracts/dashboard.md       # model / view-channel / endpoint / regression contracts
└── tasks.md                     # (/speckit-tasks output)
```

### Source Code (repository root)

```text
src/pra/dash/                  # NEW — the consumer, the server, the page
├── __init__.py                #   public surface re-exports
├── model.py                   #   DashboardModel + RunModel (payloads → state, bounded histories, liveness)
├── server.py                  #   ThreadingHTTPServer: /, /runs, /run/<id>/state, /run/<id>/ctrl (verbatim)
├── page.html                  #   one self-contained page — simple + advanced tabs, SVG world view
└── cli.py                     #   pra-dash entry point (lazy real transport, prints the URL)

src/pra/nats/
├── subjects.py                #   + view_static_subject / view_live_subject (additive)
└── tap.py                     #   + NatsTap.world_view(kind) adapter: attach_layout / record_reset /
                               #     record_step → the existing buffer/pump/seq machinery (additive)

examples/nats/
├── brain_rover.py             # NEW — paced rover brain: tap + view channel + store, publishes summary
├── dashboard_demo.py          # NEW — the one documented command: server + rover brain + dashboard +
│                              #   headless proofs (model fed, state served, ctrl round-trip); prints URL
└── README.md                  #   + the dashboard section

tests/
├── unit/test_dash_model.py           # RunModel from scripted payloads: discovery, liveness, histories,
│                                     #   malformed frames, completion, two-run separation
├── contract/test_dash_contract.py    # view channel journal + byte-identity + heartbeat; endpoints via
│                                     #   urllib: /runs, state shape (both modes), every ctrl path,
│                                     #   unknown-run 404, unknown-view-kind fallback data
└── integration/test_dash_live.py     # polling-hammer observer proof (rover + view, attach/detach);
                                      #   ctrl round-trip through the dashboard endpoint during a live
                                      #   run; scaled-config advanced-mode completeness

pyproject.toml                 # + pra-dash script; + pra.dash package-data (page.html)
```

**Structure Decision**: `pra.dash` is a separate subpackage from `pra.nats`
because the spec makes it contractually a *consumer* of the documented
scheme (FR-001) — the import boundary (`subjects` names + the transport
protocol, nothing else) is the enforcement. The world-view channel lives
on the tap side of the fence because observer safety is provable only
where the run path is (spec checklist note), and it reuses the mirror
buffer so no new no-backpressure machinery exists to get wrong. No
changes under `core/`, `harness/`, `world/`, `persistence/`, or
`config.py`; `examples/rover/` untouched (the adapter speaks its
language, not vice versa).

## Complexity Tracking

No constitution-gate violations to justify. Named deferrals with owners:
pose coalescing for fast worlds with views (research R2 — arrives with the
first such world); push transport for the page (R1 — polling is proven and
sufficient); durable telemetry history (B6's deferral, carried); the
showcase-grade presentation (roadmap principle 1 — gated by C1/C2, not by
this instrument).
