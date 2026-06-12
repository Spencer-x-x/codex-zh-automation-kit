---
name: report-to-xlsx
description: 将符合项目日报接口的 JSON 转换为无需第三方依赖的 XLSX 工作簿。用于用户要求 Excel 交付、日报表格化、来源清单或访问异常清单时。
---

# 日报导出 Excel

输入必须先通过日报校验：

```bash
python3 scripts/validate_report.py <report.json>
```

然后执行：

```bash
python3 scripts/report_to_xlsx.py <report.json> <report.xlsx>
```

## 工作簿结构

- `摘要`: 生成时间、标题和摘要。
- `条目`: 标题、摘要、来源 URL 和发布时间。
- `访问异常`: 来源 URL 和失败原因。

## 交付检查

1. 保留全部来源链接和访问异常。
2. 不把无法核验的来源混入正常条目。
3. 导出后运行 `python3 -m zipfile -t <report.xlsx>`。
4. 仅在校验成功后交付文件。

