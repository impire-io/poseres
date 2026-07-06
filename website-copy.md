# PRA
## An intelligence with no task.

How do you learn about a new room? You don't read a manual. You move, you look, you reach for something and watch what happens, and you adjust. Nobody labels the room for you — you build your own picture, and you keep the parts that hold up.

Now swap the room for anything you can explore the same way: a language, a market, a game, a space of ideas. The trick doesn't change — act, see what shifts, keep what predicts.

That's PRA.

**PRA — Pose Resolution Architecture** — is an AI that learns a world by *doing*, not by being told. No labels. No dataset. No task you hand it. You give it a way to sense, a way to act, and one built-in urge to make sense of what it meets — and it builds its own model of that world from scratch, keeping only the structure that earns its place.

The world can be physical or utterly abstract. PRA doesn't know the difference — to it, everything is just signals coming in and actions going out. Meaning is learned, never wired in.

---

### No labels. No task. No dataset.

Most AI is trained. You show it millions of examples with the answers attached, and it learns to copy the pattern. PRA isn't trained like that. It has no answer key and no goal you assign. It starts empty and figures out the shape of its world by living in it — the way an animal does, or a child.

Which means it's never "finished." It keeps learning for as long as it's running.

---

### How it works, without the math

Three moves, over and over:

**Act and predict.** PRA does something, then guesses what it will sense next. When the guess is wrong, that error is the lesson.

**Grow small maps.** Instead of one giant brain, PRA grows many small models, each trying to explain a slice of what it sees — competing maps of the same territory.

**Keep what pays for itself.** A map that predicts well survives. A map that's lazy, redundant, or needlessly complicated gets pruned. The population polices its own size, so it never bloats.

One quiet finding fell out of this: we built a version that learns *without* trying to predict the future. It learned nothing useful. Prediction isn't a feature of PRA — it's the engine.

---

### What counts as a world?

Almost anything PRA can poke and watch. The rules are simple:

- it can **sense** a state as it changes,
- it can **act**, and those actions change what it senses next,
- and the results come back **soon enough to learn from**.

A hand learning the shape of an object fits. So does attention moving through a space of ideas, a system feeling out what a user likes, or something finding its way around a body of knowledge. Fast, responsive worlds are its home turf.

Slow, shifting worlds are the wrong *shape* for it. Anywhere a move only pays off months later, or the ground keeps moving under you, this kind of learning has nothing steady to grip. And PRA is a model-builder, not a manager: it learns how a world *works* — it doesn't run one for you.

---

### The part most AI projects hide

What makes PRA unusual isn't a capability. It's the honesty.

Most impressive AI demos are curated — you see the wins, not the misses. PRA ships with the opposite: a test rig built to catch it cheating. It runs PRA against worlds where the true answer is already known, and it's designed to fail loudly whenever PRA only *looks* smart.

The rules are strict on purpose. Show every result, never just the flattering average. Run it twice and demand identical output, down to the byte. A failing test isn't an error to bury — it's the data.

That's rare, and it's the whole point: you can trust what PRA claims, because the same project built the thing that tries to disprove it.

---

### What's true today

**On simple worlds, it works.** PRA starts from nothing and reliably works out roughly how complex its world is, sharpens its predictions as it goes, and keeps its own size in check. Provably, repeatably.

**On complex worlds, not yet.** Give it a world with many moving parts and PRA currently grabs the *simplest* explanation instead of the real one. The machinery runs at full scale — millions of steps on one machine, no supercomputer — but the discovery breaks down. We know exactly where, because the harness measures it.

That gap isn't swept under the rug. It's the headline question the whole project exists to answer.

---

### Yours to experiment with

PRA isn't a paper you read. It's a working core you download, install, and point at a world of your own.

Every piece is built to be swapped. Wire in your own world through one clean connection and PRA starts learning it. Change what "better" means to it, change how it grows, change how ruthlessly it prunes — each is a single part you replace without touching the rest. Configure it, run it, watch what it does.

Putting it in people's hands is the whole bet. The discoveries that matter won't come from us guarding PRA as research — they'll come from people plugging it into worlds we'd never think of. And the open question, *does it hold up as worlds get bigger?*, isn't a disclaimer. It's the invitation.

**[ Get the code ]**  ·  **[ Read the spec ]**  ·  **[ See what it can do ]**
