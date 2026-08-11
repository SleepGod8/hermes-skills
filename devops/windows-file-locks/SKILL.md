---
name: windows-file-locks
description: "Windows 上文件/目录移动、重命名、删除被拒（Permission denied / Device or resource busy）的诊断与处理：Hermes 终端会话 cwd 锁、psutil 定位占用进程、中文路径用 Python os.rename、cmd ren 中文编码坑。Use when mv/rm/rmdir 报 Permission denied 或 Device or resource busy，目录删不掉/改不了名，中文路径操作失败。"
version: 1.0.0
author: agent
license: MIT
tags: [windows, filesystem, locks, rename, psutil, chinese-path, git-bash]
platforms: [windows]
---

# Windows 文件/目录锁处理

## 触发条件

- `mv` / `rmdir` / `rm -rf` 报 `Permission denied` 或 `Device or resource busy`
- 目录改名/删除失败，怀疑有进程占用（改了名也删不掉）
- 中文路径改名/删除（git-bash 与 cmd 编码双坑）

## 先分清三种报错（决定处理路径）

| 报错 | 含义 | 处理 |
|------|------|------|
| `Directory not empty` | 目录里有内容（非锁） | 先看内容；确认无用后 `rm -rf` |
| `Device or resource busy` | **有进程 cwd 停在里面 / 句柄锁** | 找占用进程 → 释放 cwd → 再删 |
| `Permission denied`（mv 整个目录） | 同上，目录被锁 | 找占用进程 → 释放 → 再 mv |

> 注意：`rmdir` 报 `Directory not empty` 而目录里**确实有东西**时，先 `ls -a` 看清内容——可能是残留的嵌套 git 仓库（如早期 clone 失败残留：含 `.git`/`.gitignore`/LICENSE）。先 `git log --oneline -3` 确认是旧仓库残留（历史已并入主仓库）再删，避免误删有价值内容。

## 🔴 最隐蔽的锁：Hermes 终端自己的持久 bash 会话

**Hermes terminal 工具的工作目录在调用间持久化**。如果之前某次命令 `cd` 进了该目录（比如为了查看内容），后续 Hermes 的 bash 会话 cwd 可能一直停在里面——即使命令早已结束，shell 进程还在，目录就被锁。**每次查占用进程 PID 都变 = 是 Hermes 自己的会话池，不是用户进程。**

**关键解法：把 cwd 移出去即可释放锁**（不用 kill 进程）：
```bash
cd /e/项目/smart-wealth   # 先 cd 到目标目录外面
# 再查占用：
python - <<'EOF'
import psutil
target = r"E:\项目\smart-wealth\smart-wealth"
found = False
for p in psutil.process_iter(['pid','name','cwd']):
    try:
        cwd = p.info.get('cwd') or ''
        if cwd.lower().startswith(target.lower()):
            found = True
            print(f"LOCK: PID={p.info['pid']} NAME={p.info['name']}")
    except Exception:
        pass
if not found:
    print("NO_LOCK")
EOF
# NO_LOCK 后立刻 rm -rf / 改名
```
**不要 kill 查到的 bash/python 进程**——它们是 Hermes 自己的 terminal 后端，kill 会破坏工具会话（且 kill 一批又冒一批）。正确顺序永远是：**移 cwd → 确认 NO_LOCK → 再删/改名**。

## 中文路径改名：用 Python os.rename，别用 cmd ren

实测（2026-08）：中文目录改名
- `mv` 报 Permission denied（锁）→ 解锁后可行
- `cmd //c 'ren "E:\项目\X" newname'` **可能返回成功但实际没改名**——git-bash 传参给 cmd 的 UTF-8→GBK 编码会把中文路径变成乱码，cmd 匹配不到就静默退出（echo 显示成功不可信）
- **最可靠：Python `os.rename`**（Python 内部 Unicode 路径，不受 shell 编码影响）：
```bash
python - <<'EOF'
import os, psutil
src = r"E:\项目\智能财富管家系统"
dst = r"E:\项目\smart-wealth"
# 先确认无占用
locked = [p.info for p in psutil.process_iter(['pid','name','cwd'])
          if (p.info.get('cwd') or '').lower().startswith(src.lower())]
if locked:
    print("占用:", locked)
elif os.path.exists(dst):
    print("目标已存在，中止")
else:
    os.rename(src, dst)
    print("OK:", os.path.exists(dst))
EOF
```

## 其他工具坑

- **taskkill 在 git-bash 的 `//F` 转义**：`taskkill //F //PID x` 会被 cmd 解析成无效参数（乱码报错）。要强杀进程直接用 Python `psutil.Process(pid).kill()`，或 `cmd //c "taskkill /F /PID x"`。
- **wmic 查询不稳定**：`wmic process where "ProcessId=..." get CommandLine` 有时返回空——用 psutil 更可靠。
- **修改了 git 仓库文件后 pull 被锁**：不相关（那是 git merge 保护，见 gitee-git-workflow）。

## 验证清单

- [ ] `ls -a` 看清目录内容（确认无价值再删）
- [ ] psutil 查 cwd 锁：`NO_LOCK` 才动手
- [ ] 删除/改名后 `ls` 确认 + git 仓库验证 `git status`（若是仓库目录）
