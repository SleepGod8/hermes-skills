# Milvus 迁移包还原部署（2026-08-07 实测）

场景：把另一台机器打包的 milvus-docker-migration.tar.gz（docker-compose.yml + volumes/{etcd,milvus,minio}）还原到本机。

## 部署位置与最终状态

- 解压目录：`E:\ai1\milvus-docker`（用户偏好工作目录）
- 数据卷：84M（etcd 8 文件 + milvus 38 文件 + minio 149 文件，共 197 项）
- 服务：milvus-etcd / milvus-minio / milvus-standalone(v2.6.1) / attu
- 端口：19530(Milvus) 9091(healthz) 9100/9101(minio) **9500(attu，原 8900 被保留段占用)**

## 迁移包完整性校验（还原前先做）

```bash
gzip -t <包>.gz                                   # gzip 完整性
tar -tzf <包>.gz | wc -l                          # 文件数核对（197）
tar -tzf <包>.gz | awk -F/ '{print $1"/"$2}' | sort -u   # 确认三卷 + compose 都在
tar -xzf <包>.gz -O docker-compose.yml            # 抽查 compose 内容
```

## Docker Desktop 启动（daemon 没跑时）

```bash
powershell.exe -NoProfile -Command "Start-Process 'E:\Docker\Docker Desktop.exe'"
# 轮询等 daemon：for i in $(seq 1 24); do docker info >/dev/null 2>&1 && break; sleep 10; done
```
注意：Docker Desktop 起来后，其他 `restart: always` 的 compose 栈（如 Dify）会自动跟着起。

## 拉镜像时间线（镜像源限速 ~1MB/s）

- etcd/minio/attu 三个小镜像：几分钟内就位
- milvusdb/milvus:v2.6.1（~1.1GB，首个 layer 487-750MB）：**15-25 分钟**
- 首次 up 卡死 10 分钟无进展 → kill 后用 daemon 自己重试即恢复（第一次可能是回落 Docker Hub 直连挂起）
- 诊断细节见 SKILL.md「拉镜像卡死诊断」；du 数据盘 0 增长 = 卡死

## 端口保留段实测

`netsh interface ipv4 show excludedportrange protocol=tcp` 输出：
```
1369-1468, 2869, 5357, 8482-8581, 8582-8681,
8749-8848, 8849-8948, 8949-9048,   ← 三连段覆盖 8749-9048，attu 8900/8901 都中招
9181-9280, 50000-50059*
```
- 8900/8901 报 `bind: An attempt was made to access a socket in a way forbidden by its access permissions`
- 换 9500 成功（9281+ 段安全）
- 改完 `docker compose up -d attu` 单独重建（会 Recreate）

## 验证

```bash
docker compose ps                      # standalone 应 Up (healthy)
curl -s http://localhost:9091/healthz  # OK
python -c "from pymilvus import MilvusClient; c=MilvusClient(uri='http://localhost:19530'); print(c.list_collections())"
```
本包数据：documents=5, rag_citation_demo=2, rag_minimal_demo=4, resume_vectors=13, resume_vectors_test=11。

## 遗留注意

- 迁移后建议改 minio 默认账号 minioadmin/minioadmin
- 容器名冲突处理：见 SKILL.md「中断 compose up 后的残留容器」（compose down 清残留）
