#!/usr/bin/env python3
"""Validate a source-backed daily brief JSON file."""

import json
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


REQUIRED_FIELDS = (
    "generated_at",
    "title",
    "summary",
    "items",
    "access_issues",
)


def _is_non_empty_string(value):
    return isinstance(value, str) and bool(value.strip())


def _is_http_url(value):
    if not _is_non_empty_string(value):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _is_iso8601(value, require_timezone=False):
    if not _is_non_empty_string(value):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return not require_timezone or parsed.tzinfo is not None


def validate_report(report):
    errors = []
    if not isinstance(report, dict):
        return ["日报根节点必须是 JSON 对象"]

    for field in REQUIRED_FIELDS:
        if field not in report:
            errors.append(f"缺少必填字段: {field}")

    for field in ("generated_at", "title", "summary"):
        if field in report and not _is_non_empty_string(report[field]):
            errors.append(f"{field} 必须是非空字符串")

    generated_at = report.get("generated_at")
    if _is_non_empty_string(generated_at) and not _is_iso8601(
        generated_at, require_timezone=True
    ):
        errors.append("generated_at 必须是 ISO 8601 时间")

    items = report.get("items")
    if items is not None:
        if not isinstance(items, list):
            errors.append("items 必须是数组")
        else:
            for index, item in enumerate(items):
                if not isinstance(item, dict):
                    errors.append(f"items[{index}] 必须是 JSON 对象")
                    continue
                for field in ("title", "summary", "published_at"):
                    if not _is_non_empty_string(item.get(field)):
                        errors.append(
                            f"items[{index}].{field} 必须是非空字符串"
                        )
                published_at = item.get("published_at")
                if _is_non_empty_string(
                    published_at
                ) and not _is_iso8601(published_at):
                    errors.append(
                        f"items[{index}].published_at 必须是 ISO 8601 时间"
                    )
                if not _is_http_url(item.get("source_url")):
                    errors.append(
                        f"items[{index}].source_url 必须是 http 或 https URL"
                    )

    access_issues = report.get("access_issues")
    if access_issues is not None:
        if not isinstance(access_issues, list):
            errors.append("access_issues 必须是数组")
        else:
            for index, issue in enumerate(access_issues):
                if not isinstance(issue, dict):
                    errors.append(
                        f"access_issues[{index}] 必须是 JSON 对象"
                    )
                    continue
                if not _is_http_url(issue.get("source_url")):
                    errors.append(
                        "access_issues"
                        f"[{index}].source_url 必须是 http 或 https URL"
                    )
                if not _is_non_empty_string(issue.get("reason")):
                    errors.append(
                        f"access_issues[{index}].reason 必须是非空字符串"
                    )

    return errors


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("用法: validate_report.py <report.json>", file=sys.stderr)
        return 2

    path = Path(argv[0])
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"无法读取日报: {exc}", file=sys.stderr)
        return 2

    errors = validate_report(report)
    if errors:
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("日报有效")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
