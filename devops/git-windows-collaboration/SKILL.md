---
name: git-windows-collaboration
description: "Windows 上 git 多人协作（Gitee/GitHub）：团队分支规范流程、代理绕过、中文路径与目录锁、pull 阻塞处理、提交与 PR 规范。"
version: 1.0.0
author: agent
license: MIT
tags: [git, gitee, collaboration, windows, branch-workflow, pull-request, chinese-paths]
platforms: [windows]
---

# Windows Git 多人协作（Gitee 实测）

Windows 环境（git-bash / PowerShell 混用）下参与多人 git 项目的完整工作流与踩坑实录。覆盖：团队分支规范、Gitee 代理绕过、中文路径与目录锁、pull 阻塞、提交/PR 规范。

## 触发条件

- 用户参与多人 git 项目（Gitee 或 GitHub），需要拉分支/同步/提交/开 PR
- git 命令报错但肉眼看不到原因（路径、编码、隐藏字符、文件锁）
- 中文目录名/中文路径操作卡住（改名、删除、pull 被挡）

## 团队分支工作流（GitHub Flow 变体，多人项目标准）

```
日常同步（每天开工）：
  git fetch origin
  git switch develop
  git pull --ff-only origin develop      # 只用 ff-only，禁止 merge 式 pull 污染
  git switch feature/<自己的分支>
  git pull --ff-only origin feature/<自己的分支>

功能开发（每个原子任务）：
  git switch feature/<自己的分支>
  git pull --ff-only origin feature/<自己的分支>
  git add <自己的文件>                    # 只加相关的，别 git add .
  git commit -m "feat(scope): 完成原子任务"   # Conventional Commits
  git push origin feature/<自己的分支>

完成后：Gitee 网页 新建 Pull Request：feature/<分支> -> develop
（PR 描述写：改动 / 验证证据 / 风险等级 L1-L3 / 影响）
功能分支合入 develop 后，下一轮开发前再同步 develop 进功能分支：git merge develop
```

**铁律**：
- 永不直接推 main/develop；永不 `push -f`
- 一个 commit 一件事（原子提交）
- 提交前三查：`git branch --show-current` + `git status` + `git diff --cached --name-only`
- 不要在 develop 上长时间写代码，功能一律在 feature 分支

## pull 被阻塞的两种情况和处理

**1. 未跟踪文件会被覆盖**：远程新增了本地未跟踪的同名文件（常见：.obsidian/、IDE 配置）→ 报 `untracked working tree files would be overwritten by merge`。
处理：先备份再让远程接管：
```bash
mkdir -p /tmp/backup && mv .obsidian/appearance.json /tmp/backup/
git checkout -- .obsidian/app.json      # 已跟踪文件被本地改过 → 还原远程版
git pull origin develop
```

**2. 已跟踪文件本地有修改且远程也改了** → 报 `local changes would be overwritten`。
处理：`git stash`（或 commit）→ pull → `git stash pop`。

**心法：pull 前先 `git status` 干净（提交或 stash），就不会被卡。**

## Windows 特有坑（实测）

### 1. git config 命令行空字符串 = 删除配置（绕代理必须写配置文件）
```bash
git config --global http.https://gitee.com.proxy ""   # ❌ 这是"删除该 key"，不是设空值！
```
git 对命令行空值执行 unset。**正确做法**：直接编辑 `~/.gitconfig` 写入：
```ini
[http "https://gitee.com"]
	proxy =
```
配置文件里的空值才被解析为"该 URL 不用代理"。验证：`GIT_TRACE_CURL=1 git ls-remote <url> 2>&1 | grep -E "proxy tunnel|Established connection"`——走代理会看到 `proxy tunnel to <host>` + 连到 127.0.0.1；绕开则 `Established connection to <真实IP>`。`git config --get` 空值无法区分"未配置/空配置"（exit code 才能区分，0=存在）。

### 2. PowerShell vs git-bash 路径写法
- git-bash：`/e/项目/xxx`；PowerShell：`E:\项目\xxx`（中文路径务必加引号 `cd "E:\项目\xxx"`）
- 给用户发命令时**先确认对方在哪个 shell**，混用必然报 `找不到路径`。PowerShell 里跑 `/e/...` 会报 PathNotFound。

### 3. 中文目录改名/删除被锁（Windows 目录锁）
症状：`mv` 报 `Permission denied` / `Device or resource busy`；`rmdir` 报 `Directory not empty`（其实空）。
排查占用（cwd 锁）：
```bash
python - <<'EOF'
import psutil
target = r"E:\项目\xxx"
for p in psutil.process_iter(['pid','name','cwd']):
    try:
        cwd = p.info.get('cwd') or ''
        if cwd.lower().startswith(target.lower()):
            print(f"PID={p.info['pid']} NAME={p.info['name']}")
    except Exception: pass
EOF
```
**Hermes 特有坑**：Hermes terminal 工具的后台持久 bash 会话可能 cwd 停在目标目录里（之前 cd 进去查过）——表现为"kill 一批进程又冒出新 PID"。**解决：执行一条 `cd <父目录>` 让会话 cwd 离开，锁即释放**，再删。
改名本身：git-bash `mv` 和 `cmd //c ren` 在中文路径下都可能失败/无效（编码问题）→ **用 Python 最稳**：
```bash
python -c "import os; os.rename(r'E:\项目\旧名', r'E:\项目\新名')"
```

### 4. 隐藏 Unicode 字符（U+200B）
从网页/微信复制的命令可能带零宽空格 → CLI 报"格式正确但失败"。规律：**任何"肉眼正确但 CLI 报错"的复制命令，先怀疑隐藏字符，手动重敲一遍**。见 docker-windows-setup 技能（docker invalid reference format 一节）有完整排查方法。

## 提交规范速查

```bash
git commit -m "feat(scope): 一句话"    # feat/fix/refactor/docs/test/ci/chore
git commit -m "feat(risk): 规则引擎框架

- 明细点 1
- 明细点 2"
git push -u origin feature/xxx          # 首次推送建立跟踪
git branch -m 新名字                     # 分支改名（未推送时）
```

## 参考

- 本会话完整排障实录（Gitee 绕代理过程、目录锁排查、PR 描述模板）：见 `references/windows-git-pitfalls-2026-08.md`
- GitHub PR 生命周期（gh CLI 方式）：见 github-pr-workflow 技能
- Docker compose 相关坑（端口冲突/override/milvus）：见 docker-windows-setup 技能
