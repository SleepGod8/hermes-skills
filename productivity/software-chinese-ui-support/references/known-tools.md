# 常见开发工具中文界面支持速查（2026-08 核验）

| 工具 | 中文 | 说明 |
|------|------|------|
| Docker Desktop 4.83.0 | ❌ | 官方仅英文无语言切换；社区汉化包只到 4.9.1 且已弃坑（app.asar 替换，版本差大=白屏） |
| Redis Insight 2.x | ❌ | 无 i18n 目录，纯英文 |
| Redis Insight 3.x | ❌ | 刚加 i18n 框架，`SUPPORTED_LANGUAGES=['en','bg']`，语言切换器仍是 TODO |
| Portainer CE | ✅ | Web 管理面板官方中文，Settings 切换；`docker run -d -p 9000:9000 -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce:latest` |
| Another Redis Desktop Manager (ARDM) | ✅ | qishibo/AnotherRedisDesktopManager，免费开源（28k+ stars），Windows 全中文界面，Redis Insight 最佳中文替代 |
| QuickRedis | ✅ | 免费有中文，功能弱于 ARDM |
| Redis Desktop Manager (RDM) | ⚠️ | 仅社区汉化/付费版含中文 |

## 核验来源

- Docker Desktop：github.com/raccoon666666/DockerDesktopChinese README（适配 4.9.1，作者弃坑）；本机 4.83.0 实测无语言选项
- Redis Insight：github.com/RedisInsight/RedisInsight main 分支 `redisinsight/ui/src/i18n/i18n.constants.ts`（SUPPORTED_LANGUAGES=['en','bg']）与 `i18n.ts`（TODO 语言切换器）；2.x tags（2.16.0~2.64.1）无 i18n 目录
- ARDM：github.com/qishibo/AnotherRedisDesktopManager（中文界面，releases 提供 .exe）
