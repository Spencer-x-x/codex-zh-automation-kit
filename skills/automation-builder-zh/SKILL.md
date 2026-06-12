---
name: automation-builder-zh
description: 将中文自然语言需求整理为可校验的 Codex 自动化 JSON 配置。用于用户提出定时任务、周期性采集、日报生成或需要明确时区、来源、输出和失败回退策略时。
---

# 中文自动化配置

把用户需求转换为一个 JSON 对象，只使用以下顶层字段：

- `name`: 自动化名称。
- `schedule`: 五段 cron 表达式。
- `timezone`: IANA 时区，例如 `Asia/Shanghai`。
- `task`: 清晰、可独立执行的任务说明。
- `sources`: 一个或多个 `http` 或 `https` 来源 URL。
- `output`: 包含 `format` 和 `path`；格式只能是 `json` 或 `xlsx`。
- `fallback`: 来源失败或数据不足时的明确处理方式。

## 工作流

1. 从用户原话提取执行频率、时区、任务、来源和交付格式。
2. 缺少时区时明确询问；不得静默猜测用户时区。
3. 缺少来源时使用用户指定主题的官方来源，不得虚构 URL。
4. 将失败行为写入 `fallback`，要求保留访问异常并继续处理可用来源。
5. 保存 JSON 后运行：

```bash
python3 scripts/validate_config.py <config.json>
```

6. 修复所有错误后再交付配置。

## 输出要求

只生成合法 JSON，不添加注释。不得加入未定义的敏感凭据字段。

