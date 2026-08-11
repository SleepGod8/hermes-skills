---
name: gitee-git-workflow
description: "Gitee（码云）远程仓库工作流：clone/拉取/提交/PR、SSH key 配置、绕过代理直连（.gitconfig 空 proxy 技巧）、git 身份配置、pull 被未跟踪文件/本地修改拦截的处理。Use when 用户操作 Gitee 仓库、git pull 被挡（would be overwritten by merge）、配置 Gitee SSH/代理/身份、问 Gitee 命令怎么用。"
version: 1.0.0
author: agent
license: MIT
tags: [gitee, git, ssh, proxy, windows, workflow, pull-conflict]
platforms: [windows, linux, macos]
---

# Gitee 远程仓库工作流

国内团队常用 Gitee（码云）做版本管理。本技能记录 Gitee 专属的配置坑与日常 git 操作被拦时的处理。通用 GitHub 流程见 github-pr-workflow / github-repo-management（bundled，只读）。

## 触发条件

- 用户要给 Gitee 配 SSH key / 绕代理 / 设置 git 身份
- `git pull` 报 `error: The following untracked working tree files would be overwritten by merge` 或 `Your local changes ... would be overwritten`
- 用户问 Gitee clone/pull/分支命令怎么用

## 1. 首次配置（一次性）

```bash
# 身份（用真实姓名 + Gitee 绑定邮箱，别用工具默认值）
git config --global user.name "真实姓名"
git config --global user.email "邮箱"

# SSH key（ed25519）
ssh-keygen -t ed25519 -C "邮箱" -f ~/.ssh/id_ed25519 -N ""
# 公钥内容贴到 Gitee → 设置 → SSH 公钥
cat ~/.ssh/id_ed25519.pub
# 验证
ssh -T -o StrictHostKeyChecking=accept-new git@gitee.com
# 成功标志: Hi <用户名>(@<用户名>)! You've successfully authenticated
```

克隆、切 develop、拉功能分支：
```bash
git clone git@gitee.com:<用户名>/<仓库>.git
cd <仓库>
git checkout -b develop origin/develop   # 或 git checkout develop
git checkout -b feature/xxx develop      # 每个任务拉功能分支
```

## 2. 🔴 绕过代理直连 Gitee（.gitconfig 空 proxy 技巧）

国内 git 全局配了代理（如 `http.proxy=http://127.0.0.1:12450`）时，Gitee 应直连（国内不需要代理，代理断连会拖垮 clone/push）。

**陷阱：`git config --global http.https://gitee.com.proxy ""` 是删除该配置，不是设空值！** git 对命令行空字符串 = unset（key 消失，--get 返回 exit 1）。必须**直接编辑 ~/.gitconfig 文件**写入空值：
```ini
[http "https://gitee.com"]
	proxy =
```
文件里的空值才被 git 解析为"该 host 不用代理"。

验证（两步）：
```bash
# 1. key 存在且为空
git config --global --get http.https://gitee.com.proxy; echo "exit=$?"   # 0=存在
# 2. 真实连接不建代理隧道（有 proxy tunnel 字样=没生效）
GIT_TRACE_CURL=1 git ls-remote git@gitee.com:<用户名>/<仓库>.git HEAD 2>&1 | grep -iE "proxy tunnel|Established connection"
# 期望: Established connection to gitee.com (真实IP), 无 proxy tunnel
```

## 3. git pull 被拦截（最常见：远程新增文件 vs 本地未跟踪）

症状：`git pull` 报
```
error: The following untracked working tree files would be overwritten by merge:
	<文件>
Please move or remove them before you merge.
```
或 `Your local changes to the following files would be overwritten by merge: <文件>`

原因：远程提交里新增/修改了某个文件，而本地同名文件是**未跟踪**（?? 状态）或**已修改**（M 状态）——git 怕覆盖本地内容而中止。

处理：
```bash
git status   # 先看挡路的是谁

# 未跟踪文件（?? 状态）：备份后让远程接管（如 Obsidian 配置这类本地生成物）
mkdir -p /tmp/backup && mv .obsidian/appearance.json /tmp/backup/

# 已修改的跟踪文件（M 状态）：备份后放弃本地版本（确定不要时）
git checkout -- .obsidian/app.json
# 或想保留：先提交 / git stash，再 pull

git pull origin develop   # 再拉
```

**先备份再放弃**，Obsidian 等本地自动生成配置丢了也无所谓，但别误删自己写的代码。

## 4. 日常节奏（避免 pull 被卡）

```bash
git status          # 1. 看有没有未提交
git stash           # 2. 有就 stash（或 commit）
git pull origin develop   # 3. 拉最新
git stash pop       # 4. 恢复自己的改动
git checkout -b feature/xxx   # 5. 功能分支
```

## 5. 多目录并存时先确认权威版本

本机可能同时存在多个项目副本（改名/复制残留），操作前先确认哪个是最新/权威：
```bash
git remote -v                       # 看 remote 指向
git fetch origin && git log origin/develop --oneline -3   # 远程最新
git log --oneline -3                 # 本地
git merge-base HEAD origin/develop   # 无共同历史 = 另一条线（可能未推送/拷贝来的）
```
**教训：先 ls-remote / git log 对比版本，再决定 pull 还是 push**——队友发的 clone 命令可能指向旧版，而你本地副本反而更新（或相反）。拿不准先问团队"哪个是权威分支"。

## 验证清单

- [ ] `ssh -T git@gitee.com` 显示 Hi <用户名>
- [ ] GIT_TRACE_CURL 无 proxy tunnel（绕代理生效）
- [ ] `git status` 干净后再 pull
- [ ] pull 后 `git log --oneline -3` 确认最新提交
