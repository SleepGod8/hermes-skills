---
name: windows-file-ops
description: "Windows 上文件/目录操作排障：删除/改名/移动失败(Permission denied/Device busy/Directory not empty)、中文路径操作、文件锁排查。When a directory or file won't delete/rename/move on Windows, Chinese-path operations fail, or you need to find which process is locking a folder. 核心：psutil 查 cwd 锁、Python os.rename 处理中文路径、Hermes 终端持久 cwd 锁释放、cmd ren 中文编码假成功。"
version: 1.0.0
tags: [windows, filesystem, troubleshooting, path, locks]
metadata:
  hermes:
    tags: [windows, filesystem, troubleshooting, path, locks]
    category: devops
---

# Windows 文件/目录操作排障

## 触发条件
- `mv` / `rm` / `rmdir` 报 `Permission denied` / `Device or resource busy` / `Directory not empty`
- 中文路径改名、删除、移动失败
- 需要找出哪个进程锁住了目录
- PowerShell 与 git-bash 路径写法混淆
- 项目目录里出现嵌套的 `.git` 残留

## 铁律
1. **中文路径改名/删除首选 Python**：`mv` 在 git-bash 对中文路径常报 Permission denied（Windows 锁 + 编码）；`cmd ren` 会因 GBK vs UTF-8 编码问题**假成功**（返回 0 但实际没生效，且输出乱码）。直接用 Python：
   ```python
   import os
   os.rename(r"E:\项目\旧名", r"E:\项目\new-name")   # 改名
   os.rmdir(r"E:\项目\空目录")                        # 删空目录
   ```
2. **目录删不掉 = 有进程 cwd 停在里面**。用 psutil 找锁（不要靠猜）：
   ```python
   import psutil
   target = r"E:\路径\目标目录"
   for p in psutil.process_iter(['pid','name','cwd']):
       try:
           cwd = p.info.get('cwd') or ''
           if cwd.lower().startswith(target.lower()):
               print(p.info['pid'], p.info['name'], cwd)
       except Exception: pass
   ```
   `wmic process where "CommandLine like '%xxx%'"` 查命令行经常返回空/超时，不可靠。
3. **Hermes 终端持久 cwd 是隐藏锁源**：Hermes 的 terminal 工具持久化 cwd——只要某次执行过 `cd` 进某目录，那个 bash 会话进程会一直锁住该目录。特征：kill 掉一批锁进程后又出现新 PID（终端进程池重启/复用）。**解法：执行 `cd /e/项目/父目录`（让持久 cwd 离开目标目录），锁立即释放**，然后再 rm -rf。不要 kill 这些 bash/python 进程（会破坏 terminal 工具本身）。用户终端/编辑器停在目录里同理——提示用户关闭，不擅自 kill。
4. **嵌套 git 仓库残留**：`E:\项目\repo\repo\` 里有 `.git` 时，先判断它是否有独有提交再删：
   ```bash
   cd repo/repo && git log --oneline -3 && git rev-parse --short HEAD
   ```
   内容已包含在主仓库历史里（如空壳 clone 残留：只有 Initial commit + 测试文件）就安全 `rm -rf`。注意：用 `ls -a` 看目录内容，别假设它是空的。
5. **路径写法**：git-bash 用 `/e/项目/...`，PowerShell 用 `E:\项目\...`（中文路径务必加引号 `cd "E:\项目\xxx"`）。把 `/e/` 写进 PowerShell 会报"找不到路径"。
6. **clone 到非空目录失败**：`git clone <url> <dir>` 要求目标为空或不存在。处理：先 `mv` 现有文件到临时位置 → clone → 把文件移回（或提交进仓库）。
7. **taskkill 在 git-bash 的坑**：`taskkill //F //PID x` 的 `//` 转义常失效（报"无效参数"）。用 Python `psutil.Process(pid).kill()` 代替。

## 排查流程（目录删不掉）
1. 先 `ls -a` 看目录内容（是空壳还是有嵌套仓库/文件）
2. `rmdir` 报 `Directory not empty` → 内容未清干净；报 `Device or resource busy` / Permission denied → 有进程锁
3. psutil 查 cwd 锁 → 区分锁源：
   - Hermes 终端会话 → `cd` 离开目标目录 → 重试删除
   - 用户编辑器/终端 → 提示用户关闭，不擅自 kill
4. 中文路径一切失败 → Python `os.rename` / `os.rmdir`
5. 删除成功 → `git status` 验证仓库未受影响

## references
- `references/dir-lock-cases.md` — 2026-08 智能财富管家目录清理实战案例（完整排查链）
