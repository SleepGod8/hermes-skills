"""Regression tests for persona-distillation local OCR V4.1."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "ocr_extract.py"
WORK = Path(r"E:/Hermes workspace")
PDF = WORK / "ocr-engine-test-scanned.pdf"
JSON_OUT = WORK / "ocr-regression-output.json"
MD_OUT = WORK / "ocr-regression-report.md"


def main() -> int:
    assert PDF.is_file(), f"missing fixed fixture: {PDF}"
    subprocess.run([sys.executable, str(SCRIPT), str(PDF), "--json-output", str(JSON_OUT), "--markdown-output", str(MD_OUT)], check=True)
    payload = json.loads(JSON_OUT.read_text(encoding="utf-8"))
    report = MD_OUT.read_text(encoding="utf-8")
    assert payload["skill_version"] == "0.5.0"
    assert payload["protocol_version"] == "V4.1"
    assert payload["report_schema"] == "ocr-report-v1"
    assert len(payload["records"]) == 1
    record = payload["records"][0]
    assert record["source_id"] == "PDF-001-P001"
    assert record["text_layer"] is False
    assert record["ocr_engine"] == "tesseract"
    assert record["status"] == "success"
    assert record["confidence_score"] > 0
    normalized = record["text"].replace(" ", "")
    assert "扫描PDF端到端测试" in normalized
    assert "LOCALOCRTEST789" in normalized
    assert "## OCR/文档来源报告" in report
    assert "## 提取结果摘要" in report
    assert "## OCR/隐私风险" in report
    print("persona-distillation OCR regression: PASS")
    print(f"fixture: {PDF}")
    print(f"json: {JSON_OUT}")
    print(f"markdown: {MD_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
