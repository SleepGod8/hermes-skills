# 团队项目 Docker 封装（compose 模式）— 2026-08 实测

给多人协作项目（如智能财富管家系统：FastAPI+MySQL+Milvus+Neo4j+Redis+MinIO）封装容器的实测模式。演示项目在 `workspace/docker-demo/`（FastAPI 最小封装，已 build+run+curl 验证通过）。

## 三个文件的最小模式

**Dockerfile**（缓存层顺序是关键）：
```dockerfile
FROM python:3.12-slim
WORKDIR /app
# 依赖先复制 → 依赖不变时该层缓存，改代码不重装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# 代码后复制（经常改）
COPY app ./app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**.dockerignore**：必排除 `.env`、`.git`、`__pycache__/`、`venv/`——密钥永远不进镜像。

**docker-compose.yml** 要点：
- 开发期代码挂载 + `--reload` 热重载：`volumes: - ./app:/app/app`
- 数据卷 `db_data:/var/lib/mysql`：容器删了数据不丢
- **端口冲突**：本机已有服务占端口时改映射（本机 MySQL 3306 → 容器 MySQL 映射 3307）

## 验证命令

```bash
docker build -t <name> .
docker run -d --name <name> -p 8000:8000 <name>
curl -s http://localhost:8000/health   # 必须实测返回，不能只看容器 Up
docker images <name> --format "{{.Size}}"  # 检查镜像大小（slim 基础镜像 ~212MB 合理）
```

## 本机端口地图（2026-08-10，智能财富管家项目）

| 服务 | 容器 | 端口 | 备注 |
|------|------|------|------|
| MySQL 9.7 | Windows 服务（非容器） | 3306 | 容器版映射用 3307 |
| Redis | my-redis | 6379 | |
| Neo4j | neo4j:latest | 7474/7687 | 首次要改默认密码 |
| Milvus | milvus-standalone v2.6.1 | 19530 | attu 面板 9500 |
| MinIO | milvus-minio | 9100/9101 | |
| Dify | docker-* | 80/443/5003 | 全家桶 |
| Portainer | portainer | 9000 | |

即项目 6 个基础设施中 5 个本机已跑——本机可作为团队「环境样板机」，端口方案直接照抄给团队 compose。8749-9048 曾被 Win 保留，**部署前重新查** `netsh interface ipv4 show excludedportrange protocol=tcp`。

## 团队落地顺序

1. 一人写基础 Dockerfile/compose（建议环境负责人，如本机有全套组件的人）
2. 密钥走 `.env`（已被 .gitignore 排除）+ compose `environment` 注入
3. 数据库容器必须配数据卷
4. 团队大时推镜像仓库（阿里云 ACR/腾讯 TCR），成员 `docker pull` 同一镜像
