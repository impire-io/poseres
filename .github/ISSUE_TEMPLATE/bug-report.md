---
name: Bug report
about: Something misbehaves, crashes, or does not reproduce byte-identically
title: "bug: "
labels: bug
---

## What happened

<!-- Plain description. If a number looks wrong, include the number. -->

## Reproduction

<!-- The exact commands, from a clean checkout or install. Include the
seed — almost everything here is a pure function of (config, seed), so
a repro without the seed is half a repro. -->

```bash
# e.g.
# pra-validate suite --seed ...
```

- Seed(s):
- Config (if not defaults):

## Expected vs actual

<!-- What should have happened, what did. One expectation holds
everywhere and needs no justification: two runs of the same
(config, seed) must produce byte-identical serialized summaries —
`pra-validate determinism --seed N` checks it. If determinism broke,
say so; that alone is a bug regardless of anything else. -->

## Environment

- OS:
- Python version:
- `python -c "import pra; print(pra.__version__)"`:
- Install method: <!-- PyPI (poseres) / source / uvx -->
