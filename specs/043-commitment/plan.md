# Implementation Plan: Commitment

**Branch**: `043-commitment` | **Date**: 2026-08-16 | **Spec**: [spec.md](spec.md)

## Summary

Promote the measured commitment mechanism (the-last-crack, design
0014) to product, the feature-040/041/042 pattern: two additive
keyword params on `CompletionItchPolicy` (`commit_kappa`,
`explore_defers_holds`) with `RecipePolicy` passthrough, the
incumbency bonus + exploration deferral + intention boundary already
landed and unit-tested during the research (commits cab6631/7846c27);
this feature formalizes the surface: inventory rows, Doc 0008 release
note, Doc 0005 + Doc 0011 vocabulary, CHANGELOG, version 2.1.0.

## Technical Context

Python 3.12, numpy only; pure policy arithmetic (FR-005). Code +
tests: landed on main during research (constitution-I opt-in pattern,
bit-exact off, RNG parity). This branch touches:
`tests/contract/surface_inventory.py` (param rows), Doc 0008
(inventory + 2.1.0 note), Doc 0005 (mechanism paragraph), Doc 0011
(dial rows + section), `CHANGELOG.md` ([2.1.0]), `pyproject.toml`
(2.0.0 → 2.1.0), CLAUDE.md speckit pointer. Constitution check:
article I held by the off-parity suite (already green); III by
measured provenance (episode 0101's frozen bars). Post-design
re-check PASS (no new deps, additive only).
