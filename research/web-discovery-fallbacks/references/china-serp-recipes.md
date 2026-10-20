# 中文 SERP / 中文站点正文抓取配方（2026-10 实测）

场景：主人问中文游戏/软件/资讯类事实，bing cn 返回无关结果、百度 302 验证、维基不通。
整条链路只用 terminal + execute_code，无需浏览器授权。

## 1. 搜狗出结果（唯一稳定入口）

```bash
cd "$LOCALAPPDATA/Temp"
curl -s -m 25 -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0 Safari/537.36" \
  -G "https://www.sogou.com/web" --data-urlencode "query=终末地 特许寻访 保底 概率" -o sg.html -w "%{http_code} %{size_download}\n"
```

- 返回 200 / 300-600KB 即成功；0 字节多为参数拼接方式错（手工 `+`）。
- 摘要文本里经常已经含答案，可直接引用（记得标注是搜索摘要、非原文）。

## 2. 解析结果块

```python
import re, html, os
s = open(os.path.expandvars(r"%LOCALAPPDATA%\Temp\sg.html"), encoding="utf-8", errors="ignore").read()
blocks = re.findall(r'<div class="vrwrap".*?</div>\s*</div>', s, re.S)
for b in blocks[:12]:
    t = re.sub(r'<[^>]+>', ' ', b)
    print(re.sub(r'\s+', ' ', html.unescape(t)).strip()[:350])
# 标题+跳转链接
for h, t in re.findall(r'<h3[^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', s, re.S):
    print(re.sub(r'<[^>]+>', '', html.unescape(t)).strip()[:60], "|", h[:120])
```

## 3. 把 /link?url= 还原成真 URL

```bash
curl -s -m 20 -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125.0" \
  -e "https://www.sogou.com/" "https://www.sogou.com/link?url=<段>" \
  | grep -oE "https?://[a-zA-Z0-9./?=&_%:-]+" | head -2
```

`-o /dev/null -D -` / `-I` 都拿不到 Location（服务端回 200 + JS 跳转），必须读 body。

## 4. 正文提取（按站点）

| 站点 | 正文容器 | 备注 |
|---|---|---|
| 微信公众平台 `mp.weixin.qq.com` | `id="js_content"` | 标题 `var msg_title = '...'`；官方公告首发地，一手源 |
| 网易号 `163.com/dy/article/...` | `<div class="post_body">` | 转载多，注意作者与日期 |
| 3DM 手游 `shouyou.3dmgame.com/gl/<id>.html` | `<div class="news_warp_center">` | 正文里带「时间：」字段，用来判断测试期/正式服 |
| 心愿游戏 `wishdown.com` | 无固定容器，`find("保底")` 定位 | GBK 编码 |
| 游侠 `m.ali213.net` | 移动版整页 `re.sub` 即可 | 攻略汇总类，常含最新版本结论 |

通用流程：`<script|style>` 剥离 → 标签换行 → `html.unescape` → `\n{2,}` 压缩 → 关键词定位切片。

```python
raw = open(p, "rb").read()
for enc in ("utf-8", "gbk", "gb18030"):
    try: s = raw.decode(enc); break
    except Exception: pass
```

## 5. 官方 Next.js 站（RSC）公告挖掘

官网列表页（如 `https://endfield.hypergryph.com/news`）把数据塞在 `self.__next_f.push([...])` 的转义 JSON 里：

```bash
curl -sL -m 25 -A "Mozilla/5.0 ... Chrome/125.0" "https://<site>/news" -o news.html
grep -oE '\\"cid\\":\\"[0-9]+\\"' news.html | sort -u | head
```

- 同时能抠到 `title` / `brief`（正文摘要）/ `displayTime`（unix 秒）。
- 详情页路由**不**一定是 `/news/<cid>`；试错成本高时，优先用同一篇公告的公众号版本（内容一致、纯文本更好解析）。
- `/api/...` 猜测多半 404；`/sitemap.xml` 只列一级页面，不含详情。

## 6. 死路记录（省下下次的时间）

- `baike.baidu.com` 直连 curl → 403（需浏览器）；
- `prts.wiki`、`*.huijiwiki.com` → 403；
- `wiki.biligame.com/<游戏>` 有时 302 到 BWIKI 站总首页（1.4MB 的模板页，正文无游戏内容），判断依据：HTML 里连游戏名都搜不到；
- `endfield.gamekee.com` 等 gamekee 站是 JS 壳，curl 只回 3-4KB，正文必须走浏览器或站内 API。
