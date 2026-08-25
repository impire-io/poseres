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

## 2026-08-25 — teaches and round 1–8 lives: M0 PASS, the rig valid, and the scale clause fires

Three teaches, 45 live lessons each, every lesson passing its gate.
**Bar M0 PASS** [measured]: (a) tier-2 map rate ≥ 0.9986 through
teach and lives; (b) the arbiter genuinely engages in the wild —
tier-2 held the policy predictor 31–52% of calls in EVERY composed
life (clause asked ≥ 5% once); (c) byte-exact composed resume on the
echo world plus the sidecar round-trip asserted byte-identical live
at every one of 90 composed lessons. The lifecycle telemetry is a
result in itself: each bind-pred life churned 69–78 orphan events
with 22–31 of ~39 tier-2 frames dangling at end — and the population
never destabilized (map 0.999, no starvation, foraging intact):
graceful degradation holds under real churn.

The 24 interleaved lives (8 rounds), eats per life:
flat [0,0,4,0,0,3,3,7] = 17 total, 4/8 lives eating, first-eats
1392/3832/4645/5850, 1 chain, 3 distant collects. tower
[7,0,0,0,0,0,0,6] = 13, 2/8, first-eats 1327/4468, 1 chain, 4
distant collects. bind-pred [0,0,7,4,3,0,0,7] = 21, 4/8, first-eats
1005/2018/3352/5215, 3 chains, 6 distant collects. No starvation
loss anywhere. The flat arm reproduces d23-class foraging — the
instrument-failure reversal clause does NOT fire.

**The registered noise clause DOES fire** [measured]: every pairwise
eats difference sits inside one life-spread SE (bind−tower +1.0 ±
1.38 paired by round, 4 wins 1 loss 3 ties; bind−flat +0.5 ± ~1.3;
tower−flat −0.5). Per the pre-registration the protocol SCALES
rather than declaring a null. Registered now, before any further
data: **8 more interleaved rounds (n = 16 lives/arm), then the
verdict lands whatever it says** — if every pairwise difference is
still inside spread at n = 16, the recorded verdict is
measured-indistinguishable-at-protocol-scale, not a refutation in
either direction. Noted for the record before the added rounds: the
nominal ordering at n = 8 is bind-pred > flat > tower — the OPPOSITE
sign from the transparent world — and bind-pred leads every
compound meter (chains, distant collects, first-eat at every rank);
all inside spread, none of it leaned on.
