# 01 — System Overview

This document is the map of the system: its parts, how they connect, the event-driven model they run on, and how the system starts and stops. Every component named here is specified in detail in a later document.

---

## 1. What the system is

A continuously-learning intelligence composed of:

- a **body** — a configurable set of sensors and actuators (the anatomy);
- a **sensorimotor core** — reference frames that build and continuously refine a model of the world from sensorimotor experience;
- a **structural-learning process** — that grows, prunes, and reshapes the frame population over time;
- a **motivation layer** — a fixed innate drive that produces the system's only notion of "better," from which the system discovers its own goals;
- an **action layer** — that selects actions to satisfy the drive;
- a **persistence layer** — that snapshots the entire evolving state so it can be restored.

The system is **event-driven**: it processes a stream of events — observations arriving from sensors, and internal signals crossing thresholds — against its state, with no clock. It sustains its own activity (its actions generate its next observations) and acts on its own initiative via internal events. Structural change and snapshotting happen during a consolidation phase, triggered by an internal event rather than a schedule. The full model is Section 3.

It has no fixed task. It is configured with a body and a drive, and it learns whatever its experience and drive lead it to. **[D]**

---

## 2. Component map

```
                          ┌─────────────────────────────────────────┐
                          │                 BODY                     │
        world  ───────▶   │  Sensors  ──────────────▶  observations  │
          ▲               │  Actuators ◀── actions                   │
          │               └─────────────────────────────────────────┘
          │                        │ observations                 ▲ actions
          │                        ▼                               │
          │               ┌──────────────────┐                    │
          │               │       BUS         │  sensorimotor      │
          │               │  (delivery)       │  events            │
          │               └──────────────────┘                    │
          │                        │ broadcast                     │
          │                        ▼                               │
          │        ┌───────────────────────────────┐              │
          │        │      SENSORIMOTOR CORE          │             │
          │        │  Reference frames (SIMD)        │             │
          │        │  → local poses, global pose     │             │
          │        │  → recon / prediction / effort  │             │
          │        └───────────────────────────────┘              │
          │             │ measurements        │ poses, transitions │
          │             ▼                     ▼                    │
          │   ┌──────────────────┐   ┌──────────────────┐         │
          │   │ STRUCTURAL        │   │  MOTIVATION       │        │
          │   │ LEARNING          │   │  Innate drive     │        │
          │   │ spawn/select/decay│   │  → value signal   │        │
          │   └──────────────────┘   └──────────────────┘         │
          │             │                     │ value             │
          │             │                     ▼                   │
          │             │            ┌──────────────────┐         │
          │             │            │   ACTION          │ ────────┘
          │             │            │   policy          │
          │             │            └──────────────────┘
          │             ▼
          │   ┌──────────────────────────────────────────┐
          └── │            PERSISTENCE                     │
              │  snapshot / restore the whole state        │
              └──────────────────────────────────────────┘
```

---

## 3. The event-driven model

The system is **not** a loop. There is no clock and no fixed-rate cycle. The system processes a stream of **events** against its state. Events come from two sources, and the system sustains its own activity rather than polling the world. **[D]**, with **[V]** sensorimotor core.

### 3.1 Two kinds of event

- **Exteroceptive events** — an observation arrived from a sensor (Doc 02). Each exteroceptive event carries the **priority of its source stream** (Section 3.3).
- **Interoceptive events** — an internal state crossed a threshold (Doc 05): "act" (the drive is unsatisfied and the system should act into the world), "consolidate" (enough new experience has accumulated, or uncertainty is high enough, to restructure), and "begin" (the single seed event at startup). Interoceptive events are how the system acts into a quiet world and how consolidation is triggered without a clock.

The system is **self-sustaining**: an "act" event makes the policy emit an action, which produces an observation (an exteroceptive event), which is processed and may produce the next "act" event. In a quiet world with no external change, this chain keeps the system active; it neither polls nor goes inert. Continuity — the `(previous_observation, action, observation)` thread the world-model learns from — lives in the persistent state that spans events.

### 3.2 The event queue: serialized, with priority and preemption

- All events, exteroceptive and interoceptive, enter a **single queue** and are processed **one at a time against the state**. At most one action is ever in flight. This makes the transition thread coherent by construction. **[D]**
- Events have a **priority** (Section 3.3). Higher-priority events are processed before lower-priority ones, **and** a higher-priority event **preempts** the processing of a lower-priority one already in progress, including preempting the wait for a pending action's consequence. **[D]**
- **Modulation.** A high-priority event does not only cut the line; for a configured window afterward it **modulates** how subsequent events are processed — narrowing attention and reweighting the value signal toward the high-priority drive (e.g. threat-avoidance) over curiosity. This couples the event system to the motivation layer (Doc 05). **[O]** (interface specified; exact dynamics to be tuned, because the drive layer is **[O]**).

### 3.3 Priority levels — **[D]**

There are exactly **three** priority levels: **high**, **normal**, **low**. Priority is a **fixed property of the source event stream** (e.g. a threat sensor's stream is high; ordinary sensors are normal). It is set at configuration (Doc 07). A content-appraisal hook — by which an event becomes high-priority because of what it *contains* rather than where it came from — is left as an **unbuilt interface seam** (so a fast threat-appraisal path can be added later); it is not in the base build. **[O]** seam.

### 3.4 Processing an exteroceptive (observation) event — **[V]** core

When an observation event is processed:
1. **Deliver.** The bus broadcasts a sensorimotor event to every frame. (Doc 02)
2. **Interpret & learn.** Each frame maps or drops it; mapping frames place it at a local pose, learn, and produce measurements. The set of local poses is the global pose. (Doc 03)
3. **Evaluate.** The motivation layer updates the value signal from the frames' measurements and observation novelty. (Doc 05)
4. This may raise an interoceptive "act" or "consolidate" event onto the queue.

Structure is fixed during event processing, except that a frame is **born on demand** if no frame maps an observation (Doc 04).

### 3.5 Processing an "act" event — **[D]**, **[O]** policy

The action layer selects an action expected to increase the value signal, using the frames' transition models to anticipate consequences (Doc 05), and sends it to the actuators (Doc 02). The action's consequent observation returns as the next exteroceptive event.

### 3.6 The interrupted-action (abandon) rule — **[D]**, mandatory

An action produces a learning triple `(previous_observation, action, observation)` **only if** its consequent observation is processed with **no intervening preemption**. If a higher-priority event preempts a pending action before its consequence is processed, that action is **abandoned**: no triple is formed and the frames learn nothing from it. Because the queue processes one event against state at a time, at most one action is ever in flight, so "the next observation, absent preemption, is the consequence of the last action" is unambiguous and no consequence-pairing tag is required.

### 3.7 Consolidation — **[V]** mechanism, **[D]** triggering

Consolidation (restructuring + snapshot) is triggered by a **"consolidate" interoceptive event**, not a clock. When it runs:
1. **Restructure.** Spawn candidate frames, evict frames that have not earned their place, age the population. (Doc 04)
2. **Snapshot.** Persist the full system state. (Doc 06)

Consolidation runs while normal event processing is paused, on a consistent, point-in-time state. A **high-priority event MAY abort** an in-progress consolidation so the system can respond — **except** that a snapshot write already in flight completes atomically first (Doc 06). An aborted consolidation is simply re-triggered later by the next "consolidate" event.

---

## 4. Lifecycle

### 4.1 Boot — **[D]**

The system starts in one of two ways:

- **Fresh boot.** Given a configuration (Doc 07) that declares the anatomy (Doc 02) and the innate drive (Doc 05), the system starts with an **empty frame population** (zero-start). A single **"begin" interoceptive event** seeds the event stream so the system takes its first action; thereafter the action→observation chain and interoceptive events sustain activity. Frames are born as observations arrive. (Doc 04)
- **Restore.** Given a snapshot (Doc 06), the system reconstructs its entire state — frame population, drive state, policy state, counters — and resumes processing events from a consistent point. A "begin" event re-seeds the stream after restore.

### 4.2 Run

The system processes events continuously — exteroceptive events as observations arrive and interoceptive events as internal thresholds are crossed — pausing for consolidation when a "consolidate" event fires. It runs indefinitely. There is no clock.

### 4.3 Stop

The system **MUST** be stoppable only at a consistent point (between processed events, or during consolidation outside an in-flight snapshot write), and **MUST** take a final snapshot on a clean stop so it can be restored.

---

## 5. Cross-cutting requirements (apply to every component)

- **C1 — Homogeneous, vectorized frames.** All reference frames run one identical computational kernel; frames are evaluated in batches grouped by dimensionality (the SIMD requirement). No per-frame branching. Detailed in Doc 03. **[V]**
- **C2 — Component isolation.** The Bus, the Scorer, the structural-learning policies, the Drive, the Policy, and the Storage backend are each a single replaceable component behind an interface. Swapping any one **MUST NOT** require edits to the others. **[D]**
- **C3 — Fixed innate drive.** The innate (terminal) drive is set at configuration and **MUST NOT** be modifiable by the running system. Only instrumental goals and learned parameters change at runtime. Detailed in Doc 05. **[D]**
- **C4 — Consistent state.** The complete system state is always serializable at any consolidation point, with no in-flight partial updates. Detailed in Doc 06. **[D]**
- **C5 — Configurability.** Anatomy and drive are supplied by configuration at boot. Detailed in Docs 02, 05, 07. **[D]**
- **C6 — Serialized, priority-ordered events.** All events are processed one at a time against the state, in priority order, with higher-priority events preempting lower-priority ones and modulating subsequent processing. At most one action is in flight. Detailed in Section 3. **[D]**

---

## 6. Glossary

| Term | Meaning |
|---|---|
| **Body / anatomy** | The configured set of sensors and actuators. |
| **Sensor** | A source of observations. |
| **Actuator** | A sink for actions; changes the world or the body. |
| **Tool** | A sensor or actuator added beyond the base anatomy, possibly at runtime. |
| **Observation** | A fixed-length real vector produced by sensing. |
| **Action** | A command issued to actuators, drawn from the configured action space. |
| **Sensorimotor event** | The unit on the bus: previous observation, action taken, resulting observation. |
| **Reference frame (frame)** | A learnable dimensioned coordinate space with an encoder, decoder, and per-action transition model. Holds many concepts. |
| **Local pose** | The coordinate a single frame assigns to an observation. |
| **Global pose** | The set of local poses from all frames that mapped an observation; the system's interpretation. |
| **Transition** | A frame's learned map from (pose, action) to predicted next pose. |
| **Reconstruction error** | How poorly a frame reconstructs an observation from its pose (the *explanatory* measurement). |
| **Prediction error** | How poorly a frame's transition predicts the next pose (the *predictive* measurement). |
| **Effort** | The magnitude of the displacement a transition predicts (the *regularizing* measurement). |
| **Survival score** | The combined quantity used to keep or evict a frame; lower is better. |
| **Event** | A unit processed against the state: exteroceptive (an observation arrived) or interoceptive (an internal threshold crossed). |
| **Exteroceptive / interoceptive event** | From a sensor / from internal state ("act", "consolidate", "begin"). |
| **Priority** | One of three levels (high/normal/low), a fixed property of an event's source stream; governs ordering and preemption. |
| **Preemption** | A higher-priority event interrupting the processing of a lower-priority one, including a pending action's wait. |
| **Modulation** | The temporary reweighting of the value signal (and narrowing of attention) toward a high-priority drive after a high-priority event. |
| **Online learning** | Weight changes within fixed structure, during event processing. |
| **Structural learning** | Birth, eviction, and re-dimensioning of frames, during consolidation. |
| **Consolidation** | The paused, internally-triggered phase that restructures the population and snapshots. |
| **Candidate** | A newly spawned frame, protected from eviction until it has had exposure. |
| **Innate / terminal drive** | The fixed value the system is wired to pursue; not self-modifiable. |
| **Instrumental goal** | A learned, revisable sub-goal the system discovers serves its drive. |
| **Value signal** | The scalar the drive produces, used by the action layer. |
| **Abandon rule** | A preempted in-flight action forms no learning triple. |
| **Snapshot** | A serialized point-in-time copy of the entire system state. |

---

## 7. Definition of done (system level)

The system is complete when:
1. It boots fresh from a configuration declaring anatomy and drive, with an empty frame population.
2. It processes events continuously (exteroceptive and interoceptive) with no clock, and consolidates when a "consolidate" event fires, as specified in Docs 02–06.
3. Frames are homogeneous and SIMD-batched per C1 and Doc 03.
4. The innate drive is fixed per C3 and produces a value signal that the action layer consumes (Doc 05).
5. The full state can be snapshotted and restored to a consistent point per C4 and Doc 06.
6. Every component in C2 is independently replaceable.
7. Events are serialized and priority-ordered with preemption and modulation per C6 and Section 3; a preempted action forms no learning triple.
8. Every configuration parameter in Doc 07 is exposed.

Per-component "done" criteria are given in each component's document.
