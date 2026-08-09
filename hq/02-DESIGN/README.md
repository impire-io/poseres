# 02-DESIGN — PRA System Specification (Document Set)

This set specifies, without ambiguity and from a functional point of view, the system to be built. It defines **what must exist** and **how each part behaves**, not the reasoning behind the choices. An implementer should be able to build a working system from these documents without needing undocumented decisions.

**The spec-kit rule:** every document here is written explicit enough to be the argument to `/speckit-specify` — the capability, its seams, its configuration surface, and its acceptance criteria, with no guessing left to the spec writer. New documents take the next free `NNNN-` number (`0008-…` onward). Graduating research enters through `/research-graduate`; behavioral changes made during implementation propagate back here (see [`../00-GENESIS/how-we-work.md`](../00-GENESIS/how-we-work.md)). `validate/` holds the normative specifications (PRA-01, PRA-02), the founding bet (`pose-resolution-architecture.md`), and the `*-DIAGNOSIS.md` evidence trails.

The system is a **continuously-learning machine intelligence** with a configurable body (sensors and actuators), a fixed innate drive, and a brain that learns and restructures itself online. It is not trained-then-frozen; it learns for as long as it runs. Its perception-and-world-model core is the Pose Resolution Architecture (PRA), from which the whole system takes its name.

---

## Reading order

| # | Document | Covers |
|---|---|---|
| 01 | `0001-system-overview.md` | What the system is, the component map, the runtime loop, boot/restore lifecycle, scope, glossary |
| 02 | `0002-anatomy-io-bus.md` | Sensors, actuators, tools, and the communication bus |
| 03 | `0003-sensorimotor-core.md` | Reference frames, the SIMD requirement, scoring, the global pose |
| 04 | `0004-structural-learning.md` | Online/offline learning, spawn-and-select, eviction, earned persistence |
| 05 | `0005-motivation-action.md` | The innate drive, the value signal, action selection |
| 06 | `0006-state-persistence.md` | What system state is, snapshot/restore, the storage layer |
| 07 | `0007-configuration-reference.md` | Every configuration parameter, defaults, ranges |
| 08 | `0008-public-api-versioning.md` | The v1 public surface, semver promise, deprecation policy |
| 09 | `0009-brain-side-hold.md` | The head-derived hold: the composition with zero scaffolding (graduated research, episode 0074) |
| 10 | `0010-recipes-and-the-label.md` | Recipes and the praise label: taught reach as product (graduated research, episode 0077) |

Read 01 first; it is the map. The rest may be read in any order, but 03 and 04 describe the validated core and are the natural place for an implementer to begin building.

---

## Status legend (used throughout)

Every component and requirement carries one of these tags. They describe **validation maturity**, not importance. All tagged items are mandatory unless marked otherwise.

- **[V] Validated** — the mechanism has been confirmed in simulation at small scale. Build it as specified; deviations must be justified against the acceptance behavior.
- **[D] Design** — fully specified functionally, but not yet validated. Build it as specified; expect refinement once it runs.
- **[O] Open** — the interface and a default behavior are specified, but the best internal algorithm is a known unsolved problem. Build the interface and the default; expect the internal to be replaced. **[O]** items are where implementation risk concentrates.

---

## Requirement language

- **MUST** / **MUST NOT** — mandatory / prohibited.
- **MAY** — permitted, not required.
- A value given as a *default* is the value shipped unless configuration (Document 07) overrides it.

---

## What is out of scope for the first build

Stated so their absence is unambiguous; each has a defined seam so it can be added later without rework. See the named document for the seam.

- **Distributed / multi-machine operation** — the bus is an abstraction; only the in-memory backend is built now (Doc 02).
- **An external message broker** (e.g. NATS/JetStream) — a bus-backend seam exists (Doc 02).
- **A nearest-neighbour pose index** (e.g. a vector database) — a storage seam exists (Doc 06); build only if a frame is shown to need fast pose lookup.
- **Multi-step planning / sophisticated action selection** — a policy seam exists with a one-step default (Doc 05).
- **Self-invention of new tools** — the tool-registration interface exists (Doc 02); the mechanism that *invents* tools is **[O]** and not built now.
- **Evolution of the innate drive across snapshots** — an optional future capability noted in Doc 05/06; the running system's drive is fixed.
