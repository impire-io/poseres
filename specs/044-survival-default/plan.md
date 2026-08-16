# Implementation Plan: The Survival Body Is the Default

**Branch**: `044-survival-default` | **Date**: 2026-08-16 | **Spec**: [spec.md](spec.md)

## Summary

The feature-033 pattern (the default body changes; every prior form
stays reachable by explicit flag): sentinel defaults on `c1_anatomy`
resolve the zero-override call to design 0015's blessed stack
(survival + flood intrusion + worth channel, obs 86/13); the bridge
wire defaults flip in lockstep (SURVIVAL default-on with "0" opt-out,
FLOOD/AIM defaulting intrusion/worth when unset); `contract_check`
infers all three from the hello table. Explicit calls are
behavior-identical to pre-044 — the sentinel resolution is the whole
trick. Docs: module/contract notes, Doc 0008 release note, CHANGELOG
[2.2.0], pyproject 2.2.0.

## Technical Context

Touches: `src/pra/anatomy/minecraft/anatomy.py` (sentinels + docs),
`examples/minecraft/bridge/bridge.js` (env defaults),
`examples/minecraft/contract_check.py` (aim inference),
`tests/unit/test_anatomy_meta.py` (default test + opt-out pins),
specs/027 contract note, Doc 0008, CHANGELOG, pyproject. Constitution
I: the frozen T1–T6 suite runs non-Minecraft worlds — untouched;
the anatomy default is surface behavior, versioned as a minor with
the 033 precedent. III: the promoted point is measured (episode 0103,
replicated), not chosen.
