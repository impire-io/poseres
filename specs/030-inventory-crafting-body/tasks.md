# Tasks: The Builder's Body — Inventory Sense and Crafting

**Input**: Design documents from `/specs/030-inventory-crafting-body/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md,
contracts/contract-amendment.md

**Tests**: included — the FakeBridge suite is the gate carrier; the
pilot is pre-registered in the spec.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: The contract, amended openly

- [ ] T001 Apply contracts/contract-amendment.md to
      `specs/027-minecraft-body/contracts/minecraft-adapter.md`
      (inventory row, craft commands, amended place, fake wood sources;
      "amended by feature 030" note).

## Phase 2: User Story 1+3 — the sense, and honest matter (P1/P2)

The fake world is one mechanism: inventory + material-honest place land
together (place's no-op needs the inventory to consult).

- [ ] T002 [US1] Extend `src/pra/anatomy/minecraft/fake.py` `_World`:
      wood columns frozenset; `inventory` dict (blocks/logs/planks/
      sticks); dig classifies (wood → logs, else blocks); place
      consumes blocks-then-planks and no-ops on empty; craft_planks /
      craft_sticks arithmetic; `inventory` channel (width 5, held bit =
      blocks+planks > 0); state seam carries the dict;
      `FakeBridge.CHANNELS` grows the row.
- [ ] T003 [US1] Amend + extend
      `tests/contract/test_minecraft_contract.py`: existing semantics
      re-baselined (place now needs material); scripted chain test
      (dig wood → craft → craft → place, every intermediate visible
      next tick); insufficient-input no-ops byte-identical; channel
      ranges/widths.
- [ ] T004 [US1] Anatomy: `c1_anatomy(crafting=True)` default in
      `src/pra/anatomy/minecraft/anatomy.py` — inventory SensorSpec +
      craft presets; `crafting=False` = exact 027 lists;
      C1_OBS_DIM/C1_N_ACTIONS follow the default (19/10).
- [ ] T005 [P] [US1] `tests/unit/test_anatomy_meta.py`: C1 meta at
      19/10 (inventory group [14:19], craft labels), legacy flag =
      exact 027 meta.
- [ ] T006 [US1] `tests/integration/test_minecraft_fake_run.py`:
      engine-over-fake runs at 19/10; byte-identity + exact-resume with
      inventory mid-chain in the snapshot (spec US3 scenario 2).

**Checkpoint**: gate green; the whole chain proven in-repo.

## Phase 3: User Story 2 — the live bridge crafts (P1)

- [ ] T007 [US2] `examples/minecraft/bridge/bridge.js`: inventory
      channel sampling (name-class counts + held bit);
      `craft_planks`/`craft_sticks` via minecraft-data + bot.recipesFor
      + bounded bot.craft (species name-transform, first-found);
      `equipAnyBlock` extended to planks.
- [ ] T008 [US2] Live smoke (documented in quickstart): stack up,
      `rcon give pra oak_log 8`, drive craft via the running brain or a
      scripted pra-mc client; verify inventory channels move and both
      craft commands execute against the real 1.21.11 server (SC-002).

## Phase 4: The pilot (pre-registered, spec FR-008)

- [ ] T009 Run the 8-paired-seed pilot (scratchpad): 19/10 vs 14/8 over
      FakeBridge, short budget; record improvement per seed, craft
      counts, inventory movement. Bars (a)(b) decide; (c) context row.
      Numbers go to the journey episode verbatim.

## Phase 5: Polish & landing

- [ ] T010 [P] Docs: examples/minecraft/README.md (builder's body, the
      give-wood watching trick, snapshot-compatibility note).
- [ ] T011 Full gate green; journey episode (owner decision + reversal
      condition + pilot numbers); roadmap C1 row updated; memory.

## Dependencies

T001 → all. T002 → T003/T006. T004 → T005/T006. Phase 3 independent of
T005/T006 after T001 (contract fixed). T009 needs T002+T004. T011 last.
