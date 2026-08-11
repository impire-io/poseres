# Episode 0092 — The restless sleep: consolidation refuted, the diagnosis sharpens (2026-08-11)

The owner chose the biologically resonant regime for the lottery
head ("go with consolidation"): surprise-prioritized replay — the
head buffers the transitions that carried the largest prediction
error and re-learns them during periodic rests, sleep after school
and naps through the life. The design was honest to the no-fiat
rule: nothing named trades; surprise was supposed to find them by
their statistics.

It did not, twice, and then failed at power [measured]:

- **Pilot 1**: the buffer filled with *walking* — 86–96 locomotion
  transitions against 13–19 trades — because witness-time surprise
  is stale: early-life residuals, measured against a raw head, keep
  their giant scores forever. Sleep consolidated locomotion.
- **Amendment 1** (re-evaluate surprise against the current head at
  every rest — recorded openly, constants untouched): *worse*.
  Under a churning η = 0.5 head, current residual error
  concentrates on whatever the churn last disturbed — still
  locomotion — and extra high-η passes interfered (sharpness 0.75).
  Withdrawn with its numbers; per the registration's own
  no-quiet-retune rule, no third prioritization was tried.
- **The arms, on the registered design**: CN1 FAIL at **0.293**
  ruinous — worse than the linear anchor (0.252) and the online
  quadratic (0.278); the pilot's 0.183 was eight-seed noise. The
  per-seed spread survived intact (0.00 → 1.00). Sharpness **fell**
  to 0.799 from the online head's 0.874: replay actively damaged
  the trade predictions. CN2/CN3 passed — no collateral harm.

The reversal fired on its second clause, and the diagnosis is now
three notches sharper than episode 0090's: not representation (six
perfect refusers, 0091), not arbitration (sharpness below the line
both times), not replay volume (0092) — **the churn itself**.
Online NLMS at η = 0.5 over 153 correlated product features keeps
overwriting what it knows; consolidation replayed the churn's own
debris and amplified it. The remaining regimes inherit the 0090
license with the suspect ranked: **feature normalization + a lower
head η** first (treat the disease), targeted low-order terms second
(shrink the feature space). Neither is licensed to run without the
owner.

For the ledger, plainly: two consecutive headline-bar failures
(0091, 0092), each converting into a mechanism isolation the
previous failure couldn't state. This is the working agreement
doing its job — the bars are catching every plausible-but-wrong
fix before it can ship.

Reversal condition: none — records a completed measurement whose
registered reversal fired. If a future regime passes refusal, 0091
and 0092 are its baselines; a fresh consolidation dose requires a
fresh registration by this topic's own rule.

Trail: topic consolidation (folder retired; registration 27ab78f,
pilot 1 + amendment 1 + pilot 2 + arms all pushed with raw numbers
en route); Doc 0010 updated; runner `consolidation.py`
(ConsolidatedQuadHead, SleepingPolicy, the buffer-composition
instrument) + row files in the session scratchpad.
