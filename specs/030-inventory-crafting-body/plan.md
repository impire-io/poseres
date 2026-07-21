# Implementation Plan: The Builder's Body — Inventory Sense and Crafting

**Branch**: `030-inventory-crafting-body` | **Date**: 2026-07-21 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/030-inventory-crafting-body/spec.md`

## Summary

Amend the pra-mc/1 channel contract (feature 027) with a width-5
`inventory` channel and two craft commands; implement identically in the
FakeBridge (which gains wood sources, material-honest placement, and
inventory in its class-1 state seam) and the live mineflayer bridge;
grow the default C1 anatomy to 19/10 with the 14/8 body one flag away;
run the pre-registered 8-seed learnability pilot and publish its
numbers. **Zero brain-side edits beyond the anatomy declaration** — the
transport tolerates extra bridge channels (measured: it validates only
declared topics, transport.py:156), and the 029 metadata path carries
the new group/labels to the dashboard with no dashboard changes.

## Technical Context

**Language/Version**: Python ≥3.12 (repo venv), Node ≥18 (bridge)
**Primary Dependencies**: none new — mineflayer already ships `bot.craft`
+ `minecraft-data`; the FakeBridge stays stdlib-pure arithmetic
**Storage**: fake state seam grows an `inventory` dict (class-1 resume)
**Testing**: pytest — the 027 contract/integration suites amended in
place (the semantic change is the spec change), plus new chain tests;
pilot via the existing engine-over-FakeBridge pattern
(`test_minecraft_fake_run.py`)
**Target Platform**: darwin/linux localhost; live smoke vs the 1.21.11
dockerized server
**Project Type**: single Python package + one Node bridge file
**Performance Goals**: unchanged tick budgets; craft bounded like
dig/place
**Constraints**: constitution I (no core edits; reference suite
untouched), II (pilot bars pre-registered in the spec; numbers published
either way), fake/live semantic parity (SC-002)
**Scale/Scope**: obs 14→19, actions 8→10; ~6 files touched + tests

## Constitution Check

- **I — PASS**: no `src/pra/core` edits; anatomy/bridge/fake only. The
  C1 anatomy is a feature surface, not the byte-frozen reference; the
  T1–T6 suite never touches it.
- **II — PASS**: pilot bars fixed in spec FR-008 before implementation;
  the 19/10-vs-14/8 comparison is a published context row with no
  quiet tuning path.
- **III — N/A** (capability feature, not a behavioral fix); the one
  diagnosis-flavored item (fake/live placement divergence) is named in
  the spec and fixed openly.
- **IV — decision recorded**: the owner overrode the evidence gate with
  the risk stated and a reversal condition written at decision time
  (spec Overview + Assumptions). The working agreement is satisfied:
  adversarial case argued (previous turn), teach-back given ("aware of
  the consequences… in line of our ambitions"), reversal executable
  (`crafting=False`).
- **V — PASS**: the fake world keeps ground truth, determinism,
  steppable time; the material chain now exists inside it.
- **VI — applies**: full gate before done; signed commits.

**Post-design re-check: PASS** (no new dependencies, no core edits).

## Project Structure

### Documentation (this feature)

```text
specs/030-inventory-crafting-body/
├── plan.md              # This file
├── research.md          # decisions + alternatives (encoding, recipes, parity)
├── data-model.md        # channel/command/state-seam shapes
├── quickstart.md        # gate + live smoke + pilot
├── contracts/
│   └── contract-amendment.md  # the delta applied to specs/027 contract
└── tasks.md
```

### Source Code (repository root)

```text
src/pra/anatomy/minecraft/
├── anatomy.py           # + inventory SensorSpec, craft presets; crafting=True default,
│                        #   crafting=False = the exact 027 body (reversal path)
├── fake.py              # + wood columns, inventory dict, material-honest place,
│                        #   craft arithmetic, inventory channel, state-seam growth
└── (transport.py unchanged — tolerates extra channels, measured)

examples/minecraft/bridge/bridge.js
                         # + inventory channel sampling (name-class counts),
                         #   craft_planks/craft_sticks via bot.craft (budget-bounded),
                         #   equipAnyBlock extended to planks

specs/027-minecraft-body/contracts/minecraft-adapter.md
                         # table amended in place, "amended by feature 030" noted

tests/
├── contract/test_minecraft_contract.py   # amended semantics + chain scripts
├── integration/test_minecraft_fake_run.py # 19/10 run + byte-identity/resume with inventory
└── unit/test_anatomy_meta.py             # C1 meta: 19/10 groups/labels + legacy flag
```

**Structure Decision**: additions ride the 027 module boundaries
exactly; the contract amendment happens in the normative 027 file (the
027 contract itself says changing the table *is* a spec change — this
feature is that change, executed openly with its own delta doc).

## Design decisions (research.md carries rationale + alternatives)

1. **Encoding**: `inventory` = [blocks, logs, planks, sticks each
   min(count,64)/64; held_is_placeable ∈ {0,1}] at slice [14:19].
   Coarse name-classes on the live side (`dirt|stone` substrings, `*_log`,
   `*_planks`, `stick`); exact integer classes in the fake.
2. **Placement material order**: mined blocks first, then planks —
   both bridges identical; fake's held bit = (blocks+planks) > 0
   (mirrors live auto-equip).
3. **Craft mapping (live)**: species by name transform
   (`X_log → X_planks`), first inventory species wins;
   `bot.recipesFor` + `bot.craft` bounded by the tick budget.
4. **Pilot**: 8 paired seeds, FakeBridge world, the
   `test_minecraft_fake_run.py` harness scaled to a short budget; arms
   19/10 vs 14/8 (same seeds); bars per spec FR-008; numbers to the
   journey episode. Runs in the session scratchpad, conclusions land in
   git (constitution III discipline).

## Complexity Tracking

No violations; table not needed.
