# Lesson plan contract, schema_version 1

Nara authors JSON, never executable code. Validate with scripts/lesson_engine.py. Study references/rain-shadow.json for a fully populated, source-backed example. Change topic, sources, locations, questions and geometry for each new lesson; do not merely change its title.

Required top-level fields:

| Field | Meaning |
|---|---|
| schema_version | integer 1 |
| topic | subject requested by learner, at most 200 characters |
| title | lesson title, at most 200 characters |
| audience | learner level, at most 200 characters |
| learning_goal | what the learner should explain, at most 200 characters |
| sources | 2 to 15 source objects |
| steps | 2 to 8 inquiry stops; first prediction, at least one later transfer |

Each source contains id, title, url (HTTPS), supports (what you read that supports a claim). All four are nonempty strings, at most 600 characters. Use concise source titles for on-screen attribution. Validator checks URL structure, NOT whether you read it or whether a claim is true. Source IDs must be unique.

Each step requires:

- id: unique lowercase identifier matching [a-z][a-z0-9-]{0,39}.
- kind: prediction or transfer.
- title: up to 110 characters.
- place: up to 120 characters; real geographic context.
- time_context: up to 180 characters; seasonal, present-day, historical date range or dated observation.
- question: up to 430 characters; genuinely asks for an explanation before the answer.
- narration: up to 650 characters; spoken opening question, with NO answer reveal.
- follow_up: up to 350 characters; asks for reasoning after a bare choice or ambiguous response.
- visual_note: up to 250 characters; explain schematic/approximate geometry and data scope.
- source_ids: nonempty list of existing source IDs supporting this stop.
- camera: longitude [-180,180], latitude [-89,89], range [500,25000000] metres, tilt [0,80], heading [-360,360]. All are finite numbers. The camera aims at actual geography, not an invented coordinate.
- hints: 1 to 3 strings, each at most 350 characters, increasing in specificity.
- rubric: expected (up to 500 characters), reasoning (1 to 6 causal criteria, each up to 300 characters), misconceptions (1 to 6 likely misconceptions, each up to 300 characters). These are model-facing and not rendered to the learner before an answer.
- explanation: 2 to 4 beats, each with title (100 characters), text (500 characters), narration (700 characters). Each beat should explain ONE relationship and reveal relevant geometry. Learner says next to continue.
- features: 1 to 35 feature objects.

Feature contract:

| Field | Allowed values |
|---|---|
| type | point, line, arrow, polygon |
| label | concise legend description, up to 120 characters |
| color | cyan, amber, green, red, white, violet |
| geometry_kind | location, schematic, sourced |
| source_id | required for sourced geometry; reference a known source |
| show | question, hint, explain, or zero-based integer explanation beat |
| coordinates | point: [lon,lat] or [lon,lat,alt]; others: list of such coordinates |
| radius_km | point ring radius, optional, 0.1 to 300, default 5 |

Altitude is metres above terrain for schematic arrows; lines/polygons clamp to the terrain. Polygons require a closed ring of at least four coordinates (repeat the first coordinate at the end). Two to 1000 vertices for line/polygon/arrow. Longitude always comes FIRST. The engine intentionally does not execute KML/XML supplied by the model.

Point markers render as zoom-scaled coloured teaching rings with labels; their displayed size is not a measured area. Initial feature labels appear in the right-panel legend and abbreviated on the globe. Optional map_label (max 24 characters) gives a separate short globe label. Keep the first five labels particularly clear. Use the same colour for the same concept within a stop. Do not make a source-less polygon look like a precise official boundary. Approximate regions should be explicitly schematic in visual_note and narration.

Reveal semantics: question features remain visible throughout. hint features appear at a hint or explanation. explain features appear on every explanation beat. Integer features appear starting at that beat, accumulating as next advances. Avoid revealing the whole answer with the initial features or first hint.

The engine persists plan snapshots plus attempts and assessment evidence. It does not require A/B: comparison, causal explanation, route choice and counterfactual questions all use the same assessment contract. For a counterfactual, explain that the geometry represents a hypothetical teaching scenario rather than an observed event.

Optional explanation-beat field: diagram is a list of 2–4 strings, each at most 30 characters. It renders a causal chain of linked cards on the panel. Use only the mechanism already explained by that beat.

Avoid drawing watercourse paths from a handful of guessed coordinates. If suitable geometry is unavailable, show the real satellite river and use neutral comparison-area highlights, explicitly schematic.


Visual system v0.4.0: normal views are north-up. Set optional camera.allow_rotation=true to honour a deliberate nonzero heading outside an orbit. Point locations receive at most four map labels; arrow/line/polygon labels remain in the panel legend. Shared font, contrast, spacing, strokes and arrowhead limits apply to all plans. Keep initial visual comparisons to a few salient concepts.
