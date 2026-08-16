---
name: web-resource-download
description: "Use when 下载网页文件/游戏. DevTools抓包, Cloudflare验证, Flash存档。"
version: 1.0.0
author: Hermes Agent + agent
tags: [download, flash, swf, devtools, cloudflare, ruffle, flashpoint]
---

# Web Resource Download (网页文件/游戏/媒体下载)

下载网页上的二进制资源(.swf Flash 游戏、视频、图片、安装包等)的完整套路。
实测案例: 2026-08 从 comdotgames 站下载 Flash 游戏(comdotcdn.com CDN)。

## 1. 定位资源真实地址 (DevTools Network)

- F12 → Network 面板 → 刷新页面 → 按类型/关键字过滤(如 `swf`)
- ⚠️ **新版 Chrome 的 Network 面板右键菜单【没有】单文件 "Save as" 选项** —
  只有 "Save all as HAR with content"(保存全部)。用户找不到是正常的, 不是操作错!
- 正确姿势:
  - 右键请求 → **「在新标签页中打开」** → 浏览器直接下载/显示 → 没自动下就 Ctrl+S
  - 或右键 → 复制 → 复制链接地址 → 新标签打开或 curl/wget 下载
  - 或点开请求详情, 从 Headers 的 Request URL 复制完整地址
- 游戏常是加载器模式: 页面主 .swf 和真正的游戏 .swf 可能在不同域/路径

## 2. 直接下载 (curl)

```bash
curl -sL -o game.swf "URL" \
  -H "Referer: https://游戏站域名/" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
```
- 很多 CDN 需要 Referer/UA, 否则 403
- `-w "HTTP:%{http_code} SIZE:%{size_download}"` 看真实结果; HTTP:000 = 没连上(见下节)

## 3. Cloudflare 人机验证 (Turnstile) 拦路 — 直接转人工

实测 (comdotcdn.com, 2026-08):
- `curl -sL` 对 https 返回 **HTTP:000**(Cloudflare 拦 curl 的 TLS 指纹); http 先 301→https 然后同样失败
- headless 浏览器/自动化点 Turnstile「请验证您是真人」复选框会**无限循环**:
  「正在验证…」几秒后回到未勾选状态 — 自动化指纹被识别
- **唯一可靠路径: 让用户用自己的 Chrome 打开该 URL**, 勾选验证,
  验证通过后浏览器自动下载 .swf(或页面乱码则 Ctrl+S)
- 不要反复尝试 curl/换 headless 配置, 直接给出链接让用户动手, 省时省力

## 4. Flash 游戏专项

- 游戏已死/源文件找不到 → 用存档库:
  - **BlueMaxima's Flashpoint** (https://flashpointarchive.org) — 10万+ 游戏离线版
  - Internet Archive (archive.org) 搜 `flash games` 合集
- 本地播放 .swf → **Ruffle** (https://ruffle.rs) 浏览器扩展/桌面版, 兼容性已很好
- 拆解资源 → **JPEXS Free Flash Decompiler** (FFDEC) 反编译 .swf, 导出图片/音频/代码

## 5. 从截图读取 URL (vision 兜底)

用户发 DevTools 截图时, 让 vision 模型读图提取完整 URL(模型会截断, 专门追问
「一字不差完整输出 URL」)。若 Hermes 的 auxiliary.vision 报
`No LLM provider configured for task=vision provider=custom:X` 而 API 实际可用,
用 `scripts/zhipu_vision_probe.py` 直连 OpenAI 兼容端点看图:
```bash
python scripts/zhipu_vision_probe.py <image.png> "完整输出那个 .swf 请求的 URL, 不要截断"
```
细节: Zhipu glm-4.6v-flash 免费; 复杂问题偶尔返回空内容 → 重试; 429 = 模型名有效但过载 → 退避重试。
