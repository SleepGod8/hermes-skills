# Milvus 跨机迁移 + standalone 崩溃诊断 (Docker Compose)

同 Dify 的迁移通用模型:数据全在 bind-mount 的 `volumes/`,迁移 = 复制 compose + volumes。区别在于 Milvus 是 **etcd + minio + standalone(4 容器)** 组合,三个数据卷缺一不可。

## Milvus 部署模型

| 容器 | 镜像 | bind-mount 数据卷 |
|------|------|------------------|
| milvus-standalone | milvusdb/milvus:v2.6.1 | `volumes/milvus` (→/var/lib/milvus) |
| milvus-etcd | quay.io/coreos/etcd:v3.5.18 | `volumes/etcd` (→/etcd) |
| milvus-minio | minio/minio:RELEASE... | `volumes/minio` (→/minio_data) |
| attu (可选) | zilliz/attu | 无数据(可视化 UI,端口 8900) |

**关键**:`volumes/etcd`(元数据)、`volumes/milvus`(数据+本地索引)、`volumes/minio`(对象存储底层)**三者共同组成存储,缺一不可**。用 `docker inspect <容器> --format '{{range .Mounts}}{{.Type}} {{.Source}} -> {{.Destination}}{{println}}{{end}}'` 确认 bind 源。

## 迁移打包 / 还原

**打包前先停容器**(保证数据静止一致):
```bash
docker stop milvus-standalone milvus-etcd milvus-minio attu   # 注意:resume-minio/resume-mysql 是别的项目的,别停
mkdir -p /d/milvus-migration
cd /d/milvus-docker && tar -czf /d/milvus-migration/milvus-docker-migration.tar.gz -C /d/milvus-docker docker-compose.yml volumes
gzip -t ... && tar -tzf ... | grep -E 'volumes/(etcd|milvus|minio)'   # 校验
```

**新机还原**:
```bash
tar -xzf milvus-docker-migration.tar.gz
docker compose up -d      # 拉 4 个镜像 + 加载 volumes
curl -s localhost:9091/healthz   # 期望 OK (standalone 健康端口 9091, gRPC 19530)
```

## 离线方案(新机无外网)

```bash
docker save quay.io/coreos/etcd:v3.5.18 minio/minio:RELEASE.2024-05-28T17-19-04Z \
  milvusdb/milvus:v2.6.1 zilliz/attu:latest -o milvus-images.tar
# 新机
docker load < milvus-images.tar
```

## 崩溃诊断:Exited(134) + goroutine dump

**症状**:`docker ps -a` 显示 standalone `Exited (134)`(Go panic → SIGABRT → exit 134)。日志尾部是几十万行 goroutine 栈 dump。

**定位根因方法**(日志可能 69 万行):
```bash
docker logs milvus-standalone 2>&1 | grep -nE "panic:|SIGABRT|fatal error|runtime error"   # 找 panic 触发行号
docker logs milvus-standalone 2>&1 | sed -n '<panic行号前后各30行>p'                        # 看崩溃前上下文
```

本次遇到:`panic: failed to create etcd client: context deadline exceeded` —— standalone 启动瞬间连 etcd 超时。属**瞬时故障**(当时 Docker/系统网络波动),etcd 本身 healthy,数据未损。

**修复**:确认 etcd healthy(`docker exec milvus-etcd etcdctl endpoint health`)后干净重启:
```bash
docker start milvus-standalone     # compose 里 standalone 无 restart 策略,崩一次即停,需手动启
sleep 20 && docker ps --filter name=milvus-standalone   # 期望 Up (healthy)
```

**注意**:`docker compose up -d` 在 Hermes git-bash terminal 可能被误判为"长驻服务"而拒绝执行;用 `docker start <names>` 逐个启动已存在容器更稳。

## 验证数据完整性

```bash
# pymilvus(新版用 MilvusClient —— ORM 的 utility.list_collections/get_collection_stats 已废弃)
python -c "
from pymilvus import MilvusClient
c = MilvusClient(uri='http://localhost:19530')
print(c.list_collections())
for col in c.list_collections():
    s = c.get_collection_stats(col)
    print(col, s.get('row_count'))
"
```

## 迁移前的健康优先级

主人若遇到容器异常退出,先 `clarify` 是"直接打包"还是"先修复确认数据可用再打包"。优先修好确认数据完好再迁,避免打包一份坏数据。
