# 本地 HTML 文档转纯文本（python 正则，无第三方依赖）

需求文档/功能设计文档常以 HTML 导出（飞书/网页另存），直接用 read_file 会看到一堆标签。
以下方法转纯文本后按章节 grep 定位，比浏览器/bs4 轻量。

## 转换脚本

```bash
python - <<'EOF'
import re, html

def html_to_text(src, dst):
    with open(src, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    # 去掉 script/style
    content = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', content, flags=re.S|re.I)
    # 标题/段落标签换行
    content = re.sub(r'<(h[1-6])[^>]*>', r'\n### ', content, flags=re.I)
    content = re.sub(r'<(p|div|li|tr|br|td|th)[^>]*>', '\n', content, flags=re.I)
    content = re.sub(r'</(h[1-6]|p|div|li|tr|table|ul|ol)>', '\n', content, flags=re.I)
    # 去标签
    content = re.sub(r'<[^>]+>', '', content)
    text = html.unescape(content)
    # 压缩空行
    lines = [l.strip() for l in text.split('\n')]
    out, blank = [], 0
    for l in lines:
        if l:
            out.append(l); blank = 0
        else:
            blank += 1
            if blank == 1: out.append('')
    with open(dst, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out))
    print(f"{dst}: {len('\n'.join(out))} chars, {sum(1 for l in out if l)} lines")

html_to_text('需求文档.html', 'req_text.txt')
EOF
```

## 定位章节

```bash
grep -n "^### " req_text.txt          # 看全部章节标题 + 行号
grep -n "^### " req_text.txt | head   # 前面部分
# 用 read_file offset=<行号> 精准读目标章节，避免全文进 context
```

## 经验值

- 152KB HTML → 约 46K 字符纯文本（正文密度约 1/3）
- 表格被拆成逐行文本，适合 grep 关键词定位，不适合直接视觉阅读
- 对比同一文档的 HTML 版和 -纯文本.md 版：仓库 docs/_ref/ 通常已有纯文本版，先找现成的
