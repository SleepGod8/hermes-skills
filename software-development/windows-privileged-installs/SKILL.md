---
name: windows-privileged-installs
description: "Windows 上装需管理员权限的软件（Docker/WSL）：UAC 限制、bat 编码、离线包代理下载。"
version: 1.0.0
author: agent
tags: [windows, install, uac, docker, wsl, bat, proxy, admin]
platforms: [windows]
---

# Windows 特权安装（Docker Desktop / WSL / 需提权的软件）

在 Windows 上安装需要管理员权限的软件（Docker Desktop、WSL、MSI 等）的完整套路。核心前提：**Hermes 后台终端会话无法弹交互式 UAC**，必须引导用户手动运行提权脚本。

## 触发条件

- 用户要求在 Windows 上安装 Docker Desktop / WSL / 其他需管理员权限的软件
- 安装器需要 UAC 提权但弹窗不出现/无法确认
- bat 脚本运行出现中文乱码导致命令找不到路径

## ⚠️ 核心约束：Hermes 终端无法弹交互式 UAC

**实测**（2026-08-07）：`Start-Process -Verb RunAs` 在 Hermes 后台终端报 `InvalidOperationException`（无交互桌面），UAC 弹窗根本不会出现。`schtasks /RL HIGHEST` 创建也需要提权（当前用户非管理员时 `0x80070002` 启动失败）。**不要试图从终端内提权**，正确做法：

1. 用 `write_file` 创建 **bat 脚本**（放 E:\ai1 等用户目录）
2. 引导用户：**右键 bat → 以管理员身份运行 → UAC 点「是」**
3. 安装器以管理员权限跑完后，用户贴输出/自己验证

## ⚠️ bat 中文乱码坑（UTF-8 vs GBK）

`write_file` 默认 UTF-8，但 cmd 用 GBK（代码页 936）解析 → 中文字符乱码，且**中文路径（如 `D:\软件\`）会被解析成乱码 → "系统找不到指定的路径"**。

**修复**：
- bat 内容**全英文**（echo、注释全 ASCII）
- 含中文的路径**先复制到无中文路径**（如 `cp "D:\软件\X.exe" E:\ai1\X.exe`）
- 验证：bat 里无任何非 ASCII 字符

## Docker Desktop 安装到非 C 盘

```bat
"D:\path\Docker Desktop Installer.exe" install --quiet --accept-license --installation-dir="E:\Docker"
```
- 4.16+ 支持 `--installation-dir`（E 盘）；用户数据（wsl 镜像）可在 Desktop 设置里改 `Disk image location`
- 安装日志：`%LOCALAPPDATA%\Docker\install-log*.txt`（多次运行写 .0/.1/.2 后缀）
- 验证：`E:\Docker\resources\bin\docker.exe --version`、服务 `com.docker.service`、`E:\Docker\Docker Desktop.exe`

## Docker Desktop 依赖 WSL2（Win10 家庭版无 Hyper-V）

**WSL 三部分**：
1. **系统功能**（Microsoft-Windows-Subsystem-Linux + VirtualMachinePlatform）→ 固定 C 盘，`dism /online /enable-feature /featurename:X /all /norestart`，**必须重启才生效**
2. **WSL2 内核**（wsl_update_x64.msi，~17MB）→ 可离线装，`msiexec /i xxx.msi /quiet`
3. **WSL 完整应用**（2.x，msixbundle ~494MB）→ Windows 10 新版 wsl.exe 是引导器，**必须装 Store 版 WSL 应用**才工作；`Add-AppxPackage` 报 `0x80073D28` = 需管理员 → 走 bat 提权

**下载顺序**：先 `wsl --status` 判断缺哪部分（"未安装适用于 Linux 的 Windows 子系统" = 缺应用/功能；内核目录 `C:\Windows\System32\lxss\tools\kernel` 缺失 = 缺内核）。

**下载慢的解法**：`wsl --install` / GitHub 直连在国内慢（0.3% 龟速）→ 用户开代理 VPN 后：
```python
import urllib.request
opener = urllib.request.build_opener(urllib.request.ProxyHandler({"http": "http://127.0.0.1:12450", "https": "http://127.0.0.1:12450"}))
data = opener.open(url, timeout=120).read()   # 注意带 User-Agent，读 Content-Length 显示进度
```
- 内核：`https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi`
- 应用：`https://github.com/microsoft/WSL/releases/download/<ver>/Microsoft.WSL_<ver>.0_x64_ARM64.msixbundle`（GitHub API 会 403 rate limit，但 release 直链可下）
- curl 走代理下载大文件可能静默失败（0 字节/无文件），**用 Python urllib 更可靠**

**完整启用序列**（一条龙 bat，全英文）：
```bat
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
msiexec /i "E:\ai1\wsl_update_x64.msi" /quiet /norestart
```
然后**重启电脑** → 启动 Docker Desktop。

**验证**：`wsl --version`（输出 UTF-16 在 GBK 终端显示乱码，看数字即可：WSL 2.x + 内核 6.x）；`Get-AppxPackage -Name '*WindowsSubsystemForLinux*'` Status=Ok。

## 验证清单

- [ ] bat 全英文、无中文路径
- [ ] 用户右键管理员运行 bat（UAC 确认）
- [ ] Docker：`docker --version` + `com.docker.service` 服务存在
- [ ] WSL：`wsl --version` 有版本号 + Appx Status=Ok
- [ ] 首次启动 Docker Desktop 完成 WSL2 初始化（鲸鱼图标变绿）
