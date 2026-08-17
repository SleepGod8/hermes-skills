#!/usr/bin/env python3
"""
ppt_qa.py — 用 qwen-vl-plus 对 PPT 导出的 PNG 逐页做视觉 QA。

用法:
  python ppt_qa.py <图片目录> [起始页] [结束页] [--detail 页码,...]

示例:
  python ppt_qa.py C:\\Users\\80704\\AppData\\Local\\hermes\\workspace\\ppt_qa 1 15
  python ppt_qa.py ... 10 12 --detail 11,14     # 对 11/14 页做细节追问

依赖: 无第三方包（只用 urllib/base64），DASHSCOPE_API_KEY 从 ~/.hermes/.env 读取。
"""
import os, sys, base64, json, urllib.request, time

def load_dashscope_key():
    env = os.path.join(os.path.expanduser("~"), "AppData", "Local", "hermes", ".env")
    with open(env, encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("DASHSCOPE_API_KEY="):
                return line.strip().split("=", 1)[1].strip().strip('"').strip("'")
    return None

def ask_qwen_vl(key, img_path, question):
    with open(img_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    payload = {
        "model": "qwen-vl-plus",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
                {"type": "text", "text": question},
            ],
        }],
    }
    req = urllib.request.Request(
        "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode())
    return data["choices"][0]["message"]["content"]

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    qa_dir = sys.argv[1]
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    end = int(sys.argv[3]) if len(sys.argv) > 3 else None
    detail_pages = []
    if "--detail" in sys.argv:
        idx = sys.argv.index("--detail")
        detail_pages = [int(x) for x in sys.argv[idx + 1].split(",")]

    key = load_dashscope_key()
    if not key:
        print("❌ 未找到 DASHSCOPE_API_KEY")
        sys.exit(1)

    # 自动探测页数
    if end is None:
        files = sorted(f for f in os.listdir(qa_dir) if f.startswith("slide-") and f.endswith(".png"))
        end = len(files)

    print(f"QA 范围: 第 {start}-{end} 页, 图片目录: {qa_dir}")
    for p in range(start, end + 1):
        img = os.path.join(qa_dir, f"slide-{p:02d}.png")
        if not os.path.exists(img):
            print(f"⚠️ 缺少 {img}")
            continue
        q = (f"这是答辩PPT第{p}页。用中文检查排版质量，只报告问题："
             f"1.文字是否溢出卡片/重叠 2.表格是否错位 3.元素是否超出页面边界 "
             f"4.信息是否拥挤无法阅读。如果没有问题就说'无问题'。")
        try:
            r = ask_qwen_vl(key, img, q)
            flag = "✅" if "无问题" in r else "⚠️"
            print(f"页 {p:02d} {flag}: {r[:150]}")
        except Exception as e:
            print(f"页 {p:02d} ❌ 调用失败: {e}")
        time.sleep(0.5)

    # 细节追问页
    for p in detail_pages:
        img = os.path.join(qa_dir, f"slide-{p:02d}.png")
        q = ("仔细看页面细节：任何关键框/文字是否完整？有没有截断、溢出、重叠？"
             "请逐字读出你看到的重要文字验证完整性。")
        try:
            r = ask_qwen_vl(key, img, q)
            print(f"\n=== 第{p}页细节 ===")
            print(r[:400])
        except Exception as e:
            print(f"第{p}页细节 ❌: {e}")

if __name__ == "__main__":
    main()
