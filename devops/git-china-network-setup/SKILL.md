---
name: git-china-network-setup
description: "Configure git on Chinese networks: per-host proxy bypass (Gitee/domestic hosts direct, GitHub via proxy), Gitee SSH keys, clone/auth from Gitee, and Windows shell path pitfalls. Use when the user sets up git for Gitee, has proxy problems with domestic git hosts, configures per-host proxy exceptions, or needs SSH auth for Gitee."
version: 1.0.0
tags: [git, gitee, proxy, ssh, china-network, windows]
metadata:
  hermes:
    tags: [git, gitee, proxy, ssh, china-network, windows]
    category: devops
---

# Git 中国网络配置（Gitee 直连 / 代理绕过 / SSH）

在中文网络环境配置 git：国内主机（Gitee 等）直连、国外主机（GitHub）走代理、Gitee SSH 认证、Windows 双 shell 路径坑。

## 触发条件

- 用户要 clone/push Gitee 仓库、配 Gitee SSH key、设置 git 身份
- git 走代理连不上国内主机（代理常断导致超时）
- 需要"某个域名绕过代理、其他走代理"的 per-host 配置
- 用户在多台电脑上重复做同样的 git 初始化

## 核心：per-host 代理绕过（本会话踩过的大坑）

全局代理（如 `http://127.0.0.1:12450`）会让 Gitee 等国内主机也走代理，代理一断就超时。正确做法是给国内主机单独设空代理：

### ❌ 错误做法（命令行的坑）

```bash
git config --global http.https://gitee.com.proxy ""   # ⚠️ 无效！
```

**git 会把命令行传入的空字符串值当作"删除该配置项"**（等价于 unset），不报错但 key 根本没写入。PowerShell 或 bash 里传 `""` 都一样。用户会以为配好了，实际 `--get` 返回 exit=1。

### ✅ 正确做法：直接编辑配置文件

`~/.gitconfig`（Windows: `C:\Users\<user>\.gitconfig`）里写**空值**，git 才解析为"该 URL 不用代理"：

```ini
[http]
	proxy = http://127.0.0.1:12450
[https]
	proxy = http://127.0.0.1:12450
[http "https://gitee.com"]
	proxy =            # ← 空值 = 该域名直连，绕过全局代理
```

注意：Gitee 也用 HTTPS，必须放在 `[http "https://gitee.com"]` 段（不是 `[https "..."]`）。

## 验证（两种方法都要用）

### 1. 配置是否存在（不能用裸 --get 判断）

```bash
git config --global --get http.https://gitee.com.proxy; echo "exit=$?"
# exit=0 → key 存在（即使值为空）；exit=1 → key 不存在
```

`--get` 对"空值"和"没配置"都打印空行，**必须看 exit code** 或 `git config --global --list | grep gitee`。

### 2. 真实连接测试（最可靠）

```bash
GIT_TRACE_CURL=1 git ls-remote https://gitee.com/<owner>/<repo>.git HEAD 2>&1 | grep -iE "proxy tunnel|Established connection"
```

- 走了代理：`Establish HTTP proxy tunnel to gitee.com:443` + `Established connection to 127.0.0.1 (127.0.0.1 port 12450)`
- 直连成功：`Established connection to gitee.com (180.76.198.77 port 443)`（无 proxy tunnel 行）

注意 curl 命令测的是 curl 的环境变量，**不读 git config**——要测 git 的行为必须用 `GIT_TRACE_CURL` + `git ls-remote`。

## Gitee SSH key（一劳永逸，免密码）

```bash
ssh-keygen -t ed25519 -C "你的邮箱" -f ~/.ssh/id_ed25519 -N ""   # -N "" 免密码短语
cat ~/.ssh/id_ed25519.pub   # 公钥，一整行
```

粘贴到 **https://gitee.com/profile/sshkeys**（标题随意）。测试（首次自动接受 host key 避免卡交互）：

```bash
ssh -T -o StrictHostKeyChecking=accept-new -o ConnectTimeout=15 git@gitee.com
# 成功: Hi SleepGod8(@SleepGod8)! You've successfully authenticated...
```

## git 身份配置

多人协作前必须改默认身份（工具默认值如 `Hermes`/`80704@hermes.local` 会让同事认不出提交人）：

```bash
git config --global user.name "真实姓名"
git config --global user.email "Gitee 绑定的邮箱"
```

⚠️ 给用户的命令模板里**不要留占位符让用户原样复制**（用户会真的把 `"你Gitee绑定的邮箱"` 敲进去）。要么先问清真实值，要么用 `<占位>` 并显式警告"把尖括号内容替换成你的真实值"。

## clone 到已存在目录

`git clone` 目标目录非空会报 `fatal: destination path 'X' already exists and is not an empty directory`。处理：

```bash
mv "旧目录/现有文件" /tmp/          # 先移走文件
git clone <url> "旧目录"
mv /tmp/现有文件 "旧目录/"
```

若目录里已有别人 clone 的子目录（嵌套），把子目录内容（含 `.git` 隐藏文件）移到父目录后 `rmdir` 空壳即可。

## Pitfalls

- **PowerShell vs git-bash 路径语法**：`/e/项目/xxx` 是 MSYS/git-bash 写法，PowerShell 报"找不到路径"。PowerShell 用 `cd "E:\项目\xxx"`（中文路径必须加引号）。给用户命令前先看提示符（`PS>` 还是 `$`）用对应语法。
- **rmdir "Device or resource busy"**：用户的 PowerShell/资源管理器还停在该目录时删不掉，提示用户关掉占用窗口，或忽略（不影响使用）。
- **SSH 不走 HTTP 代理**：`ssh -T git@gitee.com` 走 22 端口，与 http.proxy 无关；配了 per-host 代理后 clone 用 SSH 地址最稳。
- **clone 地址格式**：`git@gitee.com:仓库所有者用户名/仓库名.git`——`xxx` 是**建仓库的人**（或组织）的用户名，不是自己的账号。最省事是让对方从仓库页"克隆/下载→SSH"直接复制地址。
- **远程分支是 master 不是 main**：Gitee 默认主干常叫 `master`，文档约定可能是 `main`——先 `git branch -a` 看实际分支，别假设。
