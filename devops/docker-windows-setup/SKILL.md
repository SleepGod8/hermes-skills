---
name: docker-windows-setup
description: "Windows 装 Docker+WSL2+镜像加速+compose部署。提权/bat/tag/symlink坑。"
version: 1.0.0
author: agent
license: MIT
tags: [docker, wsl2, windows, docker-desktop, compose, dify, mirror]
platforms: [windows]
---

# Docker Windows Setup & Deployment

Windows 上从零装 Docker Desktop（装到非 C 盘）、配 WSL2 后端、国内镜像加速，以及部署 docker compose 应用（实测 Dify 1.16 迁移）。本技能记录 2026-08-07 全流程踩过的坑。

## 触发条件

- 用户要在 Windows 上安装 Docker Desktop / 启用 WSL2
- docker compose 应用部署失败（拉镜像断连、镜像 tag 不存在、容器循环重启）
- 用户偏好软件装 E 盘等非系统盘

## 安装 Docker Desktop 到非 C 盘（实测流程）

1. 安装包静默安装（装到 E:\Docker）：
   ```
   "Docker Desktop Installer.exe" install --quiet --accept-license --installation-dir="E:\Docker"
   ```
2. **UAC 提权坑**：Hermes 后台终端会话**无法弹出交互式 UAC**（PowerShell `Start-Process -Verb RunAs` 报 InvalidOperationException；schtasks /RL HIGHEST 也失败）。**必须让用户手动右键 bat → 以管理员身份运行**。这是唯一可靠路径。
3. **bat 中文乱码坑**：bat 文件 UTF-8 编码会被 cmd（GBK 代码页 936）解析成乱码 → 中文 echo 被当命令执行、中文路径找不到。**规则：bat 全英文 + 安装包复制到无中文路径**（如 `D:\软件\...` 里的「软件」必乱码，复制到 `E:\ai1\DockerDesktopInstaller.exe`）。
4. git-bash 直接传 `--installation-dir="E:\Docker"` 参数可能失效（引号被吞）→ 放 bat 里写死路径最稳。
5. 验证：`E:\Docker\resources\bin\docker.exe --version`；`com.docker.service` 服务已注册（`Get-Service *docker*`）。

## WSL2 后端（Win10 家庭版必需）

Win10 家庭版没有 Hyper-V，Docker Desktop 必须用 WSL2 后端。三件套缺一不可：

1. **启用 Windows 功能**（dism，需管理员）：
   ```
   dism /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
   dism /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
   ```
   必须**重启电脑**才生效（/norestart 挂起）。
2. **WSL2 内核 MSI**（`wsl_update_x64.msi`，~17MB）：
   - 官方源 `https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi` 国内慢（>2 分钟下不完）→ **走代理秒下**（Python urllib + ProxyHandler 最稳，curl -o 在 git-bash 会静默失败）。
   - `msiexec /i wsl_update_x64.msi /quiet /norestart`
3. **完整 WSL 应用（Store 版 2.x）**：`wsl --version` 仍报"未安装"= 缺 WSL Appx。wsl.exe 的 `--install` 从 GitHub 下载极慢（0.3% 卡住）→ 用代理从 GitHub Releases 下载 msixbundle：
   ```
   https://github.com/microsoft/WSL/releases/download/<ver>/Microsoft.WSL_<ver>.0_x64_ARM64.msixbundle
   ```
   （~494MB，代理下 3.3MB/s）。安装 `Add-AppxPackage` **需要管理员**（0x80073D28 提权错误）→ 又走用户手动运行 bat。
4. 注意区分：`wsl_update_x64.msi` = 内核；GitHub 的 msixbundle = 完整 WSL 应用，两个都要。

## 国内镜像加速（拉 Docker Hub 镜像断连时）

症状：`docker compose up` 拉镜像报 `short read: expected X bytes but got Y: unexpected EOF`（国内连 Docker Hub 不稳）。

修复：改 `%USERPROFILE%\.docker\daemon.json`（Docker Desktop daemon 配置；write_file 拒绝写受保护文件 → 用 Python json 读写）加 registry-mirrors，然后**重启 Docker Desktop** 才生效：
```json
{ "registry-mirrors": ["https://docker.m.daocloud.io", "https://docker.1ms.run", "https://docker.xuanyuan.me", "https://dockerproxy.net"] }
```
验证：`docker info | grep -A5 "Registry Mirrors"`。

### 拉镜像卡死（不是断连）诊断

症状：`docker compose up` 长时间停在 `Downloading` 同一进度不动。Docker Hub 直连在国内是**超时**（`curl -m 10 https://registry-1.docker.io/v2/` → 000），daemon 在镜像源缺 layer 时会回落 Docker Hub → 挂起。

诊断步骤：
1. **看数据盘是否增长**：`du -sh <docker-data目录>` 隔 30 秒对比（本例 E:\docker-data 0 增长 = 卡死；在涨 = 只是慢，耐心等）。本例 750MB 大 layer 走镜像源只有 ~1MB/s，milvus v2.6.1 约 1.1GB 拉 15-25 分钟属正常。
2. **测加速源连通性**：对 `https://<mirror>/v2/<org>/<repo>/manifests/<tag>` 发请求（带 `Accept: application/vnd.docker.distribution.manifest.list.v2+json`）。**401 是正常的**（registry token 认证，非失败）；**完全没有 WWW-Authenticate 响应 = 该源不可达/不代理**（实测 docker.xuanyuan.me、dockerproxy.net 均不可达，daocloud/1ms.run 可用）。
3. **token 服务地址从 401 的 WWW-Authenticate realm 拿**，不要猜：
   - daocloud realm：`https://m.daocloud.io/auth/token`（注意**不是** `docker.m.daocloud.io/token`，猜错会 TOKEN_FAIL）
   - 1ms.run realm：`https://docker.1ms.run/openapi/v1/auth/token`
4. 镜像源可用时不需要手动干预，重启 `docker compose up -d` 让 daemon 自己走镜像源即可。

### 中断 compose up 后的残留容器

`docker compose up -d` 是**边拉镜像边建容器**的：拉到一半杀掉进程，已建容器会残留，再次 up 报 `Conflict. The container name "/xxx" is already in use by container "..."`。修复：`docker compose down` 清残留（volumes 若是 bind mount 到宿主机则数据不丢），再 up。注意 compose 输出带 `version` 属性会告警 obsolete（无害，可删）。

## docker compose 部署常见坑

- **镜像 tag 不存在**：`docker compose up` 卡在拉取重试。查 Docker Hub 可用 tag（代理访问 `https://hub.docker.com/v2/repositories/<org>/<repo>/tags`），把 compose 的 image 改成存在的 tag。实例：`langgenius/dify-plugin-daemon:0.6.3-local` 不存在，改 `0.6.10-local` 可用。
- **tar 迁移包 symlink 解压失败**（Windows tar 不支持 Linux symlink）：配置文件目录变空目录 → 容器报 `cp: -r not specified; omitting directory '...'` 循环重启。修复：从上游 GitHub raw 按版本下载补全（走代理），如 Dify 1.16 的 `docker/nginx/`、`docker/ssrf_proxy/` 下 5+2 个文件。检查：`ls -la` 看到空目录即中招。
- compose 默认启动的服务看 `docker compose config --services`；可选服务（certbot/oracle/vastbase）挂载缺失不影响。

## Docker Desktop 引擎未运行（compose 连不上 daemon）

症状：`docker compose up` 立即报 `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine ... The system cannot find the file specified`。注意此时 `docker ps` 可能返回空**但不报错**，容易误判为"没有容器"而非"引擎没起"。

修复（2026-08 实测）：
```bash
# 用 PowerShell 启动（不要用 cmd //c start：中文路径/引号会被吞，进程起不来）
powershell -Command "Start-Process -FilePath 'E:\Docker\Docker Desktop.exe'"
# 轮询引擎就绪（WSL2 后端通常 10-60s）
for i in $(seq 1 24); do docker info >/dev/null 2>&1 && break; sleep 10; done
docker info 2>/dev/null | grep "Server Version"
```
启动后确认进程：`python -c "import psutil; print([p.info['name'] for p in psutil.process_iter(['name']) if 'docker' in (p.info.get('name') or '').lower()])"`。

## compose 端口冲突用 override 文件（不动仓库主文件）

本机已有服务占端口（如 Windows MySQL80 服务占 3306，容器 MySQL 也想绑 3306）时，**不要改仓库的 docker-compose.yml**（会污染团队文件、pull 冲突）。新建 `docker-compose.override.yml` 只覆盖冲突端口：

```yaml
# docker-compose.override.yml（compose 自动与主文件合并；建议 gitignore）
services:
  mysql:
    ports:
      - "3307:3306"   # 宿主 3307，容器内仍 3306，backend 连 mysql:3306 不受影响
```
`docker compose up -d --build` 会自动应用 override。容器间通信不受影响，只改宿主端口映射。本机 MySQL 实际版本以 `SELECT VERSION()` 实测为准（目录可能是 9.7、服务名 MySQL80、实跑 8.0.42——三处不一致时信连接实测）。


## Docker 相关工具中文界面（官方大多无中文）

**Docker Desktop 官方界面只有英文**，设置里没有语言切换（2026-08 实测 4.83.0）；社区汉化包（`raccoon666666/DockerDesktopChinese`）只适配 4.9.1、作者弃坑、新版替换 app.asar 会白屏 → 不要汉化。

⚠️ **Portainer 官方也无中文**（2.39.5 实测 + GitHub 确认：translations/ 仅 en，中文 PR #12700 未合并）——「Settings 里切中文」是错误说法，别再这么推荐。要中文：Web 工具用浏览器右键翻译；原生中文选 1Panel（国产面板）。各工具语言支持速查与验证方法见 `references/docker-gui-tools-chinese.md`。

## Portainer 部署（Web 容器管理面板）

```bash
docker volume create portainer_data
docker run -d -p 9000:9000 --name portainer --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data portainer/portainer-ce:latest
```
浏览器访问 `http://localhost:9000`。

坑：
1. **Setup token（2.39+ 新机制）**：首次初始化管理员必须填 Setup token（不填 Create user 按钮禁用）。token 打印在启动日志：`docker logs portainer | grep setup_token`。**一次性**（创建管理员后失效）；泄露可被抢先初始化劫持；`--no-setup-token` 启动参数可禁用。
2. **docker run 客户端超时 ≠ 失败**：拉镜像 + run 连写超时被 kill 后，daemon 端可能已创建容器。再跑报 `Conflict. The container name ... is already in use` → 先 `docker ps -a --filter name=portainer` 确认，已 Up 就不用重复 run（镜像此时其实已拉全，只需单独 docker run）。
3. **9000 端口**：bind 前按下一节「Windows 保留端口范围」重新查保留段（2026-08-10 实测 9000 可用）。

## docker 命令报 invalid reference format（隐藏 Unicode 字符）

症状：命令肉眼完全正常，如 `docker run -d --name my-redis -p 6379:6379 redis:latest`，却报：
```
docker: invalid reference format
Run 'docker run --help' for more information
```
（exit 125）。**最常见原因：从网页/微信/聊天记录复制命令时带入了零宽空格（U+200B，UTF-8 字节 `e2 80 8b`）**，Docker 解析镜像引用时遇到非法字符即报此错。已实测复现（Docker 29.6.2，2026-08）。

排查与验证：
```bash
# 1. 十六进制转储看命令末尾是否有 e2 80 8b
printf 'docker run -d --name my-redis -p 6379:6379 redis:latest\xe2\x80\x8b' | xxd | tail -2
# 2. PowerShell 检查字符串长度（redis:latest 正常为 12，大于 12 即藏了字符）
('redis:latest').Length
# 3. 列出所有非 ASCII 字符
('redis:latest').ToCharArray() | ForEach-Object { if ([int]$_ -gt 127) { "隐藏字符: U+{0:X4}" -f [int]$_ } }
```

修复：**手动重新敲一遍命令，不要复制粘贴**。通用规律：任何「肉眼正确但 CLI 报格式/参数错误」的复制命令，先怀疑隐藏 Unicode 字符（不只 docker，pip/git/curl 都可能中招）。

## Windows 保留端口范围导致端口绑定失败

症状：容器能创建但报 `Error response from daemon: ports are not available: exposing port TCP 0.0.0.0:8900 -> ... bind: An attempt was made to access a socket in a way forbidden by its access permissions`。**不是端口被占用**，是 Hyper-V/WinNAT 保留端口段。

排查命令：
```
netsh interface ipv4 show excludedportrange protocol=tcp
```
实测（2026-08 本机）：8749-8848、8849-8948、8949-9048 **三连段被保留**（覆盖 8749-9048），8900/8901 都中招；9100/9091/19530 不受影响。**避开保留段选端口**（本例 attu 改 9500）。改 compose 的 ports 后 `docker compose up -d <service>` 单独重建即可。

⚠️ **保留段是动态的，部署前必须重新查，不要复用旧结论**：2026-08-10（重启后）实测保留段已整体变化——当前为 2869、13817-13916、14124-14223、14224-14323、14324-14423、14424-14523、14524-14623、14624-14723、14828-14927、50000-50059，原先被卡的 **9000 已可正常绑定**（Portainer 部署成功）。每次 bind 端口前跑 `netsh interface ipv4 show excludedportrange protocol=tcp` + `netstat -ano | grep :<port>` 双确认。

## 验证清单

- [ ] `docker --version` + `docker info`（Server 在跑）
- [ ] `docker compose version`
- [ ] `docker ps` 目标容器 `Up(healthy)`
- [ ] 浏览器访问 Web 入口（Dify 默认 80 端口）

## 参考

- Dify 迁移部署细节：见 `references/dify-deployment-2026-08.md`
- Milvus 迁移包还原部署细节（含端口保留段实测、镜像拉取时间线、Docker Desktop 启动方式）：见 `references/milvus-migration-deploy-2026-08.md`
- Docker 相关 GUI 工具中文支持现状与验证方法（Docker Desktop / Redis Insight / Portainer / ARDM / 1Panel）：见 `references/docker-gui-tools-chinese.md`
- 团队项目 Docker 封装（Dockerfile 缓存顺序 / compose 端口冲突 / 本机端口地图）：见 `references/team-project-compose.md`
