# -*- coding: utf-8 -*-
"""docs-to-knowledge-map 实测代码骨架（2026-08 langchain.com.cn 成功案例）

三步流程：curl 抓页 → 正则解析标题+链接 → 程序化生成 Mermaid mindmap + 详细清单。
环境：Windows git-bash + execute_code（Python 3.12+）。
"""

import re
import html
import json

# ============ Step 1: 抓取（terminal，不用 /tmp！） ============
# curl -sL --max-time 60 -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" \
#   "https://www.langchain.com.cn/docs/how_to/" \
#   -o "C:/Users/<user>/AppData/Local/Temp/langchain_howto.html" \
#   -w "HTTP %{http_code} size %{size_download}\n"
# => HTTP 200 size 91426

# ============ Step 2: 解析结构 ============
with open(r"C:/Users/<user>/AppData/Local/Temp/langchain_howto.html",
          encoding="utf-8", errors="replace") as f:
    content = f.read()
content = content.replace("\x00", "")  # 页面偶含 NUL 字节，先清

# 2a. 全量真实链接映射（详细清单唯一合法来源）
all_links = {}
for href, txt in re.findall(r'<a[^>]+href="(/docs/how_to/[^"]+)"[^>]*>(.*?)</a>', content, re.S):
    txt = html.unescape(re.sub(r"<[^>]+>", "", txt)).strip()
    if txt:
        all_links[href] = txt

# 2b. 标题序列（剔除页脚噪音）
NOISE = {"Was this page helpful?", "You can also leave detailed feedback on GitHub."}
tokens = []
for m in re.finditer(r"<h([1-4])[^>]*>(.*?)</h\1>", content, re.S):
    lvl, t = int(m.group(1)), m.group(2)
    t = html.unescape(re.sub(r"<[^>]+>", "", t)).strip().replace("\u200b", "")
    if t not in NOISE:
        tokens.append((m.start(), lvl, t))

# 2c. 每个标题块 = 该标题到下一标题之间的链接
blocks = []
for i, (start, lvl, title) in enumerate(tokens):
    end = tokens[i + 1][0] if i + 1 < len(tokens) else len(content)
    seg = content[start:end]
    links, seen = [], set()
    for href, txt in re.findall(r'<a[^>]+href="(/docs/how_to/[^"]+)"[^>]*>(.*?)</a>', seg, re.S):
        txt = html.unescape(re.sub(r"<[^>]+>", "", txt)).strip()
        if txt and href not in seen:
            seen.add(href)
            links.append({"href": href, "title": txt})
    blocks.append({"level": lvl, "title": title, "links": links})

# 2d. 存 JSON 供生成阶段复用
with open(r"C:/Users/<user>/AppData/Local/Temp/langchain_structure.json",
          "w", encoding="utf-8") as f:
    json.dump({"blocks": blocks, "links": all_links}, f, ensure_ascii=False, indent=1)

# ============ Step 3/4: 生成详细清单（真实 href，不手写） ============
lines, section, sub = [], 0, 0
for r in blocks:
    title, lvl, links = r["title"], r["level"], r["links"]
    if not links:          # 关键：先跳过空块，再递增编号 → 无孤立空标题
        continue
    if lvl == 2:
        section += 1
        sub = 0
        lines.append(f"\n### {section}. {title}")
    else:
        sub += 1
        lines.append(f"\n#### {section}.{sub} {title}")
    for l in links:
        lines.append(f"- [{l['title']}](https://www.langchain.com.cn{l['href']})")
detail_md = "\n".join(lines)

# ============ Step 5: 验证 ============
# 1) 链接数核对：len(all_links) 应 ≈ detail_md.count("https://www.langchain.com.cn")
# 2) 无孤立编号：正则 r"### \d+\. .*\n\n###" 之间不应有空头
# 3) mindmap 手写精简版（见 SKILL.md Step 3），与详细清单并存于最终 MD
