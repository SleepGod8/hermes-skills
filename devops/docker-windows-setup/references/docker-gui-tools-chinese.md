# Docker 相关 GUI 工具中文支持现状（2026-08-10 实测验证）

用户连续问 Docker Desktop / Redis Insight / Portainer 是否支持中文 → 逐一用 GitHub 源码验证。**速查表 + 验证方法 + 兜底方案**。

## 速查表

| 工具 | 官方中文 | 说明 |
|------|---------|------|
| Docker Desktop 4.83.0 | ❌ | 官方仅英文，无语言切换选项。社区汉化包（GitHub raccoon666666/DockerDesktopChinese）仅适配 4.9.1，作者弃坑；新版替换 app.asar 会白屏 |
| Redis Insight 3.x | ❌ | 3.x 才引入 i18n 框架，但 `SUPPORTED_LANGUAGES = ['en','bg']`（英文+保加利亚语），语言切换器仍是 TODO；2.x 无任何多语言文件 |
| Portainer CE 2.39.5 | ❌ | 官方 `translations/` 目录仅 `en/`；中文支持 PR #12700（2025-05 提）至今 open 未合并 |
| Another Redis Desktop Manager (ARDM) | ✅ | 免费开源（qishibo/AnotherRedisDesktopManager），完整中文界面，集群/哨兵/SSH 隧道，Redis Insight 最佳中文替代 |
| QuickRedis | ✅ | 免费中文，功能弱于 ARDM |
| 1Panel | ✅ | 国产开源面板，原生中文，容器/镜像/网络/卷 + 网站/数据库管理，Portainer 的中文替代 |

## 验证方法（别再凭记忆说"支持中文"）

教训：凭印象推荐"Portainer Settings 里切中文"→ 用户找不到 → 当场打脸。**推荐任何工具支持某语言前，用 GitHub 源码验证**：

1. **查翻译目录**：`GET /repos/<owner>/<repo>/contents/<path>` 找 `translations/`、`locales/`、`i18n/`，列出语言文件。
   - Portainer: `translations/` 仅 `en/`
   - Redis Insight: `redisinsight/ui/src/i18n/i18n.constants.ts` → `SUPPORTED_LANGUAGES = ['en','bg']`
2. **查语言常量/配置**：i18n constants、语言下拉枚举。
3. **查 open PR/issue**：`search/issues?q=repo:<owner>/<repo>+chinese+language+in:title`——PR 还 open = 没落地。
4. **查 tag/release**：大版本重写可能砍掉旧能力（Redis Insight 2.x→3.x 重写后语言支持反而更少；tag 名不带 v 前缀，如 `2.64.1`）。

## 兜底方案

- Web 类工具（Portainer 等）：Chrome/Edge 右键「翻译成中文」，零成本。
- 想要原生中文：优先国产工具（ARDM、1Panel、QuickRedis）。
- 涉及容器管理时：Portainer 部署配方与坑见 SKILL.md 主文件。

## 相关坑

- Portainer 2.39+ 初始化管理员必须填 **Setup token**（`docker logs portainer | grep setup_token`，一次性，创建管理员后失效；泄露可被抢先初始化劫持）。加 `--no-setup-token` 启动参数可禁用。
