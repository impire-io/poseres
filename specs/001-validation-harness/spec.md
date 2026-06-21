# Feature Specification: PRA Validation Harness

**Feature Branch**: `001-validation-harness`  
**Created**: 2026-06-21  
**Status**: Draft  
**Input**: User description: "A reproducible validation harness for the PRA system that runs the acceptance test suite (T1–T6 and the investigatory T-SCALE) from PRA-02 across all configured seeds and emits an honest, human- and machine-readable PASS/FAIL verdict per test; it surfaces the per-seed best_dim spread at multiple horizon checkpoints so the dimensionality test T4 cannot pass on a lucky single-horizon snapshot, judges T5 as self-limiting rather than merely capped, provides a determinism mode that runs one seed twice and asserts byte-identical summaries, and never smooths or cherry-picks results."

## User Scenarios & Testing *(mandatory)*

The harness exists so that the architecture's behavioral claims can be confirmed or refuted **honestly and reproducibly**, before and while the production core is built. The exploratory prototype gave false confidence by reading the load-bearing result at one lucky horizon; this harness must make that failure mode impossible.

### User Story 1 - Trustworthy go/no-go on the behavioral claims (Priority: P1)

A researcher runs the whole acceptance suite in one command and gets, for every test, a PASS or FAIL together with the measured number and the criterion it was judged against — so they can decide whether the architecture's claims hold before investing in the production build.

**Why this priority**: This is the harness's entire reason to exist. Without a single, honest, per-test verdict there is no validation. It is the minimum viable product.

**Independent Test**: Run the suite at the default configuration and confirm it emits a PASS/FAIL line for each of T1–T6 with the measured aggregate and the pass criterion shown alongside.

**Acceptance Scenarios**:

1. **Given** the default configuration, **When** the suite is run, **Then** each of T1–T6 reports PASS or FAIL, the measured aggregate (with mean and standard deviation across seeds), and the exact criterion used.
2. **Given** a test that fails, **When** results are reported, **Then** the failure is shown as FAIL with the numbers that explain why — never hidden, softened, or omitted.
3. **Given** the validated reference configuration, **When** the suite is run, **Then** T1–T6 all PASS, matching the established reference behavior.

---

### User Story 2 - Dimensionality result that cannot be a lucky snapshot (Priority: P1)

The load-bearing test (T4 — structure grows to the right dimensionality) is judged across multiple horizon checkpoints, not at a single end-of-run moment, so a result that agrees early but drifts later is correctly reported as a failure.

**Why this priority**: The prototype passed T4 at one horizon (18 cycles) and failed at another (30). Reading a single snapshot is exactly how a false positive slips through. This protection is as essential as the suite itself.

**Independent Test**: Run a configuration whose dimensionality result is known to drift with horizon and confirm the harness reports the per-seed spread at each checkpoint and a FAIL when the within-one majority does not hold at every checkpoint.

**Acceptance Scenarios**:

1. **Given** a run, **When** T4 is evaluated, **Then** the per-seed `best_dim` list (the spread, not just the mean) is reported at each of several horizon checkpoints.
2. **Given** a run that meets the within-one majority at an early checkpoint but not at a later one, **When** T4 is judged, **Then** the verdict is FAIL.
3. **Given** any T4 report, **When** it is read, **Then** the mean alone is never presented as the verdict; the spread is always visible.

---

### User Story 3 - Reproducibility you can trust (Priority: P2)

A developer runs the same seed twice and confirms the two run summaries are byte-identical, proving a failure can always be attributed to one cause rather than to hidden randomness.

**Why this priority**: Reproducibility is what makes every other verdict meaningful and every failure attributable. It is a precondition for trusting the suite but is not itself the suite, so it sits just below the verdicts.

**Independent Test**: Invoke the determinism mode on one seed and confirm the two summaries compare as identical down to the byte.

**Acceptance Scenarios**:

1. **Given** determinism mode on a single seed, **When** the seed is run twice, **Then** the two run summaries are byte-identical.
2. **Given** any divergence between the two runs, **When** determinism mode completes, **Then** it reports a determinism FAILURE and points at the differing summary.

---

### User Story 4 - Self-limiting, not merely capped (Priority: P2)

The population test (T5 — decay is default) passes only when the population genuinely self-limits — eviction keeps pace with growth — and not merely because it slammed into a hard ceiling.

**Why this priority**: A population that grows until it hits a cap looks "bounded" but is not earning persistence; conflating the two is how the prototype's runaway growth hid behind a finite number. The distinction must be enforced.

**Independent Test**: Run a configuration whose population grows at the spawn rate up to the cap and confirm T5 reports FAIL despite the final count being finite.

**Acceptance Scenarios**:

1. **Given** a run, **When** T5 is judged, **Then** it passes only if the final population is bounded below the hard cap AND no seed's population is still increasing over the final third of its cycles.
2. **Given** a population still growing at the end of the run, **When** T5 is judged, **Then** the verdict is FAIL even if the final count is below the cap.

---

### User Story 5 - The scale question is runnable and measured (Priority: P3)

A researcher runs the investigatory scale test at large true dimensionality and reads the dimensionality spread and throughput, understanding that the *value* of the result is a research finding, not a build pass/fail.

**Why this priority**: The scale question is the open research goal, but the build is "done" when it is *runnable and measured*, so this rounds out the suite without gating it.

**Independent Test**: Launch the scale test at a large true dimensionality and confirm it emits the per-seed dimensionality spread, throughput, and wall-clock, labelled investigatory.

**Acceptance Scenarios**:

1. **Given** the scale configuration, **When** the scale test runs, **Then** it emits the per-seed dimensionality spread and throughput and is labelled investigatory (never reported as a build failure on a poor dimensionality result).

---

### Edge Cases

- **No data yet**: when too few prediction-error samples exist to compute the early/late comparison, the affected test reports "not available" rather than a misleading number.
- **A seed errors mid-run**: the harness reports which seed failed and does not silently drop it from the aggregate or present the remaining seeds as a complete result.
- **Warmup births**: observation losses during warmup are not counted against the no-loss test; only post-warmup losses count.
- **Population at the hard cap**: a run pinned at the cap is reported as capped (and fails the self-limiting test), distinct from a genuinely self-limiting population.
- **Nondeterminism detected**: any byte-level divergence in the determinism check is a hard failure, not a warning to be averaged away.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The harness MUST run every configured seed (default 8) and aggregate the per-seed summaries, reporting mean and standard deviation for each field a test uses.
- **FR-002**: The harness MUST emit, for each of T1–T6, the measured aggregate, the exact pass criterion, and a PASS or FAIL verdict, in a single invocation.
- **FR-003**: The harness MUST report the full per-seed `best_dim` list (the spread) for T4 and MUST NOT present the mean as the verdict.
- **FR-004**: The harness MUST record `best_dim` at multiple horizon checkpoints (default three) and MUST require the within-one-of-true majority to hold at **every** checkpoint for T4 to PASS.
- **FR-005**: The harness MUST judge T5 as PASS only when the final population is bounded below the hard cap AND no seed is still growing over the final third of its cycles, reporting a per-seed "still-growing" flag.
- **FR-006**: The harness MUST provide a determinism mode that runs one seed twice and asserts the two run summaries are byte-identical, reporting PASS/FAIL.
- **FR-007**: The harness MUST write a human-readable summary of the aggregated results, and MAY additionally write a machine-readable summary.
- **FR-008**: The harness MUST measure honestly: it MUST NOT smooth, cherry-pick, or report only favorable seeds; a failing test is reported as FAIL with the numbers that show why.
- **FR-009**: The harness MUST make the investigatory scale test runnable at large true dimensionalities, emitting the per-seed dimensionality spread, throughput, and wall-clock, and labelling it investigatory rather than pass/fail.
- **FR-010**: The harness MUST be fully reproducible from a seed: all randomness draws from a single seeded source in a fixed order, so two runs of a seed produce identical telemetry.
- **FR-011**: The only artifact the harness writes to disk MUST be the result summary; it MUST NOT persist system/model state.
- **FR-012**: The harness MUST default to multi-seed; a single-seed result MUST be labelled as for-debugging-only and MUST NOT be presented as validating a behavioral claim.
- **FR-013**: The harness MUST exercise the system-under-test exactly as specified (nonlinear emission and hidden latent state in the world; observation-space, coverage-fair, parsimony-aware scoring in the system), so the verdicts reflect the validated design rather than a gameable one.

### Key Entities *(include if feature involves data)*

- **Acceptance test**: a named claim (T1–T6, T-SCALE) with a measure, an exact criterion, and a verdict (PASS/FAIL, or investigatory for T-SCALE).
- **Per-seed run summary**: the recorded outcome of one seed — sparsity, early/late prediction error, `best_dim` at each horizon checkpoint, final population and its late growth, loss fraction, and throughput.
- **Across-seed aggregate**: the combination of per-seed summaries — means, standard deviations, and the per-seed spreads the tests are judged on.
- **Verdict report**: the human- and machine-readable output binding each test to its measured number, criterion, and PASS/FAIL.
- **Horizon checkpoint**: a point in the run (measured in consolidation cycles) at which `best_dim` and population are sampled for the horizon-robustness reading.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A single invocation at the default configuration produces a PASS/FAIL verdict for every one of T1–T6, each accompanied by its measured number and criterion.
- **SC-002**: The T4 verdict is derived from `best_dim` sampled at three or more horizon checkpoints; a run that satisfies the within-one majority at an earlier checkpoint but not a later one is reported FAIL.
- **SC-003**: Determinism mode runs one seed twice and the two summaries differ by zero bytes; any non-zero difference is reported as a determinism FAILURE.
- **SC-004**: Every reported verdict shows the measured value and the criterion; no test that requires a per-seed spread is reported by its mean alone.
- **SC-005**: Running the validated reference configuration reproduces the established reference behavior — T1–T6 all PASS, with T4 holding the within-one majority at every checkpoint and T5 self-limiting.
- **SC-006**: The scale test is executable at each large true dimensionality in scope and emits a per-seed dimensionality spread plus throughput and wall-clock, without ever being scored as a build failure.
- **SC-007**: Re-running any seed reproduces its summary byte-for-byte across repeated runs.

## Assumptions

- The system-under-test conforms to the updated PRA design (observation-space prediction, coverage-fair survival scoring, a parsimony term, and the corrected population-scaled decay). The harness validates that system; it does not redefine the scoring.
- The default configuration is `true_dim = 3`, `obs_dim = 10`, eight seeds, warmup per the system specification, and three horizon checkpoints (the validated reference uses 18 / 30 / 50 consolidation cycles).
- The world is the specified sensorimotor environment (nonlinear emission, hidden latent state never exposed to the system); the true latent dimensionality is known only to the harness, for scoring T4.
- The harness runs in-memory on a single machine; distributed execution, external brokers, durable model-state persistence, and a vector index are out of scope for this feature (seams exist for them).
- "Honest summary" is the governing principle: where a tension arises between a tidy report and a faithful one, the faithful one wins.
