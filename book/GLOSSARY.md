# Glossary

Every italicized first-use definition from the main text, in order of
appearance. Plain words only; the technical version lives in the chapter's
`Under the hood` boxes.

## Part 1

**training** — the study phase of a machine brain: learning from a big pile
of examples before the machine ever does its real job. (Ch 1)

**frozen** — a brain whose learning has been switched off: a snapshot of
what was learned during training, shipped as the product. (Ch 1)

**catastrophic forgetting** — new learning destroying old competence,
because both are stored in the same shared numbers. (Ch 2)

**dimensions** — the separate knobs you'd need on a control panel to pin
down what state a thing is in; a world's hidden size is its knob count.
(Ch 3)

## Part 2

**triplet** — one recorded moment of experience: what I sensed, what I
did, and what I sensed next. The only input PRA ever learns from. (Ch 4)

**observation** — one simultaneous reading of every sensor, packed into
a fixed-order list of numbers. The "before" and "after" of a triplet
are both observations. (Ch 4)

## Part 3

**frame** — one member of the crowd: a bet that the world can be
described with a particular number of knobs, backed by placing every
sight on those knobs and predicting where they'll land next. (Ch 6)

**pose** — where a frame's knobs point for the current observation: the
frame's reading of one moment, expressed in its own coordinates. Not the
frame itself, and not the world. (Ch 6)

**drive** — the fixed, unlearnable rule that scores which action looks
worth taking; the system's wanting, kept outside the market. (Ch 9)

**competence drive** — the shipped default want: prefer the familiar and
the mastered, weighted by how well prediction is going there. (Ch 9)

**frontier drive** — the current edge: prefer places where prediction
error has been falling, so noise and mastered ground both score zero.
(Ch 9)

## Part 5

**pre-registration** — deciding what will count as success, and what will
count as failure, before an experiment runs, so the goalposts cannot move
once the data is in. (Ch 13)
