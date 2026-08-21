"""Local OCR extractor and V4.1 report generator.

Only processes one explicitly supplied image/PDF. Uses local Tesseract on E:.
Outputs a stable JSON schema and the fixed Markdown report.
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
from pathlib import Path
from typing import Any

import pymupdf
import pytesseract
from PIL import Image

SKILL_VERSION = "0.5.0"
PROTOCOL_VERSION = "V4.1"
REPORT_SCHEMA = "ocr-report-v1"
TESSERACT_CMD = Path(r"E:/Tesseract-OCR/tesseract.exe")
TESSDATA_DIR = TESSERACT_CMD.parent / "tessdata"
DEFAULT_LANG = "chi_sim+eng"
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE_RE = re.compile(r"(?<!\d)(?:\+?86[- ]?)?1[3-9]\d{9}(?!\d)")
TOKEN_RE = re.compile(r"\b(?:sk|pk|ghp|github_pat|xox[baprs]-)[A-Za-z0-9_\-]{8,}\b", re.I)
COOKIE_RE = re.compile(r"\b(?:session|sessionid|sid|token|authorization)\s*[=:]\s*[^\s;]{8,}", re.I)


def configure_tesseract() -> None:
    if not TESSERACT_CMD.is_file():
        raise FileNotFoundError(f"Tesseract not found: {TESSERACT_CMD}")
    if not (TESSDATA_DIR / "chi_sim.traineddata").is_file():
        raise FileNotFoundError(f"Chinese language data not found: {TESSDATA_DIR / 'chi_sim.traineddata'}")
    pytesseract.pytesseract.tesseract_cmd = str(TESSERACT_CMD)
    pytesseract.pytesseract.tesseract_env = {"TESSDATA_PREFIX": str(TESSDATA_DIR)}


def sensitive_fields(text: str) -> list[str]:
    found: list[str] = []
    if EMAIL_RE.search(text): found.append("email")
    if PHONE_RE.search(text): found.append("phone")
    if TOKEN_RE.search(text): found.append("token/key")
    if COOKIE_RE.search(text): found.append("cookie/session")
    return found


def ocr_image(image: Image.Image, lang: str) -> tuple[str, float]:
    data = pytesseract.image_to_data(image, lang=lang, output_type=pytesseract.Output.DICT)
    values: list[float] = []
    for raw, conf in zip(data.get("text", []), data.get("conf", [])):
        if str(raw).strip():
            try:
                value = float(conf)
                if value >= 0: values.append(value)
            except (TypeError, ValueError):
                pass
    text = " ".join(str(x).strip() for x in data.get("text", []) if str(x).strip()).strip()
    return text, round(sum(values) / len(values), 2) if values else 0.0


def confidence_label(score: float, text: str) -> str:
    if not text or score < 50: return "low"
    if score < 80: return "medium"
    return "high"


def image_result(path: Path, lang: str) -> dict[str, Any]:
    with Image.open(path) as image:
        text, score = ocr_image(image, lang)
    return {
        "source_id": "IMG-001", "source_type": "image", "source_path": str(path), "page": None,
        "text_layer": None, "ocr_engine": "tesseract", "language": lang,
        "confidence_score": score, "confidence": confidence_label(score, text),
        "privacy": "unknown", "sensitive_fields": sensitive_fields(text),
        "status": "success" if text else "partial", "text": text,
    }


def pdf_results(path: Path, lang: str) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    with pymupdf.open(path) as doc:
        for number, page in enumerate(doc, start=1):
            page_id = f"PDF-001-P{number:03d}"
            layer = page.get_text().strip()
            if layer:
                results.append({
                    "source_id": page_id, "source_type": "pdf", "source_path": str(path), "page": number,
                    "text_layer": True, "ocr_engine": "pymupdf", "language": None,
                    "confidence_score": 100.0, "confidence": "high", "privacy": "unknown",
                    "sensitive_fields": sensitive_fields(layer), "status": "success", "text": layer,
                })
                continue
            pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2), alpha=False)
            with Image.open(io.BytesIO(pix.tobytes("png"))) as image:
                text, score = ocr_image(image, lang)
            results.append({
                "source_id": page_id, "source_type": "pdf", "source_path": str(path), "page": number,
                "text_layer": False, "ocr_engine": "tesseract", "language": lang,
                "confidence_score": score, "confidence": confidence_label(score, text),
                "privacy": "unknown", "sensitive_fields": sensitive_fields(text),
                "status": "success" if text else "failed", "text": text,
            })
    return results


def markdown_report(payload: dict[str, Any]) -> str:
    records = payload["records"]
    rows = ["## OCR/文档来源报告", "| ID | 类型 | 页码/区域 | 引擎 | 置信度 | 分数 | 隐私级别 | 状态 |", "|---|---|---|---|---|---:|---|---|"]
    for r in records:
        area = "-" if r["page"] is None else str(r["page"])
        rows.append(f"| {r['source_id']} | {r['source_type']} | {area} | {r['ocr_engine']} | {r['confidence']} | {r['confidence_score']:.2f} | {r['privacy']} | {r['status']} |")
    success = [r["source_id"] for r in records if r["status"] == "success"]
    partial = [r["source_id"] for r in records if r["status"] == "partial"]
    failed = [r["source_id"] for r in records if r["status"] == "failed"]
    low = [r["source_id"] for r in records if r["confidence"] == "low"]
    sensitive = sorted({item for r in records for item in r["sensitive_fields"]})
    rows += ["", "## 提取结果摘要", f"- 成功页面/图片：{', '.join(success) or '无'}", f"- 部分读取页面/区域：{', '.join(partial) or '无'}", f"- 失败页面/区域：{', '.join(failed) or '无'}", f"- 低置信度内容：{', '.join(low) or '无'}", "- 未识别内容：见各记录 text 字段", "- 是否联网：否", "", "## OCR/隐私风险", f"- 是否包含私人材料：未判定（privacy=unknown）", f"- 是否检测到敏感字段：{', '.join(sensitive) or '否'}", f"- 是否需要人工复核或脱敏：{'是' if sensitive or low else '按需'}", "- 是否写入长期存储：否", "", f"<!-- skill_version={SKILL_VERSION}; protocol={PROTOCOL_VERSION}; report_schema={REPORT_SCHEMA} -->"]
    return "\n".join(rows) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--lang", default=DEFAULT_LANG)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()
    if not args.input.is_file(): parser.error(f"input file not found: {args.input}")
    if args.input.suffix.lower() not in IMAGE_SUFFIXES | {".pdf"}: parser.error("unsupported input type")
    configure_tesseract()
    records = pdf_results(args.input, args.lang) if args.input.suffix.lower() == ".pdf" else [image_result(args.input, args.lang)]
    payload = {"skill_version": SKILL_VERSION, "protocol_version": PROTOCOL_VERSION, "report_schema": REPORT_SCHEMA, "ocr_engine": str(TESSERACT_CMD), "records": records}
    output_json = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    output_md = markdown_report(payload)
    if args.json_output: args.json_output.write_text(output_json, encoding="utf-8")
    else: print(output_json, end="")
    if args.markdown_output: args.markdown_output.write_text(output_md, encoding="utf-8")
    return 0


if __name__ == "__main__":
    try: raise SystemExit(main())
    except Exception as exc:
        print(f"OCR failed: {exc}", file=sys.stderr); raise SystemExit(1)
