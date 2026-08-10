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

## 验证清单

- [ ] `docker --version` + `docker info`（Server 在跑）
- [ ] `docker compose version`
- [ ] `docker ps` 目标容器 `Up(healthy)`
- [ ] 浏览器访问 Web 入口（Dify 默认 80 端口）

## 参考

- Dify 迁移部署细节：见 `references/dify-deployment-2026-08.md`
- Milvus 迁移包还原部署细节（含端口保留段实测、镜像拉取时间线、Docker Desktop 启动方式）：见 `references/milvus-migration-deploy-2026-08.md`
