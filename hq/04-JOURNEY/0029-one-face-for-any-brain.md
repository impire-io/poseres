# Chapter 29 — One face for any brain: the dashboard, and the browser that caught a bug (2026-07-18)

B7 landed hours after its gate opened, closing Phase B. The dashboard
is contractually a *pure consumer* of the B6 surface — `pra.dash`
imports the subject names and the transport protocol and structurally
nothing else, collecting the promise B6's SC-006 made (that B7 could be
built against the documented scheme without reading B6's source). One
`DashboardModel` turns received payloads into per-run state (identity,
authoritative state, monotonic liveness, bounded census history, the
honesty counters, snapshot notices); one stdlib server serves a single
self-contained page (`pra-dash`); simple mode is for a person standing
in front of the brain, advanced mode is the researcher's instrument
panel with the four control buttons and every reply — B6's error
grammar included — surfaced verbatim.

The roadmap's named gap closed on the tap's side of the fence, where
observer safety is provable: a **world-view telemetry family**
(`tele.view.static` once + heartbeat, `tele.view.live` per record)
whose adapter exposes exactly the three-call surface the rover world
has spoken since feature 006 (`attach_layout` / `record_reset` /
`record_step`) — so the rover mounted on the bus **unchanged**, and
the B1 viewer's world now renders from any machine. Observer safety
was re-proven at the new layer: byte-identity with the whole dashboard
attached and hammered by a polling thread (reference, rover-with-view,
multi-stream continuous, attach-and-detach mid-run), and
pause-through-the-dashboard byte-identical to never-paused.

The chapter's recorded lesson: **the browser is an instrument too.**
The headless real-stack demo passed on the first run (world view
consumed and served, pause frozen at step 145, snapshot fulfilled
through the dashboard's own endpoint) — but opening the page in an
actual browser showed `SEQ GAPS 1171` on a run with zero drops. The
model had derived gaps from `tele.step` sequence numbers alone, and
the tap's mirror family is *shared* — steps, episodes, views, and
snapshots interleave one sequence, so every step legitimately skips.
Gap detection now runs on the union of the family (regression test
recorded), which is exactly the kind of honest-instrument bug the
endpoint tests could never see: the data was correct; the *reading* of
it lied. Both modes were then verified rendering live — arena,
obstacles, pose, trail, census history, histogram, counters. Phase B
closes with the brain watchable, manageable, and shareable from
anywhere, and the whole gate still needs no NATS, no server, and no
browser. Trail: `specs/015-web-dashboard/` (spec, plan, research
R1–R7, data-model, contracts, quickstart, tasks), `src/pra/dash/`,
`examples/nats/dashboard_demo.py`; commits `5b91d90` (spec), `d45baf3`
(plan), `a9ce3a3` (tasks), and the implementation commits following.
