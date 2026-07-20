# Chapter 35 — Three spaces, one ceiling: the signal was the problem all along (2026-07-18)

The third anchor space for staleness detection was the most elegant and
the cheapest to test: index error memory by the brain's own last-m
actions — a space the world cannot move by construction, with
spike-robust cells (windowed medians, running best-median) replacing
the arithmetic that had painted phantom staleness. The offline gate ran
the frozen (m, W) grid over captured traces from BOTH shift modes plus
the benign floor, against the chapter-34 bracket.

Every grid point failed. Emission mode separates directionally but
weakly (~1.5–2×, never 4×); dynamics mode stays blind (~1×); the benign
floor never approaches zero. And with that, three consecutive
eliminations — sliding FIFOs (ch. 32), observation places (ch. 33),
action contexts (ch. 35) — share one ceiling, which is the tell: **the
anchor space was never the problem. The signal is.** Per-step
errors-at-visit are a *tracking* error: they move with ecology churn,
election composition, and ongoing learning everywhere, and that
within-life nonstationarity is background no indexing scheme can
cancel. The project learned exactly this lesson once before, one level
down — all-step EMAs score tracking, not structure, and the remedy was
the fair judge scoring episode-start transfer. The staleness program
needs the same move at the drive level: a **transfer-error stream**
(episode-start prediction errors, read before within-episode adaptation
masks the damage) as the input to any staleness memory, with all three
eliminated spaces available for retry once the signal is right.

Third gate-stop in a row, each cheaper than the last (this one reused
every instrument and wrote no src), and jointly they bought what a
lucky pass never could: measured brackets on both world modes, three
eliminated representations, and a signal-level diagnosis with an
in-house precedent for the fix. Doc 05 guidance unchanged — competence
stands. Trail: `hq/02-DESIGN/validate/CONTEXTMEM-DIAGNOSIS.md`;
`specs/021-context-memory/spec.md`; commit `bba601a` and this close.
