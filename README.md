# The Globe Is Your Classroom

An adaptive teaching skill for **Nara and Liquid Galaxy**.

Explore a real place, make a prediction, receive feedback on your reasoning, and apply what you learned at another location.

## How it works

1. **Predict:** Nara displays a geographical scene and asks a question.
2. **Reason:** The learner answers in the Nara chat.
3. **Adapt:** An incomplete answer receives targeted help; a strong explanation unlocks the next stage.
4. **Explore:** Staged explanations connect the geography to the underlying mechanism.
5. **Transfer:** A different location tests whether the learner can apply the idea.
6. **Reflect:** A recap describes the learner's actual reasoning and where support was needed.

Optional local narration accompanies the teaching stages. Lessons support bounded camera orbits, saved progress and cleanup through “End the lesson”.

## Subjects

The framework supports subjects where geography meaningfully helps explain an idea, including climate, earthquakes, ecosystems, civilizations, trade and city development.

River civilizations and earthquake lessons were tested on a three-VM Liquid Galaxy rig. Bundled reference plans cover river civilizations and rain shadows.

New lessons require authoritative research and factual review. Structural validation alone does not establish factual accuracy.

## Rig layout

On the tested three-screen rig:

- Left: classroom branding.
- Centre: Google Earth, location markers and teaching illustrations.
- Right: question, explanation, feedback and next action.

Learners answer in Nara chat. The rig panels are not clickable answer buttons.

## Requirements

- A working Nara/Hermes installation.
- An existing Liquid Galaxy connection configured through lg-ssh-control.
- Ubuntu or WSL with OpenSSH, sshpass, Python 3.8+ and Pillow.
- A configured AI provider and working research tools for generating new lessons.

The lesson engine makes no AI API calls itself. Research and conversational assessment use Nara's configured provider. Optional narration uses local system speech.

## Installation

Run in Ubuntu or WSL:

```bash
git clone https://github.com/DevAni27/globe-classroom.git "$HOME/globe-classroom-source"
sudo apt install -y python3-pil
/usr/bin/python3 "$HOME/globe-classroom-source/install.py"
```

The installer uses the existing `liquid-galaxy-agent` profile. For another existing profile:

```bash
/usr/bin/python3 "$HOME/globe-classroom-source/install.py" --profile YOUR_PROFILE_NAME
```

Updating an installed skill backs up the previous skill directory while preserving saved connection details and lesson state.

## Try it in Nara

Ask:

> Use globe-classroom to teach me why civilizations developed near rivers. Research authoritative sources, create a beginner lesson with a prediction and a transfer question at another location, enable local narration, display the opening scene and wait for my answer.

For the bundled reviewed lesson:

> Use globe-classroom. Start the bundled references/river-civilizations-reviewed.json with local narration. Reuse the saved connection and completed setup. Display the opening scene and wait for my answer.

## Source and documentation

- [Skill instructions](SKILL.md)
- [Lesson engine](scripts/lesson_engine.py)
- [Shared visual system](scripts/visuals.py)
- [Lesson plan format](PLAN_FORMAT.md)
- [Live test guide](TEST_GUIDE.md)
- [Validation record](VALIDATION.md)
- [Sources](SOURCES.md)
- [Design preview](docs/design-preview.png)

## Tests

From the repository directory:

```bash
/usr/bin/python3 -m unittest discover -s tests -v
```

The development validation includes 41 passing automated tests. Live acceptance was completed by the contributor on a three-VM rig.

## License and credits

Code is licensed under [Apache-2.0](LICENSE). Bundled DejaVu fonts retain their own license.

Built for the Liquid Galaxy community and Harsh Mehta's Nara integration. Google Earth imagery and attribution remain the property of their respective providers.
