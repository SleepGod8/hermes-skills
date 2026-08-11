---
name: windows-file-lock-pitfalls
description: "Windows 中文路径/目录锁/改名坑：mv Permission denied、cmd ren 假成功、Hermes 终端 cwd 锁目录、psutil 诊断、Python os.rename。"
version: 1.0.0
author: agent
license: MIT
tags: [windows, filesystem, chinese-path, file-lock, rename, git-bash]
platforms: [windows]
---

# Windows File & Directory Lock Pitfalls

Windows 上中文路径操作和目录锁的实测经验（2026-08）：改名/移动/删除失败时怎么诊断、用什么工具最稳。

## 触发条件

- 中文路径的目录 mv/rmdir/rm -rf 报 `Permission denied` 或 `Device or resource busy`
- cmd 改名显示成功但实际没变
- 目录删不掉、移动不了（疑似被占用）

## 1. 中文路径改名/移动：Python os.rename 最稳

| 工具 | 结果 |
|------|------|
| git-bash `mv` | 目录被锁时报 `Permission denied` |
| `cmd //c 'ren ...'` | **中文路径编码被吞，返回 0 但实际没改名（假成功）**——不要信 echo 结果，必须回读验证 |
| PowerShell `Rename-Item` | 可用（-LiteralPath 更稳） |
| **Python `os.rename`** | **最稳**（Unicode 路径原生支持），失败会抛真实异常 |

```bash
python - <<'EOF'
import os
src = r"E:\项目\智能财富管家系统"
dst = r"E:\项目\smart-wealth"
os.rename(src, dst)   # 失败会抛 OSError，不会假成功
EOF
```

## 2. 目录被占用诊断（Device or resource busy / Permission denied）

**psutil 遍历进程 cwd**（wmic 查 CommandLine 常返回空，不可靠）：

```python
import psutil
target = r"E:\项目\xxx"
for p in psutil.process_iter(['pid','name','cwd']):
    try:
        cwd = p.info.get('cwd') or ''
        if cwd.lower().startswith(target.lower()):
            print(f"LOCK: PID={p.info['pid']} NAME={p.info['name']}")
    except Exception:
        pass
```

- `rmdir` 报 `Directory not empty` = 目录里有内容（先 `ls -a` 看，可能有隐藏 .git 等）
- `rmdir`/`rm -rf` 报 `Device or resource busy` = 有进程 cwd 停在里面

## 3. ⚠️ Hermes 终端持久 shell 会锁住 cd 过的目录（关键坑）

Hermes 的 `terminal` 工具**跨调用持久化 cwd**：一旦某条命令 `cd` 进某目录，后续 Hermes 的持久 bash 会话可能一直停在里面，导致该目录 `mv`/`rmdir`/`rm -rf` 报 `Device or resource busy`，怎么都删不掉。psutil 看到的锁进程**每次 PID 都不同**（是进程池，kill 一批又冒一批）——**别 kill 它们，会破坏 terminal 工具**。

**解法：执行一条 `cd <别的目录>` 让会话 cwd 离开，锁即释放**：
```bash
cd /e/项目/smart-wealth && pwd   # 离开被锁目录
# 再查 psutil 应显示 NO_LOCK，然后 rm -rf / mv 就能成功
```

## 4. kill 占用进程的正确姿势

- git-bash 里 `taskkill //F //PID x` 的 `//` 转义常被解析错（报"无效参数"）→ 用 Python `psutil.Process(pid).kill()`
- `cmd //c 'start "" "path"'` 启动 GUI 程序：中文路径/引号会被吞，进程起不来 → 用 `powershell -Command "Start-Process -FilePath '...'"` 或 Python

## 5. 清理顺序（完整套路）

1. `ls -a` 确认目录内容（可能有隐藏 .git，非空删不掉）
2. psutil 查 cwd 占用 → 若是 Hermes 会话，`cd` 出去释放
3. 若确认是旧副本/残留仓库（`git log` 看内容、`git remote -v` 看指向，历史已并入主仓库的即可安全删）
4. 删除用 `rm -rf`（bash）或 Python `shutil.rmtree`；改名用 Python `os.rename`

## 参考

- git 环境配置（代理/身份/SSH）：`git-windows-setup` 技能
- Docker Desktop 启动（PowerShell Start-Process）：`docker-windows-setup` 技能
