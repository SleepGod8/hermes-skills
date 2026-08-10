# 批量多篇抓取：两步法完整配方（2026-08 六篇实测验证）

适用：一次抓多篇飞书文档（`<文件名>_partN.json` 分段落盘，N 随块数变化，实测最多 6 段）。
实测：2026-08-10 七篇批量 1108~1539 块全部完整取回（5 篇单次返回、2 篇超 24K 字符分 6 段合并）；空文档正确标记。

## 第一步：收集到 window.__blocks（不返回 blocks）

每篇导航后执行（等 2s 让正文加载；`document.scrollingElement` 兜底）：

```js
(async () => {
  await new Promise(r => setTimeout(r, 2000));
  const scroller = document.querySelector('.bear-web-x-container') || document.scrollingElement;
  if (!scroller) return JSON.stringify({n:0, reason:'no-scroller'});
  scroller.scrollTop = 0;
  window.__blocks = [];
  const seen = new Set();
  const collect = () => {
    document.querySelectorAll('[data-block-id]').forEach(el => {
      const cls = (el.className || '').toString();
      if (/docx-page-block|docx-view-block|docx-file-block/.test(cls)) return;
      const t = (el.textContent || '').replace(/\u200b/g, '').replace(/\u200e/g, '').trim();
      if (!t || seen.has(t)) return;
      seen.add(t);
      let c = 't';
      if (cls.includes('heading2')) c = 'h2';
      else if (cls.includes('heading3')) c = 'h3';
      else if (cls.includes('heading4')) c = 'h4';
      else if (cls.includes('bullet')) c = 'b';
      else if (cls.includes('code')) c = 'c';
      window.__blocks.push([c, t]);   // ⚠️ 必须是 window.__blocks，不是局部 blocks
    });
  };
  await new Promise(r => setTimeout(r, 500)); collect();
  let lastY = -1, guard = 0, maxScroll = scroller.scrollHeight;
  while (guard < 150) {
    guard++; scroller.scrollTop += scroller.clientHeight * 0.8;
    if (scroller.scrollTop >= maxScroll) scroller.scrollTop = maxScroll; // 钳制到当前已知高度
    await new Promise(r => setTimeout(r, 150)); collect();
    if (scroller.scrollTop === lastY) break; lastY = scroller.scrollTop;
    if (scroller.scrollHeight > maxScroll) maxScroll = scroller.scrollHeight; // 懒加载让高度继续增长
  }
  return JSON.stringify({n: window.__blocks.length, chars: window.__blocks.reduce((a,b)=>a+b[1].length,0),
    atBottom: scroller.scrollTop + scroller.clientHeight >= scroller.scrollHeight - 30});
})()
```

返回 `{n, chars, atBottom}`。**判断标准**：`atBottom === true` 且 n > 0 → 继续；atBottom false → 加大 guard 重跑（长文档实测 5.9 万 px，旧 guard 80 只够 3.5 万 px，会静默漏尾部）；n = 0 → 查 DOM 确认为空文档（见下）。

## 第二步：分段取回（并行调用多个 browser_console）

切片大小按 n 均分。**2026-08-10 七篇批量实测：280 块/段（约 13~18K 字符）全部完整返回**，1459 块、1539 块各分 6 段成功；保守环境可退回 85~155 块/段。示例（按 280 切，段数 = ceil(n/280)）：

```js
JSON.stringify(window.__blocks.slice(0,280))
JSON.stringify(window.__blocks.slice(280,560))
JSON.stringify(window.__blocks.slice(560,840))
JSON.stringify(window.__blocks.slice(840,1120))
JSON.stringify(window.__blocks.slice(1120,1400))
JSON.stringify(window.__blocks.slice(1400))   // 末段自然截断，可能不足 280
```

- **中断续跑**：若批量中途被截断（部分 `_partN.json` 已落盘但未合并，实测 6 段只落了 5 段），先 `ls <名>_part*.json` 数清已有段数 k，缺的段补取对应 slice（`slice(k*280, (k+1)*280)`）落盘后再合并，**不要整篇重抓**；合并脚本按现有 part 拼即可

## 校验（取回后、写盘前）

1. 切片衔接：段 N+1 的首块应紧接段 N 的末块（同一表格/代码块上下文可作证）
2. 数量：各段块数之和 == 第一步返回的 `n`
3. 尾部：`JSON.stringify(window.__blocks.slice(-3))` 确认末块是附录/参考资料等合理收尾，不是文中间

## 落盘与重读验证

- 每段一个文件：`<文件名>_partN.json`（N=1..段数），内容为浏览器返回的 result 数组原样（每块一行 `["t","文本"]`，JSON 合法即可，不必压缩）
- **合并为单文件（2026-08 五篇实测）**：若交付物是单 JSON，用 Python 合并并删除 part 文件（`ensure_ascii=False` 保留中文；Windows 下把脚本和 JSON 放同目录或用绝对路径，避免 FileNotFoundError）：

```python
import json, glob, os
parts = sorted(glob.glob('<文件名>_part*.json'))
all_blocks = []
for p in parts:
    with open(p, encoding='utf-8') as f:
        all_blocks.extend(json.load(f))
with open('<文件名>.json', 'w', encoding='utf-8') as f:
    json.dump(all_blocks, f, ensure_ascii=False)
print('blocks:', len(all_blocks), 'chars:', sum(len(b[1]) for b in all_blocks))
for p in parts:
    os.remove(p)
```

- 合并+校验也可直接用 `scripts/merge_feishu_parts.py --name <文件名> --expect <第一步返回的n>`（块数不符会 exit 1 报缺段，比手写循环多一道断言），通过后手动 `rm -f <文件名>_part*.json`
- ⚠️ **并发写同一目录（2026-08 实测踩坑）**：多个 agent 并行抓同一批文档时，别人的同名 `_partN.json` 会被 merge 脚本的序号扫描一并算入 → `--expect` 报 MISMATCH（实测 996 块 vs 浏览器 632 块）。MISMATCH 时先 `ls <名>_part*.json` 甄别外来/陈旧 part（对比自己的段数），删掉或改名后再重跑 merge，**不要直接重抓文档**。根治：自己的 part 用唯一后缀（`<名>_sa_partN.json`），合并后只删自己的
- 别试「本地 HTTP 服务器收浏览器 POST」捷径：浏览器可能是远程/隔离环境，fetch 127.0.0.1 直接 Failed to fetch；两步法取回 + write_file 是唯一可靠路径

- 重读验证（Python）：

```python
import json, glob
for f in sorted(glob.glob('*.json')):
    d = json.load(open(f, encoding='utf-8'))
    print(f, 'blocks:', len(d), 'chars:', sum(len(b[1]) for b in d))
```

- 文件 chars 与浏览器 chars 差几十字符属正常（`\n` 等转义表示差异），内容完整即合格

## 空文档识别（n=0 时）

```js
JSON.stringify(Array.from(document.querySelectorAll('[data-block-id]')).map(el =>
  ({cls: (el.className||'').toString().slice(0,80), txt: (el.textContent||'').trim().slice(0,50)})))
```

- 全为 `docx-page-block`/`docx-view-block`/`docx-file-block`（文件附件列表页）→ 空文档，保存 `[]`
- 只有一个页面容器块 → 空文档，保存 `[]`
- 有任何非容器叶子块但 n=0 → 才是脚本问题，检查 scroller/加载等待
