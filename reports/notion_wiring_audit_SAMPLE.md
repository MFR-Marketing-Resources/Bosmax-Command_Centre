# BOSMAX Notion Wiring Audit

- Execution timestamp: 2026-06-21T16:47:15+00:00
- Source mode: fixture
- Target: all
- Total records checked: 5
- Pass count: 3
- Mismatch count: 2
- Critical count: 7
- High count: 9
- Affected rows: HYBRID Starter, Kenduri 05
- Recommended next action: Review critical findings first, fix authority inputs, and regenerate generated/check fields without touching legacy manual fields.
- Manual legacy fields were not overwritten: YES

## Findings
[HIGH] Kenduri 05 — Avatar code stale
Reason: Manual AvatarCode `BOS_F_AISYAH_05` does not contain CharacterName `Zara`.
Action: Regenerate AvatarCode_Generated and keep AvatarCode read-only in this phase.

[HIGH] Kenduri 05 — Prompt identity stale
Reason: PromptV1 does not mention CharacterName `Zara`.
Action: Regenerate PromptV1_Generated and keep PromptV1 read-only in this phase.

[HIGH] Kenduri 05 — Generated code mismatch
Reason: Generated avatar code resolves to `BOS_F_ZARA_05` while manual AvatarCode remains `BOS_F_AISYAH_05`.
Action: Use the generated/check fields to surface the mismatch before any migration decision.

[HIGH] HYBRID Starter — Compiler payload stale
Reason: Legacy payload is missing the current selected avatar name `Zara`.
Action: Regenerate CompilerPayload_Generated and keep the legacy payload read-only.

[HIGH] HYBRID Starter — Compiler payload stale
Reason: Legacy payload is missing the current selected avatar code `BOS_F_ZARA_05`.
Action: Regenerate CompilerPayload_Generated and keep the legacy payload read-only.

[HIGH] HYBRID Starter — Compiler payload stale
Reason: Legacy payload is missing the current product truth ref `BOSMAX_SERUM_TRUTH_V1`.
Action: Regenerate CompilerPayload_Generated and keep the legacy payload read-only.

[HIGH] HYBRID Starter — Compiler payload stale
Reason: Legacy payload is missing the current copy hook `Kulit cepat kusam lepas kerja?`.
Action: Regenerate CompilerPayload_Generated and keep the legacy payload read-only.

[HIGH] HYBRID Starter — Compiler payload stale
Reason: Legacy payload is missing the current copy body `BOSMAX Serum bantu nampak lebih segar dan kemas untuk kamera harian.`.
Action: Regenerate CompilerPayload_Generated and keep the legacy payload read-only.

[HIGH] HYBRID Starter — Compiler payload stale
Reason: Legacy payload is missing the current copy CTA `Grab sekarang dan cuba rutin ringkas ini.`.
Action: Regenerate CompilerPayload_Generated and keep the legacy payload read-only.

[CRITICAL] HYBRID Starter — Continuation lock missing
Reason: Required continuation field `part1_final_frame_state` is missing from the continuity surface.
Action: Backfill the continuation authority fields before any non-dry-run migration step.

[CRITICAL] HYBRID Starter — Continuation lock missing
Reason: Required continuation field `part2_first_frame_state` is missing from the continuity surface.
Action: Backfill the continuation authority fields before any non-dry-run migration step.

[CRITICAL] HYBRID Starter — Continuation lock missing
Reason: Required continuation field `part2_first_0_5s_action` is missing from the continuity surface.
Action: Backfill the continuation authority fields before any non-dry-run migration step.

[CRITICAL] HYBRID Starter — Continuation lock missing
Reason: Required continuation field `part2_first_1s_lipsync_lock` is missing from the continuity surface.
Action: Backfill the continuation authority fields before any non-dry-run migration step.

[CRITICAL] HYBRID Starter — Continuation lock missing
Reason: Required continuation field `part2_no_vo_lock` is missing from the continuity surface.
Action: Backfill the continuation authority fields before any non-dry-run migration step.

[CRITICAL] HYBRID Starter — Continuation lock missing
Reason: Required continuation field `part2_no_cutaway_until_lipsync_established` is missing from the continuity surface.
Action: Backfill the continuation authority fields before any non-dry-run migration step.

[CRITICAL] HYBRID Starter — Continuation lock missing
Reason: Required continuation field `part2_dialogue_word_target` is missing from the continuity surface.
Action: Backfill the continuation authority fields before any non-dry-run migration step.

## Record Outputs
### AVATAR :: Kenduri 05
- Status: STALE_MANUAL_FIELD
- Mismatch fields: {"AvatarCode_Mismatch": "MISMATCH", "PromptV1_Mismatch": "MISMATCH"}
- Generated fields: {"AvatarCode_Generated": "BOS_F_ZARA_05", "PromptV1_Generated": "Create a photorealistic avatar reference image. Identity: Zara, Code: BOS_F_ZARA_05. Demographic: Female, Young Adult, Malay/SEA market fit. Role: family celebration host. Styling: Soft peach baju kurung with neat drape. Hair: Pinned-back dark hair. Skin tone: Warm medium tan. Expression: Friendly confident smile. Pose: Relaxed, natural. Environment: Kampung home interior, Warm window light. Camera framing: Head-and-shoulders portrait, clear face. Safety: Do not generate nudity, sexual content, gore, violence, hate symbols, illegal activity, or any harmful or unsafe depiction. Keep the character fully clothed, respectful, and suitable for general audience and commercial use.", "AvatarCode_Mismatch": "MISMATCH", "PromptV1_Mismatch": "MISMATCH", "Avatar_Wiring_Status": "STALE_MANUAL_FIELD", "Avatar_Last_Generated_At": "2026-06-21T16:47:15+00:00", "Avatar_Generation_Source": "fixture:notion_wiring_audit.py"}
- Preserved legacy fields: {"AvatarCode": "BOS_F_AISYAH_05", "PromptV1": "Create a photorealistic avatar reference image. Identity: Aisyah, Code: BOS_F_AISYAH_05. Commercial-safe wardrobe and market-ready expression."}

### AVATAR :: Kenduri 05
- Status: PASS
- Mismatch fields: {"AvatarCode_Mismatch": "PASS", "PromptV1_Mismatch": "PASS"}
- Generated fields: {"AvatarCode_Generated": "BOS_F_ZARA_05", "PromptV1_Generated": "Create a photorealistic avatar reference image. Identity: Zara, Code: BOS_F_ZARA_05. Demographic: Female, Young Adult, Malay/SEA market fit. Role: family celebration host. Styling: Soft peach baju kurung with neat drape. Hair: Pinned-back dark hair. Skin tone: Warm medium tan. Expression: Friendly confident smile. Pose: Relaxed, natural. Environment: Kampung home interior, Warm window light. Camera framing: Head-and-shoulders portrait, clear face. Safety: Do not generate nudity, sexual content, gore, violence, hate symbols, illegal activity, or any harmful or unsafe depiction. Keep the character fully clothed, respectful, and suitable for general audience and commercial use.", "AvatarCode_Mismatch": "PASS", "PromptV1_Mismatch": "PASS", "Avatar_Wiring_Status": "PASS", "Avatar_Last_Generated_At": "2026-06-21T16:47:15+00:00", "Avatar_Generation_Source": "fixture:notion_wiring_audit.py"}
- Preserved legacy fields: {"AvatarCode": "BOS_F_ZARA_05", "PromptV1": "Create a photorealistic avatar reference image. Identity: Zara, Code: BOS_F_ZARA_05. Commercial-safe wardrobe and market-ready expression."}

### HYBRID :: HYBRID Starter
- Status: STALE_MANUAL_FIELD
- Mismatch fields: {"CompilerPayload_Mismatch": "MISMATCH"}
- Generated fields: {"CompilerPayload_Generated": "mode: HYBRID\nproduct_truth_ref: BOSMAX_SERUM_TRUTH_V1\navatar_name: Zara\navatar_code: BOS_F_ZARA_05\nengine: GOOGLE_FLOW\nduration: 16s\ncopy_set:\n  hook: Kulit cepat kusam lepas kerja?\n  body: BOSMAX Serum bantu nampak lebih segar dan kemas untuk kamera harian.\n  cta: Grab sekarang dan cuba rutin ringkas ini.\nmanual_legacy_writeback: DISABLED\ncontinuation:\n  part1_final_frame_state: ''\n  part2_first_frame_state: ''\n  part2_first_0_5s_action: ''\n  part2_first_1s_lipsync_lock: ''\n  part2_no_voiceover_lock: ''\n  part2_no_product_cutaway_until_lipsync_established: ''\n  part2_dialogue_word_target: {}", "CompilerPayload_Mismatch": "MISMATCH", "CompilerPayload_Wiring_Status": "STALE_MANUAL_FIELD", "CompilerPayload_Last_Generated_At": "2026-06-21T16:47:15+00:00", "CompilerPayload_Source_Signature": "fixture::hybrid::HYBRID_STARTER::BOSMAX_NOTION_WIRING_CONTROL_LAYER_v1"}
- Preserved legacy fields: {"Compiler Payload / RAW Prompt": "Legacy payload hardcodes Aisyah and BOS_F_AISYAH_05 for a 16s GOOGLE_FLOW serum script. Hook: Kulit cepat kusam? CTA: Grab sekarang."}

### FRAMES :: FRAMES Continuation Sample
- Status: PASS
- Mismatch fields: {"CompilerPayload_Mismatch": "PASS"}
- Generated fields: {"CompilerPayload_Generated": "mode: FRAMES\nproduct_truth_ref: BOSMAX_SERUM_TRUTH_V1\navatar_name: Zara\navatar_code: BOS_F_ZARA_05\nengine: GOOGLE_FLOW\nduration: 16s\ncopy_set:\n  hook: ''\n  body: ''\n  cta: ''\nmanual_legacy_writeback: DISABLED\nframe_truth:\n  completed_frame_upload: frame://kenduri-05-final.png\n  frame_context: Presenter already holding BOSMAX Serum at chest height in kampung\n    dining room.\n  motion_delta: Continue with small wrist lift and direct-to-camera explanation.", "CompilerPayload_Mismatch": "PASS", "CompilerPayload_Wiring_Status": "PASS", "CompilerPayload_Last_Generated_At": "2026-06-21T16:47:15+00:00", "CompilerPayload_Source_Signature": "fixture::frames::FRAMES_CONTINUATION_SAMPLE::BOSMAX_NOTION_WIRING_CONTROL_LAYER_v1"}
- Preserved legacy fields: {"Compiler Payload / RAW Prompt": "Mode: FRAMES. Avatar: Zara. Avatar code: BOS_F_ZARA_05. Product truth ref: BOSMAX_SERUM_TRUTH_V1. Engine: GOOGLE_FLOW. Duration: 16s. Use frame://kenduri-05-final.png as the visual truth. Presenter already holding BOSMAX Serum at chest height in kampung dining room. Continue with small wrist lift and direct-to-camera explanation."}

### INGREDIENTS :: INGREDIENTS Style Optional
- Status: PASS
- Mismatch fields: {"CompilerPayload_Mismatch": "PASS"}
- Generated fields: {"CompilerPayload_Generated": "mode: INGREDIENTS\nproduct_truth_ref: BOSMAX_SERUM_TRUTH_V1\navatar_name: Zara\navatar_code: BOS_F_ZARA_05\nengine: GOOGLE_FLOW\nduration: 16s\ncopy_set:\n  hook: ''\n  body: ''\n  cta: ''\nmanual_legacy_writeback: DISABLED\ningredients_truth:\n  product_reference:\n  - product://bosmax-serum-front.png\n  avatar_reference:\n  - avatar://zara-reference.png\n  style_scene_reference: []\n  style_scene_source: SCENE_CONTEXT_ONLY\n  asset_role_map:\n    product_reference_role: PRODUCT_TRUTH\n    avatar_reference_role: AVATAR_IDENTITY\n    style_scene_role: SCENE_CONTEXT_ONLY\n  hierarchy: PRODUCT_TRUTH > AVATAR_IDENTITY > STYLE_SCENE", "CompilerPayload_Mismatch": "PASS", "CompilerPayload_Wiring_Status": "PASS", "CompilerPayload_Last_Generated_At": "2026-06-21T16:47:15+00:00", "CompilerPayload_Source_Signature": "fixture::ingredients::INGREDIENTS_STYLE_OPTIONAL::BOSMAX_NOTION_WIRING_CONTROL_LAYER_v1"}
- Preserved legacy fields: {"Compiler Payload / RAW Prompt": "Mode: INGREDIENTS. Avatar: Zara. Avatar code: BOS_F_ZARA_05. Product truth ref: BOSMAX_SERUM_TRUTH_V1. Engine: GOOGLE_FLOW. Duration: 16s. PRODUCT_TRUTH > AVATAR_IDENTITY > STYLE_SCENE. style_scene_source: SCENE_CONTEXT_ONLY. Product reference and avatar reference are present; style image intentionally omitted."}
