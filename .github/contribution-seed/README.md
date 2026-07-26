# Contribution seed material

Files the maintainer applies to GitHub by hand — labels and the
initial good-first-issue shelf. They live in the repository (instead
of having been applied by the feature that created them) because
label and issue creation are repository-authority acts with a timing
judgment attached: apply them when you actually want contributors to
find them.

Every draft here was verified against the real APIs at the time of
writing (feature 038); re-skim a draft against the tree before
opening it if significant time has passed.

## Apply the labels

`--force` makes each command idempotent (it updates an existing
label, including GitHub's default `good first issue`, instead of
failing):

```bash
gh label create "good first issue" --color 7057ff --force \
  --description "Scoped first contribution — seams, acceptance bar, and honest size are named in the issue"
gh label create "new-world" --color 0e8a16 --force \
  --description "A new world or body for the brain to learn — the natural contributor on-ramp"
gh label create "new-sensor-actuator" --color 1d76db --force \
  --description "A sensor or actuator behind the Doc 02 anatomy seam (src/pra/anatomy/body.py)"
gh label create "new-drive" --color 5319e7 --force \
  --description "An innate drive behind the Drive protocol; research-adjacent — value claims get measured"
gh label create "proposal" --color d4c5f9 --force \
  --description "Design conversation before code — required for anything touching core behavior (constitution I)"
```

(The same data is in [`labels.json`](labels.json) if you prefer to
script it.)

## Open the seed issues

Each draft file is a ready issue body; its title and labels are in
the HTML comment at the top of the file (the comment does not render
on GitHub, so leaving it in the body is harmless):

```bash
gh issue create \
  --title "A second Gymnasium worked example: Acrobot-v1" \
  --label "good first issue" --label "new-world" \
  --body-file .github/contribution-seed/gfi-01-acrobot-example.md

gh issue create \
  --title "A delayed-echo world — observations that lag actions by k steps" \
  --label "good first issue" --label "new-world" \
  --body-file .github/contribution-seed/gfi-02-delayed-echo-world.md

gh issue create \
  --title "An opt-in odometry sensor for the rover" \
  --label "good first issue" --label "new-sensor-actuator" \
  --body-file .github/contribution-seed/gfi-03-rover-odometry-sensor.md

gh issue create \
  --title "Gymnasium adapter: opt-in reward-as-sensor (a documented v1 deferral)" \
  --label "good first issue" --label "new-sensor-actuator" --label "proposal" \
  --body-file .github/contribution-seed/gfi-04-gym-reward-sensor.md
```

## The roadmap exit stays honest

Phase D's exit for the contribution surface is *first external world
contribution merged*. Shipping this folder does not meet it — an
external human does. The roadmap entry stays pending until that
merge.
