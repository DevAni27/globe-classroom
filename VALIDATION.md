# Validation record — version 0.4.0

## Historical development checks

The entries below describe evidence available at each version; the final acceptance entry supersedes their pending items.

18 offline tests passed on 26 October 2026. Coverage includes complete camera/KML XML, stage gating, partial/unclear answers, hint and explicit reveal tracking, staged explanation beats, transfer progression, source-reference and coordinate validation, polygon rendering, dynamic panel generation and private state permissions. Shared transport backup/deployment/restore was tested against a temporary local filesystem, not a remote rig.

Six dynamic panel layouts were visually inspected; all ten legacy prepared panels were previously inspected. Bundled reference facts use primary/institutional sources listed in SOURCES.md and the lesson JSON. Structural validity is not a factual correctness guarantee for new generated plans.

User-confirmed real-rig evidence for version 0.1: valid camera XML moved Earth; old app content cleared; opening lesson rendered with both location rings, left branding and right question panel.

Not yet confirmed on the user's rig: version 0.2 dynamic rendering, local narration, arbitrary new-topic research/authoring, conversational assessment, full transfer flow and restoration. Runtime checks and source validation are not a substitute for these observations.

The package has no model/provider credentials. All provider calls remain in Nara. Optional voice uses installed local system speech with variable quality; it does not provide microphone input. Standard odd LG layout and port 81 are assumed.


Version 0.2.1: 24 offline tests pass, including feedback persistence, panel/narration consistency, matching final question, progression/clearing and old-state compatibility. Personalised cards rendered locally. The user confirmed v0.2.0 deployment and local voice on a real virtual rig; v0.2.1 still requires live confirmation. No claim of historical fact verification.


Version 0.3.0: 28 offline tests pass. Added complete partial-to-correct-to-transfer-to-recap regression, legacy correct-feedback migration, every reviewed-river panel/beat and label visibility checks. Dynamic branding and panels were rendered and visually inspected. SSH/restore tests use a local test double; updated 0.3.0 Google Earth rendering, label visibility at rig resolution, narration and live model assessment remain pending contributor acceptance. The existing 0.2.x live run established SSH/overlay/voice operation only.


Version 0.3.1: 34 offline tests pass. Added finite 28-second native tour XML, last-view return, shell/test-double orbit/stop cleanup preserving unrelated links and lesson progress, compact context bounds, duplicate-question rejection, aspect-ratio overlay settings and engine-owned navigation prompts. Contributor completed v0.3.0 live adaptation sequence including contextual Nile follow-up and recap (2 correct assessments, 2 follow-ups). v0.3.1 camera playback, actual stopping on Earth, overlay fit and native navigation controls remain live checks. No user-PC/rig execution is available from this development environment.


Version 0.3.2: cleanup regressions cover empty scene before unlink, preservation of later-added links, preservation of side panels replaced by other apps, missing original side files and repeat cleanup. Climate reference validates/renders through the same engine; its full live run and permanent end cleanup remain contributor checks. User confirmed orbit playback in v0.3.1. Existing visual design retained.


v0.4.0: shared visual-system regression checks cover north-up defaults/explicit rotation, native orbit heading changes, one LineStyle per polygon, selective map labels and bounded arrowheads. All panel phases and explanation beats rendered across river, climate and the uploaded generated earthquake plan. New look and map geometry styles remain pending a live rig check.


## Final contributor acceptance — 26 October 2026

Final packaging check: all 41 local automated tests pass.

The contributor reports the v0.4.0 design is cleaner and confirms completion of both Japan misconception/strong-answer responses and packaged “End the lesson” cleanup. Together with the earlier river sequence, this provides live evidence of targeted follow-up, successful causal reasoning, transfer to another location, two subject areas, narration, orbit and cleanup on the three-VM rig. The developer did not independently operate the user's rig. A full climate live test is not claimed. Publication and demo recording are delivery tasks, not runtime checks.
