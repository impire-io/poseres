# 0097 — Nothing is faked: the estate deleted, the proof goes live

**Date:** 2026-08-13 · **Kind:** load-bearing decision (owner's rule) ·
**Version:** v2.0.0

## What happened

Three arcs in a row spent effort on behavior the fake bridge blessed
and the real world broke `[measured]`: c1e's digs are
client-wall-clock and its drops far-scatter (amendments 1/1b); the
native-survival teaching leaked through bridge-virtual hands and
split samples (arms amendments 2/3); and the same taught brain that
ate five times in the fake pilot ate zero times live (the parked
stomach). The live-only evidence rule landed in GENESIS earlier the
same week — with a carve-out keeping the FakeBridge for adapter
code-path tests. The carve-out then did what carve-outs do: every new
sense grew a fake "shape" (a sketch glance, an empty drops channel, a
fake flood curve with a fake test), each a small world able to put
the work on the wrong foot again.

Mid-flood-build the owner ended it: **"I don't want you to fake
anything anymore. We have been put on the wrong foot too many times
by trying to fake stuff."** Asked how far, he chose full deletion.

## What was done

- `pra.anatomy.minecraft.FakeBridge` (the ~500-line voxel sketch) and
  its three suites (`test_minecraft_contract`,
  `test_minecraft_survival`, `test_minecraft_fake_run`) **deleted**;
  the runners' fake branches and the pilot phase stripped.
- The adapter's proof is now **`examples/minecraft/contract_check.py`**
  — the wire protocol and the channel table checked against the REAL
  bridge and server, mode inferred from the bridge's own hello table
  (shipped / survival / survival+flood). First run: CONTRACT OK,
  every check green `[measured]`.
- `item_signature` moved to `pra.anatomy.minecraft.protocol` (the
  contract's reference arithmetic, module-level).
- **v2.0.0**: removing a public class is a major by Doc 0008's own
  law; the deprecation grace ladder was superseded by the integrity
  rule via the doc's urgent path, recorded in its release notes.
- Doctrine hardened in place: GENESIS how-we-work (both entries), Doc
  0012 step 7 ("nothing is faked"), the 027 contract ("there is no
  fake side of this seam"), the-flood registration scope.

## The principle

A fake world is a debt instrument: it pays development speed now and
charges research direction later, at an interest rate three arcs
measured. The pytest gate keeps what is honestly unit-testable
(arithmetic, persistence, policies over recorded vectors); everything
that claims to be about the WORLD is proven in the world.

Reversal condition: if the live contract check proves too weak — a
bridge regression shipping undetected through green checks — the
answer is a stronger live check (more ops, more readings, CI against
a real server), never a fake's return.
