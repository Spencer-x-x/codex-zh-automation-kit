import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.removesuffix(".py"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ProjectStructureTests(unittest.TestCase):
    def test_plugin_manifest_declares_release_metadata(self):
        manifest_path = ROOT / ".codex-plugin" / "plugin.json"
        self.assertTrue(manifest_path.exists(), "plugin.json 必须存在")

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        self.assertEqual("codex-zh-automation-kit", manifest["name"])
        self.assertEqual("0.1.0", manifest["version"])
        self.assertEqual("MIT", manifest["license"])
        self.assertEqual("./skills/", manifest["skills"])
        self.assertEqual(
            "https://github.com/Spencer-x-x/codex-zh-automation-kit",
            manifest["repository"],
        )

    def test_three_skills_have_frontmatter_and_agent_metadata(self):
        skill_names = {
            "automation-builder-zh",
            "source-backed-daily-brief",
            "report-to-xlsx",
        }

        self.assertEqual(
            skill_names,
            {
                path.name
                for path in (ROOT / "skills").iterdir()
                if path.is_dir()
            },
        )
        for skill_name in skill_names:
            skill_path = ROOT / "skills" / skill_name
            skill_text = (skill_path / "SKILL.md").read_text(encoding="utf-8")
            self.assertTrue(skill_text.startswith("---\n"))
            self.assertIn(f"name: {skill_name}", skill_text)
            self.assertTrue((skill_path / "agents" / "openai.yaml").exists())

    def test_examples_pass_public_validators(self):
        config_validator = load_script("validate_config.py")
        report_validator = load_script("validate_report.py")
        config = json.loads(
            (ROOT / "examples" / "automation.json").read_text(encoding="utf-8")
        )
        report = json.loads(
            (ROOT / "examples" / "daily-brief.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual([], config_validator.validate_config(config))
        self.assertEqual([], report_validator.validate_report(report))

    def test_repository_has_required_maintenance_files(self):
        required_paths = [
            "README.md",
            "README.en.md",
            "LICENSE",
            "CONTRIBUTING.md",
            "SECURITY.md",
            "CHANGELOG.md",
            ".github/workflows/ci.yml",
            ".github/ISSUE_TEMPLATE/bug_report.yml",
            ".github/ISSUE_TEMPLATE/feature_request.yml",
        ]

        for relative_path in required_paths:
            self.assertTrue(
                (ROOT / relative_path).exists(),
                f"{relative_path} 必须存在",
            )


if __name__ == "__main__":
    unittest.main()
