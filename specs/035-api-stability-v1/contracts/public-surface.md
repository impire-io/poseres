# Contract: The Public Surface, its Promise, and its Guard

## The promise (v1.x, restating constitution I outward)

- **Patch**: fixes only; no public name or shape changes; behavior of
  existing modes byte-identical.
- **Minor**: additive only — new opt-in capability, new keyword-only
  parameters, new public names; existing modes' RNG stream, behavior,
  and serialized summaries untouched (constitution I); deprecations
  may be announced.
- **Major**: removals allowed, only of elements deprecated ≥ one minor
  release earlier (urgent-removal exception must be documented in the
  changelog with its reason).
- **Snapshots**: same-version round-trip is exact (already measured at
  500k steps, episode 0041); cross-version loading within v1.x is
  supported forward (older snapshot → newer v1.x) per Doc 0006's
  config-in-force rules; anything beyond that is explicitly
  documented, never implied.
- **Internals**: everything not in the inventory. Importable, visibly
  unpromised — research instruments (the arcs' copy-patch discipline)
  rely on this and it stays legal.

## The guard (tests/contract/test_public_surface.py)

1. Every inventory entry imports/resolves.
2. Kind matches; declared parameter names present in live signatures
   (keyword-only additions legal).
3. CLI entries exist in `pyproject.toml` and resolve.
4. Doc 0008 and the inventory agree bidirectionally on names.
5. Negative control: a mutated copy of one entry (removed symbol,
   renamed param) makes the guard fail — demonstrated, not assumed.

## The notice (deprecations)

One sentence, uniform, produced by the single helper:
`"{element} is deprecated and may be removed in {removal}; use {replacement}."`
— as `DeprecationWarning` for library elements, once-per-invocation
stderr line for CLI surfaces.
