# Codex 中文自动化工具包

一个面向中文用户的开源 Codex 插件，把自然语言自动化需求连接到可校验配置、来源化日报和 Excel 交付。

[English](README.en.md)

## 功能

- `automation-builder-zh`：把中文定时任务需求转换为固定 JSON 接口。
- `source-backed-daily-brief`：生成包含来源、发布时间和访问异常的日报。
- `report-to-xlsx`：使用 Python 标准库将日报导出为 `.xlsx`。

项目不包含网络爬虫、账号凭据或虚构数据。来源采集由 Codex 使用可用工具完成，脚本负责确定性的结构校验和文件导出。

## 要求

- Codex 插件环境
- Python 3.9 或更高版本
- 无第三方 Python 运行时依赖

## 快速开始

克隆仓库后，在仓库根目录运行：

```bash
python3 scripts/validate_config.py examples/automation.json
python3 scripts/validate_report.py examples/daily-brief.json
python3 scripts/report_to_xlsx.py examples/daily-brief.json outputs/demo.xlsx
python3 -m zipfile -t outputs/demo.xlsx
```

将此仓库作为本地 Codex 插件源加载后，可以直接调用：

```text
$automation-builder-zh
$source-backed-daily-brief
$report-to-xlsx
```

## 固定接口

自动化配置顶层字段：

```text
name, schedule, timezone, task, sources, output, fallback
```

日报顶层字段：

```text
generated_at, title, summary, items, access_issues
```

完整示例位于 [`examples/`](examples/)。

## 测试

```bash
python3 -m unittest discover -s tests -v
```

## 维护原则

- 只记录真实的使用、问题、PR、星标和下载。
- 无法访问的来源必须进入 `access_issues`。
- 新行为先写测试，再实现。
- 发布变更记录在 [`CHANGELOG.md`](CHANGELOG.md)。

## 许可证

[MIT](LICENSE)

