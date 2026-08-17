"""PPTX 渲染 + 视觉 QA 工作流脚本（Windows）

用法:
  python pptx_render_qa.py <pptx路径> [--out <图片目录>] [--pdf <pdf路径>]

功能:
  1. PowerPoint COM 打开 pptx → 导出每页 PNG (1600x900)
  2. 可选: SaveAs 32 导出 PDF
  3. 逐页调 qwen-vl-plus (DashScope) 视觉检查排版, 输出 ✅/⚠️ 报告

依赖: pywin32 (COM), urllib (标准库)
注意: 用 terminal 的 python 跑, 不是 execute_code 沙箱 (可能缺 pywin32)
"""
import argparse
import base64
import json
import os
import sys
import time
import urllib.request

def load_key(env_path=None):
    env_path = env_path or os.path.expanduser(r"~\AppData\Local\hermes\.env")
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("DASHSCOPE_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None

def export_pngs(pptx_path, out_dir, pdf_path=None):
    import win32com.client
    os.makedirs(out_dir, exist_ok=True)
    ppt = win32com.client.Dispatch("PowerPoint.Application")
    try:
        pres = ppt.Presentations.Open(pptx_path, True, False, False)
        n = pres.Slides.Count
        print(f"幻灯片共 {n} 页")
        for i in range(1, n + 1):
            out = os.path.join(out_dir, f"slide-{i:02d}.png")
            pres.Slides(i).Export(out, "PNG", 1600, 900)
            print(f"  OK slide-{i:02d}.png")
        if pdf_path:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
            pres.SaveAs(pdf_path, 32)
            print(f"  OK PDF: {pdf_path}")
        pres.Close()
        return n
    finally:
        ppt.Quit()

def check_slide(img_path, page_num, key, api="https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"):
    with open(img_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    payload = {
        "model": "qwen-vl-plus",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
                {"type": "text", "text": (
                    "这是答辩PPT第%d页。用中文检查排版质量，只报告问题："
                    "1.文字是否溢出卡片/重叠 2.表格是否错位 3.元素是否超出页面边界 "
                    "4.信息是否拥挤无法阅读。如果没有问题就说'无问题'。" % page_num
                )},
            ],
        }],
    }
    req = urllib.request.Request(
        api, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode())
    return data["choices"][0]["message"]["content"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pptx")
    ap.add_argument("--out", default="ppt_qa")
    ap.add_argument("--pdf", default=None, help="可选 PDF 输出路径")
    ap.add_argument("--skip-qa", action="store_true", help="只渲染不检查")
    ap.add_argument("--pages", default=None, help="只检查指定页, 逗号分隔如 1,3,10")
    args = ap.parse_args()

    n = export_pngs(args.pptx, args.out, args.pdf)
    if args.skip_qa:
        return

    key = load_key()
    if not key:
        print("!! 未找到 DASHSCOPE_API_KEY (.env)")
        return

    pages = [int(x) for x in args.pages.split(",")] if args.pages else list(range(1, n + 1))
    for p in pages:
        img = os.path.join(args.out, f"slide-{p:02d}.png")
        if not os.path.exists(img):
            print(f"页 {p:02d} 缺图: {img}")
            continue
        try:
            r = check_slide(img, p, key)
            flag = "OK " if "无问题" in r else "WARN"
            print(f"页 {p:02d} [{flag}]: {r[:150]}")
        except Exception as e:
            print(f"页 {p:02d} [ERR]: {e}")
        time.sleep(0.5)

if __name__ == "__main__":
    main()
