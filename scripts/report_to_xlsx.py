#!/usr/bin/env python3
"""Export a validated source-backed daily brief to an XLSX workbook."""

import importlib.util
import json
import sys
import zipfile
from html import escape
from pathlib import Path


def _load_report_validator():
    validator_path = Path(__file__).with_name("validate_report.py")
    spec = importlib.util.spec_from_file_location(
        "codex_zh_validate_report", validator_path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate_report


def _column_name(index):
    name = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        name = chr(65 + remainder) + name
    return name


def _xml_safe_text(value):
    return "".join(
        character
        for character in str(value)
        if character in "\t\n\r"
        or 0x20 <= ord(character) <= 0xD7FF
        or 0xE000 <= ord(character) <= 0xFFFD
        or 0x10000 <= ord(character) <= 0x10FFFF
    )


def _cell(reference, value, style=0):
    text = escape(_xml_safe_text(value), quote=False)
    style_attr = f' s="{style}"' if style else ""
    return (
        f'<c r="{reference}" t="inlineStr"{style_attr}>'
        f'<is><t xml:space="preserve">{text}</t></is></c>'
    )


def _worksheet(rows, widths):
    row_xml = []
    for row_index, row in enumerate(rows, start=1):
        cells = []
        for column_index, value in enumerate(row, start=1):
            reference = f"{_column_name(column_index)}{row_index}"
            cells.append(_cell(reference, value, style=1 if row_index == 1 else 0))
        row_xml.append(f'<row r="{row_index}">{"".join(cells)}</row>')

    columns = "".join(
        f'<col min="{index}" max="{index}" width="{width}" customWidth="1"/>'
        for index, width in enumerate(widths, start=1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/'
        'spreadsheetml/2006/main">'
        f"<cols>{columns}</cols>"
        f'<sheetData>{"".join(row_xml)}</sheetData>'
        "</worksheet>"
    )


def _workbook_files(report):
    summary_rows = [
        ["字段", "内容"],
        ["生成时间", report["generated_at"]],
        ["标题", report["title"]],
        ["摘要", report["summary"]],
    ]
    item_rows = [["标题", "摘要", "来源 URL", "发布时间"]]
    item_rows.extend(
        [
            item["title"],
            item["summary"],
            item["source_url"],
            item["published_at"],
        ]
        for item in report["items"]
    )
    issue_rows = [["来源 URL", "失败原因"]]
    issue_rows.extend(
        [issue["source_url"], issue["reason"]]
        for issue in report["access_issues"]
    )

    content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/worksheets/sheet3.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>"""
    root_relationships = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>"""
    workbook = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>
    <sheet name="摘要" sheetId="1" r:id="rId1"/>
    <sheet name="条目" sheetId="2" r:id="rId2"/>
    <sheet name="访问异常" sheetId="3" r:id="rId3"/>
  </sheets>
</workbook>"""
    workbook_relationships = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet3.xml"/>
  <Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>"""
    styles = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="2">
    <font><sz val="11"/><name val="Arial"/></font>
    <font><b/><sz val="11"/><name val="Arial"/></font>
  </fonts>
  <fills count="2">
    <fill><patternFill patternType="none"/></fill>
    <fill><patternFill patternType="gray125"/></fill>
  </fills>
  <borders count="1"><border/></borders>
  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
  <cellXfs count="2">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
    <xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/>
  </cellXfs>
  <cellStyles count="1">
    <cellStyle name="Normal" xfId="0" builtinId="0"/>
  </cellStyles>
</styleSheet>"""

    return {
        "[Content_Types].xml": content_types,
        "_rels/.rels": root_relationships,
        "xl/workbook.xml": workbook,
        "xl/_rels/workbook.xml.rels": workbook_relationships,
        "xl/styles.xml": styles,
        "xl/worksheets/sheet1.xml": _worksheet(summary_rows, [16, 80]),
        "xl/worksheets/sheet2.xml": _worksheet(
            item_rows, [28, 70, 55, 26]
        ),
        "xl/worksheets/sheet3.xml": _worksheet(issue_rows, [55, 50]),
    }


def export_report(report, output_path):
    errors = _load_report_validator()(report)
    if errors:
        raise ValueError("日报结构无效: " + "; ".join(errors))

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
        output_path, "w", compression=zipfile.ZIP_DEFLATED
    ) as archive:
        for name, content in _workbook_files(report).items():
            archive.writestr(name, content.encode("utf-8"))


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        print(
            "用法: report_to_xlsx.py <report.json> <report.xlsx>",
            file=sys.stderr,
        )
        return 2

    input_path, output_path = map(Path, argv)
    try:
        report = json.loads(input_path.read_text(encoding="utf-8"))
        export_report(report, output_path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"导出失败: {exc}", file=sys.stderr)
        return 1

    print(f"已生成: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
