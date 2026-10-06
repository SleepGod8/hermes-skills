# -*- coding: utf-8 -*-
"""用本机 Microsoft Word 把 .docx 渲染成 PNG，宽度对齐参考图，供像素级比对。

用法:
    python render_docx_win.py <docx> [--width 1280] [--pages 1]

做什么:
    Word COM (pywin32) 打开 docx -> 导出 PDF (FileFormat=17) -> PyMuPDF 渲染 PNG，
    zoom 取 参考宽度 / PDF页宽，使输出与原扫描件同宽（例如 1280px）。

依赖:
    python -m pip install pywin32 pymupdf     # Word 必须已安装
    Word 路径参考: C:/Program Files/Microsoft Office/root/Office16/WINWORD.EXE

无 Word 的退路:
    soffice --headless --convert-to pdf --outdir <dir> <docx>   然后用 pymupdf 渲染。
"""
import argparse
import os
import sys

import pymupdf
import win32com.client

WD_FORMAT_PDF = 17


def to_pdf(docx_path, pdf_path):
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    try:
        try:
            word.DisplayAlerts = 0
        except Exception:
            pass
        d = word.Documents.Open(os.path.abspath(docx_path), ReadOnly=True)
        d.SaveAs(os.path.abspath(pdf_path), FileFormat=WD_FORMAT_PDF)
        d.Close(False)
    finally:
        word.Quit()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("docx")
    ap.add_argument("--width", type=int, default=1280, help="输出 PNG 宽度（对齐扫描件）")
    ap.add_argument("--pages", type=int, default=1)
    ap.add_argument("--outdir", default=None)
    args = ap.parse_args()

    outdir = args.outdir or os.path.dirname(os.path.abspath(args.docx))
    stem = os.path.splitext(os.path.basename(args.docx))[0]
    pdf = os.path.join(outdir, stem + ".pdf")
    to_pdf(args.docx, pdf)

    doc = pymupdf.open(pdf)
    for i in range(min(args.pages, doc.page_count)):
        page = doc[i]
        zoom = args.width / page.rect.width
        pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
        png = os.path.join(outdir, "render.png" if i == 0 else f"render_{i + 1}.png")
        pix.save(png)
        print(png, pix.width, pix.height)


if __name__ == "__main__":
    sys.exit(main())
