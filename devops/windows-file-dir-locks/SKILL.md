---
name: windows-file-dir-locks
description: "Windows 上目录/文件/进程操作实战坑：中文路径改名删除、目录被锁(Device or resource busy)、Hermes持久bash会话cwd锁、psutil排查、GUI程序启动、taskkill转义。Invoke when mv/rm/rmdir 报 Permission denied / Device or resource busy、中文目录改名失败、cmd 输出乱码、需要启动桌面程序或查进程占用。"
version: 1.0.0
author: agent
license: MIT
tags: [windows, git-bash, filesystem, locks, psutil, powershell, path]
platforms: [windows]
---

# Windows 文件/目录/进程操作实战（git-bash 视角）

在 Windows 上通过 git-bash 终端做目录改名、删除、进程排查时踩过的坑与解法。2026-08 实测（Windows 11，git-bash MSYS）。

## 触发条件

- `mv`/`rm`/`rmdir` 报 `Permission denied` 或 `Device or resource busy`
- 中文目录/文件名改名失败、删除失败
- cmd/PowerShell 输出乱码（GBK vs UTF-8）
- 需要启动桌面 GUI 程序（Docker Desktop 等）、排查哪个进程占用目录

## 1. 目录删不掉/改不了名：先查"谁占用"（cwd 锁）

`rmdir` 报 `Device or resource busy`、`mv` 报 `Permission denied`，最常是**有进程的 cwd（工作目录）停在该目录里**。Windows 锁的是目录本身，不是文件。

用 psutil 查占用（比 lsof/handle 靠谱，机器必有 python）：
```bash
python - <<'EOF'
import psutil
target = r"E:\项目\smart-wealth\some-dir"
for p in psutil.process_iter(['pid','name','cwd']):
    try:
        cwd = p.info.get('cwd') or ''
        if cwd.lower().startswith(target.lower()):
            print(f"PID={p.info['pid']} NAME={p.info['name']} CWD={cwd}")
    except Exception:
        pass
EOF
```

## 2. 🔑 大坑：Hermes 终端自己的 bash 会话会锁目录

Hermes 的 terminal 工具用**持久 bash 会话**（cwd 在调用间保持）。如果之前某条命令 `cd` 进了目标目录（哪怕已执行完），该会话的 cwd 可能仍停在那里 → 目录被自己的终端锁住，kill 一批进程又冒出一批（进程池）。

**解法：执行 `cd` 离开目标目录，锁即释放**，然后立即删除：
```bash
cd /e/项目/smart-wealth && pwd   # 先让持久会话 cwd 离开
# 再查 psutil → NO_LOCK → 此时 rm -rf 才成功
```

## 3. 中文路径改名：直接 Python os.rename（最稳）

git-bash 的 `mv` 遇到中文目录可能 Permission denied；`cmd //c ren` 因 UTF-8→GBK 编码把路径解析成乱码，**返回 0 但实际没生效**（误导！）。

```bash
python -c "import os; os.rename(r'E:\项目\智能财富管家系统', r'E:\项目\smart-wealth')"
```
Python 对 Unicode 路径最稳。改名后验证：`git status`、`git remote -v` 一切照旧（`.git` 跟着文件夹走，**本地文件夹名与 git 推送完全无关**）。

## 4. 启动桌面 GUI 程序：PowerShell Start-Process（不要 cmd start）

`cmd //c 'start "" "path"'` 在 git-bash 里常因引号/编码被吞，进程根本没起来（检查 `tasklist` 或 psutil 才知道）。用 PowerShell：
```bash
powershell -Command "Start-Process -FilePath 'E:\Docker\Docker Desktop.exe'"
```
启动后轮询就绪（例：`for i in $(seq 1 24); do docker info >/dev/null 2>&1 && break; sleep 10; done`）。

## 5. taskkill 参数转义坑 → 用 psutil kill

git-bash 里 `taskkill //F //PID x` 会把 `//F` 原样传给 cmd 报"无效参数/选项"。直接 Python：
```bash
python - <<'EOF'
import psutil, time
for pid in [1234, 5678]:
    try:
        psutil.Process(pid).kill()
    except psutil.NoSuchProcess:
        pass
time.sleep(1)
EOF
```
（kill 前先确认进程身份，别误杀用户活跃进程。）

## 6. cmd 输出乱码（GBK）

`cmd //c` 的任何中文输出在 git-bash 显示为乱码（代码页 936 vs UTF-8）。**不要用 cmd 做关键判断**（如 ren 是否成功）；用 Python 或看文件系统实测结果验证。

## 7. 删除前确认"无价值"

删目录/嵌套 git 仓库前，先确认内容可弃：
```bash
cd <dir> && git log --oneline -3 && git remote -v   # 嵌套仓库是什么
git rev-parse --short HEAD  # 对比主仓库 HEAD，若历史已包含则可删
```

## 验证清单

- [ ] psutil 显示 NO_LOCK 后再删
- [ ] 改名/删除后 `ls` + 业务验证（git status / docker ps）
- [ ] GUI 程序启动后用 psutil/tasklist 确认进程存在
