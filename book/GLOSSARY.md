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

**encoder** — the small network that reads one observation onto a
frame's knobs: observation in, pose out. (Ch 6)

**decoder** — the encoder's mirror: pose in, reconstructed observation
out, proving the frame's knobs can still express what it is looking at.
(Ch 6)

**drive** — the fixed, unlearnable rule that scores which action looks
worth taking; the system's motivation, kept outside the market. (Ch 9)

**competence drive** — the shipped default motivation: prefer the
familiar and the mastered, weighted by how well prediction is going
there. (Ch 9)

**frontier drive** — the current edge: prefer places where prediction
error has been falling, so noise and mastered ground both score zero.
(Ch 9)

## Part 4

**snapshot** — the brain paused into a file: the complete learned state
written out, so the same mind can be stopped, copied, moved, and resumed
exactly. (Ch 11)

## Part 5

**pre-registration** — deciding what will count as success, and what will
count as failure, before an experiment runs, so the goalposts cannot move
once the data is in. (Ch 13)

## Part 6

**oracle** — a measurement taken by peeking at the world's ground truth,
which the brain itself could never make, used to mark the ceiling of what
any learnable version could reach. (Ch 14)

**election** — choosing, on purpose, to begin a sequence you know: its
first step and all the steps after it. (Ch 14)

**completion itch** — a small standing pull that makes begun things want
finishing: starting is worth a little, continuing is worth more, and
abandoning charges everything sunk. (Ch 14)

**event head** — a small second predictor beside the frames, one model
per action, predicting how every sensed number will change next; learned
online from lived steps and built to be sharp about the moments when a
number jumps. (Ch 14)

**post-approval hangover** — the measured backfire of making expected
praise valuable: right after praise lands, the praised loop's own next
steps all predict praise going away, so the learner avoids the loop that
earned it. (Ch 15)

**recipe memory** — the remembered sequence of observations from a
demonstrated success, kept whole and in order, so the steps that led to
a result can be walked again. (Ch 16)

**the obsessive** — the failure twin of a borrowed goal: a learner that
pursues what its teacher applauds until its own goals lose time to it.
(Ch 16)

**the parrot** — the failure twin of taught order: a learner performing
remembered recipe steps somewhere they do not apply. (Ch 16)

**provisioning** — a parent covering a child's costs until the child's
own competence can pay them. (Ch 16)

**the stipend** — this project's measured dose of provisioning: the
parent pays the whole metabolic bill through tick 1,500, then coverage
fades in a straight line to nothing at tick 3,000, and the learner
lives at full stakes after that. (Ch 16)
