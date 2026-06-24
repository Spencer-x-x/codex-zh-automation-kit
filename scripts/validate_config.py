#!/usr/bin/env python3
"""Validate Codex Chinese automation configuration JSON."""

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


REQUIRED_FIELDS = (
    "name",
    "schedule",
    "timezone",
    "task",
    "sources",
    "output",
    "fallback",
)
CRON_TOKEN_RE = re.compile(r"^[0-9*,\-/]+$")


def _is_non_empty_string(value):
    return isinstance(value, str) and bool(value.strip())


def _is_http_url(value):
    if not _is_non_empty_string(value):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def validate_config(config):
    errors = []
    if not isinstance(config, dict):
        return ["配置根节点必须是 JSON 对象"]

    for field in REQUIRED_FIELDS:
        if field not in config:
            errors.append(f"缺少必填字段: {field}")

    for field in ("name", "schedule", "timezone", "task", "fallback"):
        if field in config and not _is_non_empty_string(config[field]):
            errors.append(f"{field} 必须是非空字符串")

    schedule = config.get("schedule")
    if _is_non_empty_string(schedule):
        schedule_parts = schedule.split()
        if len(schedule_parts) != 5:
            errors.append("schedule 必须是五段 cron 表达式")
        elif any(not CRON_TOKEN_RE.match(part) for part in schedule_parts):
            errors.append("schedule 只能包含数字、星号、逗号、连字符和斜杠")

    timezone = config.get("timezone")
    if _is_non_empty_string(timezone):
        try:
            ZoneInfo(timezone)
        except (ZoneInfoNotFoundError, ValueError):
            errors.append("timezone 必须是有效的 IANA 时区")

    sources = config.get("sources")
    if sources is not None:
        if not isinstance(sources, list) or not sources:
            errors.append("sources 必须是非空数组")
        elif isinstance(sources, list):
            for index, source in enumerate(sources):
                if not _is_http_url(source):
                    errors.append(
                        f"sources[{index}] 必须是 http 或 https URL"
                    )

    output = config.get("output")
    if output is not None:
        if not isinstance(output, dict):
            errors.append("output 必须是 JSON 对象")
        else:
            if output.get("format") not in {"json", "xlsx"}:
                errors.append("output.format 必须是 json 或 xlsx")
            if not _is_non_empty_string(output.get("path")):
                errors.append("output.path 必须是非空字符串")

    return errors


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("用法: validate_config.py <config.json>", file=sys.stderr)
        return 2

    path = Path(argv[0])
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"无法读取配置: {exc}", file=sys.stderr)
        return 2

    errors = validate_config(config)
    if errors:
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("配置有效")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
