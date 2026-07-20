# Chapter 8 — Feature 004: anatomy & body — the design is fully built (2026-07-08)

Doc 02, the last unbuilt design document (its Bus half was already validated in
feature 001), landed as the body layer: Sensor/Actuator interfaces, a Body
composing observations by fixed-order concatenation and routing a
disjoint-union action space, and a ToolRegistry whose registrations defer to
the slow loop and apply through the Doc 03 §7 **frame I/O resize** — learned
weights preserved bit-for-bit, fresh trailing slices at the §8.8 effective
scale, draws from the single generator in a fixed order. The integration
insight kept it small: the Body implements the existing EventSource seam, so a
world mounted through it is **byte-identical** to the direct connection (tested,
SC-001), and the only engine change is an inert duck-typed hook. Mid-run growth
works: register a sensor + actuator at a consolidation boundary, obs_dim
10→13 and n_actions 4→6, every frame adapted without forgetting, the run
completing deterministically. Deferred with loud edges: snapshots of resized
runs (Doc 06 format-version follow-up), in-process timeouts, tool
self-invention [O]. Trail: `specs/004-anatomy-body/`; commits `536baee`, and
the implementation commit following it.

---
