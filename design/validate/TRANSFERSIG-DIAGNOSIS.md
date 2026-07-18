# Transfer-signal arc — the fair-judge lesson, applied to the staleness program

Date: 2026-07-18. Question under test: CONTEXTMEM-DIAGNOSIS (ch. 35)
closed the anchor-space search with a signal-level diagnosis — three
spaces share one ~1–2× ceiling because per-step errors-at-visit are a
*tracking* signal, moved everywhere by ecology churn, election
composition, and ongoing learning. The in-house precedent
(THRESHOLD-DIAGNOSIS) says what to do: score transfer, not tracking. This
arc asks whether staleness statistics computed on the **transfer stream**
— errors at the first K steps of each episode, before within-episode
adaptation masks damage — clear the chapter-34 bracket that the tracking
stream could not.

## The design under test (frozen here, before any run)

- **The signal**: the same per-step errors-at-visit series, filtered to
  episode-relative steps t mod 40 ∈ {1..K} with **K = 5 — the fair
  judge's recorded `score_window_steps` value, reused, not invented**.
- **The statistics** (the 021 cell arithmetic, unchanged): per cell, a
  bounded window of the last W transfer errors, summarized by its median;
  best = running min of full-window medians; staleness = max(0, median −
  best).
- **The spaces** (retrying the eliminated ones on the new signal,
  cheapest first): `global` (one cell — no space at all: a world change
  moves transfer error globally), `context-1` and `context-2` (last 1–2
  actions). W ∈ {8, 16} (the stream is 8× sparser than tracking).
- **Bars — the chapter-34 bracket, verbatim**: ONE (space, W) setting
  must clear post-shift median > 0, > 4× the pre-shift median, AND > 4×
  the benign (multiregion) median, on BOTH shift modes, every seed
  (dynamics 1–3, emission 1–3). No per-world tuning.

Anchors inherited and frozen: tracking-stream ceilings ~1.5–2×
(emission) / ~1× (dynamics), benign floors 0.02–0.11 (ch. 33–35 reads);
shift at step 6760; windows pre 2000..6760, post 6760..7240, benign
2000..12000.

## P1 — offline gate (scratchpad; BEFORE any src change)

Recapture the seven traces (frontier arm, 017 dials: dynamics-shift
seeds 1–3, emission-shift seeds 1–3, multiregion seed 1), filter to the
transfer steps, replay the grid. Accept: one setting clears every bar.

## Failure exits

- **X0** — no setting clears: the fourth gate-stop; recorded with the
  best setting's numbers. The reading would be that even transfer errors
  carry too much population-composition noise at the drive level, and
  the successor moves inside the frames (per-frame honest transfer error
  on frames that survive the shift) — named, not improvised.
- **X1** — P1 passes but the later live stage fails to collect: the map
  ships if no-harm holds; the acting question is named (E1 protocol to
  be frozen in this document before any live run, mirroring arc 021's).

Results are appended as they land; the Outcome section closes the arc.
