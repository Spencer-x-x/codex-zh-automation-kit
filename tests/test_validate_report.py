import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_validator():
    path = ROOT / "scripts" / "validate_report.py"
    if not path.exists():
        raise AssertionError("scripts/validate_report.py has not been implemented")
    spec = importlib.util.spec_from_file_location("validate_report", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ValidateReportTests(unittest.TestCase):
    def test_accepts_report_with_sources_and_access_issues(self):
        validator = load_validator()
        report = {
            "generated_at": "2026-06-12T09:00:00+08:00",
            "title": "每日 AI 简报",
            "summary": "OpenAI 发布了新的开发者更新。",
            "items": [
                {
                    "title": "开发者更新",
                    "summary": "更新了 API 文档。",
                    "source_url": "https://openai.com/news/",
                    "published_at": "2026-06-11T12:00:00Z",
                }
            ],
            "access_issues": [
                {
                    "source_url": "https://example.com/feed",
                    "reason": "访问超时",
                }
            ],
        }

        self.assertEqual([], validator.validate_report(report))

    def test_rejects_item_without_source(self):
        validator = load_validator()
        report = {
            "generated_at": "2026-06-12T09:00:00+08:00",
            "title": "每日简报",
            "summary": "摘要",
            "items": [{"title": "无来源条目", "summary": "内容"}],
            "access_issues": [],
        }

        errors = validator.validate_report(report)

        self.assertIn("items[0].source_url 必须是 http 或 https URL", errors)

    def test_rejects_missing_access_issue_reason(self):
        validator = load_validator()
        report = {
            "generated_at": "2026-06-12T09:00:00+08:00",
            "title": "每日简报",
            "summary": "摘要",
            "items": [],
            "access_issues": [{"source_url": "https://example.com"}],
        }

        errors = validator.validate_report(report)

        self.assertIn("access_issues[0].reason 必须是非空字符串", errors)

    def test_rejects_invalid_iso_timestamps(self):
        validator = load_validator()
        report = {
            "generated_at": "今天早上",
            "title": "每日简报",
            "summary": "摘要",
            "items": [
                {
                    "title": "条目",
                    "summary": "内容",
                    "source_url": "https://example.com",
                    "published_at": "昨天",
                }
            ],
            "access_issues": [],
        }

        errors = validator.validate_report(report)

        self.assertIn("generated_at 必须是 ISO 8601 时间", errors)
        self.assertIn("items[0].published_at 必须是 ISO 8601 时间", errors)


if __name__ == "__main__":
    unittest.main()
