# Pronunciation and delivery guide

Give this to the narrator (or paste it into a synthetic-voice tool's
pronunciation dictionary) before the first session. Every term below appears
in the manuscript. Terms marked **(box only)** appear only inside the
technical asides, so they matter only if you record a box variant. IPA is
given for anything a competent English reader could plausibly get wrong;
respellings are the practical fallback.

Stress is marked with a capitalised syllable in the respelling: `POH-zresh`.

---

## The one that matters most

**PRA** — say the letters, `P-R-A` (/ˌpiː ɑːr ˈeɪ/). Never "prah", never
"pra" as a word. It expands to **Pose Resolution Architecture**, which is
spoken in full at first use in chapter 1 and then abbreviated throughout.

A listener who mishears this in the first minute mishears it for three hours.
Consider a retake if the first occurrence is at all soft.

---

## Core vocabulary

These are ordinary English words the book uses as precise technical terms.
They must sound identical every single time — no elegant variation, no
softening into a synonym. STYLE.md forbids variation in print; audio has the
same rule, and breaking it is more damaging aloud than on the page, because a
listener cannot glance back.

| Term | Say | Note |
|---|---|---|
| pose | pohz (/poʊz/) | Rhymes with "rose". Never "poss". |
| frame | fraym | Countable. "A frame", "the frames", "fifteen frames". |
| triplet | TRIP-lit | Not "TRIP-lay". |
| drive | dryv | Noun throughout, not a verb. |
| dimension | dih-MEN-shun | Also appears clipped as "dim" — see below. |
| dim | dim | Said as the short word, not "D-I-M". "dim 18" = "dim eighteen". |
| oracle | OR-uh-kul | |
| stipend | STY-pend (/ˈstaɪpɛnd/) | Not "STIP-end". |
| provisioning | pruh-VIZH-uh-ning | |
| election | ih-LEK-shun | Deliberately the political word, used in a non-political sense. Do not stress it as if surprising. |
| tick | tik | Unit of simulated time. "tick 1,500" = "tick fifteen hundred". |
| seed | seed | Random-number seed. "seeds one, three, five". |
| eviction / evicted | ih-VIK-shun | Of frames, not tenants. Neutral tone. |

---

## Acronyms and initialisms

| Written | Say |
|---|---|
| PRA | letters: P-R-A |
| LLM, LLMs | letters: L-L-M, L-L-Ms |
| AI | letters: A-I |
| ROS2 | "ross two" (/rɒs tuː/) — the robotics framework, said as a word plus the digit |
| ULP | letters: U-L-P. Expanded in text as "unit in the last place"; read the expansion when it appears, then the letters after |
| RNG | letters: R-N-G **(box only)** |
| EMA, EMAs | letters: E-M-A, E-M-As **(box only)** |
| NLMS, LMS | letters, spelled out **(box only)** |
| CLI | letters: C-L-I **(box only)** |
| TPS | letters: T-P-S **(box only)** |
| UTC | letters: U-T-C **(box only)** |
| TV | letters: T-V |
| RCON | "AR-con" **(box only)** |
| nats | "nats" as a word, rhymes with "cats" — the unit of information **(box only)** |

## Gate and experiment labels

These appear in the **main text**, not only in boxes, and they carry the
book's plot: each one names an experiment that either passed or failed.

| Written | Say |
|---|---|
| G1, G5 | "gate one", "gate five" |
| T7 | "test seven" |
| V0, V+ | "V zero", "V plus" |
| E3.1 | "E three point one" |
| STEP-0 | "step zero" |
| c1c, c1d | "C one C", "C one D" (run identifiers) |
| Bar A, Bar T2, Bar R1 | "bar A", "bar T two", "bar R one" **(box only)** |

Say the label the same way every time. The listener is tracking a scoreboard
across three hours and cannot look anything up.

## Identifiers with underscores

Read as separate words. Never say "underscore".

| Written | Say |
|---|---|
| `best_dim` | "best dim" |
| `turn_left` | "turn left" |
| `score_window_steps` | "score window steps" **(box only)** |
| `drive_value`, `pred_a`, `event_head`, `pos_after` | as spaced words **(box only)** |

## Not to be read aloud

The manuscript carries internal document references — `PRA-01`, `PRA-02`,
`LONGEVITY-DIAGNOSIS.md`, `SCORER-DIAGNOSIS.md`, `THRESHOLD-DIAGNOSIS.md`,
`C1D-LAB-RUN-PLAN.md`, `hq/02-DESIGN/validate/...`, `README.md`, `specs/...`
— plus `PASS` / `FAIL` gate outcomes and journey episode numbers.

**None of these belong in audio.** File paths read aloud are noise; a
listener cannot write one down and cannot click it. All of them sit inside
`Under the hood` boxes or HTML comments, which is why the default build omits
boxes entirely (see NARRATOR-BRIEF.md). If you record a box variant, the
audio rewrite must drop every path and keep only the result — including
turning "PASS 24/24" into a spoken sentence rather than a label.

---

## Numbers

The book is full of measurements, and this is where synthetic voices fail
most often. Rules, in order of precedence:

1. **Decimals below one**: say "zero point", not "point" or "oh point".
   `0.0081` → "zero point oh oh eight one". Reading long decimal strings
   digit-by-digit after "zero point" is correct and clearer than grouping.
2. **Decimals above one**: `3.1` → "three point one". `98.22` → "ninety-eight
   point two two".
3. **Percentages**: `20%` → "twenty percent". `100.0%` → "one hundred
   percent" — drop the trailing point-zero, it adds nothing aloud.
4. **Thousands**: `5,000` → "five thousand". `57,219` → "fifty-seven thousand,
   two hundred and nineteen". `1,957` → "one thousand nine hundred fifty-seven",
   not "nineteen fifty-seven", which sounds like a year.
5. **Ratios written with a slash**: `24/24` → "twenty-four out of twenty-four".
   `6/8` → "six out of eight". Never "twenty-four slash twenty-four".
   **Exception — genuine fractions.** `1/12 ≈ 0.083` in chapter 14 is one
   twelfth, not one out of twelve. If the slash sits between a small number
   and a larger one *and the sentence is about a share or a rate rather than
   a score*, read it as a fraction. There are only a handful; check each.
6. **Comparators**: `≥` → "at least". `≤` → "at most". `≈` → "about".
   `±` → "plus or minus". `−0.006` → "minus zero point oh oh six".
   `→` → "becomes" or "going to", whichever the sentence wants: "printed nan
   early, becoming nan late". `·` (multiplication dot) → "times".
7. **Greek letters**: say the letter name, then the value. `β` → "beta".
   `κ` → "kappa". `λ` → "lambda". `Φ` → "phi". `Δ` → "delta". `π` → "pi"
   (the number, said like "pie"). Subscripts are read as plain numbers:
   `κ₅` → "kappa five". A trailing star is said: `κ*` → "kappa star".
8. **Ranges with an en dash**: `62–74` → "sixty-two to seventy-four".
   `18–20` → "eighteen to twenty". Never "dash".
9. **`dim N`**: "dim eighteen", "dim two", "dim sixty". `33-dim` → "thirty-three dim".
10. **Version numbers**: `v3`, `v4` → "vee three", "vee four" — these are
    the project's own prototype generations and the book treats them as
    names. Software versions with dots are read digit-grouped: `1.20.3` →
    "one point twenty point three"; `v1.1.0 → v1.2.0` → "version one point
    one point zero, to version one point two point zero".
11. **Clock times** are 24-hour in the manuscript and mark events during a
    single working day. Convert to 12-hour: `13:11` → "eleven minutes past
    one"; `21:55` → "five to ten at night"; `22:49` → "ten forty-nine at
    night". The point of these is lateness, so keep whatever phrasing makes
    the hour audible.
12. **Dates**: `2026-07-18` → "the eighteenth of July, twenty twenty-six".
    `2026-08` → "August twenty twenty-six".
13. **Degrees**: `180 degrees` as written. **Units** are always spelled out
    in the manuscript already; read them as they appear.

A note on why this matters here specifically: STYLE.md makes real numbers the
book's defence against sounding machine-written ("One seed climbed to dim 18
of a true 20" cannot be generated by a model that wasn't there). A number
garbled in narration doesn't just lose precision — it loses the thing that
makes the passage credible.

---

## Commands and code

Two chapters display commands:

- `pip install poseres` → "pip install poseres" — "pip" as a word,
  "poseres" as `POHZ-res`.
- `pra-rover` → "P-R-A rover".

Do not spell out hyphens or punctuation. The front matter tells listeners
these appear in the accompanying text, so the audio only needs to convey
what the command is, not how to type it.

---

## Other technical words in the main text

| Term | Say | Note |
|---|---|---|
| lidar | LY-dar | Not spelled out. |
| odometry | oh-DOM-uh-tree | |
| diff-drive | DIF drive | Two-wheel robot drive. Not "diff dash drive". |
| nan | "nan" as a word (/næn/) | Chapter 12. It is the floating-point "not a number", and the book uses it as a word — "nan early, nan late". Not "N-A-N". |
| subgoal | SUB-gohl | |
| Frobenius | fro-BEE-nee-us | **(box only)** |
| juveniles / adults | ordinary words | Of frames, not animals. Neutral. |

## Proper nouns

| Written | Say |
|---|---|
| Minecraft | MYNE-kraft |
| Gazebo | GAZ-uh-boh — the robot simulator, said like the garden building |
| CartPole | CART-pole — one word, both parts stressed |
| Gymnasium | jim-NAY-zee-um — the reinforcement-learning library, said like the English word |
| Stephen Fry | STEE-vun FRY |
| Daan Gerits | "Dahn HHEH-rits" — Dutch. `Daan` rhymes roughly with "barn" without the r (/daːn/); `Gerits` opens with the Dutch voiceless velar fricative /ɣ/~/x/, closest English approximation a soft throat-clearing "h". An English narrator saying "Dan Gerrits" is acceptable if the author approves; confirm before recording, because it is the author's own name in a first-person book. |
| Pose Resolution Architecture | pohz res-uh-LOO-shun AR-ki-tek-cher |
| poseres | POHZ-res (the package name) |
