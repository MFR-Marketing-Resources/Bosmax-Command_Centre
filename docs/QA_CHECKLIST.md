# QA Checklist

## Pre-Commit

- Confirm all retained files are present under canonical paths.
- Confirm no business-copy rewrite occurred.
- Run `.\scripts\validate_bosmax_pack.ps1`.
- Review JSON, YAML, CSV, and XLSX validation output.
- Review manifest SHA256 comparisons.
- Review the retained-package count note.
- Confirm the macro status line is structurally correct:
  - `NOT APPLICABLE` for a non-macro `.xlsx` package with no embedded VBA payload.
  - `NOT VERIFIED` only if a macro-capable workbook is actually retained.
- Review `git status --short` and `git diff --stat`.

## Pre-Release

- Confirm PR body includes validation proof and known gaps.
- Confirm any YAML repair is syntax-only and line-specific.
- Confirm no direct push to `master`.
- Confirm merge approval is complete.
- Confirm only reviewed retained-package assets are used for the Custom GPT upload.
