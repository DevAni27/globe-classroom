# Live acceptance test: adaptation, not a fixed tour

Run this in Nara after installing v0.3.2. Read the skill instructions from disk again. Use /usr/bin/python3 with your active profile HERMES_HOME. No commands need to be run manually to teach the lesson.

## Start prompt

Use globe-classroom. Reload its installed SKILL.md. Start references/river-civilizations-reviewed.json from the installed skill directory using lesson_engine.py. Use /usr/bin/python3 and HERMES_HOME=/home/immor/.hermes/profiles/liquid-galaxy-agent. Enable local narration, deploy the opening scene yourself, explain how I answer here, and wait. Reuse the saved connection. Do not edit the plan or generate a different lesson.

Expected: Mesopotamia, labelled cyan/amber comparison rings over the real river imagery, a right-panel question, updated left branding and narration. Confirm visual rendering; file transfer alone is insufficient.

## Incomplete answer

Send: “People needed drinking water. I don't know how that helped cities grow.”

Expected: partial feedback summarises the answer, explains one missing connection and asks ONE question. Voice and chat end with the same question as the panel. The rig stays in Mesopotamia. No full explanation or Nile jump. Status phase should be partial, index 0. If Nara explains everything immediately, this test fails even if files transfer correctly.

## Strong reasoning

Send: “Farmers could use canals to water crops. Extra food could support people who built things or traded instead of farming. People still had to organise that work; the river didn't create a city by itself.”

Expected: correct acknowledgement; phase feedback. Say next. FIRST explanation must be “01 / Move water to crops”, with illustrative canal/field geometry and a cause-and-effect diagram. Then next shows “02 / Connect food to other work”; next shows “03 / Resources are not destiny”. One more next moves to Egypt. No scene may be skipped. Do not assume identical wording is required for semantic grading.

## Transfer: changed condition

The Nile question asks about too little floodwater. First send: “Egypt also had drinking water.”

Expected: partial/unclear, no recap and no invented claim that the learner applied the mechanism. Stay in Egypt and ask about water, crops and food dependence.

Then send: “Less floodwater could leave crops short of water, so harvests might shrink. There could be less food for farmers and people doing other jobs. Stored food or better water management might help.”

Expected: correct feedback identifying the NEW causal application. Next shows explanation one, then explanation two, then recap. Nara should distinguish the incomplete attempts from the later causal answers, without a fabricated score or a claim of measured learning improvement.

## Additional checks before recording

- Ask for a hint after an incorrect explanation: Nara should address the misconception and stay at the stop.
- Repeat narration with speak; it should match the active stage without advancing.
- Resume the active lesson in a new Nara chat; status/continue should preserve progress and voice.
- Test the supplied rain-shadow reference on the rig to demonstrate another topic. New arbitrary topics still require source reading and factual/geometry review.
- Restore after finishing; original loading-list and side overlays should return. Camera restoration is not supported. Avoid concurrent apps editing the same files.

## Evidence log

Record observed results, not assumptions: incomplete-answer screenshot, correct-feedback screenshot, first explanation screenshot, Nile transfer screenshot, recap/chat record, narration heard yes/no, date and environment. Automated tests cover state/rendering, not the model's actual educational judgment or Earth rendering.


## Camera acceptance after adaptation checks

Say “orbit here once, without advancing the lesson.” Nara should run orbit, not write a new tour script. Confirm Earth moves for approximately 28 seconds and returns to the saved view. Then request orbit again and say “stop moving” while it is moving; it should stop without changing phase or recorded answers. Say “return to the lesson view” and check orientation. Native playback, loading latency and stopping are live checks, not guaranteed by offline XML tests. If no movement occurs, retain the visual lesson and report the actual output; do not edit master.kml or rig startup to force it.

Frame one full VM viewport when checking side-panel clipping. Overlays now preserve source aspect ratio; an off-screen or scrolled VirtualBox viewport cannot be fixed by image layout alone. Native Google Earth controls may remain above KML overlays and need a separate UI adjustment before recording. Required imagery attribution stays visible.


Cleanup acceptance: say “End the lesson and remove its markers and panels.” Nara should run ENGINE end, not a hand-written delete command. Confirm Earth’s lesson markers and panels disappear. Then say “continue”; the ended state must refuse deployment and ask for a new start. The same end command should be safe to repeat. Original pre-lesson side content can return; unrelated new app content must be preserved.
