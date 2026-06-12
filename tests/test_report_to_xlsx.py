import importlib.util
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NS = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL_NS = {
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships"
}


def load_exporter():
    path = ROOT / "scripts" / "report_to_xlsx.py"
    if not path.exists():
        raise AssertionError("scripts/report_to_xlsx.py has not been implemented")
    spec = importlib.util.spec_from_file_location("report_to_xlsx", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sample_report():
    return {
        "generated_at": "2026-06-12T09:00:00+08:00",
        "title": "每日 AI 简报",
        "summary": "包含 <XML> 与 & 符号的摘要。",
        "items": [
            {
                "title": "OpenAI 更新",
                "summary": "发布新的开发者文档。",
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


class ReportToXlsxTests(unittest.TestCase):
    def test_exports_valid_workbook_with_three_named_sheets(self):
        exporter = load_exporter()
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "report.xlsx"

            exporter.export_report(sample_report(), output)

            self.assertTrue(zipfile.is_zipfile(output))
            with zipfile.ZipFile(output) as archive:
                workbook = ET.fromstring(archive.read("xl/workbook.xml"))
                names = [
                    sheet.attrib["name"]
                    for sheet in workbook.findall("main:sheets/main:sheet", NS)
                ]
                self.assertEqual(["摘要", "条目", "访问异常"], names)
                self.assertIsNone(archive.testzip())

    def test_preserves_chinese_text_urls_and_xml_characters(self):
        exporter = load_exporter()
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "report.xlsx"

            exporter.export_report(sample_report(), output)

            with zipfile.ZipFile(output) as archive:
                worksheet_xml = "".join(
                    archive.read(f"xl/worksheets/sheet{index}.xml").decode("utf-8")
                    for index in range(1, 4)
                )
                self.assertIn("每日 AI 简报", worksheet_xml)
                self.assertIn("包含 &lt;XML&gt; 与 &amp; 符号的摘要。", worksheet_xml)
                self.assertIn("https://openai.com/news/", worksheet_xml)
                self.assertIn("访问超时", worksheet_xml)

    def test_rejects_invalid_report_before_writing(self):
        exporter = load_exporter()
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "report.xlsx"

            with self.assertRaisesRegex(ValueError, "日报结构无效"):
                exporter.export_report({"title": "缺少字段"}, output)

            self.assertFalse(output.exists())

    def test_removes_xml_forbidden_control_characters(self):
        exporter = load_exporter()
        report = sample_report()
        report["summary"] = "正常文本\x00继续"
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "report.xlsx"

            exporter.export_report(report, output)

            with zipfile.ZipFile(output) as archive:
                sheet = archive.read("xl/worksheets/sheet1.xml")
                parsed = ET.fromstring(sheet)
                text = "".join(parsed.itertext())
                self.assertIn("正常文本继续", text)

    def test_declares_normal_default_style(self):
        exporter = load_exporter()
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "report.xlsx"

            exporter.export_report(sample_report(), output)

            with zipfile.ZipFile(output) as archive:
                styles = ET.fromstring(archive.read("xl/styles.xml"))
                normal = styles.find(
                    "main:cellStyles/main:cellStyle[@name='Normal']", NS
                )
                self.assertIsNotNone(normal)


if __name__ == "__main__":
    unittest.main()
