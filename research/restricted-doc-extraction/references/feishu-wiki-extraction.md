# 飞书知识库（Wiki）内容提取 —— 完整方法

2026-08 实测成功：密码保护的知识库「AI项目603」23 顶层节点 + 4 层嵌套（共 57 节点，40+ 叶子 docx），批量抓取 + 清洗为 Markdown。腾讯文档用 textPool 解码，**飞书机制完全不同**：正文走 websocket（pandora_ws）不走 REST，靠 DOM 虚拟列表渲染——必须滚动收集。

## 触发条件

- `xxx.feishu.cn/wiki/<token>` 链接（分享的知识库/文档）
- 页面显示「请输入密码访问」（密码保护）
- 要批量抓取知识库全部文档 / 导入自己的知识库

## 1. 密码解锁

`browser_navigate` 到链接 → 快照出现密码输入框 + 确定按钮 → `browser_type` 输密码 → `browser_click` 确定。
- 解锁后 cookie 在会话内延续：**子文档直接打开无需再输密码**
- ⚠️ 但**回到知识库首页又会出现密码框**，需重新输入

## 2. 目录树：页面内部 API（不要在子页面调用）

知识库可能是多层嵌套文件夹（文件夹 has_child=true，叶子文档 has_child=false, obj_type=22）。

```js
// 必须在「知识库首页」页面上下文调用！在子文档页面调用返回空 child_map
fetch('https://<host>/space/api/wiki/v2/tree/get_info/?space_id=<space_id>&with_space=true&with_perm=true&expand_shortcut=true&need_shared=true&exclude_fields=5&with_deleted=true&wiki_token=<根节点token>', {credentials:'include'})
// 返回 data.tree.child_map[token] = 子节点token数组; data.tree.nodes[token] = {title, obj_token, obj_type, has_child, url}
```

递归 DFS：对每个 has_child 节点再调 get_info（带该节点 token）展开子层。`get_node` 接口只返回节点自身，不给子列表。

## 3. 正文收集：虚拟列表边滚边收

正文在 DOM 里（`[data-block-id]` 元素），但**虚拟列表只渲染视口附近**——一次性 `querySelectorAll` 只能拿到当前视口。必须滚动 + 去重收集：

```js
(async () => {
  await new Promise(r => setTimeout(r, 2000)); // 等正文渲染
  const scroller = document.querySelector('.bear-web-x-container') || document.scrollingElement;
  if (!scroller) return JSON.stringify({n:0, reason:'no-scroller'});
  scroller.scrollTop = 0;
  const blocks = []; const seen = new Set();
  const collect = () => {
    document.querySelectorAll('[data-block-id]').forEach(el => {
      const cls = (el.className || '').toString();
      if (/docx-page-block|docx-view-block|docx-file-block/.test(cls)) return; // 容器块跳过
      const t = (el.textContent || '').replace(/\u200b/g, '').replace(/\u200e/g, '').trim();
      if (!t) return;
      if (seen.has(t)) return; // 滚动快照重叠去重
      seen.add(t);
      let c = 't';
      if (cls.includes('heading2')) c = 'h2';
      else if (cls.includes('heading3')) c = 'h3';
      else if (cls.includes('heading4')) c = 'h4';
      else if (cls.includes('bullet')) c = 'b';
      else if (cls.includes('code')) c = 'c';
      blocks.push([c, t]);
    });
  };
  await new Promise(r => setTimeout(r, 500));
  collect();
  let lastY = -1, guard = 0;
  while (guard < 60) {
    guard++;
    scroller.scrollTop += scroller.clientHeight * 0.8;
    await new Promise(r => setTimeout(r, 180));
    collect();
    if (scroller.scrollTop === lastY) break;
    lastY = scroller.scrollTop;
  }
  return JSON.stringify({n: blocks.length, chars: blocks.reduce((a,b)=>a+b[1].length,0), blocks});
})()
```

块类型 class：`docx-page-block`(容器) / `docx-view-block`(容器) / `docx-code-block` / `docx-image-block`(空文本) / `docx-file-block`(容器) / heading2-3-4 / bullet / text。代码块文本格式为「代码块\<语言\>复制\<真实代码\>」。

## 4. 长文档：返回截断 → 分段取回

`browser_console` 返回超 ~24k 字符会截断。检测到 chars > 24000 时：
1. 同款脚本改为存 `window.__blocks`（只返回 {n, chars}）
2. 分 4 段取回：`(() => JSON.stringify(window.__blocks.slice(0,90)))()`、`slice(90,180)`、`slice(180,270)`、`slice(270)`
3. 每段 write_file 为 `<名>_part1.json` 等 → Python 合并

## 5. 空文档与验证

- 收集返回 n=0 / blocks=[] → 空文档（知识库里常有），仍保存 `[]` 并标记
- 每篇落盘后 read_file 确认非空；合并后对比收集时的 chars 校验完整性

## 6. Markdown 清洗（Python）

```python
def extract_code(text):
    import re
    m = re.search(r'代码块\s*(.*?)复制\s*(.*)$', text, re.S)  # 提取真实代码
    if m: return m.group(1).strip(), m.group(2).strip()
    return '', re.sub(r'^代码块|复制$', '', text).strip()
# cls 映射: h2→'## ', h3→'### ', h4→'#### ', b→'- ' + 去•, c→```<lang>\n<code>\n```, t→段落
# 语言映射: python→python, java→bash, go→bash, markdown→yaml, xml→xml, powershell→powershell
# 零宽字符 \u200b \u200e 全部删除; 表格在 textContent 里是粘连文本，保留原样
```

## 7. 批量与并行

- 43+ 篇批量时用 `delegate_task` 3 个子 agent 并行：把本文档的收集脚本 + 密码 + 落盘路径放 context，每个 agent 负责 5-8 篇（browser_navigate → browser_console → write_file），只返回状态摘要不返回正文
- ⚠️ 子 agent 运行期间**不要自己操作同一浏览器**（会互相干扰）

## 8. 写入自己的知识库（lark-mcp 路径）

官方 MCP `@larksuiteoapi/lark-mcp`（`hermes mcp add` stdio 方式）支持：`docx.v1.document.rawContent`(读) / `docx.v1.document.convert`(Markdown→块) / `docx.v1.document.create`(建文档) / `wiki.v2.spaceNode.moveDocsToWiki`(移入知识库) / `wiki.v2.spaceNode.create`(建节点)。权限需 `wiki:wiki` + `docx:document` + `drive:drive`，且应用必须是知识空间成员。

## 坑汇总

1. **get_info 依赖当前页面**：必须在知识库首页上下文调用，子页面调用返回空
2. **正文不走 REST**：`/space/api/docx/...`、`explorer/v2/entity/info` 都 Failed to fetch（meta 接口可用但只有元信息）；正文靠 DOM 渲染 + websocket
3. **虚拟列表**：一次性抓只有视口内容；必须边滚边收 + Set 去重
4. **滚动容器**是 `.bear-web-x-container`（scrollHeight 远大于 clientHeight 的元素），不是 window
5. **长返回截断**：>24k 字符分段，别硬取
6. **代码块带 UI 噪音**：「代码块」「复制」等文字混在 textContent 里，必须正则清洗
7. **密码框 ref 会过期**：导航后要重新 snapshot 拿 ref；密码输入后确定按钮从 disabled 变可用
