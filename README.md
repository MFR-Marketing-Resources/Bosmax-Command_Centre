# Bosmax Command Centre

Repo: `MFR-Marketing-Resources/Bosmax-Command_Centre`

Bosmax Command Centre is the GitHub source-of-truth control layer for the retained BOSMAX Custom GPT knowledge pack. This repository is the audit, version-control, QA, and release-governance surface for the retained package without rewriting approved business content.

## Runtime Distinction

- GitHub: master source, version control, audit trail, QA gate, and release governance.
- Custom GPT: runtime assistant and operator-facing execution interface.
- Notion: downstream operator database and UI layer.
- Codex: audit, repair, validation, PR proof, merge, and post-merge validation engine.

## Repository Structure

```text
.
├── README.md
├── AGENTS.md
├── SKILLS.md
├── CHANGELOG.md
├── docs/
├── knowledge-pack/
├── scripts/
├── package.json
└── .github/
```

## Knowledge-Pack Boundary

`knowledge-pack/` contains retained production assets only. Those files are governed under canonical paths and should not be casually edited. Any content repair must be separately scoped, validated, and reviewed through branch and PR.

## Validate

From the repo root:

```powershell
.\scripts\validate_bosmax_pack.ps1
```

Mandatory local repo gates for this repository are:

```powershell
npx @biomejs/biome check --write .
npx depcruise scripts --no-config --output-type err
npx tsx scripts/mandor-check.ts
```

## Release To Custom GPT

1. Branch from `main`.
2. Limit edits to approved repo-governance and retained-package surfaces.
3. Run the local validation gates.
4. Commit and open a PR with proof.
5. Merge after review.
6. Upload only the reviewed retained-package files from `knowledge-pack/` to the Custom GPT release bundle.

## Current Retained Package Status

- Current retained package resolves to 10 canonical files.
- `BOSMAX_FINAL_11_FILE_MANIFEST.csv` still uses an `11` filename label.
- The manifest content currently lists 10 rows, including the manifest itself as `SELF_REFERENCE_NOT_HASHED`.
- `VIDEO_PROMPT_COMPILER_TEMPLATES.yaml` required syntax-only scalar quoting to satisfy strict YAML parsing.
- The retained manifest has been refreshed to match the current repository-retained bytes for the three drifted files while keeping the historical `11` filename label intact.
- `knowledge-pack/wps/WPS_Blocking_Template_REPAIRED.xlsx` is retained as a non-macro `.xlsx` workbook. No embedded `vbaProject.bin` payload is present, so macro execution is treated as `NOT APPLICABLE` for this retained package.

## Warning

Do not casually edit copywriting, hooks, dialogue, CTA text, product truth, avatar descriptions, workbook contents, or commercial claims from this repository. Use a scoped branch, validator proof, PR review, and post-merge validation for every change.
