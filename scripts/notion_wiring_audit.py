from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "notion-wiring-map.yaml"
TARGET_ORDER = ("avatar", "hybrid", "frames", "ingredients")
SEVERITY_RANK = {"critical": 3, "high": 2, "info": 1}
FAIL_ON_THRESHOLD = {"none": 0, "any": 1, "high": 2, "critical": 3}
SOURCE_TO_CONFIG_KEY = {
    "avatar": "avatar_ai",
    "hybrid": "hybrid_operator_intake",
    "frames": "frames_operator_intake",
    "ingredients": "ingredients_operator_intake",
}


class AuditError(RuntimeError):
    """Raised when audit execution must fail closed."""


@dataclass
class Finding:
    severity: str
    target: str
    row_name: str
    title: str
    reason: str
    action: str


@dataclass
class RecordAudit:
    target: str
    row_name: str
    status: str
    generated_fields: dict[str, Any]
    mismatch_fields: dict[str, str]
    preserved_legacy_fields: dict[str, Any]
    findings: list[Finding]


def _read_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AuditError(f"YAML config must resolve to a mapping: {path}")
    return payload


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AuditError(f"Fixture must resolve to a mapping: {path}")
    return payload


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def _normalize_space(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _contains_token(haystack: Any, needle: Any) -> bool:
    return _normalize_space(needle).lower() in _normalize_space(haystack).lower()


def _slug(value: Any) -> str:
    token = re.sub(r"[^A-Za-z0-9]+", "_", str(value or "").strip())
    return token.strip("_").upper() or "ROW"


def _yaml_dump(payload: dict[str, Any]) -> str:
    return yaml.safe_dump(payload, sort_keys=False, allow_unicode=True).strip()


def _severity_value(level: str) -> int:
    return SEVERITY_RANK.get(str(level or "").lower(), 0)


def _make_finding(
    severity: str,
    target: str,
    row_name: str,
    title: str,
    reason: str,
    action: str,
) -> Finding:
    return Finding(
        severity=str(severity).lower(),
        target=target,
        row_name=row_name,
        title=title,
        reason=reason,
        action=action,
    )


def _resolve_targets(target: str) -> list[str]:
    if target == "all":
        return list(TARGET_ORDER)
    if target not in TARGET_ORDER:
        raise AuditError(f"Unsupported target: {target}")
    return [target]


def _fixture_path(config: dict[str, Any]) -> Path:
    defaults = config.get("defaults") or {}
    path = defaults.get("fixture_path") or "tests/fixtures/notion_wiring_fixture.json"
    return ROOT / str(path)


def _load_fixture_rows(config: dict[str, Any], limit: int | None) -> dict[str, list[dict[str, Any]]]:
    payload = _read_json(_fixture_path(config))
    rows: dict[str, list[dict[str, Any]]] = {}
    remaining = limit if limit and limit > 0 else None
    for target in TARGET_ORDER:
        values = payload.get(target) or []
        if not isinstance(values, list):
            raise AuditError(f"Fixture target must be a list: {target}")
        selected: list[dict[str, Any]] = []
        for item in values:
            if not isinstance(item, dict):
                raise AuditError(f"Fixture row must be an object: {target}")
            if remaining is not None and remaining <= 0:
                break
            selected.append(copy.deepcopy(item))
            if remaining is not None:
                remaining -= 1
        rows[target] = selected
        if remaining is not None and remaining <= 0:
            break
    for target in TARGET_ORDER:
        rows.setdefault(target, [])
    return rows


def _live_guard() -> None:
    token = os.environ.get("NOTION_TOKEN", "").strip()
    api_key = os.environ.get("NOTION_API_KEY", "").strip()
    if not token and not api_key:
        raise AuditError("LIVE_MODE_NOT_CONFIGURED: missing NOTION_TOKEN or NOTION_API_KEY")
    raise AuditError("LIVE_MODE_NOT_CONFIGURED")


def _role_text(record: dict[str, Any], source_cfg: dict[str, Any]) -> str:
    for key in source_cfg.get("role_fields") or []:
        value = record.get(key)
        if isinstance(value, list):
            rendered = ", ".join(str(item).strip() for item in value if str(item).strip())
            if rendered:
                return rendered
        if value not in (None, ""):
            return str(value)
    return "commercial avatar lead"


def _gender_code(record: dict[str, Any], source_cfg: dict[str, Any]) -> str:
    raw = str(
        record.get("GenderCode")
        or record.get("gender_code")
        or record.get("Gender")
        or record.get("gender")
        or ""
    ).strip()
    token = raw.upper()
    female_tokens = {str(item).upper() for item in (source_cfg.get("female_gender_tokens") or [])}
    if token in female_tokens:
        return "F"
    if token.startswith("M"):
        return "M"
    return str(source_cfg.get("default_gender_code") or "F").strip().upper() or "F"


def _scene_code(name: Any) -> str:
    match = re.search(r"(\d{2})(?!.*\d)", str(name or ""))
    return match.group(1) if match else ""


def _generated_avatar_code(record: dict[str, Any], source_cfg: dict[str, Any]) -> str:
    row_name = record.get(source_cfg["row_name_field"])
    character_name = _normalize_space(record.get(source_cfg["character_name_field"]))
    scene = _scene_code(row_name)
    if not character_name or not scene:
        return "NEEDS_REGENERATION"
    return f"BOS_{_gender_code(record, source_cfg)}_{_slug(character_name)}_{scene}"


def _generated_prompt(record: dict[str, Any], source_cfg: dict[str, Any], avatar_code: str) -> str:
    character_name = _normalize_space(record.get(source_cfg["character_name_field"]))
    demographic = str(record.get("Demographic") or "Female, Young Adult, Malay/SEA market fit").strip()
    wardrobe = str(record.get("Wardrobe") or "commercial-safe wardrobe").strip()
    hairstyle = str(record.get("HairStyle") or "natural tidy hair").strip()
    skin = str(record.get("SkinTone") or "healthy medium skin tone").strip()
    expression = str(record.get("Expression") or "friendly confident expression").strip()
    environment = str(record.get("Environment") or "neutral studio-ready environment").strip()
    lighting = str(record.get("Lighting") or "soft commercial lighting").strip()
    camera = str(record.get("Camera") or "medium close-up").strip()
    safety = str(
        record.get("SafetyBlock")
        or "Do not generate nudity, sexual content, gore, violence, hate symbols, illegal activity, or any harmful or unsafe depiction."
    ).strip()
    return (
        "Create a photorealistic avatar reference image. "
        f"Identity: {character_name}, Code: {avatar_code}. "
        f"Demographic: {demographic}. "
        f"Role: {_role_text(record, source_cfg)}. "
        f"Styling: {wardrobe}. Hair: {hairstyle}. Skin tone: {skin}. "
        f"Expression: {expression}. Pose: Relaxed, natural. "
        f"Environment: {environment}, {lighting}. "
        f"Camera framing: {camera}, clear face. "
        f"Safety: {safety} "
        "Keep the character fully clothed, respectful, and suitable for general audience and commercial use."
    )


def audit_avatar(record: dict[str, Any], source_cfg: dict[str, Any], timestamp: str) -> RecordAudit:
    row_name = str(record.get(source_cfg["row_name_field"]) or "Unnamed Avatar")
    character_name = _normalize_space(record.get(source_cfg["character_name_field"]))
    manual_code = str(record.get(source_cfg["manual_avatar_code_field"]) or "")
    manual_prompt = str(record.get(source_cfg["manual_prompt_field"]) or "")
    generated_code = _generated_avatar_code(record, source_cfg)
    prompt_generated = _generated_prompt(record, source_cfg, generated_code)
    field_map = source_cfg["generated_field_map"]
    findings: list[Finding] = []

    if generated_code == "NEEDS_REGENERATION":
        findings.append(
            _make_finding(
                "critical",
                "avatar",
                row_name,
                "Avatar code cannot be derived safely",
                "Scene code or identity inputs are insufficient to derive BOS_<GenderCode>_<NAME>_<SceneCode>.",
                "Complete the missing authority fields and regenerate only the generated/check surfaces.",
            )
        )
    if character_name and not _contains_token(manual_code, character_name):
        findings.append(
            _make_finding(
                "high",
                "avatar",
                row_name,
                "Avatar code stale",
                f"Manual AvatarCode `{manual_code}` does not contain CharacterName `{character_name}`.",
                "Regenerate AvatarCode_Generated and keep AvatarCode read-only in this phase.",
            )
        )
    if character_name and not _contains_token(manual_prompt, character_name):
        findings.append(
            _make_finding(
                "high",
                "avatar",
                row_name,
                "Prompt identity stale",
                f"PromptV1 does not mention CharacterName `{character_name}`.",
                "Regenerate PromptV1_Generated and keep PromptV1 read-only in this phase.",
            )
        )
    if manual_code and not _contains_token(manual_prompt, manual_code):
        findings.append(
            _make_finding(
                "high",
                "avatar",
                row_name,
                "Prompt code stale",
                f"PromptV1 does not preserve AvatarCode `{manual_code}`.",
                "Regenerate PromptV1_Generated and keep PromptV1 read-only in this phase.",
            )
        )
    if generated_code not in {"", "NEEDS_REGENERATION"} and manual_code != generated_code:
        findings.append(
            _make_finding(
                "high",
                "avatar",
                row_name,
                "Generated code mismatch",
                f"Generated avatar code resolves to `{generated_code}` while manual AvatarCode remains `{manual_code}`.",
                "Use the generated/check fields to surface the mismatch before any migration decision.",
            )
        )

    prompt_mismatch = (
        (character_name and not _contains_token(manual_prompt, character_name))
        or (generated_code not in {"", "NEEDS_REGENERATION"} and not _contains_token(manual_prompt, generated_code))
    )
    status = "PASS" if not findings else ("NEEDS_REGENERATION" if generated_code == "NEEDS_REGENERATION" else "STALE_MANUAL_FIELD")
    generated_fields = {
        field_map["avatar_code"]: generated_code,
        field_map["prompt"]: prompt_generated,
        field_map["mismatch_code"]: "MISMATCH" if manual_code != generated_code else "PASS",
        field_map["mismatch_prompt"]: "MISMATCH" if prompt_mismatch else "PASS",
        field_map["status"]: status,
        field_map["generated_at"]: timestamp,
        field_map["source"]: "fixture:notion_wiring_audit.py",
    }
    return RecordAudit(
        target="avatar",
        row_name=row_name,
        status=status,
        generated_fields=generated_fields,
        mismatch_fields={
            field_map["mismatch_code"]: generated_fields[field_map["mismatch_code"]],
            field_map["mismatch_prompt"]: generated_fields[field_map["mismatch_prompt"]],
        },
        preserved_legacy_fields={
            source_cfg["manual_avatar_code_field"]: manual_code,
            source_cfg["manual_prompt_field"]: manual_prompt,
        },
        findings=findings,
    )


def _copy_set(record: dict[str, Any]) -> dict[str, str]:
    payload = record.get("CopySet")
    if not isinstance(payload, dict):
        payload = {}
    return {
        "hook": str(payload.get("hook") or record.get("Hook") or "").strip(),
        "body": str(payload.get("body") or record.get("Body") or "").strip(),
        "cta": str(payload.get("cta") or record.get("CTA") or "").strip(),
    }


def _base_payload(record: dict[str, Any], mode: str) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "mode": mode,
        "product_truth_ref": str(record.get("ProductTruthRef") or "").strip(),
        "avatar_name": str(record.get("SelectedAvatarName") or record.get("CharacterName") or "").strip(),
        "avatar_code": str(record.get("SelectedAvatarCode") or record.get("AvatarCode_Generated") or record.get("AvatarCode") or "").strip(),
        "engine": str(record.get("Engine") or "").strip(),
        "duration": str(record.get("Duration") or "").strip(),
        "copy_set": _copy_set(record),
        "manual_legacy_writeback": "DISABLED",
    }
    if mode == "HYBRID":
        payload["continuation"] = record.get("Continuation") or {}
    if mode == "FRAMES":
        payload["frame_truth"] = {
            "completed_frame_upload": str(record.get("Completed Frame Upload") or "").strip(),
            "frame_context": str(record.get("Frame Context") or "").strip(),
            "motion_delta": str(record.get("Motion Delta") or "").strip(),
        }
    if mode == "INGREDIENTS":
        payload["ingredients_truth"] = {
            "product_reference": list(record.get("Product Reference") or []),
            "avatar_reference": list(record.get("Avatar Reference") or []),
            "style_scene_reference": list(record.get("Style Image") or []),
            "style_scene_source": str(record.get("style_scene_source") or "").strip(),
            "asset_role_map": record.get("Asset Role Map") or {},
            "hierarchy": "PRODUCT_TRUTH > AVATAR_IDENTITY > STYLE_SCENE",
        }
    return payload


def _source_signature(row_name: str, target: str) -> str:
    return f"fixture::{target}::{_slug(row_name)}::BOSMAX_NOTION_WIRING_CONTROL_LAYER_v1"


def _continuation_value(continuation: dict[str, Any], aliases: list[str]) -> Any:
    for alias in aliases:
        value = continuation.get(alias)
        if value not in (None, "", {}, []):
            return value
    return ""


def audit_compiler_row(
    target: str,
    mode: str,
    record: dict[str, Any],
    source_cfg: dict[str, Any],
    timestamp: str,
) -> RecordAudit:
    row_name = str(record.get(source_cfg["row_name_field"]) or f"Unnamed {target.title()}")
    manual_payload = str(record.get(source_cfg["manual_payload_field"]) or "")
    payload = _base_payload(record, mode)
    generated_payload = _yaml_dump(payload)
    findings: list[Finding] = []
    field_map = source_cfg["generated_field_map"]

    for label, value in (
        ("selected avatar name", payload["avatar_name"]),
        ("selected avatar code", payload["avatar_code"]),
        ("product truth ref", payload["product_truth_ref"]),
        ("engine", payload["engine"]),
        ("duration", payload["duration"]),
        ("copy hook", payload["copy_set"]["hook"]),
        ("copy body", payload["copy_set"]["body"]),
        ("copy CTA", payload["copy_set"]["cta"]),
    ):
        if value and not _contains_token(manual_payload, value):
            findings.append(
                _make_finding(
                    "high",
                    target,
                    row_name,
                    "Compiler payload stale",
                    f"Legacy payload is missing the current {label} `{value}`.",
                    "Regenerate CompilerPayload_Generated and keep the legacy payload read-only.",
                )
            )

    if mode == "HYBRID":
        continuation = record.get("Continuation") if isinstance(record.get("Continuation"), dict) else {}
        if bool(record.get("RequiresContinuation")):
            for logical_name, aliases in (source_cfg.get("continuation_aliases") or {}).items():
                if _continuation_value(continuation, [str(item) for item in aliases]) in (None, "", {}, []):
                    findings.append(
                        _make_finding(
                            "critical",
                            target,
                            row_name,
                            "Continuation lock missing",
                            f"Required continuation field `{logical_name}` is missing from the continuity surface.",
                            "Backfill the continuation authority fields before any non-dry-run migration step.",
                        )
                    )

    if mode == "FRAMES":
        for field_name in ("Completed Frame Upload", "Frame Context", "Motion Delta"):
            value = str(record.get(field_name) or "").strip()
            if value and not _contains_token(manual_payload, value):
                findings.append(
                    _make_finding(
                        "high",
                        target,
                        row_name,
                        "Frames payload incomplete",
                        f"Legacy FRAMES payload does not preserve `{field_name}`.",
                        "Regenerate CompilerPayload_Generated from frame-truth inputs only.",
                    )
                )
        if bool(record.get("RebuildSceneFromScratch")):
            findings.append(
                _make_finding(
                    "critical",
                    target,
                    row_name,
                    "Frames mode drifted into scene rebuild",
                    "FRAMES payload is rebuilding product/avatar/scene instead of extending the uploaded finished frame.",
                    "Remove scene-rebuild behavior and keep the payload motion-delta only.",
                )
            )

    if mode == "INGREDIENTS":
        product_reference = list(record.get("Product Reference") or [])
        avatar_reference = list(record.get("Avatar Reference") or [])
        style_reference = list(record.get("Style Image") or [])
        asset_role_map = record.get("Asset Role Map") or {}
        style_scene_source = str(record.get("style_scene_source") or "").strip()

        if not product_reference:
            findings.append(
                _make_finding(
                    "critical",
                    target,
                    row_name,
                    "Product reference missing",
                    "INGREDIENTS row is missing Product Reference input.",
                    "Attach product reference authority before generating payloads.",
                )
            )
        if not avatar_reference:
            findings.append(
                _make_finding(
                    "critical",
                    target,
                    row_name,
                    "Avatar reference missing",
                    "INGREDIENTS row is missing Avatar Reference input.",
                    "Attach avatar reference authority before generating payloads.",
                )
            )
        if not isinstance(asset_role_map, dict) or not asset_role_map:
            findings.append(
                _make_finding(
                    "critical",
                    target,
                    row_name,
                    "Asset role map ambiguous",
                    "INGREDIENTS row is missing an explicit Asset Role Map.",
                    "Define a deterministic asset role map before generation.",
                )
            )
        else:
            if "AMBIGUOUS" in json.dumps(asset_role_map, ensure_ascii=False).upper():
                findings.append(
                    _make_finding(
                        "critical",
                        target,
                        row_name,
                        "Asset role map ambiguous",
                        "Asset Role Map explicitly remains ambiguous.",
                        "Resolve role ownership for product, avatar, and style inputs before generation.",
                    )
                )
        if not style_reference and style_scene_source != "SCENE_CONTEXT_ONLY":
            findings.append(
                _make_finding(
                    "high",
                    target,
                    row_name,
                    "Style source policy mismatch",
                    "Style image is absent but style_scene_source is not `SCENE_CONTEXT_ONLY`.",
                    "Set style_scene_source to SCENE_CONTEXT_ONLY or attach a valid style image.",
                )
            )
        if not _contains_token(manual_payload, "PRODUCT_TRUTH > AVATAR_IDENTITY > STYLE_SCENE"):
            findings.append(
                _make_finding(
                    "high",
                    target,
                    row_name,
                    "Hierarchy not preserved",
                    "Legacy payload does not preserve product-truth hierarchy.",
                    "Regenerate CompilerPayload_Generated with explicit hierarchy ordering.",
                )
            )

    status = "PASS" if not findings else "STALE_MANUAL_FIELD"
    generated_fields = {
        field_map["payload"]: generated_payload,
        field_map["mismatch"]: "MISMATCH" if findings else "PASS",
        field_map["status"]: status,
        field_map["generated_at"]: timestamp,
        field_map["source_signature"]: _source_signature(row_name, target),
    }
    return RecordAudit(
        target=target,
        row_name=row_name,
        status=status,
        generated_fields=generated_fields,
        mismatch_fields={field_map["mismatch"]: generated_fields[field_map["mismatch"]]},
        preserved_legacy_fields={source_cfg["manual_payload_field"]: manual_payload},
        findings=findings,
    )


def audit_record(target: str, record: dict[str, Any], config: dict[str, Any], timestamp: str) -> RecordAudit:
    source_cfg = config["sources"][SOURCE_TO_CONFIG_KEY[target]]
    if target == "avatar":
        return audit_avatar(record, source_cfg, timestamp)
    return audit_compiler_row(target, target.upper(), record, source_cfg, timestamp)


def build_summary(
    source: str,
    target: str,
    records: list[RecordAudit],
    timestamp: str,
    dry_run: bool,
    fail_on: str,
) -> dict[str, Any]:
    findings = [finding for record in records for finding in record.findings]
    affected_rows = sorted({finding.row_name for finding in findings})
    critical_count = sum(1 for finding in findings if finding.severity == "critical")
    high_count = sum(1 for finding in findings if finding.severity == "high")
    pass_count = sum(1 for record in records if record.status == "PASS")
    mismatch_count = sum(
        1 for record in records if any(value == "MISMATCH" for value in record.mismatch_fields.values())
    )
    if critical_count:
        next_action = "Review critical findings first, fix authority inputs, and regenerate generated/check fields without touching legacy manual fields."
    elif high_count:
        next_action = "Review stale manual fields against generated surfaces and keep live write-back disabled."
    else:
        next_action = "Audit passed. Generated/check fields align and legacy manual fields remained read-only."
    return {
        "execution_timestamp": timestamp,
        "source_mode": source,
        "target": target,
        "dry_run": dry_run,
        "fail_on": fail_on,
        "total_records_checked": len(records),
        "pass_count": pass_count,
        "mismatch_count": mismatch_count,
        "critical_count": critical_count,
        "high_count": high_count,
        "affected_rows": affected_rows,
        "recommended_next_action": next_action,
        "manual_legacy_fields_overwritten": False,
    }


def execute_audit(
    config: dict[str, Any],
    *,
    source: str,
    target: str,
    dry_run: bool,
    limit: int | None,
    fail_on: str,
) -> dict[str, Any]:
    if source == "live":
        _live_guard()
    if source != "fixture":
        raise AuditError(f"Unsupported source: {source}")

    timestamp = _utc_now()
    rows = _load_fixture_rows(config, limit)
    audits: list[RecordAudit] = []
    for target_name in _resolve_targets(target):
        for row in rows.get(target_name, []):
            audits.append(audit_record(target_name, row, config, timestamp))

    summary = build_summary(source, target, audits, timestamp, dry_run, fail_on)
    findings = [asdict(finding) for audit in audits for finding in audit.findings]
    records = [
        {
            "target": audit.target,
            "row_name": audit.row_name,
            "status": audit.status,
            "generated_fields": audit.generated_fields,
            "mismatch_fields": audit.mismatch_fields,
            "preserved_legacy_fields": audit.preserved_legacy_fields,
            "findings": [asdict(finding) for finding in audit.findings],
        }
        for audit in audits
    ]
    return {"summary": summary, "records": records, "findings": findings}


def _should_fail(report: dict[str, Any], fail_on: str) -> bool:
    threshold = FAIL_ON_THRESHOLD[fail_on]
    if threshold == 0:
        return False
    highest = 0
    for finding in report.get("findings") or []:
        highest = max(highest, _severity_value(str(finding.get("severity") or "")))
    return highest >= threshold


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# BOSMAX Notion Wiring Audit",
        "",
        f"- Execution timestamp: {summary['execution_timestamp']}",
        f"- Source mode: {summary['source_mode']}",
        f"- Target: {summary['target']}",
        f"- Total records checked: {summary['total_records_checked']}",
        f"- Pass count: {summary['pass_count']}",
        f"- Mismatch count: {summary['mismatch_count']}",
        f"- Critical count: {summary['critical_count']}",
        f"- High count: {summary['high_count']}",
        f"- Affected rows: {', '.join(summary['affected_rows']) if summary['affected_rows'] else 'None'}",
        f"- Recommended next action: {summary['recommended_next_action']}",
        "- Manual legacy fields were not overwritten: YES",
        "",
        "## Findings",
    ]
    findings = report.get("findings") or []
    if not findings:
        lines.append("- None")
    else:
        for finding in findings:
            lines.append(f"[{str(finding['severity']).upper()}] {finding['row_name']} — {finding['title']}")
            lines.append(f"Reason: {finding['reason']}")
            lines.append(f"Action: {finding['action']}")
            lines.append("")
    lines.append("## Record Outputs")
    for record in report.get("records") or []:
        lines.append(f"### {record['target'].upper()} :: {record['row_name']}")
        lines.append(f"- Status: {record['status']}")
        lines.append(f"- Mismatch fields: {json.dumps(record['mismatch_fields'], ensure_ascii=False)}")
        lines.append(f"- Generated fields: {json.dumps(record['generated_fields'], ensure_ascii=False)}")
        lines.append(f"- Preserved legacy fields: {json.dumps(record['preserved_legacy_fields'], ensure_ascii=False)}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False) + "\n"


def write_output(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dry-run BOSMAX Notion wiring validator/generator without overwriting legacy manual fields."
    )
    parser.add_argument("--source", choices=("fixture", "live"), default="fixture")
    parser.add_argument("--target", choices=("avatar", "hybrid", "frames", "ingredients", "all"), default="all")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--output")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--fail-on", choices=("critical", "high", "any", "none"), default="critical")
    parser.add_argument("--config", default=str(CONFIG_PATH))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = _read_yaml(Path(args.config))
    report = execute_audit(
        config,
        source=args.source,
        target=args.target,
        dry_run=bool(args.dry_run),
        limit=args.limit,
        fail_on=args.fail_on,
    )
    content = render_markdown(report) if args.format == "markdown" else render_json(report)
    if args.output:
        write_output(Path(args.output), content)
    else:
        print(content, end="")
    return 1 if _should_fail(report, args.fail_on) else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc
