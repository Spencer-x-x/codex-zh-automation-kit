---
name: source-backed-daily-brief
description: 生成可追溯来源的中文日报 JSON，并记录来源访问失败。用于新闻简报、官方更新汇总、周期性研究或任何要求来源链接、发布时间和降级说明的报告任务。
---

# 来源化中文日报

生成包含以下顶层字段的 JSON：

- `generated_at`: 带时区的 ISO 8601 生成时间。
- `title`: 日报标题。
- `summary`: 简明总览。
- `items`: 已核验条目数组。
- `access_issues`: 无法访问或无法核验的来源数组。

每个 `items` 条目必须包含 `title`、`summary`、`source_url` 和
`published_at`。每个 `access_issues` 条目必须包含 `source_url` 和
`reason`。

## 工作流

1. 优先检查官方博客、官方文档、GitHub 发布页和论文原文。
2. 区分页面发布时间与事件发生时间，不确定时在摘要中说明。
3. 仅将已打开并核验的来源写入 `items`。
4. 将超时、登录限制、地区限制或缺少发布日期写入
   `access_issues`，不要静默删除。
5. 不得用推测补齐缺失事实。
6. 保存 JSON 后运行：

```bash
python3 scripts/validate_report.py <report.json>
```

7. 修复结构错误后再交付或传给 Excel 导出技能。

