# C1B run journal — hourly observations

Live notes on the multi-week `c1b` run (pre-registration:
[C1-RUN-PLAN.md](C1-RUN-PLAN.md), amendment v2). One entry per hour,
appended by the automated watch: a single "nothing special" line when
the hour was routine; a written-out note when something happened and
why it matters. The raw numbers behind every entry are in S3 under
`pra/v1/c1b/`. Notability bar: first mined log, any grid offer, any
craft, persistence records (deepest held dig), camping episodes,
population/error anomalies, restarts, gaps, disk events.

---

**2026-07-22 06:45 — opening entry (the first night, summarized).**
Run `c1b` launched 2026-07-21 ~22:55 local on the property body
(obs 32 / actions 12). First ~9.5 hours: operationally flawless (zero
restarts, zero telemetry gaps, 4.0 steps/s every hour, disk flat).
Learning: error floor deepened to 0.029 and recurs between selection
sweeps; population breathing 12–28. The exciting part: the bot already
uses its body far beyond the ≈0 chance baseline — repeated full
hold→place chains (8 leaf litter + dirt placed back into the world),
several completed 3-tick held digs (dirt in the pocket proves them),
and one ~10-consecutive-tick dig streak reaching 0.84 progress on a
hard block. Not yet: no log (the 12-tick wood dig unclimbed), so no
offers and no crafts — the emergence headline stays open, as expected
at this age. One one-hour camping episode (motionless to the
centimeter) self-resolved. Watch items: first log, offer, craft;
whether camping episodes lengthen; dig-streak record (0.84).

**2026-07-22 08:01 — nothing special.** step 131,354, err 0.027 (a hair under the old floor), pop 22, all green.

**2026-07-22 09:02 — the run survived its first real restart, and resumed exactly.**
At 08:45 local the brain unit was manually restarted (operator; clean
stop→start, no crash — bridge untouched). This was the resume
machinery's first production test and it passed: the brain reloaded its
newest snapshot and continued at cycle ~575 / step ~133k with its
learned state intact — error read 0.021 immediately after resume, the
night's floor, where a fresh brain would read ~0.5+. Snapshot ids
continue on the cumulative counter (now snap-139000); the dashboard's
per-process step counter reset to zero by design. Also this hour: a
striking dig burst (124 dig actions in one 150s window — 21% of all
actions vs ~8% uniform). All units green, zero gaps.

**2026-07-22 10:05 — nothing special.** cumulative ~157k steps (cycle 650), err 0.129 (sweep churn), pop 19, another dirt mined, all green.
