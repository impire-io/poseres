# Revisit list

Things to resolve once the full draft exists. Working file, not part of the
book. Add items as they come up; strike them when resolved.

## Planted claims — Daan must verify or replace (highest priority)

- [ ] **Ch 1** — the robot-vacuum opener is the ghostwriter's, not Daan's
  real origin moment. If a real "why I started PRA" moment exists, it
  belongs in the "I've been building" paragraph and possibly replaces the
  opener.
- [ ] **Ch 2** — invented emotional beats: "briefly, very pleased with
  myself", "made me laugh out loud". Replace with what the v3 afternoon
  actually felt like.
- [ ] **Ch 2** — "deleting is where understanding comes from" is an
  editorial claim in Daan's voice. Own it or cut it.
- [ ] **Ch 4** — the stated rationale for reward-free triplets
  ("understanding and wanting in separate rooms, because a brain that
  learns forever must be able to change its wants") is reconstructed
  reasoning, not sourced. Verify against the actual design motivation.
- [ ] **Ch 5** — "(I use one most days, and gladly)" about LLMs. Confirm
  or cut.
- [ ] **Ch 7** — closing thesis "Learning was cheap. Measuring learning
  was the work." and "my favorite result in the project". Both inferred
  from the record's shape; confirm they're true of Daan.
- [ ] **Ch 9** — "the one half the field and I both reached for first"
  and "It's also what I would have bet on" (about curiosity): the record
  shows curiosity *was* built first, but the framing of Daan's prior
  expectation is inferred. Confirm.
- [ ] **Ch 9** — closing "life lessons" paragraph (practice vs novelty):
  deliberately restrained, but it's still an editorial move. Keep or cut.
- [ ] **Ch 11** — "worth a moment of awe" and the closing claim that the
  byte-identity discipline is "the whole reason there's anything in this
  book worth telling": strong editorial statements in Daan's voice.
- [ ] **Ch 12** — section heading "The first real sensor drew blood" —
  register check; also verify the ~4-minute / "well under five minutes"
  claim matches the current pra-rover defaults before publication.

## Register — cute-risk spots (Daan to arbitrate, per 2026-07-18 note)

- [x] **Ch 7** — "bouncer" heading renamed to "make eviction toothless"
  in the cheat expansion pass (2026-07-18).
- [x] **Ch 7** — "one-word diary" image: removed in the concrete rewrite
  of cheat one (2026-07-18). Check whether ch 2's preview of the same
  cheat still reads well on its own.
- [ ] **Ch 6** — "employees at a company that has figured out its
  headcount"; also check "parliament of coordinate systems".
- [ ] **Ch 4** — "the baby is running experiments" framing (probably
  fine, checking anyway).
- [ ] General: chapters 1–5 were written before the "clear, not cute"
  register rule was added to STYLE.md; give them one full pass against it.

## Clarity — flagged by Daan

- [ ] Terminology: ch 4 now says "motivation" (Daan's preference over the
  abstract "wanting"). Ch 9 is still titled "Wanting things" and the
  glossary defines drive as "the system's wanting". Align across the
  book once Daan picks the canonical word (motivation vs wanting vs
  drive).
- [x] Em-dash sweep across all 12 chapters (2026-07-18): ~210 → ~1.
  STYLE.md rule tightened to "almost never".
- [ ] Fluency pattern to sweep for globally: colon-fragment lists
  ("what I heard, what I said, what came back") and stacked appositives.
  Daan has now flagged three such passages (ch 4 motivation paragraph,
  ch 5 creek paragraph, ch 5 language paragraph). Assume more exist in
  chapters 1–3 and 6–12; do a dedicated read-aloud pass.

- [ ] **Ch 2** — the ending turns abstract (the "honest, unavoidable
  accounting" paragraph and the hand-off into ch 3). Reground it in
  something concrete — likely the v3 population chart or a physical
  image — before the chapter closes.

## Style-guide decisions to confirm

- [ ] Reading-level target amended (2026-07-18) from "grade 6–7" to
  "6–8, mechanism chapters may run higher". Confirm or revert.
  Measured so far: ch1 ~5.8, ch2 ~6.9, ch3 ~6.8, ch4 ~6.4, ch5 ~6.8,
  ch6 ~7.6, ch7 ~8.5, ch8 ~9.3.

## Structural / bookkeeping

- [ ] Decide whether parts get intro pages (currently they don't).
- [ ] Open question (Daan's, 2026-07-18): whether and where the book
  acknowledges the Thousand Brains lineage
  (pose-resolution-architecture.md §9). No change made; decide at
  revision time.
- [ ] Chapter length balance: ch5 (~870 words) is the shortest; consider
  expanding once the whole arc is visible.
- [ ] Cross-references ("chapter 8's subject", "Part 4") — verify all
  once chapter numbering is final.
- [ ] Glossary completeness pass against every italicized definition.
- [ ] **Ch 4** — the worked triplet in "One triplet, in numbers" uses
  constructed illustrative values. Replace with a real logged triplet
  from an actual pra-rover run (trivially dumpable) so the example is
  authentic to the last digit.
- [ ] **Ch 11 accuracy check** — "Not one triplet is retained" may be
  overstated: the novelty/frontier drives keep a bounded windowed
  observation memory (Doc 05; PREDLP). Verify the exact mechanism and
  soften to "outside a small fixed window in the drive layer" if
  confirmed. Also consider adding the recognition-vs-prediction
  distinction (two faces of dispositional memory) to ch 6 or ch 11.
- [ ] **Numbers audit before any publication**: re-verify every empirical
  claim against the repo at that date. Known risk: channel weighting
  (spec 016) is in progress and may change scaled results; the
  "medians 10/9/9" and price-crossing numbers are 2026-07 snapshots.
- [x] hq/04-JOURNEY/: when the book/ directory is first committed, consider an
  episode recording the book decision (voice, two-lane rule, register).
  Daan's call and Daan's file. Done: episode 0047 (2026-07-21).
- [ ] Part 5 has no measured foundation yet beyond multi-stream (journey 0022).
  Before drafting chapters 13–14, re-check whether any teacher-related
  work has landed since 2026-07-18.

## STYLE-checklist audit, 2026-07-27 — findings for arbitration

Full revision-checklist pass (STYLE.md items 1–7) over all 12 drafted
chapters, every cited number cross-checked against `hq/04-JOURNEY/` and the
`hq/02-DESIGN/validate/*-DIAGNOSIS.md` trail. Findings only; no prose was
touched. Items already tracked above are referenced, not repeated.

### Mechanical results (whole book)

- Banned words/phrases (item 2): zero hits in any chapter's prose. PASS.
- Em dashes (item 3): exactly one in the book (ch 1, "on your own
  screen — from first command"); within budget. PASS.
- No bullet lists anywhere; all headings sentence case; boxes strippable in
  every chapter with the story intact (items 1, 3). PASS.
- First-sentence parallelism (item 4): none found beyond ch 1's deliberate
  "The world changes / The task changes / The body changes" triple. PASS.
- [ ] Bold outside first definitions: ch 7's four run-in cheat labels
  ("**Cheat one: grade me in my own coordinates.**" etc.). They function as
  structural labels like the box titles, but sit outside the letter of the
  bold rule. Style call.
- [ ] One exclamation mark outside dialogue: ch 6 "(motors forward!)" — a
  mock command, borderline under the humor policy.
- [ ] Chapters with no dated, record-sourced event (item 5): ch 1 (only the
  planted vacuum opener, tracked above), ch 4, ch 5. Ch 4/5 are concept
  chapters; recorded here so the gap is a decision, not an oversight.
- [ ] Reading ease: ch 9–12 not yet measured (extends the style-guide item
  above; ch 8's measured ~9.3 leans on the "mechanism chapters may run
  higher" clause).

### Numbers audit (item 7) — claims I could not find in the record

Everything not listed here traced cleanly: the v3 postmortem set (18→30
cycles, 6/8→3/8, best_dim drift 1/2/6, ~+1 frame/cycle, 0.36 vs ~1.0, 23%,
0.04/dim; `pra_sim_v4.py` header, journey 0002), the T-SCALE set (~40×,
td 20/35/50, obs 60/105/150, best_dim≈1; journey 0003), the scale-rule set
(patience 2/12/24/29 → 4.7/5.7/6.7/10.7; 65%/18% saturation; medians
8/10.5/9.5; one seed to 18; climbers 62–74; census 29/0; 24/24 anchored;
10/9/9; 0.0067/dim crossing 8–12; dim-28 minimum at 4×; journey 0004/0009/
0011/0014, SCALE-/THRESHOLD-/SCORER-DIAGNOSIS), the E3 fair-judge grid
(median 32.5; 8/8 at dims 7–11, ages 353–496/500; pops 44–57 vs cap 200;
K=5/K=2), the full T7/agency set (−0.006±0.036; 3/8; −0.062; 1/8; 87%;
+0.014; +0.067 in 6/8; +0.064/+0.027 in 6/8; journey 0005/0007,
AGENCY-DIAGNOSIS), the rot/cap set (dims 8–24; onset 400–800 cycles;
∞/1.5/1.2 dose–response; 6.0→10.0; anchors 4–8→7–12; tenures 1736–1977;
+4/+1/+0.5; SCORER §E2, LONGEVITY), and the ch 12 set (five obstacles,
10-channel anatomy, ~50-line adapter, 3.6% respawns, ±inf lidar,
half-channel static collapse, populations 15/19/13, best_dim 2).

Not found or discrepant (do not fix without Daan; publication numbers
audit needs this list):

- [ ] **Ch 8** — "After a year of removing every dishonesty I could find":
  the recorded honesty arc runs June 2026 (journey 0002) to 2026-07-11
  (journey 0014). Nothing in the record supports "a year". Looked: episode
  dates 0001 ("up to 2026-06-20") through 0014. Either real unrecorded
  prehistory (Daan to confirm) or the wording overstates.
- [ ] **Ch 8** "Months of measurement said otherwise" and **ch 7** "the
  months of it": the scale/judge campaign is dated 2026-06-29 → 07-11 in
  the record (journey 0004, 0011, 0013, 0014) — weeks, not months. Same
  question as above.
- [ ] **Ch 11** — "Five features after snapshots shipped": snapshots are
  feature 003 (journey 0006); the one-ULP bug was caught in feature 010
  (journey 0023), with six features (004–009) landing between. "Five" is
  not supported by any counting I could construct. The section heading
  repeats the count.
- [ ] **Ch 10** — "roughly doubling their honest prediction error between
  the standard budget and the long one": SCORER-DIAGNOSIS §E2 records the
  doubling vs the 4× budget (2400 episodes: dim 8 0.31→0.49, dim 20
  0.25→0.53), not vs the standard 600. The box's "norm 20 → 18 → 29" is
  the top of the record's 27–29 range (substantively verified; noting for
  precision).
- [ ] **Ch 7** — "across all eight seeds" for the v4 full-suite pass:
  journey 0002 records "passed T1–T6 honestly" with no per-seed spread;
  the nearest seed-level reading (journey 0003's oracle checkpoints) shows
  6/8 at one checkpoint. Not confirmable as stated.
- [ ] **Ch 9** — "four hundred simulation runs": no such count in the
  record; the journey 0024 grid alone was 576 runs. Unverifiable as
  stated (rhetorical understatement, but it is a number).
- Ch 12 "about four minutes" and ch 4's constructed worked triplet:
  already tracked above (no change; this pass confirms neither is in the
  record — journey 0020 says "well under five minutes").

### Since-reversed or superseded results (text predates the record's turn)

- [ ] **Ch 9 (most severe)** — the drive-layer ending. "The shipped drive
  became competence... it held up later on worlds built specifically to
  punish it"; the frontier drive "wins nothing over competence"; its
  payoff worlds are "named, instrumented, and not yet measured." Since
  drafting: journey 0031 measured the camping bill (competence stood, at
  reference), then journey 0053 reversed the competence-alone posture for
  Minecraft (idling 26.7% of steps, mechanism traced to
  familiarity-as-competence) and journey 0054 vindicated the frontier
  drive live (idle 3.1%, reversal untriggered). The chapter's
  reference-scale story remains true as written; its "current edge"
  framing and the held-up claim now have a measured sequel that reverses
  the posture in a rich world. (Update 2026-08-08: the sequel is drafted
  as ch 13, `part-5-the-long-run/13-the-log-it-put-back.md`, from the
  c1c close, journey 0068 — arbitration of ch 9 can point forward to it.)
- [ ] **Ch 12** — "learned channel weighting, is on the bench as I write
  this, and it explicitly gates the physical-robot showcase": journey 0030
  (2026-07-18) landed it — L3 noise PASSes opt-in at 24 seeds, the
  default-config FAIL kept as the recorded reference — and journey 0060
  then parked C2 (the showcase in question). Stale on both counts.
- [ ] **Ch 10** — "Whether very long reference-scale lives eventually
  would [need the cap] is a named open question, not a settled one":
  journey 0041 answered it at deployment length — no rot in 500k-step
  reference-scale soaks, cap measured behaviorally free, C1 runs cap-on.
- [ ] **Ch 5 and ch 12 closings** — the Part 5 teacher hook ("The record
  hasn't answered"; "Part 5 asks what this architecture becomes when the
  world teaches back"): journey 0054–0058 have since answered a large part
  of it (teaching alone moved nothing at full power; knowledge plus even a
  failing want produced the record's only deliberate chains; the topic is
  parked with the existence proof standing). The hooks are not wrong; the
  tense is. Part 5's premise needs re-arbitration against the parked
  topic before those chapters are drafted (extends the Part 5 item above).
- [ ] **Ch 11** — "Not one triplet is retained": this pass confirms the
  accuracy concern tracked above — Doc 05 §3.2–3.3's
  `recent_observation_memory` is "a bounded store of recent observations"
  in drive bookkeeping, so the flat claim is overstated per the record.
- Ch 1 — "runs, today, on worlds ranging from simulated rovers to anything
  that speaks a robot's message protocol": since journey 0043 the record
  also has Minecraft. Understated, not wrong; currency note only.

### Voice and lane findings (new ones only)

- [ ] **Ch 4** — broken cross-reference: "When chapter 3 said PRA's models
  compete to predict well" — chapter 3 says no such thing; the
  crowd-of-rivals preview is chapter 2's ("keeps a whole crowd of small
  rival models"). Concrete instance for the cross-reference item above.
- [ ] **Ch 6** — encoder/decoder arrive in the main text without the
  italicized one-line definition, and have no glossary entries; the
  glossary also has no Part 4 section at all (extends the glossary
  completeness item above).
- [ ] **Ch 8** — "the emission function saturated" in main text: the term
  exists only in ch 3's Under-the-hood box, so the main-text lane has
  never met it. Lane wobble.
- [ ] **Ch 8 / ch 12** — `best_dim` appears in main text (ch 8 quotes the
  readout; ch 12 names the on-screen quantity). The only code identifiers
  in the main lane; ch 12's is arguably earned since the screen shows it.
  Style call.
- [ ] **Ch 12** — "The instrument smiled; the numbers were garbage":
  cute-risk candidate for the register list above (not previously
  tracked). Same section as the tracked "drew blood" heading.
- [ ] **Ch 10** — "death with the lights left on": strong metaphor,
  arguably load-bearing; register call.
- [ ] **Ch 2** — "the way you laugh at a plumbing disaster": extends the
  tracked invented-emotional-beats item (same paragraph family as "made
  me laugh out loud").
- [ ] Colon-fragment sweep candidates found for the tracked fluency item:
  ch 8 "why it moves, what it practices, what it seeks out"; ch 10 "what
  'memory' even means" hand-off; ch 3's "what you sensed, what you did,
  what you sensed next" is the triplet formula itself and probably stays.

### Summary

| ch | voice/register | lanes | unverified numbers | stale vs record | verdict |
|----|----------------|-------|--------------------|-----------------|---------|
| 1 | planted opener (tracked) | clean | 0 | currency note | needs arbitration |
| 2 | tracked beats + 1 new | clean | 0 | — | needs arbitration |
| 3 | clean | clean | 0 | — | pass |
| 4 | tracked register item | clean | tracked triplet; broken xref | — | needs arbitration |
| 5 | tracked planted claim | clean | 0 | Part 5 hook | needs arbitration |
| 6 | 2 tracked + exclamation | encoder/decoder defs | 0 | — | needs arbitration (minor) |
| 7 | tracked editorial claims | bold labels | "all eight seeds"; "months" | — | needs arbitration |
| 8 | clean | emission function; best_dim | "a year"; "months"; else verified | — | needs arbitration |
| 9 | tracked editorial claims | clean | "four hundred runs" | drive posture reversed (0053/0054) | needs arbitration |
| 10 | 1 register note | clean | doubling baseline | cap question answered (0041) | needs arbitration |
| 11 | tracked editorial claims | clean | "five features" | retention overstated (confirmed) | needs arbitration |
| 12 | 1 new + tracked heading | best_dim in main | tracked "four minutes" | weighting landed (0030); C2 parked (0060); Part 5 hook | needs arbitration |

### For arbitration, by severity

1. Ch 9's ending vs journey 0053/0054: the competence posture is reversed
   for Minecraft and the frontier drive vindicated; the book's "current
   edge" is no longer the record's.
2. Ch 8 "after a year" and ch 7/8 "months" vs the record's June–July 2026
   arc: confirm real prehistory or correct before the publication numbers
   audit.
3. Ch 12's channel-weighting sentence vs journey 0030 and 0060 (landed;
   showcase parked).
4. Ch 5/12 Part 5 teacher hooks vs the parked self-set-goals topic
   (journey 0054–0058).
5. Ch 10's cap open question vs journey 0041 (answered at C1 length).
6. Ch 11: "five features" count; "not one triplet is retained" (confirmed
   overstated per Doc 05).
7. Ch 4's chapter-3 cross-reference (the statement is chapter 2's).
8. Precision fixes: ch 7 "across all eight seeds"; ch 9 "four hundred
   runs"; ch 10 doubling baseline.
9. Style calls: ch 7 bold cheat labels; ch 6 "(motors forward!)"; register
   candidates in ch 10 and ch 12.

## Part 6 (chapters 14–15, drafted 2026-08-09)

- [ ] **Ch 14** — "because I was only thinking about digs when I wrote it"
  (the G1 completion-rule beat): interior moment inferred from the record's
  "the hand-built rule only ever covered dig completion" — Daan confirm or
  reword.
- [ ] **Ch 15** — closing editorials in Daan's voice ("for information, not
  for payment"; "my pupil learns most from praise when…"): supported by the
  V0/V+ rows but owned opinions — confirm.
- [ ] **Ch 14** — "a faithful stand-in of the same Minecraft mechanics, one
  the test rig can copy and restart" (the FakeBridge gloss) — composite of
  scattered record claims, never stated in one place; verify wording.
- [ ] **Ch 14** — timing language ("before the day was out") inferred from
  commit dates, not a recorded clock.
- [ ] **Part 6 gap** — the parallel afternoon (episodes 0074–0075: the
  brain-side hold, the inert label, the meter's runway) post-dates these
  chapters; chapter 16 material once the reach arc concludes.
