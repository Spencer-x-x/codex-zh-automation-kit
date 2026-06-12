import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_validator():
    path = ROOT / "scripts" / "validate_config.py"
    if not path.exists():
        raise AssertionError("scripts/validate_config.py has not been implemented")
    spec = importlib.util.spec_from_file_location("validate_config", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ValidateConfigTests(unittest.TestCase):
    def test_accepts_complete_automation_config(self):
        validator = load_validator()
        config = {
            "name": "每日 AI 简报",
            "schedule": "0 9 * * *",
            "timezone": "Asia/Shanghai",
            "task": "汇总过去 24 小时的 AI 官方动态",
            "sources": ["https://openai.com/news/", "https://github.com/openai"],
            "output": {"format": "xlsx", "path": "reports/ai-daily.xlsx"},
            "fallback": "记录访问失败并继续生成可用内容",
        }

        self.assertEqual([], validator.validate_config(config))

    def test_rejects_missing_required_fields(self):
        validator = load_validator()

        errors = validator.validate_config({"name": "不完整配置"})

        self.assertIn("缺少必填字段: schedule", errors)
        self.assertIn("缺少必填字段: timezone", errors)
        self.assertIn("缺少必填字段: sources", errors)

    def test_rejects_non_http_sources(self):
        validator = load_validator()
        config = {
            "name": "每日简报",
            "schedule": "0 9 * * *",
            "timezone": "Asia/Shanghai",
            "task": "生成简报",
            "sources": ["ftp://example.com/data", "not-a-url"],
            "output": {"format": "json", "path": "report.json"},
            "fallback": "记录失败",
        }

        errors = validator.validate_config(config)

        self.assertIn("sources[0] 必须是 http 或 https URL", errors)
        self.assertIn("sources[1] 必须是 http 或 https URL", errors)

    def test_rejects_invalid_output_shape(self):
        validator = load_validator()
        config = {
            "name": "每日简报",
            "schedule": "0 9 * * *",
            "timezone": "Asia/Shanghai",
            "task": "生成简报",
            "sources": ["https://example.com"],
            "output": {"format": "pdf"},
            "fallback": "记录失败",
        }

        errors = validator.validate_config(config)

        self.assertIn("output.format 必须是 json 或 xlsx", errors)
        self.assertIn("output.path 必须是非空字符串", errors)

    def test_rejects_non_five_field_schedule(self):
        validator = load_validator()
        config = {
            "name": "每日简报",
            "schedule": "0 9 * *",
            "timezone": "Asia/Shanghai",
            "task": "生成简报",
            "sources": ["https://example.com"],
            "output": {"format": "json", "path": "report.json"},
            "fallback": "记录失败",
        }

        errors = validator.validate_config(config)

        self.assertIn("schedule 必须是五段 cron 表达式", errors)

    def test_rejects_unknown_timezone(self):
        validator = load_validator()
        config = {
            "name": "每日简报",
            "schedule": "0 9 * * *",
            "timezone": "Mars/Olympus",
            "task": "生成简报",
            "sources": ["https://example.com"],
            "output": {"format": "json", "path": "report.json"},
            "fallback": "记录失败",
        }

        errors = validator.validate_config(config)

        self.assertIn("timezone 必须是有效的 IANA 时区", errors)


if __name__ == "__main__":
    unittest.main()
