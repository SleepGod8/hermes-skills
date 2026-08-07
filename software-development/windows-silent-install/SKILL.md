---
name: windows-silent-install
description: "Windows 上静默安装需管理员权限的软件（Docker Desktop 等）。UAC 限制与 .bat 引导。"
version: 1.0.0
author: agent
tags: [windows, install, docker, uac, silent-install]
platforms: [windows]
---

# Windows 静默安装需管理员权限的软件

在 Windows 上通过 Hermes 终端后台安装需要管理员权限的软件（Docker Desktop、驱动、开发工具等）。记录已验证的路径与致命坑。

## 触发条件

- 用户要求在 Windows 上安装 Docker Desktop / 其他需 UAC 提权的软件
- 静默安装（`--quiet`）需要管理员权限但当前 shell 非管理员
- 安装器卡在 UAC 提权阶段、日志停在 "relaunching with UAC prompt"

## 核心结论：后台终端会话无法触发交互式 UAC

Hermes 的 terminal 后台进程运行在**非交互上下文**，`Start-Process -Verb RunAs` 会报
`InvalidOperationException`（无法弹 UAC），`schtasks /RL HIGHEST` 创建计划任务也需要管理员。
**任何试图从后台 shell 提权的方案都会失败**——不要浪费时间尝试。

**可靠方案：创建 .bat 脚本让用户手动右键「以管理员身份运行」**：
```bat
@echo off
chcp 65001 >nul
"D:\软件\Docker Desktop Installer.exe" install --quiet --accept-license --installation-dir="E:\Docker"
pause
```
用户：资源管理器 → 右键 .bat → 以管理员身份运行 → UAC 点「是」。
`.bat` 用 ANSI/UTF-8 编码（含中文路径时 `chcp 65001` 可避免乱码）。

## 案例：Docker Desktop 静默安装（4.83.0 实测 2026-08）

官方安装命令（Docker Desktop 4.x 均支持）：
```
"Docker Desktop Installer.exe" install --quiet --accept-license --installation-dir="E:\Docker"
```
- `--installation-dir` 指定安装目录（否则默认 `%LOCALAPPDATA%\Programs\DockerDesktop`）
- Windows 10 Home 版无 Hyper-V，Docker 走 WSL2 后端（安装器会自动处理/提示）

## 安装器行为（bootstrapper）

1. 父进程快速返回（后台 `| tail` 捕获不到输出是**正常的**）
2. 先解压安装文件到目标目录（E:\Docker 出现 `7zr.exe`, `Docker Desktop.exe`, `frontend/` 等）
3. 非管理员时"relaunching with UAC prompt"——等 UAC 确认后由提权子进程真正安装

## 日志排查（关键）

安装日志在 `%LOCALAPPDATA%\Docker\install-log*.txt`（**多个编号文件**）：
- `install-log.txt` = 最近一次启动
- `install-log.0.txt` / `install-log.1.txt` / ... = 历史/提权子进程写入
- 日志里有 `Installation succeeded` / `Uninstalled finished` / `No installation found` 等关键行
- 卡在 `[ProcessEnvironmentDetector][I] Not run as admin, relaunching with UAC prompt` = 还在等 UAC

**陷阱**：多次重复运行安装器会互相干扰（一次装 C 盘 → 下一次检测到已有安装先卸载 → 再重装）。
安装前先清残留：`rm -rf %LOCALAPPDATA%\Programs\DockerDesktop`；目标目录残留被锁删不掉时**不必强删**（安装器会覆盖）。

## git-bash 传参坑

git-bash（MSYS）直接调 exe 时 `--installation-dir="E:\Docker"` 可能被路径转换破坏
（装到默认 C 盘）。正确姿势：
- **优先用 .bat 文件**（cmd 原生解析，无 MSYS 干扰）
- 或 PowerShell：`Start-Process -FilePath '...' -ArgumentList @('install','--quiet','--accept-license','--installation-dir=E:\Docker')`
  （注意：`-Verb RunAs` 在后台会话会失败——见上）

## 验证安装

- `docker --version`（需新开 shell 或重登 PATH）
- `tasklist | grep -i docker`（Docker Desktop 主进程）
- 服务：`Get-Service | Where-Object {$_.Name -like '*docker*'}`
- E:\Docker 下应有完整程序文件（Docker Desktop.exe + frontend + resources）

## 参考

- Docker Desktop CLI 安装文档：https://docs.docker.com/desktop/install/windows-install/
- 本技能诞生于 2026-08 本机 Docker Desktop 4.83.0 安装（安装包 D:\软件，目标 E:\Docker）
