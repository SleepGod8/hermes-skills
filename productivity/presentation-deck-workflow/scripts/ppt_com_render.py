#!/usr/bin/env python
"""PowerPoint COM 渲染脚本（Windows 本机验证过，2026-08 智能财富管家答辩 PPT）。

用途：把 .pptx 渲染成 PDF 和/或逐页 PNG，供视觉 QA（qwen-vl-plus 逐页检查）。
不依赖 LibreOffice/poppler —— 用本机安装的 Microsoft Office PowerPoint COM。

依赖：pywin32 (pip install pywin32)
用法：
    python ppt_com_render.py "E:\项目\xxx.pptx"                  # 默认: 转 PDF + 导出 PNG
    python ppt_com_render.py "E:\项目\xxx.pptx" --pdf-only
    python ppt_com_render.py "E:\项目\xxx.pptx" --png-only --out-dir C:\temp\qa --size 1600 900
"""

import argparse
import os
import sys
import win32com.client


def render(pptx_path: str, pdf_path: str | None, png_dir: str | None, width: int = 1600, height: int = 900):
    ppt = win32com.client.Dispatch("PowerPoint.Application")
    try:
        # 参数: FileName, ReadOnly=True, Untitled=False, WithWindow=False
        pres = ppt.Presentations.Open(pptx_path, True, False, False)
        n = pres.Slides.Count
        print(f"幻灯片共 {n} 页")

        if pdf_path:
            # 32 = ppSaveAsPDF
            pres.SaveAs(pdf_path, 32)
            print(f"✅ PDF: {pdf_path} (存在={os.path.exists(pdf_path)})")

        if png_dir:
            os.makedirs(png_dir, exist_ok=True)
            for i in range(1, n + 1):
                out = os.path.join(png_dir, f"slide-{i:02d}.png")
                pres.Slides(i).Export(out, "PNG", width, height)
                print(f"✅ {out} ({os.path.getsize(out)} bytes)")

        pres.Close()
    finally:
        ppt.Quit()


def main():
    ap = argparse.ArgumentParser(description="PowerPoint COM 渲染 .pptx → PDF / PNG")
    ap.add_argument("pptx", help="输入 .pptx 路径（支持中文路径）")
    ap.add_argument("--pdf", default=None, help="输出 PDF 路径（默认: 与 pptx 同目录同名 .pdf）")
    ap.add_argument("--png-dir", default=None, help="PNG 输出目录（默认: 同目录 ppt_qa/）")
    ap.add_argument("--pdf-only", action="store_true", help="只转 PDF")
    ap.add_argument("--png-only", action="store_true", help="只导 PNG")
    ap.add_argument("--size", nargs=2, type=int, default=[1600, 900], help="PNG 尺寸 W H")
    args = ap.parse_args()

    if not os.path.exists(args.pptx):
        print(f"❌ pptx 不存在: {args.pptx}", file=sys.stderr)
        sys.exit(1)

    base = os.path.splitext(args.pptx)[0]
    do_pdf = not args.png_only
    do_png = not args.pdf_only
    pdf_path = args.pdf if args.pdf else (base + ".pdf") if do_pdf else None
    png_dir = args.png_dir if args.png_dir else (os.path.join(os.path.dirname(args.pptx), "ppt_qa") if do_png else None)

    render(args.pptx, pdf_path, png_dir, args.size[0], args.size[1])


if __name__ == "__main__":
    main()
