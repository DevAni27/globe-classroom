# The Globe Is Your Classroom

Version 0.1.0: adaptive rain-shadow lesson for Nara/Hermes and Liquid Galaxy.

Predict on real terrain, explain your reasoning, receive a hint if needed, then apply the concept in the northern Andes where the expected side reverses. The model assesses conversational understanding; a deterministic standard-library Python helper controls scenes and persistent state. No model API is called by the helper.

## Requirements

- Existing Nara profile named liquid-galaxy-agent, with terminal/file/skills enabled.
- Python 3.8+, OpenSSH client and sshpass in the Nara host (Ubuntu WSL supported).
- Verified machine-scoped state/lg-connection.json created by Nara's onboarding helper.
- SSH host key already trusted, correct password, a running standard LG rig, writable /var/www/html/kmls.txt and /var/www/html/kml/ on master.
- Standard LG HTTP endpoint http://lg1:81, loading list via sync_nlc.php, refreshing per-screen slave_N.kml links. These match the supplied rig configuration. Nonstandard ports/paths require adjustment and validation.
- Standard odd screen arrangement, 3/5/7 etc. Confirm physical placement. This is not a single-screen desktop Earth plugin.

No pip packages are needed at runtime. Prepared panels are bundled PNGs. Gemini's own free-tier availability and quotas remain separate. No paid services are required by this package.

## Install on Windows + Ubuntu WSL

Extract globe-classroom.zip into Windows Downloads so Downloads/globe-classroom/install.py exists. In Ubuntu:

```bash
python3 /mnt/c/Users/immor/Downloads/globe-classroom/install.py
```

This copies the skill into ~/.hermes/profiles/liquid-galaxy-agent/skills/liquid-galaxy/globe-classroom. If already installed it moves the old skill to that profile's backups folder first. It does not contact LG or change the display.

Set a convenient command for this Ubuntu terminal session:

```bash
export HERMES_HOME="$HOME/.hermes/profiles/liquid-galaxy-agent"
CLASSROOM="$HERMES_HOME/skills/liquid-galaxy/globe-classroom/scripts/classroom.py"
```

CLASSROOM is just a shell variable pointing to the helper; set it again in a new terminal. HERMES_HOME ensures lesson state and credentials come from Nara's profile.

## Direct real-rig test

```bash
python3 "$CLASSROOM" start
```

Expect real western Maharashtra terrain, cyan ring A on coastal side and amber B inland, question panel at right, branding at left. First scene may take several seconds for NetworkLinks to load. Google Earth imagery can need longer. Success from the helper means deployed, not visually verified.

```bash
python3 "$CLASSROOM" hint
python3 "$CLASSROOM" assess --verdict partial --evidence 'Correct side; mechanism not explained'
python3 "$CLASSROOM" assess --verdict correct --evidence 'Learner described moist air rising, cooling and raining on the incoming side'
python3 "$CLASSROOM" next
```

These are operator commands for testing actual scenes. In a real learner session, do not pre-label an answer; let Nara assess what the learner actually said. Do not run all commands before checking the opening scene.

`next` now shows northern Andes question. `assess --verdict correct ...` reveals its explanation. Another `next` shows recap. `reveal` is an explicit skip-to-explanation, recorded separately from a correct answer. `continue` re-renders the saved stage, and `status` reads it. `start` resets lesson progress but retains the original display backup while the same session is active.

## Run through Nara

Start a fresh Hermes chat after installation:

```bash
hermes -p liquid-galaxy-agent
```

Say: “Use globe-classroom to teach me why mountains affect rainfall. Start the lesson on my verified rig and wait for my prediction.”

Answer normally. First try “A, but I don't know why” to test the reasoning follow-up, then explain the uplift mechanism. Ask for next, answer the reversed-side Andes question and request recap. Nara must use the helper rather than generating shell/XML strings itself.

## Restore previous display

```bash
python3 "$CLASSROOM" restore
```

Restores the original loading list and left/right overlay files from the saved backup. Does not delete lesson assets or backups, restart Earth, restore camera position or undo unrelated concurrent writes. Do not run another LG controller during the lesson: restoring a loading-list snapshot would discard its later edits. If restoration occurs after other app changes, compare the backup manually first.

The helper writes only its own /var/www/html/kml/globe-classroom assets, appends its live.kml URL to kmls.txt, and replaces two side-overlay files after backing them up. It leaves master.kml and myplaces.kml untouched. live.kml requests scene.kml every two seconds. Each panel gets a unique image filename to avoid stale texture caching.

## Files and state

- SKILL.md: discovery, teaching flow and assessment rubric.
- scripts/classroom.py: XML, SSH transport, lesson state machine, backup and restore.
- assets/*.png: prepared high-contrast stages and branding.
- state/globe-classroom.json inside HERMES_HOME: stage, attempts, short assessment evidence and backup path; no password.
- SOURCES.md: geographic evidence and limitations.
- tests/test_classroom.py: offline XML and flow checks.

The connection helper stores a plaintext password in its existing mode-0600 profile file. This package reads that local file, validates its machine fingerprint, never prints it, and passes it through SSHPASS. Do not include either state file or connection credentials in your submission. The lesson package itself contains no credentials.

## Validation and practical limits

Offline tests verify XML parsing, closed camera LookAt, stage progression, reveal distinction, and backup/restore transport against a local fake filesystem. They do not replace real rig tests. This version has not yet been visually verified on your rig; record that result before claiming completion.

The model's free-text assessments are not a validated learning measurement. The state machine prevents accidental advancement, but it cannot prove an assessment is educationally correct. Prepared sources and real places are used from the start; arrows remain schematic. This release contains one polished subject lesson and one transfer case, not an unlimited curriculum generator.

If the helper reports an SSH/SCP error, check its message, IP, password, known host key and directory permissions. Do not disable host-key validation as a blanket fix. If camera moves but content does not render, inspect requests for /kml/globe-classroom/live.kml, scene.kml and slave_N.kml in Apache access logs. Do not reboot or patch LG startup automatically.

## Suggested 3-minute demo

1. Start lesson: real terrain and an unanswered prediction.
2. Give A without a reason: Nara asks for a mechanism.
3. Ask for a hint: airflow appears without a rainfall forecast claim.
4. Explain rising/cooling air: explanation scene appears.
5. Move to northern Andes: B is now the incoming-moisture side.
6. Answer, show evidence-aware recap, and demonstrate restore.

## Submission checklist

Include this skill directory, README, source list and demo video. Add your own author identity and repository link; no contributor identity is invented here. Report exactly what was observed on the rig, model/provider used and limitations. Follow contest submission instructions independently. Run the offline tests using `python3 -m unittest discover -s tests -v` from this directory.
