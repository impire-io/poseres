# Journey — partial-gap-world (started 2026-08-18)

## 2026-08-18 — the rig and the declared renewal ladder, before the walk

The 0110 rig restored from its trail (f05827f) onto its own world
(`pgw1-minecraft`, port 25605, bridge 25593): `rig/pgap.py` carries
the meter instruments unchanged (steady-state below-12 on segments
2–3, eats, starvation; the RecordingPolicy as trail), `rig/peer.js`
is byte-identical to the arms copy, and the world builder is 0110's
with the larder FROZEN at C-1's total-war shape — one patch, 2
pre-grown melons — plus 2 age-7 stems. The two pre-grown melons sit
on the stems' cardinal fruit cells, so both stems are blocked at
birth: **regrowth begins only when a melon is consumed** — renewal
is re-contested by construction, the design's "regrowth slower than
joint consumption" made mechanical.

**The one walked variable** is the world's `random_tick_speed`
gamerule, set on the record before every birth. Declared rungs,
name → tick speed:

| rung | random_tick_speed | note |
|------|-------------------|------|
| T12  | 12                | 4× the game's default renewal |
| T6   | 6                 | 2× default |
| T3   | 3                 | the game's own default — C2/C1's regrowth rate (0110) |
| T1   | 1                 | ⅓ default |
| T0   | 0                 | no renewal: C-1 plus two inert stem blocks |

**Walk order, declared:** downward from T12. At each rung: solo-86
first (the Bar P0 screen; a rung failing P0 is disqualified and gets
no hostile arm), then the hostile-86 arm (the Bar P1 hunt). The walk
stops at the first hostile reading in 0.10–0.90: that rung freezes
(`FROZEN.json`, a hand act journaled here) and Bar P2's `hostile2`
replicate runs on it. If two adjacent rungs straddle the band (one
< 0.10, the next > 0.90), intermediate tick speeds (e.g. T2, T4)
may be added as rungs — declared here before they run, the 0110
knife-edge probe's precedent made a standing rule. T0 runs only if
every renewing rung reads < 0.10, to re-anchor the floor before any
abandoned verdict; otherwise 0110's C-1 reading (1.000) stands as
the no-renewal record.

**I0 — the renewal-rate instrument, declared before the walk:** a
pure world reading, no subject and no peer (`pgap.py renewal
<rung>`): both stems freed, the six fruit cells harvest-polled every
2 s for 300 wall-seconds at tick rate 100 (30,000 game ticks ≈ 0.4
life-equivalents), every growth event logged and the summary row
reporting melons per life-equivalent (one life = 75,375 game ticks).
One reading per renewing rung, run before any arm. I0 is
interpretive — it prices the rungs in melons-per-life so the walk's
verdict can say how renewal compares to joint consumption — and
carries no bar.

**Journaled confounds, accepted going in:** random ticks are the
world's own stochasticity — the renewal *timing* is not under engine
seed 1 (the subject's stream is; live-world evidence, as
everywhere). `random_tick_speed` also scales farmland-moisture and
grass-spread checks; the patch is water-hydrated (moisture pinned at
7 by construction each birth) and the floor is grass on superflat,
so the accepted side effect is cosmetic. One life per arm remains
the walk's economy — that is what Bar P2 exists for at the only rung
that matters.

**Registered expectation (mechanism note, not a bar):** by 0110's
consumption record (the hostile peer took the 2-melon larder in its
first 2 digs; the solo-86 life needed ≥ 3 eats) the band, if it
exists on this axis, is expected between T1 and T6 — fast renewal
out-runs the peer's digging (no war), zero renewal is the measured
total war.

## 2026-08-18 — I0 first edition read zero everywhere; the instrument caught the server, not the world

The playerless I0 read **0 events at every speed** (T12/T6/T3/T1,
300 wall-s each at tick rate 100, ~30,190 game ticks per reading —
rows kept as `rig/renewal-*-playerless.jsonl`). Diagnosis, one
variable at a time [measured]: stems, age=7 state, and farmland all
verified in place by block checks; at `random_tick_speed 255` in a
forceloaded chunk a fresh `wheat[age=0]` sat unmoved for 60 s
(~9,000 game ticks — random ticks were not happening at all); the
moment one idle player joined, the same wheat raced to age 7 and two
melons fruited inside 60 s. **This 1.21.11 server random-ticks only
chunks near an online player; forceload keeps chunks loaded, not
randomly ticked.** Every real arm has the subject online, so the
world's renewal is untouched — the zero was the playerless
instrument's own assumption, the 0110 L2 lesson one rung deeper
(expectations from the world's measured facts).

**I0 second edition, before any re-reading:** the idle peer
(`peer.js` PEER_MODE=idle, name `lamp` — the rig's stationary
presence, no acts) stands in the world during the reading as the
ticking presence; everything else unchanged. I0 remains
interpretive, never a bar.

## 2026-08-18 — I0 second edition: the rungs priced, the walk may start

With the ticking presence in place, the world grows [measured]
(300 wall-s per rung at tick rate 100, ~30,100 game ticks each,
both stems slot-free throughout; rows in `rig/renewal-<rung>.jsonl`):

| rung | events | melons per life-equivalent (75,375 game ticks) |
|------|--------|------------------------------------------------|
| T12  | 23     | 57.5 |
| T6   | 13     | 32.7 |
| T3   | 5      | 12.5 |
| T1   | 3      | 7.5  |

Roughly linear in tick speed, as the mechanic predicts. Reading
honestly: these are **ceiling** rates — the instrument keeps both
fruit slots free, while in an arm a slot re-opens only when its
melon is consumed, so effective renewal in a life sits at or below
these numbers. Against the consumption record (subject minimum 3
eats/life; the 0110 peer's opening theft 2 digs), even T1's ceiling
(7.5/life) feeds one body, and T12's (57.5/life) drowns any war —
consistent with the registered expectation that the band, if it
exists, sits in the middle rungs. The walk starts downward from T12
per the declaration: solo P0 screen, then hostile.
