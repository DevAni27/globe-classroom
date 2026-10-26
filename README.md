# The Globe Is Your Classroom — version 0.4.0

A reusable, research-driven teaching skill for Nara + Liquid Galaxy. Choose a topic that real geography can meaningfully explain: earthquakes, civilizations, trade, climate, ecosystems, migration or city development. Nara researches and authors a structured lesson; the Python engine renders it, tracks progress and enforces an interactive teaching sequence.

## Demonstrated and ready to package

The contributor completed live river and earthquake lessons on a three-VM LG rig, including targeted help, strong-answer progression, transfer, local narration, orbit and packaged end cleanup. The shared visual design was also accepted. See VALIDATION.md for the distinction between local tests and contributor-reported live evidence.

Publish only this skill package, following PUBLISH.md. DEMO_SCRIPT.md provides the three-minute recording plan. The full Hermes profile is not part of the submission.

## What changed

v0.4.0 establishes a shared visual system across subjects: typographic hierarchy with regular/bold bundled fonts, restrained stage track, focused next-action card, a separate schematic-diagram column, consistent semantic colours, thin map highlights, bounded arrowheads, fewer map labels and north-up default views. Existing snapshots gain the styling on continue. docs/design-preview.png compares river, climate and generated earthquake panels. Local previews are not proof of live Earth rendering.

v0.3.2 adds end/clear cleanup that empties the active scene before detaching links and preserves other apps’ current content. The climate reference gains causal diagrams and correct central-Andes terminology. See CLIMATE_TEST.md for a short second-subject acceptance test.

v0.3.1 removes misleading guessed river traces from the prepared lesson, adds short map labels, aspect-preserving panels and centred branding, engine-owned next-step narration, compact assessment context and explicit bounded orbit/stop/return-view commands. Camera playback and final VM framing require a live check.

v0.3.0 adds a separate correct-feedback stage so next opens the first explanation, redesigned panels with stage progress and causal diagrams, labelled map highlights and dynamic branding. It includes a reviewed river lesson plus TEST_GUIDE.md, SUBMISSION.md and DEMO_SCRIPT.md. Run the live acceptance guide before claiming submission readiness.

v0.2.1 connects personalised answer feedback to the right panel and local narration using assess --feedback-json. Nara returns the same narration in chat, with the same next question. Saved scenes retain that feedback for continue/speak; advancing clears it. Updating preserves existing lesson state and saved rig connection.

The original version contained only a fixed rainfall lesson. The new engine accepts any valid researched lesson plan: new places, questions, hints, causal assessment rubric, points, lines, polygons and schematic arrows. Explanations reveal one beat at a time. Right-screen instructions explicitly tell learners to answer in Nara chat. Optional narration uses the computer's installed speech voice. The sourced rainfall reference remains available and runs through this same general engine.

Topic-independent infrastructure does not guarantee every generated lesson is accurate. Only sources actually read by Nara should be cited, and facts and geometry need review. This is an educational framework, not an unlimited curriculum or validated learning analytics system.

## Requirements

- Existing working Nara profile and verified state/lg-connection.json, OpenSSH and sshpass.
- Python 3.8+ and Pillow in the Python environment that runs the helper.
- Standard LG loading list at /var/www/html/kmls.txt; HTTP http://lg1:81; refreshing side NetworkLinks; writable LG content paths.
- Standard odd screen layout (3, 5, 7...). Confirm actual placement. Custom layouts need adaptation.
- A configured model and working research tools in Nara for NEW lesson generation. The helper itself makes no AI, TTS or weather API calls.

## Update/install on your Windows + Ubuntu WSL setup

Save globe-classroom.zip in Windows Downloads. In Ubuntu:

```bash
/usr/bin/python3 -m zipfile -e /mnt/c/Users/immor/Downloads/globe-classroom.zip "$HOME/lg-classroom-install"
/usr/bin/python3 "$HOME/lg-classroom-install/globe-classroom/install.py"
sudo apt install -y python3-pil
```

Installer backs up the previous skill directory under your profile's backups folder. It preserves state, credentials and remote content. The apt command installs the one dynamic image-rendering dependency in Ubuntu. It does not install a model or enable billing. Bundled DejaVu font has its own license in assets/FONT-LICENSE.txt.

Set shortcuts in this terminal:

```bash
export HERMES_HOME="$HOME/.hermes/profiles/liquid-galaxy-agent"
ENGINE="$HERMES_HOME/skills/liquid-galaxy/globe-classroom/scripts/lesson_engine.py"
/usr/bin/python3 "$ENGINE" check
```

## First verify the upgraded renderer

```bash
/usr/bin/python3 "$ENGINE" start --plan "$HERMES_HOME/skills/liquid-galaxy/globe-classroom/references/rain-shadow.json" --voice
```

This uses the real, sourced reference lesson, not fabricated observations. It tests upgraded panels, staged explanation and optional local voice without calling Gemini. If voice fails, read the warning; the visual lesson should remain usable. On WSL, speech uses Windows System.Speech via powershell.exe. Linux can use espeak-ng; macOS can use say. These are system voices with variable quality. No microphone capture is supplied. Answers are typed in Nara (existing system dictation can also type them).

## Start a new topic through Nara

Start a fresh chat after updating:

```bash
hermes -p liquid-galaxy-agent
```

Ask, for example: "Use globe-classroom to teach me why civilizations developed near rivers. Research authoritative sources, build a beginner lesson with a prediction and a different-location transfer question, enable local narration, show the first scene and wait for my answer."

The agent should read SKILL.md and PLAN_FORMAT.md, search and open sources, write a lesson JSON, validate it and start it. It must not run the old fixed rainfall helper for an unrelated topic. Check that its actual tool calls use lesson_engine.py and a NEW topic-specific JSON file. If research or the model API fails, report that limitation rather than silently substituting rainfall.

The skill's research, authoring and conversational assessment use your configured model and may hit its quota. This update does not bypass provider limits or guarantee arbitrary-topic quality. First topic generation may take multiple calls; the resulting lesson and progress are stored locally.

## Learner flow

1. Look at actual geography and listen/read the prediction.
2. Type your answer with reasoning in the Nara chat. Rig options are not clickable.
3. Nara evaluates against the researched rubric. Bare choices get a follow-up; uncertainty gets clarification; incorrect reasoning gets a hint.
4. A correct explanation or explicit reveal opens explanation beat one. Say next to reveal subsequent beats and geometry.
5. Next then travels to another location and asks a transfer question. You must answer before it advances.
6. Recap distinguishes independent reasoning, assisted answers and revealed explanations. No fabricated scores.

## Helper commands

- validate --plan PATH: validate JSON shape, ranges and references; no proof of factual accuracy and no network operation.
- render --plan PATH --output DIR: generate opening KML/panel/narration locally; no rig change.
- start --plan PATH [--voice]: snapshot a lesson and deploy the opening question.
- status: inspect stage, saved plan path and actual assessment records.
- assess --verdict correct|partial|incorrect|unclear --evidence TEXT: record Nara's explanation-grounded assessment; not an automatic AI classifier.
- hint: show next hint; no automatic answer reveal.
- reveal: explicitly show the answer, recorded separately from independent correctness.
- next: advance one explanation beat, then to the next inquiry stop. Refuses to skip open questions.
- continue: re-display current scene without advancing.
- speak: repeat current local narration; no camera movement.
- restore: restore pre-lesson loading list and side overlays, preserving lesson files/backups. Does not restore camera position.

## Safety and display ownership

The generic engine reuses the camera/transport tested in the first version. It validates the verified connection fingerprint, uses SSH host-key verification, and passes the password through SSHPASS without printing it. It appends one lesson NetworkLink and backs up the shared loading list and side overlays. It does not alter master.kml, myplaces.kml, network or startup settings, and does not require sudo on the rig.

Do not use another LG controller simultaneously: restoring an old shared-file snapshot would discard concurrent changes. The new engine adopts an active backup from version 0.1 when available so the original baseline can be recovered. Lesson state is now state/globe-classroom-live.json; plan snapshots live under HERMES_HOME/lessons/. Do not submit your profile's connection file, lesson-state evidence or credentials.

## Validation and demo

See VALIDATION.md for the exact checks and remaining real-rig checks. Run `/usr/bin/python3 -m unittest discover -s tests -v` from the skill directory for offline verification. Existing rainfall-only functions remain in scripts/classroom.py as transport/backward compatibility, with old operator details in LEGACY_README.md. They are not the recommended learner entry point.

Demonstrate an unseen requested topic only after verifying its source support, renderer and actual conversational flow. Record what worked and any model/voice limitations. The generic engine is locally tested; broad-topic end-to-end teaching and voice still need confirmation on your actual setup.
