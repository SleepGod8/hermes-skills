# Dify 跨机迁移打包 (Docker Compose → 另一台 Docker)

把本机 Docker Compose 部署的 Dify 完整搬到另一台电脑。核心要点:**源码不是数据,`docker/volumes/` 才是**。

## 部署模型(先认清)

- Dify 官方 Docker 部署用 `docker compose`,**数据全部通过 bind-mount** 存在项目目录下 `docker/volumes/`,**不是 Docker 命名卷**(`docker volume ls | grep dify` 通常为空)。
- 因此迁移 = **复制 `docker/` 目录**(`.env` + `docker-compose*.yaml` + `volumes/`)即可,无需动 Docker 命名卷。
- 判断实际启用的 DB:`docker ps --format '{{.Names}}' | grep -i db`。默认 `db_postgres`(PostgreSQL)。

## 关键数据目录(按重要性)

| 路径 | 内容 | 重要 |
|------|------|------|
| `volumes/db/data/` | **PostgreSQL 数据(pgdata)** | 核心,丢了即应用数据全失 |
| `volumes/app/storage/` | 上传文件、应用私钥、`.dify_secret_key` | 高 |
| `volumes/weaviate/` | 向量库数据 | 高 |
| `volumes/redis/` | 缓存(可重建) | 低 |
| `volumes/plugin_daemon/` | 插件数据 | 中 |
| `volumes/certbot/` | SSL 证书(可忽略) | 低 |
| 未启用服务目录(mysql/oceanbase/seekdb/qdrant/pgvector) | 不用的可忽略 | 忽略 |

## 打包步骤(本机)

```bash
# 估算体积
cd /d/dify/docker && du -sm volumes/db volumes/app   # 但 du 在超大目录(WSL 挂载/大 weaviate)可能超时,分项统计更稳

# 打包核心项到迁移包
mkdir -p /d/dify-migration
tar -czf /d/dify-migration/dify-docker-migration.tar.gz \
  -C /d/dify \
  docker/docker-compose.yaml docker/docker-compose-template.yaml \
  docker/.env docker/volumes
```

**git-bash/MSYS 坑**:`tar` 的路径用 `D:/...` 会报 `tar (child): Cannot connect to D: resolve failed`(把 `D:` 当远端主机)。**必须用 MSYS 路径 `/d/...`**,或 `cd` 进目录后用相对路径。

**git-bash/MSYS 坑 2 (`taskkill` 双斜杠)**:在 git-bash 里 `taskkill //F //PID 29984` 会把 `//F` 转义成字面路径参数,报 `无效参数/选项 - '//F'`。**必须用单斜杠** `taskkill /F /PID <pid>`。同理 `tasklist //FI "..."` 过滤也不可靠(直接 `tasklist | grep -w <pid>` 更稳)。可用 `wmic process where "ProcessId=<pid>" get CommandLine /format:list` 确认进程命令行(如 `--worker-profile hebe`)再决定杀不杀。

校验:
```bash
gzip -t <pkg> && tar -tzf <pkg> | grep -E "docker/volumes/db/data" 
```

## 还原(新机器)

```bash
tar -xzf dify-docker-migration.tar.gz   # 得到 docker/
cd docker && docker compose up -d       # 自动拉镜像 + 加载 volumes 数据
docker compose ps                        # 全部 Up/healthy
```

- 端口/密码修改 → 改 `.env` 的 `NGINX_PORT`/`DIFY_PORT`/`DB_PASSWORD` 再 `up -d`。
- 用 `.env` 里的 `INIT_PASSWORD` 登录。

## 离线方案(新机器无法访问 Docker Hub)

镜像需在本机先导出、新机导入:
```bash
docker compose images    # 拿到全部当前镜像:tag
docker save <img1>:<tag> <img2>:<tag> ... -o dify-images.tar   # 所有服务镜像 + 数据卷镜像(postgres/redis)
docker load < dify-images.tar                                  # 新机
```

## 传输尺寸参考

`docker/` 源目录约 392MB(其中 db 93MB),tar.gz 压缩后约 112MB,44k 文件。可放 U 盘 / 局域网拷到新机。
