---
name: git-collaboration-setup
description: "团队协作 Git/Gitee 环境搭建与日常流程：身份配置、按域名绕代理、SSH key、clone 到已有目录、master/develop/feature 分支规范。Invoke when user asks git 配置/团队协作/gitee clone/ssh key/代理设置/分支切换。"
version: 1.0.0
author: agent
license: MIT
tags: [git, gitee, collaboration, proxy, ssh, windows]
platforms: [windows]
---

# Git/Gitee 团队协作环境搭建

用户参与多人协作项目（Gitee 为主）时的环境准备与日常操作。含 2026-08 实测踩坑记录。

## 触发条件

- 用户要配置 git 身份 / SSH key / 代理 / clone 团队仓库
- 用户提到 Gitee、多人协作、feature 分支、develop 分支
- 给用户可粘贴命令前（涉及路径时）

## 环境要点（Windows 双 shell）

- **我的 terminal 是 git-bash**：路径用 `/e/项目/...`
- **用户自己跑命令的是 PowerShell**：路径必须 `E:\项目\...`，含中文必须加引号 `cd "E:\项目\智能财富管家系统"`
- **给用户的可粘贴命令一律用 PowerShell 语法**。给 git-bash 语法（`/e/...`）用户直接粘会报 `找不到路径 C:\e\...`
- 用户本机全局代理 `http://127.0.0.1:12450`（常断）；Gitee 必须直连，GitHub 走代理

## 1. 身份配置（先问真实值，再执行）

PITFALL（实测）：用户会**原样复制占位符**——给 `git config --global user.email "你Gitee绑定的邮箱"` 他真的把 `你Gitee绑定的邮箱` 当邮箱填进去了。**先问真实姓名/邮箱，拿到后再写命令**，或把占位符写成 `<替换我>` 并明确强调。

```bash
git config --global user.name "真实姓名"
git config --global user.email "真实邮箱"
```

## 2. 按域名绕开代理（Gitee 直连 / GitHub 走代理）

PITFALL（实测，反直觉）：`git config --global http.https://gitee.com.proxy ""` **不会生效**——git 命令行传空字符串 = **删除该 key**（等价 unset），不是设为空值。

正确做法：直接编辑 `~/.gitconfig`，在文件里写**空值**：

```ini
[http "https://gitee.com"]
	proxy =
```

配置文件里的 `proxy =`（空值）才会被 git 解析为「该 URL 不用代理」。

验证（`--get` 对空值和不存在都返回空，**不可靠**；必须实测）：
```bash
git config --global --get http.https://gitee.com.proxy; echo $?   # 0=key存在
GIT_TRACE_CURL=1 git ls-remote git@gitee.com:<user>/<repo>.git HEAD 2>&1 | grep -iE "proxy tunnel|Established connection"
```
- 出现 `Establish HTTP proxy tunnel to gitee.com` / `Established connection to 127.0.0.1 (port 12450)` = **还在走代理**
- 出现 `Established connection to gitee.com (x.x.x.x port 443)` = **直连成功**

## 3. SSH key（Gitee）

```bash
ssh-keygen -t ed25519 -C "邮箱" -f ~/.ssh/id_ed25519 -N ""
cat ~/.ssh/id_ed25519.pub   # 整行复制 → Gitee → 设置 → SSH公钥 https://gitee.com/profile/sshkeys
ssh -T -o StrictHostKeyChecking=accept-new git@gitee.com   # 期望输出: Hi 用户名(@用户名)!
```
- 首次连接加 `-o StrictHostKeyChecking=accept-new` 避免卡在交互确认
- 公钥整行复制，别漏字符别多空格

## 4. clone 到已有内容的目录

- **git clone 拒绝非空目录**（`destination path ... already exists and is not an empty directory`）。处理：先把已有文件 mv 到 /tmp，clone 后再移回
- **用户可能已手动 clone 过** → 出现嵌套（项目目录里套着仓库目录）：把 `.git` 及内容 mv 到项目根，rmdir 空壳
- Windows `rmdir` 报 `Device or resource busy` = 有终端/资源管理器停在该目录。文件移出后空壳不影响使用，提示用户关掉占用窗口后再删；命令链里 rmdir 失败会中断后续 `&&` 命令，注意补跑
- 仓库分支可能是 `master`（Gitee 默认）而团队文档写 `main`——以仓库实际为准，提醒用户与组长确认统一叫法

## 5. 分支规范（团队 7 人项目）

```bash
git clone git@gitee.com:<用户名>/<仓库名>.git
git checkout -b develop origin/develop   # 远程有 develop 时切开发分支
git checkout -b feature/xxx develop      # 每个任务拉功能分支
# 永不直接 push 主干；每天开工 git pull origin <主干>
```

## 验证清单

- [ ] `git config --global --list`：身份是真实姓名/邮箱（不是 Hermes 默认值）
- [ ] `ssh -T -o StrictHostKeyChecking=accept-new git@gitee.com` 显示 Hi 用户名
- [ ] `GIT_TRACE_CURL` 实测 gitee 直连、无 proxy tunnel
- [ ] `git ls-remote git@gitee.com:<user>/<repo>.git HEAD` 返回 commit（成员权限生效）
- [ ] clone 后 `git status` 干净、分支正确
