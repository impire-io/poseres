# Tasks: Honest Primitives

**Input**: Design documents from `/specs/031-honest-primitives/`

## Format: `[ID] [P?] [Story] Description`

- [ ] T001 Apply contracts/contract-amendment.md to
      `specs/027-minecraft-body/contracts/minecraft-adapter.md`
      (hand/grid rows, inventory[4] redefinition, command swap,
      body-furniture declaration; "amended by feature 031" notes).
- [ ] T002 [US1+US2] `src/pra/anatomy/minecraft/fake.py`: `held` +
      `grid` state; `hold_next` cycle; held-based `place_ahead`
      (removes 030 auto-pick); `grid_put` (column-first, held class,
      pocket-decrementing), `grid_take`, `take_result` (vanilla-exact
      offers); macro commands deleted; `hand`/`grid` channels; state
      seam grows both; `FakeBridge.CHANNELS` updated.
- [ ] T003 [US3] `src/pra/anatomy/minecraft/anatomy.py`: hand + grid
      sensors, four grid presets replacing the macros; 28/12 default;
      `crafting=False` legacy untouched.
- [ ] T004 [US1+US2] Tests amended + ladder test
      (`tests/contract/test_minecraft_contract.py`): held-based place;
      the full honest ladder step-by-step (FR-008) including the
      second-log-kills-the-offer vanilla consequence; mid-staging
      state round trip; `tests/unit/test_anatomy_meta.py` 28/12;
      `tests/integration/test_minecraft_fake_run.py` follows constants.
- [ ] T005 [US2] `examples/minecraft/bridge/bridge.js`: hand/grid
      channels, virtual staging with real material flows, real craft at
      `take_result` + re-sync, held-based place; macros deleted.
- [ ] T006 Pilot per spec FR-009 (scratchpad; results to
      pilot-results.md): bar (a) only; engagement + delta as context.
- [ ] T007 Live smoke: stage a real log over the wire, see
      result-is-planks, take it, verify 4 real planks (SC-002).
- [ ] T008 Docs (`examples/minecraft/README.md` what-the-bot-does
      section), full gate, journey episode 0050, roadmap row, memory.

Order: T001 → T002/T003 → T004 → T005 → T006/T007 → T008.
