---
name: web-discovery-fallbacks
description: "Search engines fail? Try GitHub API + domain TLD probing."
version: 1.0.0
author: agent
tags: [research, web, search, fallback, github-api, domain]
platforms: [linux, macos, windows]
---

# 网页发现兜底路径（搜索引擎被反爬拦截时）

中文网络/无住宅代理环境下，通用搜索引擎经常被反爬拦截或返回垃圾结果。本技能提供可复用的替代发现路径。

## 触发条件

- 用户问「XX 是什么/是哪个网站」且想查证（产品、工具、域名）
- Bing/百度/Brave/DuckDuckGo/Google 返回验证码、空结果、或完全无关内容
- 用户只记得名字/域名的一部分，需要定位真实站点

## 实测踩坑（2026-08 中文环境）

- **Bing cn**：能返回 HTML 但结果可能完全无关（搜 `"aigallery"` 返回宝可梦/数字0/知乎数学——疑似 query 解析错乱）。别信第一屏，用引号精确匹配 + `ensearch=1` 再试。
- **百度**：直接跳 wappass 人机验证（tuxing_v2.html），无解。
- **Brave**：跳 captcha 滑块验证页。
- **html.duckduckgo.com / lite.duckduckgo.com**：能拿到 HTML（~14KB），但结果链接经常解析为空（页面结构是反爬表单或零结果）。正则 `<a class="result__a"` 或 DDG lite 的 `<a href>` 提取常得 0 条。
- **Google 直连**：curl 常超时或返回空（无 h3 结果）。不要依赖。
- **browser_navigate 访问搜索引擎**：多数同样触发 bot 检测。
- **Wikipedia（zh/en）**：本网络直连浏览器/curl 均超时（ERR_CONNECTION_TIMED_OUT）；走本地代理 curl 会写文件失败（exit 23）。不要依赖维基。
- **Bing CN 成人/敏感词查询**：结果被本地审查过滤，返回的全是无关养生/新闻文章，没有实质内容。别浪费时间。

## 兜底路径（按优先级，实测有效）

### 1. GitHub API 仓库搜索（最可靠，免认证）
```bash
curl -sL --max-time 25 "https://api.github.com/search/repositories?q=aigallery&sort=stars&order=desc&per_page=8" \
  -H "User-Agent: Mozilla/5.0" | python3 -c "import json,sys; [print('-', r['full_name'], '| ⭐', r['stargazers_count'], '|', (r.get('description') or '')[:100]) for r in json.load(sys.stdin).get('items', [])]"
```
- 再取单仓详情：`https://api.github.com/repos/<owner>/<repo>`（描述/语言/主页/license）
- 适合：查「XX 是什么工具/项目」，能立刻得到名字+描述+星标，且能区分同名多个项目。

### 2. 域名 TLD 探测（用户记得名字但不确定后缀）
用 execute_code + urllib（比 terminal curl 稳，避免 git-bash /tmp 写文件坑）：
```python
import urllib.request, re, html
def try_fetch(domain):
    for scheme in ['https', 'http']:
        try:
            req = urllib.request.Request(f'{scheme}://{domain}', headers={'User-Agent': 'Mozilla/5.0 ... Chrome/120'})
            with urllib.request.urlopen(req, timeout=10) as r:
                body = r.read(3000).decode('utf-8', errors='ignore')
                m = re.search(r'<title[^>]*>(.*?)</title>', body, re.S)
                print(f'{scheme}://{domain} => HTTP {r.status} | {html.unescape(m.group(1)).strip()[:100] if m else "(无title)"}')
                return
        except Exception: pass
    print(f'{domain} => 全部失败')
for d in ['aigallery.ai', 'aigallery.com', 'aigallery.io', 'aigallery.app', 'aigallery.org',
          'aigallery.xyz', 'aigallery.cn', 'aigallery.dev', 'aigallery.space', 'aigallery.fun']:
    try_fetch(d)
```
- TLD 优先试：`.ai .app .io .xyz .dev .art .space .fun`（AI/工具类常见）+ `.com .net .org .cn`
- HTTP 200 + 有 `<title>` = 真实站点；title 为空可能是 JS 渲染（SPA），用 browser_navigate 打开确认；跳转域名出售页 = 停放/待售。

### 3. 直接访问候选站点读内容
- 域名探测到活站后，browser_navigate 打开看快照（标题、导航、模型列表、功能模块），比搜索更能确认「是不是用户说的那个」。
- 一次性查证类任务（「XX 是什么」）做到「定位到具体站点 + 简述它是干什么的」即可，不必深挖。

### 4. 中文百科内容：百度百科（baike.baidu.com）实测可访问
- 需要中文百科/词条类内容（维基被墙、Bing CN 被过滤时）→ **browser_navigate 直接开 `https://baike.baidu.com/item/<词条名>`**，实测可正常加载。
- 注意 URL 会自动跳转到规范词条（如「性爱姿势」），title 即词条名。
- 长词条快照会截断并保存到 `C:\Users\<user>\AppData\Local\hermes\cache\web\browser-snapshot-*.txt`——用 read_file 带 offset 分页读正文，比 browser_snapshot(full=true) 一次拿全更稳。
- 百度百科正文有「主要姿势/分类/安全」等结构化小节，适合作为知识点来源；页面也带相关词条链接可顺藤摸瓜。

## 验证/收尾

- 给用户报告时列出**查过但排除了的域名**（如「aigallery.com 是域名出售页」），帮用户排除干扰。
- 若用户给了额外线索（「无审查」「话题网站」「AI 画图」），用线索反推搜索词再走 1/2 路径，比空猜强。

## 参考

- `references/aigallery-discovery.md`：2026-08 实际案例——aigallery 全域名探测结果与站点定位过程。
