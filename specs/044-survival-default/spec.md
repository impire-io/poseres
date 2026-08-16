# Feature Specification: The Survival Body Is the Default

**Feature Branch**: `044-survival-default`
**Created**: 2026-08-16
**Status**: Shipped
**Input**: User description: "Promote the survival body into the default anatomy — design 0015's measured operating point becomes what c1_anatomy() and the bridge give you with zero configuration."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Zero-config gets the body that lives (Priority: P1)

A person mounting the brain on Minecraft with no flags gets the body
the record proved can sustain itself (episode 0103, two replicated
100k self-feeding lives): the property senses plus the mouth, the
distal senses, the flood, and the palate's worth channel — obs 86,
13 actions — with the bridge wire matching by default.

**Acceptance Scenarios**:

1. **Given** `c1_anatomy()` with no arguments, **Then** the survival
   body (86/13) with `aim` appended last.
2. **Given** the bridge with no env, **Then** SURVIVAL on,
   FLOOD=intrusion, AIM=worth — the handshake matches the default
   anatomy; `contract_check` infers all three from the hello table.

### User Story 2 - Every explicit call keeps its exact meaning (Priority: P1)

Sentinel defaults: only the ZERO-OVERRIDE call changed.
`c1_anatomy(survival=False)` is the pre-044 property body (32/12);
`c1_anatomy(crafting=False)` remains the exact feature-027 body
(14/8, no error); `survival=True` alone remains obs 73;
`survival=True, flood=True` remains 77. Bridge: `SURVIVAL=0` opts out
to the legacy wire; explicit FLOOD/AIM values (including "off"/"")
keep today's instrument semantics.

## Requirements *(mandatory)*

- **FR-001**: `c1_anatomy` flags become `bool | None` / `str | None`
  sentinels; `survival is None` resolves the blessed stack from
  `crafting`; any explicit `survival` resolves unset flags to the
  pre-044 values (False/"").
- **FR-002**: Bridge env: `SURVIVAL !== "0"` default-on; FLOOD/AIM
  default intrusion/worth only when the env var is UNSET.
- **FR-003**: `contract_check` infers survival/flood/aim from the
  hello table (mismatched stacks keep failing loud at the width
  check).
- **FR-004**: `C1_OBS_DIM`/`C1_N_ACTIONS`/`C1_SENSORS` now describe
  the survival body (86/13); `C1_MINING_INDEX`/`C1_POCKET_TOTAL_INDEX`
  are unchanged (14/15 — derived, before the widened hand).

## Success Criteria *(mandatory)*

- **SC-001**: the default-matrix test pins all six configurations
  (86/13, 32/12, 14/8, 73/13, 77/13, 86/13-explicit).
- **SC-002**: full gate green — the byte-frozen suite does not touch
  the Minecraft anatomy default and stays untouched.
- **SC-003**: the promoted default is the measured operating point of
  design 0015, referenced, not re-argued.
