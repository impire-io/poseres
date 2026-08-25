# Journey — the-opaque-world (started 2026-08-25)

## 2026-08-25 — M0(c) read on the cheap world first; the sidecar decision; two pre-run amendments

**The sidecar decision, registered:** the kernel's snapshot codec is
schema-strict (exact keys, no pickle) and byte-frozen — tier-2 state
cannot ride inside the blob without kernel changes, which research
does not make. The prototype's composed state is therefore a PAIR:
the standard blob (base tier, untouched machinery) plus a tier-2
sidecar in the same npz+json no-pickle discipline, captured at the
same C4 safe points. Bar M0(c) applies to both artifacts. The
kernel-native single-blob topology is a graduation design item,
stated openly — not a rig hack to hide.

**M0(c) echo-world reading [measured]:** byte-exact resume of the
composed system in both modes — run A (50 cycles straight) vs run B
(resumed from the cycle-25 pair): final base tensors AND final
tier-2 sidecar byte-identical; sidecar round-trip byte-identical
(tower t2 pop 13, bind-pred 9). The z caches are correctly NOT
state: snapshots land at cycle ends, where the z chain breaks with
the transition chain and rebuilds from zeros.

**Amendment 1 (pre-run, before any Minecraft arm):** lives run
INTERLEAVED round-robin — flat → tower → bind-pred per round, eight
rounds — instead of 8+8+8 serial blocks. The live world drifts
(patch wear, floor repair, server time), and d3's own protocol
interleaved its arms for exactly this reason. Teaches stay
sequential with flat first; every analysis rule was registered
before any run, so the T0 spirit — the baseline unshaped by
composed results — is preserved.

**Amendment 2 (pre-run, factual):** the rig's body is
`c1_anatomy(survival=True)` as the d23/n23 machinery declares it —
the README's "obs 86 / 13" was wrong and is corrected; the deficit
gate is OFF in every arm per 0103's blessed stack (arm-symmetric
either way; the frame mechanism stays the only variable).
