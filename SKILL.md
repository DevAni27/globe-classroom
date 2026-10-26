---
name: globe-classroom
description: Teach any topic that real geography can meaningfully explain using an adaptive Liquid Galaxy lesson. Research sources, build a lesson plan, ask predictions, assess reasoning, reveal scenes step by step and test transfer at another location. Use for globe classroom, teach me, interactive lesson, geography, earthquakes, civilizations, trade, climate, ecosystems, migration and urban development.
version: 0.4.0
license: Apache-2.0
---

# The Globe Is Your Classroom

Routine teaching uses the documented CLI below. Do not inspect Python source or re-read full plans on every answer. Use ENGINE context to retrieve the current question, rubric and content in one compact call, then write personalised feedback and run assess. Read implementation code only to diagnose an actual unsupported command or error.

A reusable teaching workflow, not a fixed rainfall tour. Nara researches and authors the lesson, interprets the learner's responses and selects the pedagogical action. Python validates the plan structure, generates XML/panels, deploys scenes and enforces progression. It does NOT verify sources or assess an answer independently.

## Entry and suitability

Use for topics where places, terrain, routes, spatial relationships or changes over time support an explanation. Welcome earthquakes, ecosystems, climate, migration, civilizations, trade and urban development. Do not force a geographic visualization onto an unsuitable topic. Explain the limitation and offer a relevant angle. Never claim unlimited subject mastery.

Load lg-ssh-control first. Use the saved machine-scoped connection verified on this installation. Do not use copied credentials or rig memories. Existing display files are backed up, and the package writes only its lesson files/loading-list entry and side overlays. No reboot, networking change, guard bypass or startup-script edit is authorized by this skill.

Locate this installed skill's directory using the skill loader. The engine is scripts/lesson_engine.py; substitute its absolute path for ENGINE in commands below. Run it yourself through the terminal tool with /usr/bin/python3 and the active Nara HERMES_HOME explicitly set. Do not ask the learner to close Nara or run deployment commands. A teach request authorizes opening-scene deployment unless the learner explicitly asks for validation only. Read PLAN_FORMAT.md before authoring a new lesson.

## Research and author a requested topic

1. Establish topic, learning goal and learner level. If level is absent default to a curious beginner and state that briefly. Ask at most one clarifying question if ambiguity changes the subject; do not turn onboarding into an interview.
2. Search and open at least two relevant authoritative sources, such as scientific institutions, official datasets, museums, heritage bodies or primary publications. Read the actual supporting content. Do not invent links, quotations, figures or source verification. Tools must be available; if research fails, explain that you cannot yet produce a verified new lesson. You may offer the sourced rainfall reference, explicitly as a different topic.
3. Choose two to four inquiry stops on actual geography: an initial prediction and at least one different-location transfer question. Make the learning objective explicit. Each stop needs a question, a causal reasoning rubric, hints, follow-up and two to four explanation beats. Correctness must not depend on guessing an arbitrary letter.
4. Represent locations/geometry honestly. Distinguish schematic arrows or approximate teaching regions from sourced boundaries and measured tracks. Specify time context. Historical maps require a date and must not be presented as today's borders or a reconstructed historical Google Earth view. Migration routes are generalized unless a source supplies actual paths. Earthquake magnitude, casualties and live event claims need dated sources. Do not invent a fault trace or claim an extruded shape is scientific 3D evidence.
5. Write the JSON plan under HERMES_HOME/lessons/. The JSON contains no code, remote commands or credentials. Include sources with a short supports field and source IDs for every stop. Put key source attributions in concise titles so the right panel stays readable. See references/DOMAIN_GUIDE.md for checks by subject.
6. Run `/usr/bin/python3 ENGINE validate --plan ABSOLUTE_JSON_PATH`. This checks structure and geometry ranges only. Separately inspect the scientific/historical claims and their sources. If validation fails, fix the plan; never edit the renderer to accept malformed XML or unbounded text.
7. Run `/usr/bin/python3 ENGINE start --plan ABSOLUTE_JSON_PATH`. Add --voice only when the learner requests spoken guidance. This displays the opening prediction and persists a snapshot of the plan. Then STOP and wait for the learner's answer.

For "teach me mountains and rain" the provided references/rain-shadow.json is a sourced reference lesson using the same general engine. It is a convenience, not the only supported subject.

## How learners interact

Clearly say: "Look at the globe, then type your answer here in Nara. Explain your reasoning. You can ask for a hint, say next during an explanation, or ask me to reveal the answer." On-screen A/B regions, if used, are not clickable. Say “end the lesson” to stop and remove this classroom display. Voice output is optional; microphone input is NOT provided by this package. The learner may use their system's dictation to enter chat text if already configured.

Commands:
- `/usr/bin/python3 ENGINE check`: report runtime dependencies without contacting LG.
- `/usr/bin/python3 ENGINE status`: read persisted stage, plan path and assessment records. Use this on resume and before assessing an answer in a new chat.
- `/usr/bin/python3 ENGINE hint`: reveal the next available hint and selected hint geometry. Wait again.
- `/usr/bin/python3 ENGINE assess --verdict correct|partial|incorrect|unclear --evidence 'brief reason grounded in the actual answer'`: record your assessment and select its scene. Correct with personalised feedback shows an acknowledgement stage; next opens explanation beat one; partial or unclear asks a follow-up; incorrect gives a hint. Ambiguity is not proof of ignorance.
- `/usr/bin/python3 ENGINE reveal`: only when the learner explicitly requests the explanation. Records revealed separately from a correct answer.
- `/usr/bin/python3 ENGINE next`: from correct feedback opens the FIRST explanation beat; during explanation advances one beat and reveals its added geometry; after the last beat, moves to the next inquiry stop. It cannot skip an open question. At the end it shows recap.
- `/usr/bin/python3 ENGINE continue`: re-display the saved stage without advancing it.
- `/usr/bin/python3 ENGINE speak`: repeat the current optional local narration without changing scenes.
- `/usr/bin/python3 ENGINE restore`: stop the classroom tour, serve an empty scene before removing classroom links, and restore its side overlays while preserving other applications’ current content. Retain assets/backups. Camera is not restored. Do not use this while another LG application is modifying the same display files.

For "restart", read status and re-run start with the saved plan path. A fresh session may choose a new topic instead. Keep all other state under the profile; never edit connection credentials during teaching.

## Assess understanding, not keywords

Read the active plan's rubric and the learner's actual answer. Accept equivalent causal reasoning, everyday vocabulary and different languages. A correct option with no explanation is partial. Explain what the answer gets right, then ask one focused follow-up. Wrong reasoning gets a relevant hint; unclear answers get clarification, not a false incorrect label. After repeated difficulty, simplify the question or offer an explicit reveal rather than an endless loop.

During explanations, give a concise narration about the currently revealed beat and invite next. Do not jump directly through all scenes or uncover the transfer answer before the learner tries. The next place should challenge a changed condition, such as moisture direction, tectonic setting, geography of a trade bottleneck, river setting or ecosystem context.

At recap, read status records. Distinguish reasoning demonstrated independently, reasoning supported by hints, partial/unclear answers, and explanations revealed. Do not claim measured learning improvement, assign a fabricated score or diagnose ability.

## Visual and voice rules

Center/middle screens: real Earth terrain and honest teaching geometry. Rightmost: question/follow-up/hint/explanation and explicit answer instructions. Leftmost: lesson branding. The helper supports the standard odd-screen LG layout and computes side indices from verified screen count; custom arrangements need manual verification.

Each feature declares whether it is a real location, schematic teaching geometry or sourced geometry, and when it appears: initial question, hint, explanation or a specific explanation beat. Do not put answer-leaking labels in initial geometry or narration. Sources and time context stay visible. Do not describe present-day imagery as a past reconstruction.

Local speech is optional and free: Windows System.Speech through WSL, espeak-ng on Linux or say on macOS. These are installed system voices; quality and availability vary. There is no external TTS subscription and no voice recognition. If audio fails the engine reports it and leaves the visual lesson usable. Do not claim voice worked until the user confirms hearing it.

Never hand-write SSH camera XML; use the helper. It produces complete closing </LookAt> elements. Successful file transfer is not visual confirmation. Ask the user to confirm first rendering. On failure report the actual error; do not reset Earth or alter the rig silently.

## Requirements and boundaries

Python standard library plus Pillow for dynamic panels; OpenSSH and sshpass; verified Nara connection; standard LG port 81 NetworkLinks and writable content paths. No AI provider calls inside the helper. Nara's research/generation and chat still use the configured provider and its quotas. See README.md for setup and limitations. The engine is topic-independent; the quality of new topics still depends on research, geography and assessment, and must be tested on the rig.

## Personalised feedback must reach the rig and voice

For EVERY answer assessment, write a small UTF-8 JSON file under HERMES_HOME/lessons/ containing:
- learner_summary: an accurate paraphrase of the learner's actual idea (max 140 characters).
- feedback: what they understood and one useful connection or correction, grounded in the researched lesson (max 300 characters). The summary plus feedback must total at most 443 characters.
- next_question: exactly one focused next question or, for correct answers entering explanation, an invitation to say next (max 200 characters).
- narration: a natural spoken version of that same feedback, ending with the EXACT next_question (max 1600 characters). Do not introduce a different question, unsupported claims, or a later lesson's answer.

Run `/usr/bin/python3 ENGINE assess --verdict partial --evidence 'reason grounded in their answer' --feedback-json ABSOLUTE_FEEDBACK_JSON` with the explicit profile HERMES_HOME. Choose the actual appropriate verdict. The helper displays their idea and your feedback on the right panel, places the next question in the lower box and speaks narration when voice is enabled. The scene remains at the current stop. It persists this feedback so continue and speak reproduce it. next clears turn feedback and advances the normal explanation sequence; partial/incorrect/unclear still cannot skip an open question.

After successful deployment, use the engine-returned Teaching reply as your reply in Nara chat, with only a brief deployment note if necessary. Do not generate a second different teaching response. Wait for the learner. For correct answers, acknowledge the causal reasoning without consuming an explanation beat. Invite next to open the FIRST explanation beat. The engine now uses a separate feedback phase, so none of the authored beats are skipped. Do not give the entire explanation when a partial answer needs one targeted question. If --feedback-json fails validation, shorten or repair the feedback and retry; do not silently fall back to a generic follow-up.

On resuming a lesson started outside Nara, read status and continue the active lesson. Keep its saved voice setting and connection. Updating the skill files does not require restarting the lesson.


## Visual teaching quality

An explanation must change what the learner can observe. Prefer a few large, labelled features to many tiny markers. Point rings are zoom-scaled teaching highlights, not measured boundaries. Lines follow approximate present-day geography unless sourced. Never label a schematic canal as an excavated ancient canal. Add an optional diagram list of 2–4 short causal labels to each explanation beat; the right panel renders these as linked cards. Keep initial question geometry neutral and reserve causal diagrams for explanation. For each new location choose a camera framing that keeps relevant geography in the central view. Do not modify Google Earth navigation preferences or remove attribution automatically.

Use references/river-civilizations-reviewed.json for a prepared museum/university-sourced river lesson. It uses current imagery and explicitly schematic geometry, not reconstructed ancient river courses. Other topics still require research. On a strong answer, use feedback then next to reveal beat zero. On incomplete/unclear answers, wait for one focused follow-up response before explanation. At the second location, require the learner to APPLY the mechanism to a changed condition; do not merely ask them to repeat a phrase.


## Camera requests and efficient runtime

- `/usr/bin/python3 ENGINE context`: compact active question, rubric, stage, current content and actual next instruction. Prefer this over reading source or an entire plan for routine answer assessment. Use explicit active-profile HERMES_HOME for every command.
- `/usr/bin/python3 ENGINE orbit`: only on an explicit request such as “orbit here.” Loads a separate named native KML tour, requests one approximately 28-second orbit and returns to the saved lesson view. No background script, no infinite loop, no lesson advancement. Native playback must be confirmed on the actual rig; file transfer or a consumed command alone does not prove it played.
- `/usr/bin/python3 ENGINE stop`: maps to “stop moving”; exits the classroom-owned tour and removes its loading-list entry, preserving progress.
- `/usr/bin/python3 ENGINE return-view`: maps to “return to the lesson view”; stops the classroom tour and requests the saved stage camera without replaying narration.

Do not orbit automatically during questions, narration or answer evaluation. Deployment/advancement/restore stops any classroom orbit first. Use existing imagery for rivers unless trustworthy geometry is available; do not invent a zigzag and call it a river course. Optional feature map_label contains at most 24 characters. Longer default labels are abbreviated; full details stay in the panel legend. Aspect-preserving side overlays reduce VM stretching; actual window cropping and native navigation controls may still need a user display adjustment. Do not change rig startup files or Google Earth preferences without an explicit request.

The engine owns navigation wording on correct feedback and explanation stages. Repeat its Teaching reply, rather than promising recap or a new stop from memory. Feedback must contain no question mark; put the ONE follow-up in next_question and finish narration with that exact question. No other question appears in narration. Repair rejected feedback using the validation message; do not open source code to rediscover the schema.


## End and cleanup

Map “end the lesson”, “clear the classroom”, or “remove this lesson” to `/usr/bin/python3 ENGINE end` with explicit active-profile HERMES_HOME. end, clear and restore use the same cleanup procedure. It stops any classroom tour, replaces the active scene with valid empty KML and allows a refresh interval before detaching links. It removes only classroom loading entries and restores side files only while those files still contain classroom overlay links. Files belonging to another application are preserved. Records and backup assets remain available locally. A new start is required to resume teaching; continue cannot redeploy an ended session.

If the user asks to clear ALL KMLs while this lesson is active, run ENGINE end first, then use lg-ssh-control for any remaining non-classroom content within that request. Do not replace cleanup with deleting kmls.txt or scene.kml. Keep the valid empty scene available for clients holding cached links. Ask for visual confirmation; waiting one refresh cycle does not prove every client fetched it.

For the prepared climate acceptance test, start references/rain-shadow.json. The first stop is the Western Ghats; the second is around 22 S in the central Andes. In the second stop, the stated incoming moisture is from the east. Assess the uplift/cooling/condensation mechanism and do not reward a fixed west/east rule. These are schematic process illustrations, not live rainfall observations or a claim that mountain uplift explains the entire Atacama climate.


## Shared visual standard (all topics)

The renderer owns typography, spacing, colours, stage tracks, action cards, attribution zones and map stroke scales. Use it for every subject; do not generate custom CSS, image panels or hand-written KML for each new lesson. scripts/visuals.py is shared by all topic plans.

- Default stage cameras are north-up so directional language is stable. If an intentional rotated view is important for terrain/building explanation, set camera.allow_rotation=true and supply heading. The explicit orbit command preserves changing headings and returns to the normal stage orientation.
- Choose two to four salient opening features. Label at most four point locations on Earth; additional details and movement labels belong in the panel legend or explanation. Renderer limits map labels to four and suppresses arrow/area labels to reduce collisions. Keep map_label short and unambiguous. Show new process geometry only when it is being explained.
- Points are thin outlined teaching highlights. Arrows have narrow strokes and small, zoom-bounded heads. Do not author a very long arrow for a local concept just because the renderer can draw it. Shaded polygons are subtle; avoid opaque shapes covering the terrain.
- Every explanation should state one relationship, then show either a concise diagram list or the relevant Earth geometry. The shared panel gives diagrams a dedicated side column. It does not invent subject-specific scientific figures, cross-sections or measurements. Where a cross-section is needed, plan and label a sourced or explicitly schematic figure rather than claiming surface KML reveals underground structure.
- Accuracy, framing and explanatory content are still author responsibilities. Structural validation and a consistent theme do not verify a fault trace or make a poor diagram pedagogically sound. Check all initial features in the central viewport and verify scene rendering with the user.

Existing lesson snapshots also use this visual standard on continue; no lesson restart or regeneration is required to apply renderer styling. Live rig controls and OS/VM cropping can appear above an overlay and are separate display concerns. Keep Earth/provider attribution intact.
