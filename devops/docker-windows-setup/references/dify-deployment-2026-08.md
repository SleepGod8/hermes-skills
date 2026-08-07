# Dify 1.16 Docker 迁移部署实录（2026-08-07）

新机器（Windows 10 家庭版 + Docker Desktop + WSL2）还原 Dify 迁移 tar 包的全过程与修复。

## 环境

- Docker Desktop 4.83.0 装于 E:\Docker（非 C 盘）
- WSL2 2.7.11（内核 6.18.33.2）
- Dify 1.16.0 迁移包（112MB，44661 文件）
- 部署目录 E:\dify\docker

## 部署步骤

1. 解压迁移包：`tar -xzf dify-docker-migration.tar.gz`（Windows 自带 tar；symlink 会解压失败，见下）
2. `docker compose up -d`（先配镜像加速器，见 SKILL.md）

## 遇到的坑（按序）

### 1. 拉镜像断连
`short read: expected 664057617 bytes but got 58942703: unexpected EOF`
→ 配 registry-mirrors + 重启 Docker Desktop（详见 SKILL.md「国内镜像加速」）。之后拉取正常（12 镜像约 10GB）。

### 2. plugin-daemon tag 不存在
compose 硬编码 `langgenius/dify-plugin-daemon:0.6.3-local`，Docker Hub 上不存在（`docker manifest inspect` 失败）。
查可用 tag：代理访问 `https://hub.docker.com/v2/repositories/langgenius/dify-plugin-daemon/tags?page_size=30`
→ 有 `0.6.10-local`、`latest-local` 等。
→ 改 compose：`image: langgenius/dify-plugin-daemon:0.6.10-local`
→ 拉取成功（0.6.3-local 实际最终也拉下来了——加速器缓存里可能有，但不要依赖）。

### 3. nginx/ssrf_proxy 循环重启：迁移包 symlink 解压失败
症状：`docker logs docker-nginx-1` 反复报
`cp: -r not specified; omitting directory '/docker-entrypoint-mount.sh'`
容器 `Restarting (1)`。

根因：迁移 tar 包里的 nginx 配置文件是 **Linux symlink**，Windows tar 解压失败 → 生成**空目录**（`E:\dify\docker\nginx\docker-entrypoint.sh` 是空目录）。Docker 挂载空目录 → 容器 entrypoint 脚本 cp 时报 "omitting directory"。

检查方法：`ls -la E:\dify\docker\nginx/` 看到 0 大小的"目录"（带 d 权限）就是中招。

修复：从 Dify 官方 GitHub 按版本下载补全（走代理 raw.githubusercontent.com）：
```
docker/nginx/   docker-entrypoint.sh, nginx.conf.template, proxy.conf.template, https.conf.template, conf.d/default.conf.template
docker/ssrf_proxy/  docker-entrypoint.sh, squid.conf.template
```
base URL: `https://raw.githubusercontent.com/langgenius/dify/1.16.0/docker/...`
然后 `docker compose up -d nginx ssrf_proxy` 重建。

### 4. 其他
- `startupscripts/` 挂载缺失 → 是 oracle 可选服务用，默认 compose 不启动，忽略。
- certbot/ 目录缺失 → 可选 HTTPS 服务，默认忽略。

## 验证

- `docker ps`：api/worker/web/plugin_daemon/postgres/redis/weaviate/sandbox 全部 `Up(healthy)`
- nginx 是 Web 入口（默认 80 端口），nginx 健康 = 可访问 `http://localhost`
- 用 .env 的 INIT_PASSWORD 登录
