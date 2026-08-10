---
name: software-chinese-ui-support
description: "调查软件是否支持中文界面 & 找中文替代品：官方语言支持核验法（GitHub 仓库 i18n 结构检查，比搜索引擎可靠）+ 常见开发工具中文支持速查（Docker Desktop / Redis Insight 无中文，Portainer / ARDM 有）。Use when 用户问某软件/工具有没有中文 / 中文界面 / 汉化 / Chinese UI / 中文替代品。"
version: 1.0.0
author: agent
license: MIT
tags: [chinese, i18n, localization, software-selection, github-api]
---

# 软件中文界面支持调查

用户（中文用户）常问「XX 有中文吗？」。回答前**先核验，不要凭印象**——2026-08 实测推翻一个直觉答案：Redis Insight 曾被认为有中文，实际 2.x 无 i18n、3.x 只有 en+bg。

## 触发条件

- 用户问某软件/工具有没有中文界面、支不支持中文、有没有汉化版
- 用户要找某工具的中文替代品（容器/数据库 GUI 等）

## 核验方法（按可靠性排序）

1. **GitHub 仓库直接查 i18n 结构**（最可靠，避开搜索引擎反爬）：
   - 列仓库目录：`https://api.github.com/repos/<org>/<repo>/contents/<path>?ref=<tag>`，找 `i18n/`、`locales/`、`translations/` 目录
   - 找语言常量文件（i18next/react-i18next 项目常见 `i18n.constants.ts` / `i18n.ts`）：`SUPPORTED_LANGUAGES = [...]` 一行定生死
   - 例：RedisInsight `redisinsight/ui/src/i18n/i18n.constants.ts` → `['en','bg']`，且语言切换器还在 TODO（`?lang=bg` 临时参数）
   - 查历史 tag：老版本连 i18n 目录都没有 = 历代都不支持多语言
2. **官方文档 / release notes**：搜 "language" / "localization"，但文档常滞后于代码。
3. **GitHub issues**：`search/issues?q=repo:<org>/<repo>+chinese+language`。
4. **搜索引擎**：bing/duckduckgo 直接抓 HTML 经常被反爬返回空页 → 放弃，直接走 GitHub API。

### 网络坑（本机）
- curl 访问 `api.github.com` / `raw.githubusercontent.com` 必须带代理绕过：`curl -s -c "http.proxy=" -c "https.proxy=" URL`（与 git 同款，见 memory）。
- GitHub tree API `?recursive=1` 对超大树可能超时/截断 → 改列具体子目录。

## 通用规律

- **Electron 桌面应用汉化包（替换 app.asar 等资源）一律不推荐**：随版本升级失效、作者常弃坑、版本差太多直接白屏。官方无中文就换工具，不折腾汉化。
- **Web 管理面板通常有多语言**（Portainer 官方中文）——容器/中间件 GUI 优先推荐这类。
- 找中文替代优先国产/开源项目（ARDM、QuickRedis 等），stars 数可佐证活跃度。

## 已核验工具速查（2026-08）

见 `references/known-tools.md`。每次新核验一个工具，补进该表（工具名 + 版本 + 中英文状态 + 核验来源）。

## 参考

- `references/known-tools.md` — 常见开发工具中文界面支持状态表（含核验来源）
