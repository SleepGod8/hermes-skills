---
name: git-china-network-config
description: "国内网络环境的 git 配置：Gitee 直连绕代理（.gitconfig 写 proxy= 空值；命令行传空串=删除配置的坑）、GitHub 走/绕代理、GIT_TRACE_CURL 实测验证、SSH key 配置、PowerShell vs git-bash 路径、非空目录 clone。Invoke when user asks 配git代理/gitee连不上/绕开代理/git clone失败/ssh key。"
version: 1.0.0
tags: [git, gitee, github, proxy, china, network, ssh]
metadata:
  hermes:
    tags: [git, gitee, proxy, china, network]
    category: devops
---

# 国内网络 git 配置（Gitee 直连 + GitHub 代理 + 验证）

中国用户典型场景：全局代理常断（如 127.0.0.1:12450），Gitee 国内直连不需要代理，GitHub 需要代理。本技能覆盖 per-host 代理配置、实测验证方法、SSH 配置和常见路径坑。

## 核心坑 1：命令行传空字符串 = 删除配置，不是设为空值

**用户常踩**：`git config --global http.https://gitee.com.proxy ""` 想给 Gitee 单独禁用代理，命令不报错，但实际**删除了该 key**（git 把空值参数当 --unset 处理），代理根本没绕开。

**正确做法**：编辑 `~/.gitconfig` 文件写入空值（文件里的空值才会被 git 解析为"该 URL 不用代理"）：

```ini
[http "https://gitee.com"]
	proxy =
```

用 patch 工具加在 `[https]` 段之后即可。

## 验证：`--get` 不可靠，必须实测

`git config --global --get <key>` 对"空值"和"key 不存在"都返回空行，无法区分。用：

```bash
# 1. key 是否存在（0=存在, 1=不存在）
git config --global --get http.https://gitee.com.proxy; echo "exit=$?"

# 2. 真实连接测试（最可靠）：观察是走代理隧道还是直连真实 IP
GIT_TRACE_CURL=1 git ls-remote https://gitee.com/<任意仓库>.git HEAD 2>&1 | grep -iE "proxy tunnel|Established connection"
#   走代理: "Establish HTTP proxy tunnel to gitee.com:443" + "Established connection to 127.0.0.1 (port 12450)"
#   绕开了: "Established connection to gitee.com (180.76.198.77 port 443)"（直连真实 IP，无 tunnel 行）
```

## 场景：Gitee 直连 + GitHub 走代理

- 保留全局代理 `http.proxy=http://127.0.0.1:12450`（GitHub 等翻墙场景用）
- 只给 gitee.com 加 per-host 空代理（上文 .gitconfig 写法）
- 临时绕过代理直连 GitHub（代理断时）：`git -c http.proxy= -c https.proxy= clone <github-url>`

## SSH key 配置（Gitee）

```bash
ssh-keygen -t ed25519 -C "你的邮箱" -f ~/.ssh/id_ed25519 -N ""   # 无密码短语
# 公钥内容贴到 Gitee → 设置 → SSH 公钥（整行，ssh-ed25519 开头）
ssh -T -o StrictHostKeyChecking=accept-new -o ConnectTimeout=15 git@gitee.com
# 成功输出: Hi <用户名>(@<用户名>)! You've successfully authenticated...
```

## 坑 2：PowerShell vs git-bash 路径写法

- `/e/项目/xxx` 是 git-bash（MSYS）写法；PowerShell 不认，报 `找不到路径 C:\e\...`
- PowerShell 用 `cd "E:\项目\xxx"`（含中文必须加引号）
- 同一台机器上两种终端改的是同一个 `~/.gitconfig`，可互相验证配置

## 坑 3：clone 进非空目录 / 目录占用

- `git clone <url> <已存在非空目录>` 报 `destination path ... exists and is not an empty directory`
- 处理：先把目录内容 mv 到 /tmp，clone 成功后再移回；或 clone 到子目录再整理
- 整理后 `rmdir` 报 `Device or resource busy`：有终端/资源管理器停在该目录，关掉占用窗口后再删，或忽略（不影响使用）

## 坑 4：git 身份默认值是工具生成的

新机器上 `git config --global user.name` 可能是 "Hermes"、email 是 `xxx@hermes.local`——多人协作前必须改成真实姓名 + 真实邮箱（建议与 Gitee 绑定的邮箱一致），否则同事看不到是谁提交的。占位符（如"你Gitee绑定的邮箱"）被复制进去要立刻发现并修正。

## 标准检查命令（新机器/新环境）

```bash
git config --global --list      # 看 proxy/user 等全局配置
git config --global user.name && git config --global user.email
```
