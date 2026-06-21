# BOSMAX Notion Wiring Control Layer

Status: draft repair contract
Scope: Notion live database wiring, stale-field prevention, compiler payload regeneration governance
Date: 2026-06-21

## Problem statement

The BOSMAX Notion workspace currently contains structured authority records and operator intake databases, but several execution fields behave as static text snapshots rather than dynamic compiler-control outputs.

Confirmed examples:

- `Avatar Ai` page `Kenduri 05` was edited to `CharacterName = Zara` while `AvatarCode` remained `BOS_F_AISYAH_05` and `PromptV1` still contained `Identity: Aisyah, Code: BOS_F_AISYAH_05`.
- `HYBRID Starter` keeps `Compiler Payload / RAW Prompt` as static text and hardcodes `Aisyah / BOS_F_AISYAH_05` even when the related avatar row changes.
- `FRAMES Starter` and `INGREDIENTS Starter` also store static prompt payloads that do not automatically recompose from their related authority records.

This means Notion is currently acting partly as a static prompt storage layer, not a fully dynamic compiler control layer.

## Non-goals

This contract does not change the retained authority pack files.
This contract does not change the three primary source-mode workflows.
This contract does not replace the video prompt compiler.
This contract does not approve Notion AI as an authority-wiring repair agent.

## Primary workflows remain unchanged

- HYBRID
- FRAMES
- INGREDIENTS

No new workflow such as `PART 2 WORKFLOW`, `CONTINUATION WORKFLOW`, or `LIPSYNC WORKFLOW` should be created. Continuation/lipsync controls are fields inside the existing three operator intakes.

## Live Notion data sources in scope

### Avatar Ai

Data source:

```text
collection://3854775a-f48a-80a7-9365-000bbe671ff7
```

Current high-risk static fields:

```text
AvatarCode
PromptV1
```

Current source fields:

```text
CharacterName
Name
Wardrobe
HairStyle
SkinTone
Expression
Environment
Lighting
Camera
SafetyBlock
approved_flag
usage_tags
```

Required repair stance:

- Do not overwrite `AvatarCode` or `PromptV1` until migration is validated.
- Add derived/generated/check fields first.
- Keep manual fields as legacy snapshot fields during migration.

Recommended new fields:

```text
AvatarCode_Generated
PromptV1_Generated
AvatarCode_Mismatch
PromptV1_Mismatch
Avatar_Wiring_Status
Avatar_Last_Generated_At
Avatar_Generation_Source
```

### HYBRID Operator Intake

Data source:

```text
collection://a47a36cc-ca74-40f7-88d3-2bd9ad67987d
```

High-risk static field:

```text
Compiler Payload / RAW Prompt
Output From Compiler
```

Source fields / relations:

```text
Product
Product Photo Upload
Avatar Ai
Avatar Source
Engine + Duration
Copy Source
BOSMAX Copy Set
MWTCB Copy Set
Scene Context
Overlay Allowed
Target Language
Platform
Project Ecosystem Files
```

Continuation fields already added:

```text
part1_end_frame_requirement
part1_final_frame_state
part2_first_frame_state
part2_first_0_5s_action
part2_first_1s_lipsync_lock
part2_no_vo_lock
part2_no_cutaway_until_lipsync_established
part2_dialogue_word_target
continuation_qa_status
```

Recommended new fields:

```text
CompilerPayload_Generated
CompilerPayload_Mismatch
CompilerPayload_Wiring_Status
CompilerPayload_Last_Generated_At
CompilerPayload_Source_Signature
```

### FRAMES Operator Intake

Data source:

```text
collection://e87788b4-1c0e-45df-91b4-4a8869a56c73
```

High-risk static field:

```text
Compiler Payload / RAW Prompt
Output From Compiler
```

Source fields / relations:

```text
Completed Frame Upload
Frame Context
Motion Delta
Product
Engine + Duration
Copy Source
BOSMAX Copy Set
MWTCB Copy Set
Overlay Allowed
Target Language
Platform
Project Ecosystem Files
```

Continuation fields already added:

```text
part1_end_frame_requirement
part1_final_frame_state
part2_first_frame_state
part2_first_0_5s_action
part2_first_1s_lipsync_lock
part2_no_vo_lock
part2_no_cutaway_until_lipsync_established
part2_dialogue_word_target
continuation_qa_status
```

Recommended new fields:

```text
CompilerPayload_Generated
CompilerPayload_Mismatch
CompilerPayload_Wiring_Status
CompilerPayload_Last_Generated_At
CompilerPayload_Source_Signature
```

### INGREDIENTS Operator Intake

Data source:

```text
collection://e179ea64-9691-4802-bbb6-cf896284a709
```

High-risk static field:

```text
Compiler Payload / RAW Prompt
Output From Compiler
```

Source fields / relations:

```text
Product Reference Photo
Avatar Reference Photo
Style Scene Reference Photo
Asset Role Map
style_scene_source
Scene Context
Product
Engine + Duration
Copy Source
BOSMAX Copy Set
MWTCB Copy Set
Overlay Allowed
Target Language
Platform
Project Ecosystem Files
```

Continuation fields already added:

```text
part1_end_frame_requirement
part1_final_frame_state
part2_first_frame_state
part2_first_0_5s_action
part2_first_1s_lipsync_lock
part2_no_vo_lock
part2_no_cutaway_until_lipsync_established
part2_dialogue_word_target
continuation_qa_status
```

Recommended new fields:

```text
CompilerPayload_Generated
CompilerPayload_Mismatch
CompilerPayload_Wiring_Status
CompilerPayload_Last_Generated_At
CompilerPayload_Source_Signature
```

## Authority records currently structured correctly

The following authorities are acceptable as source records, but must be pulled into generated payloads rather than manually copied into static snapshots.

### Product authority

Example page: `MWTCB_25ML_CAP_BURUNG`

Risk: Notion product authority is shallow compared with the retained JSON product truth. Keep retained JSON as final product truth unless Notion product schema is expanded.

### Engine duration authority

Example page: `GROK_16S`

Structured fields such as `block_plan_reference`, `compile_output_type`, `continuation_rule`, and `final_cta_rule` are source authority fields.

### Copy set authority

Example page: `MWTCB_25ML__ANG001__HOOK001`

Structured fields such as `angle`, `hook`, `subhook`, `usp1`, `usp2`, `usp3`, and `cta` are source authority fields.

### Asset role map authority

Example page: `INGREDIENTS_2_IMAGE_PRODUCT_AVATAR_SCENE_CONTEXT_ONLY`

Structured role map fields are source authority fields for Ingredients payload generation.

## Repair architecture

Recommended route: hybrid formula + script.

### Formula/check layer

Use formula/status fields for short checks only:

- mismatch flag
- wiring status
- stale indicator
- missing required input flag

### Generator/script layer

Use a deterministic generator for long fields:

- `PromptV1_Generated`
- `CompilerPayload_Generated`
- source signatures
- bulk regeneration
- stale payload validation

Long compiler payloads should not be maintained as Notion formulas because they are lengthy, multi-source, and authority-sensitive.

## Migration rule

Do not overwrite current manual fields until generated fields are validated.

Migration phases:

1. Add generated/check fields.
2. Generate values into new fields.
3. Compare manual vs generated.
4. Flag mismatch rows.
5. Operator reviews sample rows.
6. Promote generated fields to primary only after approval.

## Owner split

- ChatGPT / Notion connector: live schema patch, sample verification, operator-facing audit.
- Codex / GitHub: generator script, validator script, repeatable migration commands, repository-stored mapping contract.
- Notion AI: not recommended for schema governance or stale-field repair.

## Required validator behavior

A stale payload validator must detect:

- `CharacterName` not present in `AvatarCode`.
- `CharacterName` not present in `PromptV1`.
- `AvatarCode` not present in `PromptV1`.
- `Compiler Payload / RAW Prompt` not matching selected `Avatar Ai`.
- `Compiler Payload / RAW Prompt` not matching selected `Engine + Duration`.
- `Compiler Payload / RAW Prompt` not matching selected `Product` / product truth ref.
- `Compiler Payload / RAW Prompt` not matching selected copy set.
- Continuation fields missing while duration requires multi-block output.
- `part2_no_vo_lock` not enabled for continuation/lipsync rows.
- `part2_no_cutaway_until_lipsync_established` not enabled for continuation/lipsync rows.

## Acceptance criteria

The repair is complete only when:

- Source rows can be edited without silently leaving stale generated fields unflagged.
- Generated fields either update deterministically or mark themselves stale.
- Starter payloads no longer act as unverified static snapshots.
- Mismatch status fields are visible in operator/admin audit views.
- Any bulk regeneration script is versioned in GitHub.
- Manual legacy fields are clearly treated as legacy snapshot fields until migration is approved.
