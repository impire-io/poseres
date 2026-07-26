# Episode 0064 — Shareable brains: a snapshot becomes an artifact (2026-07-27)

Phase D's fourth item (feature 037, parallel worktree): a trained
brain is now a thing one person can hand to another. `pra-brain
export` wraps the **byte-untouched** snapshot blob in a plain zip with
a manifest (sha256 of the blob, snapshot format version, pra version,
body shape, step/cycle/population, provenance note); `inspect` reads
the manifest without ever deserializing the brain; `import` verifies
container version, snapshot version, and hash — loudly refusing and
writing nothing on any mismatch — and places the blob where the
existing store's resume path picks it up. The artifact is
deterministic: zip member times are epoch-pinned, so the same brain
with the same manifest is the same bytes [measured]. Constitution I
held by construction: the snapshot wire format and `FORMAT_VERSION`
were only ever read.

**The roadmap exit was verified twice** [measured]: as a test (person
A publishes via the CLI; person B imports into a separate store and
resumes *byte-identical* to the uninterrupted run — the repo's
standing resume-exactness bar) and end-to-end from the shell with the
installed binary (export → inspect → import → resume byte-identical;
a tampered copy exits 1 on the sha256 mismatch with the store left
empty). Twelve new tests; the public surface grew by seven inventory
entries + the fifth CLI, Doc 0008 updated in the same change and held
to it by the surface guard [measured].

Recorded assumptions: the manifest carries no seed (the resume path's
existing guards enforce compatibility); artifact *signing* — as
opposed to integrity — is out of scope and said so.

Reversal condition: none — records a completed build; the container
gains a version field of its own, so a future format change is an
anticipated turn, not a break.

Trail: `specs/037-shareable-brains/` (quickstart.md carries the usage
doc); `src/pra/persistence/portable.py`, `brain_cli.py`;
`tests/integration/test_shareable_brains.py`; Doc 0008 §Persistence.
