---
name: git-remote-config
description: "Git 远程仓库与本地配置：代理绕过(per-URL)、身份(user.name/email)、SSH key、平台差异。核心坑：git config 命令行传空字符串=删除配置项（不是设为空值）；per-URL 代理必须写配置文件。When setting up git remotes, per-host proxy bypass, identity, or SSH keys for Gitee/GitHub, or a repo clone/push times out due to proxy. 中文关键词：git配置/gitee代理/git ssh配置。"
version: 1.0.0
tags: [git, gitee, github, proxy, ssh, config]
metadata:
  hermes:
    tags: [git, gitee, github, proxy, ssh, config]
    category: devops
---

# Git 远程仓库与本地配置

## 触发条件
- 配置 git 代理（全局代理 + 某域名需要直连绕过）
- 配置 user.name / user.email
- 生成/绑定 SSH key（Gitee、GitHub、自建）
- clone/push 超时、走代理异常、绕代理直连

## 核心坑

### 1. `git config key ""` 空字符串 = 删除配置项，不是设为空值！
命令行传空串会被 git 当成 unset（静默成功，key 直接消失）。
- 错误示范：`git config --global http.https://gitee.com.proxy ""` → key 被删除，没生效
- 正确做法：**手动编辑配置文件** `~/.gitconfig`（Windows: `C:\Users\<user>\.gitconfig`）：
  ```ini
  [http "https://gitee.com"]
      proxy =
  ```
  文件里的空值才会被 git 解析为"该 URL 不使用代理"。
- 验证必须靠 exit code（空值也会显示空行，`--get` 输出无法区分）：
  ```bash
  git config --global --get http.https://gitee.com.proxy; echo "exit=$?"
  # 0=key存在(生效)，1=key不存在(没写进去)
  ```

### 2. per-URL 代理绕过与实测验证
场景：全局代理 `http://127.0.0.1:12450`（常断），Gitee 国内直连不需要代理。
- 配置：见上（`[http "https://gitee.com"] proxy =` 空值）
- 实测验证（关键步骤，不能只看配置）：
  ```bash
  GIT_TRACE_CURL=1 git ls-remote <url> HEAD 2>&1 | grep -E "proxy tunnel|Established connection"
  ```
  - 还在走代理：`Establish HTTP proxy tunnel to gitee.com:443` + `Established connection to 127.0.0.1 (port 12450)`
  - 绕开成功：`Established connection to gitee.com (真实IP port 443)`，无 proxy tunnel 行

### 3. 身份配置
- `git config --global user.name "真实姓名"` / `user.email "真实邮箱"`
- **给用户的命令模板里不要留占位符**（如"你Gitee绑定的邮箱"——用户会原样复制进去变成字面量）。先问真实邮箱，或写命令时明确提示"替换为你的真实邮箱"。
- 多人协作必须真实身份，否则提交记录显示工具默认值（如 Hermes / xxx@hermes.local），队友无法识别。

### 4. SSH key 配置流程
```bash
# 生成（ed25519，无密码短语）
ssh-keygen -t ed25519 -C "邮箱" -f ~/.ssh/id_ed25519 -N ""

# 取公钥（整行复制到 Gitee/GitHub 设置 → SSH公钥）
cat ~/.ssh/id_ed25519.pub

# 测试连接（accept-new 自动接受 host key，避免卡交互）
ssh -T -o StrictHostKeyChecking=accept-new -o ConnectTimeout=15 git@gitee.com
```
- 成功标志：`Hi 用户名(@账号)! You've successfully authenticated, but GITEE.COM does not provide shell access.`
- 失败：`Permission denied (publickey)` = 公钥没贴对/没贴
- 公钥形如 `ssh-ed25519 AAAA... 邮箱`，一整行，别漏字符别多空格

### 5. 平台路径差异
- git-bash（MSYS）：`/e/项目/...`；PowerShell：`E:\项目\...`（中文加引号）
- 把 `/e/` 风格命令贴进 PowerShell 报"找不到路径"——不是目录不存在，是写法不对

### 6. Gitee 特有
- 国内直连，全局代理反而拖慢/断连（代理一断 clone/push 就超时）
- SSH 地址格式 `git@gitee.com:仓库所有者用户名/仓库名.git`——用户名是**仓库所有者**（不一定是自己，别人建的仓库用别人的用户名）
- 获取地址最稳：让建仓库的人从 Gitee 页面「克隆/下载 → SSH」复制

## 流程速查
```
诊断代理（GIT_TRACE_CURL 实测）→ 写 per-URL 空代理（配置文件）→ 重测
身份 → 先问真实邮箱 → 设置 → 确认
SSH → ssh-keygen → 贴公钥 → ssh -T 测试
clone → git checkout develop → 每天 git pull origin develop
```

## references
- `references/gitee-setup-2026-08.md` — Gitee 全流程配置实战（代理/身份/SSH/仓库拉取/版本对齐）
