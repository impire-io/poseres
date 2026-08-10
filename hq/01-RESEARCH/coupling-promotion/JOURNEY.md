# coupling-promotion — investigation journey

Topic opened 2026-08-10 (owner: "promote the coupling with a
timing-primary bar"). Appends as it happens.

## 2026-08-10 — feature 042 built; closure exact on both bodies

Spec-kit lifecycle on branch `042-deficit-gating` (spec, plan,
tasks; tests written first). The build: `_label_weight(obs)` on
`CompletionItchPolicy` — `label_beta + deficit_kappa·clip(1 −
obs[deficit_index], 0, 1)` — used at the completion read and at
`RecipePolicy` selection; keyword-only params, loud validation,
off-path reads nothing. The closure identity held exactly as
planned (`0 + κ·d ≡ κ·d`; the extra clip is a no-op for meters in
[0, 1]): substituting the shipped gate for the instrument subclass
inside the *unchanged* archived runners reproduced **48/48 rows
with zero field mismatches** (24 × 0083-W1, 24 × 0084-T2). One
plumbing note: the version bump needed the editable install's
metadata refreshed for the single-source version test. P2/P3
arithmetic on the identical rows: 2.22× / gap 4 / 22 / 24 (C1) and
+0.216 / 0 vs 16 deaths (sample field) — all bars clear.
