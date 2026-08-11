---
name: git-windows-setup
description: "Windows 上 git 协作环境配置：代理绕过(per-host空值)、身份、SSH key、Gitee/GitHub、路径写法、多目录版本诊断。"
version: 1.0.0
author: agent
license: MIT
tags: [git, gitee, github, proxy, ssh, windows, collaboration]
platforms: [windows]
---

# Git Windows Collaboration Setup

Windows 上配置 git 多人协作环境（Gitee/GitHub 通用）的实测经验：代理绕过、身份、SSH key、路径写法、多目录版本诊断。2026-08 实测。

## 触发条件

- 用户要配置 git 访问 Gitee/GitHub（代理绕过、身份、SSH key）
- clone/push 超时、卡死、权限问题
- 机器上有多个项目目录副本，要判断哪个是最新/权威版本

## 1. 代理绕过：命令行空值 = 删除配置（关键坑）

**`git config --global http.https://gitee.com.proxy ""` 不会设置空值，而是删除该配置项！**（git config 命令行传空字符串 = unset）。执行后 `git config --global --get <key>` 返回 exit=1（key 不存在），代理照走。

**正确做法：直接编辑 `~/.gitconfig` 文件**，写入空值（文件里的空值才会被 git 解析为「该地址禁用代理」）：

```ini
[http]
	proxy = http://127.0.0.1:12450        # 全局代理（如翻墙用）
[https]
	proxy = http://127.0.0.1:12450
[http "https://gitee.com"]                # per-host 覆盖：Gitee 直连
	proxy =
```

**验证（实测可靠）**：用 GIT_TRACE_CURL 看 git 实际连接行为：
```bash
GIT_TRACE_CURL=1 git ls-remote git@gitee.com:xxx/repo.git HEAD 2>&1 | grep -iE "proxy tunnel|Established connection"
# 走代理: "Establish HTTP proxy tunnel to gitee.com:443" + "port 12450"
# 直连:   "Established connection to gitee.com (180.76.198.77 port 443)"  ← 成功绕开
```
`git config --global --get <key>` 对空值返回 exit 0、对不存在返回 exit 1，可用来确认 key 存在。

## 2. 身份配置（占位符坑）

```bash
git config --global user.name "真实姓名"
git config --global user.email "真实邮箱"   # 建议与 Gitee/GitHub 绑定邮箱一致
```
⚠️ 用户可能原样复制含占位符的命令（如 `"你Gitee绑定的邮箱"`）→ 配置里留下字面量字符串。完成后**必须 `git config --global user.name/email` 回读验证**，发现占位符立即改。

## 3. SSH key（免密）

```bash
ssh-keygen -t ed25519 -C "邮箱" -f ~/.ssh/id_ed25519 -N ""
cat ~/.ssh/id_ed25519.pub    # 公钥粘贴到 Gitee: https://gitee.com/profile/sshkeys（标题随意）
ssh -T -o StrictHostKeyChecking=accept-new git@gitee.com   # "Hi 用户名!" 即成功
```
`-o StrictHostKeyChecking=accept-new` 避免首次连接卡交互。测试失败输出 `Permission denied (publickey)` = 公钥没贴对/没生效。

## 4. 路径写法（PowerShell vs git-bash）

- git-bash（Hermes terminal）：`/e/项目/xxx` 可用
- PowerShell：`/e/项目/xxx` **不存在**，要用 `E:\项目\xxx`（中文路径加引号）
- 混用是常见报错来源：`cd : 找不到路径 "C:\e\项目\..."`

## 5. 多目录版本诊断（哪个是权威）

机器上多个项目副本时，用 git 判断版本关系：
```bash
git remote -v                                  # 远程指向
git branch -a                                  # 本地/远程分支
git log --oneline -3                           # 本地提交
git ls-remote <remote>                         # 远程最新（master/develop 各自 hash）
git merge-base HEAD origin/develop 2>/dev/null # 有输出=同源；失败=无共同历史（不同开发线）
```
实测案例：本地目录有 5 个提交（更新）、远程 develop 只有 2 个（旧）→ 拉取产生 merge commit；`git rev-parse HEAD origin/develop` 相同 = 已同步。**判断「权威版本」要问用户/组长，不要自己假设**；未跟踪的本地文件（文档等）不会被 pull 覆盖。

## 6. 其他

- clone 进非空目录会失败：先移走内容再 clone，完成后放回
- 目录改名被锁/中文问题 → 见 `windows-file-lock-pitfalls` 技能（Python os.rename 最稳）
- GitHub 专属认证/API 流程 → 见 `github-auth` 技能

## 参考

- GitHub 工作流（PR/分支管理）：`github-pr-workflow`、`github-repo-management` 技能
