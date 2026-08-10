# 飞书分享链接登录墙诊断（Login Wall Diagnosis）

> 2026-08 实测：同一分享者（Jeremy_wl）的 6 篇 wiki 链接中，3 篇匿名可开（README、RAG面试问答、面试专用题库），3 篇（WL-面试问题分类汇总、为什么需要Neo4j、Redis通俗指南）导航后一律 302 到登录页。会话本身有效（其余文档反复导航均正常）—— 是**逐文档权限差异**，不是会话过期。

## 症状识别

- `browser_navigate` 返回 timeout（页面实际跳走了，不是没加载）
- 紧接着 `browser_console` 查 `location.href`：
  ```js
  JSON.stringify({url: location.href, title: document.title, ready: document.readyState})
  ```
  命中 `https://accounts.feishu.cn/accounts/page/login?app_id=2&...&redirect_uri=https%3A%2F%2F<tenant>.feishu.cn%2Fwiki%2F<TOKEN>%3Flogin_redirect_times%3D1` → **硬登录墙**
- 登录页快照只有「扫码登录 / 切换至Lark登录 / 立即注册」，无访客入口、无密码输入框
- ⚠️ 别对同一 URL 连续重试 3 次以上：browser_navigate 会触发 repeated_exact_failure 循环警告，浪费时间

## 与密码墙的区别

| 形态 | 页面 | 处置 |
|---|---|---|
| 密码墙 | 知识库内「请输入密码访问」框 | 问用户密码 → 输入解锁 → cookie 延续 |
| 登录墙 | `accounts.feishu.cn` 登录页（二维码） | 必须真实登录态；密码 cookie 无效 |

## API 探测（确认 token 归属，browser_console 内 fetch，credentials:'include'）

1. **找 space_id**（对当前可打开的文档页面）：
   ```js
   performance.getEntriesByType('resource').map(e => e.name).filter(n => n.includes('space_id')).map(n => n.match(/space_id=(\d+)/)).filter(m => m).map(m => m[1]).filter((v, i, a) => a.indexOf(v) === i)
   ```

2. **get_info 以该 token 为根**（判断是否独立分享节点）：
   ```
   /space/api/wiki/v2/tree/get_info/?space_id=<SID>&with_space=true&with_perm=true&expand_shortcut=true&need_shared=true&exclude_fields=5&with_deleted=true&wiki_token=<TOKEN>
   ```
   - 返回 `nodeCount: 1` 且 `child_map` 为空 → 该 token 是**独立分享节点**（不是知识库树的一部分）
   - 实测：README 的 space 树里只有 README 一个节点；第二、三篇也各自只返回自己 → 6 篇是 6 个独立分享，互不隶属

3. **get_node 判定权限/归属**：
   ```
   /space/api/wiki/v2/tree/get_node/?wiki_token=<TOKEN>&space_id=<SID>&expand_shortcut=true&with_deleted=true
   ```
   - `{"code": 920004002, "msg": "SourceNotExist"}` → token 不在该 space 或当前身份无权限 → 与登录墙现象互相印证

4. **wiki_token ≠ obj_token**：wiki 短链 token 与 docx 正文 token（obj_token）是两套。get_info 响应里的 `obj_token` 才是文档 token（实测 README wiki→N8y2dVov1ojLPEx8izgcsnaYnRv，RAG 问答 wiki→DKPfdWzcnobcl8xiwEWcUf5hnAb）。拿不到 get_info 就无从猜 docx 链接，登录墙下两条路都断。

## 决策

- 登录墙文档：停止重试，向父代理/用户报告——需要用户用已登录飞书的账号扫码登录浏览器（登录后会话延续，密码墙 cookie 也还在），或核对分享链接是否给错/权限是否开放
- 可继续抓取其余匿名可开的文档，不阻塞整体进度（本次 6 篇中 3 篇照常完成）

## 附：切片大小的实测数据点

626 块 / 30545 字符的文档按 280+280+66 三片取回成功（每片约 14~16K 字符，浏览器输出未截断）。切片上限按**字符数**（~15K/片）把握即可，块数 85~155 是保守默认；平均每块字符少时（~50 字符/块）单片 280 块没问题。
