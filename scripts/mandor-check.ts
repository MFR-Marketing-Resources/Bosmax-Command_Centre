import { spawnSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

function fail(message: string): never {
	console.error(`MANDOR FAIL: ${message}`);
	process.exit(1);
}

function runPythonValidator(args: string[]): void {
	const result = spawnSync("python", args, {
		cwd: ROOT,
		encoding: "utf-8",
		stdio: "inherit",
	});
	if (result.status !== 0) {
		fail(`Validator failed: python ${args.join(" ")}`);
	}
}

const ROOT = resolve(__dirname, "..");
const moduleStatusPath = resolve(ROOT, "docs", "MODULE_STATUS.yaml");

if (!existsSync(moduleStatusPath)) {
	fail("docs/MODULE_STATUS.yaml missing");
}

const moduleStatusText = readFileSync(moduleStatusPath, "utf-8");
if (
	!moduleStatusText.includes("bosmax_command_centre_repository_governance:")
) {
	fail("bosmax_command_centre_repository_governance domain missing");
}
if (!moduleStatusText.includes("status: IN_PROGRESS")) {
	fail("bosmax_command_centre_repository_governance must remain IN_PROGRESS");
}

const requiredFiles = [
	"README.md",
	"AGENTS.md",
	"SKILLS.md",
	"CHANGELOG.md",
	"docs/PROJECT_OVERVIEW.md",
	"docs/FILE_REGISTER.md",
	"docs/QA_CHECKLIST.md",
	"docs/RELEASE_PROCESS.md",
	"docs/CUSTOM_GPT_DEPLOYMENT.md",
	"docs/PROMPT_COMPILER_CONTRACT.md",
	"scripts/validate_bosmax_pack.py",
	"scripts/validate_bosmax_pack.ps1",
	"knowledge-pack/templates/VIDEO_PROMPT_COMPILER_TEMPLATES.yaml",
	"knowledge-pack/manifests/BOSMAX_FINAL_11_FILE_MANIFEST.csv",
];

for (const relativePath of requiredFiles) {
	if (!existsSync(resolve(ROOT, relativePath))) {
		fail(`Required governance artifact missing: ${relativePath}`);
	}
}

runPythonValidator(["scripts/validate_bosmax_pack.py"]);

console.log("MANDOR CHECK PASSED: bosmax_command_centre_repository_governance");
