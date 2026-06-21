from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import notion_wiring_audit as audit  # type: ignore[import]


class NotionWiringAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = audit._read_yaml(ROOT / "config" / "notion-wiring-map.yaml")
        cls.fixture = audit._read_json(ROOT / "tests" / "fixtures" / "notion_wiring_fixture.json")

    def test_broken_avatar_mismatch(self) -> None:
        record = copy.deepcopy(self.fixture["avatar"][0])
        result = audit.audit_record("avatar", record, self.config, "2026-06-22T00:00:00+00:00")
        self.assertEqual(result.generated_fields["AvatarCode_Generated"], "BOS_F_ZARA_05")
        self.assertEqual(result.generated_fields["AvatarCode_Mismatch"], "MISMATCH")
        self.assertEqual(result.generated_fields["Avatar_Wiring_Status"], "STALE_MANUAL_FIELD")

    def test_passing_avatar_row(self) -> None:
        record = copy.deepcopy(self.fixture["avatar"][1])
        result = audit.audit_record("avatar", record, self.config, "2026-06-22T00:00:00+00:00")
        self.assertEqual(result.status, "PASS")
        self.assertEqual(result.generated_fields["AvatarCode_Mismatch"], "PASS")
        self.assertEqual(result.generated_fields["PromptV1_Mismatch"], "PASS")

    def test_prompt_v1_mismatch_when_identity_differs(self) -> None:
        record = copy.deepcopy(self.fixture["avatar"][0])
        result = audit.audit_record("avatar", record, self.config, "2026-06-22T00:00:00+00:00")
        self.assertEqual(result.generated_fields["PromptV1_Mismatch"], "MISMATCH")

    def test_hybrid_stale_payload_mismatch(self) -> None:
        record = copy.deepcopy(self.fixture["hybrid"][0])
        result = audit.audit_record("hybrid", record, self.config, "2026-06-22T00:00:00+00:00")
        self.assertEqual(result.generated_fields["CompilerPayload_Mismatch"], "MISMATCH")
        self.assertEqual(result.generated_fields["CompilerPayload_Wiring_Status"], "STALE_MANUAL_FIELD")
        self.assertIn("Zara", result.generated_fields["CompilerPayload_Generated"])

    def test_continuation_missing_fields_critical(self) -> None:
        record = copy.deepcopy(self.fixture["hybrid"][0])
        result = audit.audit_record("hybrid", record, self.config, "2026-06-22T00:00:00+00:00")
        critical_titles = [finding.title for finding in result.findings if finding.severity == "critical"]
        self.assertIn("Continuation lock missing", critical_titles)

    def test_ingredients_style_scene_context_only_passes(self) -> None:
        record = copy.deepcopy(self.fixture["ingredients"][0])
        result = audit.audit_record("ingredients", record, self.config, "2026-06-22T00:00:00+00:00")
        self.assertEqual(result.status, "PASS")
        self.assertEqual(result.generated_fields["CompilerPayload_Mismatch"], "PASS")

    def test_no_overwrite_of_legacy_fields(self) -> None:
        original = copy.deepcopy(self.fixture)
        fixture_copy = copy.deepcopy(self.fixture)
        report = audit.execute_audit(
            self.config,
            source="fixture",
            target="all",
            dry_run=True,
            limit=None,
            fail_on="none",
        )
        self.assertFalse(report["summary"]["manual_legacy_fields_overwritten"])
        self.assertEqual(fixture_copy, original)


if __name__ == "__main__":
    unittest.main()
