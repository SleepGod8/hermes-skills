---
name: windows-admin-installs
description: "Windows 装需管理员权限软件：Hermes终端无法弹UAC→手动bat方案，bat中文乱码坑。"
version: 1.0.0
author: agent
tags: [windows, install, docker, uac, admin, bat]
platforms: [windows]
---

# Windows 管理员权限软件安装（Hermes 终端环境）

在 Windows 上通过 Hermes 终端安装需要管理员权限的软件（Docker Desktop、驱动、Visual Studio 等）。本技能记录**Hermes 终端环境的 UAC 限制**和已验证的静默安装配方。

## 触发条件

- 用户要求安装 Docker Desktop / 其他需要管理员权限的 Windows 软件
- 安装器卡在 UAC 提权阶段、日志停在 "Not run as admin, relaunching with UAC prompt"
- 需要把软件装到非 C 盘（E 盘等）

## ⚠️ 核心坑 1：Hermes 后台终端无法触发交互式 UAC

**症状**：安装器日志停在 `Not run as admin, relaunching with UAC prompt`，无新日志、无弹窗；PowerShell `Start-Process -Verb RunAs` 报 `InvalidOperationException`；schtasks 注册最高权限任务也会启动失败。

**根因**：Hermes 的终端命令运行在非交互上下文，无法把 UAC 弹窗显示到用户桌面。

**解法（已验证）**：创建 bat 脚本让**主人手动**右键「以管理员身份运行」，UAC 由主人桌面确认：

```bat
@echo off
echo Installing ... please wait.
"E:\ai1\DockerDesktopInstaller.exe" install --quiet --accept-license --installation-dir="E:\Docker"
echo.
echo Install command finished.
pause
```

主人运行完 bat 后，从 Hermes 侧验证安装结果（服务、CLI、目录）。

## ⚠️ 核心坑 2：bat 中文乱码（UTF-8 vs GBK）

**症状**：write_file 写的 bat（UTF-8）用 cmd 默认 GBK 解析 → 中文 echo 乱码成 `呰剼鏈?` 被当命令执行；**中文路径（如 `D:\软件\`）里的中文乱码 → "系统找不到指定的路径"**。

**解法（已验证）**：
1. **bat 内容全英文**（不用 chcp 65001 救，设置了也救不了命令解析阶段）
2. **安装包复制到无中文路径**：`cp "/d/软件/Docker Desktop Installer.exe" /e/ai1/DockerDesktopInstaller.exe`，bat 里只用英文路径
3. 任何含中文的路径/文件都要先搬到纯 ASCII 路径

## Docker Desktop 静默安装配方（已验证 4.83.0）

```bat
"D:\path\Docker Desktop Installer.exe" install --quiet --accept-license --installation-dir="E:\Docker"
```

- `--installation-dir` 指定安装盘（git-bash 直接传参有引号坑 → 用 bat 或 PowerShell 传）
- **验证安装**：`<install_dir>/resources/bin/docker.exe --version`（如 Docker version 29.6.2）；`Get-Service com.docker.service` 应存在（Stopped/Manual 正常）；`<install_dir>/Docker Desktop.exe` 主程序存在
- 安装日志：`%LOCALAPPDATA%\Docker\install-log*.txt`（管理员进程的日志可能写旧文件，别只盯主日志）

## Win10 家庭版必须 WSL2（Docker Desktop 前提）

Home 版无 Hyper-V，Docker Desktop 必须 WSL2 后端。`wsl --status` 输出乱码但含 "未安装" 即需启用：

```bat
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
wsl.exe --set-default-version 2
REM 重启后启动 Docker Desktop 自动完成 WSL2 初始化
```

同样要走「主人手动管理员运行 bat」流程。

## ⚠️ WSL2 内核下载慢（国内网络）→ 离线包方案

**症状**：`wsl --set-default-version 2` 触发从 GitHub 下载 WSL 内核/应用包（进度条 0.3% 龟速）；`wsl.exe --install` 同理。

**解法（已验证）**：
1. 用代理下载离线内核包（17MB，秒下）：
   ```bash
   # curl 下载到 Windows 路径易失败（exit 23 写入错误）→ 用 Python urllib：
   opener = urllib.request.build_opener(urllib.request.ProxyHandler({"http": proxy, "https": proxy}))
   data = opener.open("https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi", timeout=60).read()
   open(r"E:\ai1\wsl_update_x64.msi", "wb").write(data)
   # 本机代理：http://127.0.0.1:12450；文件头 D0 CF 11 E0 = MSI/OLE 格式校验
   ```
2. 让主人管理员运行 bat：`msiexec /i "E:\ai1\wsl_update_x64.msi" /quiet /norestart`
3. 之后 `wsl --set-default-version 2` 不再下载（内核已在）

**注意区分**：`wsl_update_x64.msi` 是 WSL2 **内核**（17MB）；`wsl.exe --install` 下载的是 WSL **应用包**（2.x，更大）。两者不同；功能启用 + 重启后 wsl 组件通常由系统/ Docker Desktop 初始化补齐，内核离线包解决的是卡住的下载。

## ⚠️ dism /norestart 后必须重启（时序坑）

`dism ... /norestart` 启用 WSL 功能后，**重启前** `wsl --status` 仍报"未安装"——这是 pending reboot 的正常现象，**不是安装失败**。正确顺序：dism 启用 → 装内核 MSI → 重启 → 启动 Docker Desktop。别在未重启时误判失败而重复安装。

## Docker 数据盘迁移（省 C 盘空间）

- WSL 系统组件（C:\Windows\System32\lxss）固定 C 盘但 <1GB，无法移动
- **Docker 虚拟机数据**（几个 GB）：Docker Desktop → Settings → Resources → Advanced → **Disk image location** 改到 E 盘（如 E:\DockerData）
- 告知用户：功能组件在 C 盘没关系，大头数据可以搬

## 通用静默安装参数模式

| 安装器 | 常用静默参数 |
|--------|-------------|
| Docker Desktop | `install --quiet --accept-license --installation-dir=路径` |
| 通用 InnoSetup | `/VERYSILENT /SUPPRESSMSGBOXES /DIR="路径"` |
| 通用 NSIS | `/S /D=路径` |

## 验证清单

- [ ] 主人确认运行了 bat（无乱码、无"找不到路径"）
- [ ] 目标盘出现安装目录 + 可执行文件
- [ ] 服务/注册表项存在（Get-Service / Get-ItemProperty）
- [ ] CLI 能输出版本号
- 安装后若需 WSL2/Hyper-V → 提醒主人重启电脑

## 复用模板

- `templates/silent_install_docker.bat` — 通用静默安装 bat（全英文、参数化安装器名与目标盘，复制到无中文路径后可直接改参数使用）
