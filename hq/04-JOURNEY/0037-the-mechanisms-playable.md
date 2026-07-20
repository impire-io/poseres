# Chapter 37 — The mechanisms, playable: an interactive explainer that runs the real math (2026-07-18)

The question was communication, not capability: could the core mechanisms
be *shown* rather than described — honestly, to the hobbyist audience the
product thesis names? `explainer/index.html` is a single self-contained
page with nine live sections (loop, triplet, frame, coverage-fair
scoring, parsimony price, spawn-and-select, drives, channel weighting,
persistence), each backed by a browser simulation running the Doc 03–06
update equations — tanh nets with per-element gradient clipping,
observation-space prediction error, coverage-fair EMAs, the falling
population-scaled threshold, the five-array whiteness estimator, JSON
snapshot/restore — at demo scale (smaller nets, faster EMA clocks),
verified headless in Node before shipping.

Building it re-derived three recorded findings the hard way. The first
demo ecology reproduced the youth conveyor exactly (threshold below any
achievable score; 660 evictions, zero mature frames) until the bar and
protection window were retuned — and a fit gate below a newborn's
starting error blocked bootstrap entirely, the demo-scale shadow of
young-frame protection. The channel-static demo refused to fake the
collapse at single-frame scale (world-channel learning was fine); what
honestly reproduces is the *judge-side floor* — unweighted survival fit
0.44 vs 0.30 weighted against a 0.35 bar, so the page shows maturity
rescue, not learning rescue. And the corridor drive demo could not be
tuned to make realized-LP curiosity hold the frontier: it drifts to the
noisy TV (0.72–0.95 occupancy) while competence avoids it entirely — so
the page says so, matching the −0.062/+0.067 record instead of
prettifying it. Verified: dim ordering on a true-dim-3 world, price
winner moving 5→3→1 with `w_complexity`, cheat-vs-honest EMA gap, ρ̂
separation (world 0.8–0.9, static ≤0.11, weights at floor), bit-identical
resume over 150 resumed steps. Trail: `explainer/index.html`; this close.
(Numbering note: authored as "Chapter 35" in a parallel session while
chapters 35–36 landed on main; renumbered mechanically to 37 at merge,
content untouched.)
