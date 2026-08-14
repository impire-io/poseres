<!-- Draws on: journey 0010 (positioning vs frozen intelligence).
     No empirical numbers in this chapter. -->

# The brain in the freezer

I own a robot lawnmower. Every time it sets out across the lawn it finds
the same tree trunk, wedges itself against it, spins its wheels, and waits
for me to come rescue it. It has been stuck on that trunk more times than
I can count. It will get stuck on it again tomorrow.

This bothers me more than it should. The tree is fine. What bothers me is
what the getting stuck proves: somewhere in that mower is a brain, and
that brain is not learning. It can't. It was finished before the mower
ever saw my garden.

But honestly, what did I expect. Machine brains these days are studying in a lab,
on enormous piles of examples. The brain gets better and
better at its task. Then, one day, the studying stops and whatever the brain
knows at that moment gets copied into the product. From that point on,
nothing it experiences changes it. Engineers call this study phase *training*.
I call the copy that ships a "*frozen* brain": a snapshot of what was learned,
with the learning switched off.

And that's what's bothering me; nobody would accept this for a person. It would
mean hiring someone whose last day of learning was their final exam. Yet, we accept
it for almost every machine.

> **Under the hood: what "frozen" means precisely.** Modern learned systems
> separate training (weights are updated by gradient descent against a loss)
> from inference (weights are fixed; the model only computes outputs).
> Deployment freezes the weights. The failure mode this invites is
> distribution shift: the deployed input distribution drifts away from the
> training distribution, and the model's error grows with no mechanism to
> respond. Periodic fine-tuning doesn't change the category. It's another
> train-then-freeze cycle, with its own well-known cost: updates on new data
> overwrite what earlier data taught, unless you keep and replay the old
> data. That failure has a name, catastrophic forgetting, and it gets a
> chapter of its own.

To be fair, freezing mostly works. That's exactly why it's everywhere. A
frozen brain is predictable: you can test it for a thousand hours, and the
copy you ship behaves exactly like the copy you tested. It's also relatively
cheap: train once, stamp out a million identical copies. And when it makes a
mistake, it makes the same mistake every time, so an engineer can hunt the
mistake down and fix it in the next version. A brain that keeps changing has
none of these comforts. There's a reason nobody wants their bank's software to
improvise.

So if the world the machine lives in matches the world it studied, frozen is
fine. But the trouble starts when anything moves. And three things move all the time.

- The world changes. Furniture gets rearranged. Seasons change the light in a
  room. A warehouse gets a new kind of box.

- The task changes. The job you bought the robot for is rarely the job you
  need next month. A person who can sort packages can learn to stack shelves;
  a frozen brain cannot learn anything.

- The body changes. This is the sneaky one. Motors wear down. A gripper loses
  its rubber. Sensors drift out of calibration. My mower's blades are a
  little duller every month, so the same motor command cuts a little less
  than it used to. But the brain steering it is exactly as worn as the day it
  left the factory, which is to say not at all. The brain's own body slowly
  stops matching the body it studied with, and a frozen brain can't even
  notice.

The standard answer is: retrain it. Collect new examples, go back to the
lab, study again, ship a new snapshot. But look at what that actually is.
It isn't the machine learning: it's people, redoing the machine's entire
education because the machine can't take a single lesson on its own. It's
slow, it's expensive, and in the gap between snapshots the machine keeps
confidently (and annoyingly) doing the wrong thing. My mower will park itself
against that tree trunk until its maker ships a smarter model, which is to say: forever.

What I want is different, and it's the reason this whole project exists. I want a
brain where every single moment is a lesson. It acts, something happens, and
it is permanently, slightly changed by having found out. No study phase, no
snapshot, no lab. Learning isn't a stage of its life; learning is its life,
the way it is for anything alive. A puppy isn't trained and then deployed, although
I am pretty sure there is a big market for that.

Just imagine what these continuously learning brains could bring to my little mower.
Monday, it wedges itself against the trunk. Tuesday, it gets stuck and something in it registers:
"that spot, that approach, stuck again". Wednesday it swings a touch wider.
By Friday it slides past without touching, and nobody told it anything: no
update was downloaded, no engineer was involved. If I plant a tree next
spring, it gets stuck a few times and adjusts again. None of this is
science fiction; a mouse does it effortlessly. The reason your mower
doesn't is a design choice, not a law of nature.

I've been building a brain like that. It's called the Pose Resolution
Architecture (PRA), and it runs, today, on worlds ranging from simulated
rovers to Minecraft to anything that speaks a robot's message protocol. This book is the
story of building it: what the design is, why it is that way, and which
parts of it I got wrong before measurements straightened me out. That last
part is not modesty. You'll see refuted ideas in nearly every chapter,
because a claim that has survived a real attempt to kill it is the only kind
worth reading about. And I'll say plainly, when we get to the frontier in
the book's final parts, which claims haven't faced their attempt yet.

You won't have to take my word for any of it, either. The system is open
source, and in a future chapter, you'll install it yourself and watch a small rover's
brain learn, live, on your own screen — from first command to watching in
about five minutes. A book about a machine that learns in front of you
should let it learn in front of you.

I should also say what this book is not about. It is not about chatbots. A
system that has read every book about swimming still can't swim; what's
missing isn't more books. PRA doesn't compete with language models at
language. Nothing forbids it from learning English, mind you: words you
hear and words you say are consequences and actions like everything else,
and Part 6 takes that idea seriously. But language would be one more thing
it learns, never the thing it is. It competes with frozen brains at the one
thing they can't do by definition: keep learning.

There's a catch, of course. The moment you ask for a brain that never stops
learning, two ugly failures walk in the door. A brain that keeps changing
risks erasing the very things it knew. A brain that keeps adding risks
growing without limit, hoarding machinery forever. The next chapter is about
those two failures. One of them I got to watch happen, in my own system,
from the front row.
