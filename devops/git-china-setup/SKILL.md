---
name: git-china-setup
description: "Git/Gitee 在国内网络下的初始化与排障：per-host 绕代理直连、身份配置、SSH key、clone 到非空目录、本地与远程版本漂移检测。Invoke when user 配置 git 身份/SSH/代理/Gitee 仓库，或 clone/push 超时/走代理异常。"
version: 1.0.0
tags: [git, gitee, proxy, ssh, china-network, setup]
metadata:
  hermes:
    tags: [git, gitee, proxy, ssh, china-network, setup]
    category: devops
---

# Git 国内环境初始化与排障

## 触发条件
- 配置 git 身份 / SSH key / Gitee（或 GitHub）仓库
- clone/push 超时或走代理失败（国内网络，代理常断）
- 需要验证 git 实际是否走了代理

## 1. per-host 绕开代理（核心坑）

### ⚠️ 致命坑：命令行设置空字符串 = 删除配置项
```bash
git config --global http.https://gitee.com.proxy ""   # ❌ 无效！git 把空串当 unset，key 被删
```
PowerShell 或 bash 传 `""` 都会被 git 当作删除。**正确做法：直接编辑 `~/.gitconfig` 文件**，写入空值：
```ini
[http "https://gitee.com"]
    proxy =
```
只有配置文件里的空值才被 git 解析为"该 URL 不用代理"。

### 验证是否真的绕开（必须实测，不能只看 --get）
```bash
# 1) key 是否存在：空值 exit=0，不存在 exit=1
git config --global --get http.https://gitee.com.proxy; echo "exit=$?"
# 2) 真实连接测试：观察 git 实际连到哪
GIT_TRACE_CURL=1 git ls-remote git@gitee.com:owner/repo.git HEAD 2>&1 | grep -iE "proxy tunnel|Established connection"
# 走代理: "Establish HTTP proxy tunnel to gitee.com" + "port 12450"
# 直连:   "Established connection to gitee.com (x.x.x.x port 443)"
```

### per-host 语法
`http.https://gitee.com.proxy` = section `http` + subsection `https://gitee.com` + key `proxy`。只影响该 host，全局代理（GitHub 翻墙用）保留。

## 2. 身份配置（多人协作前必做）
```bash
git config --global user.name "真实姓名"
git config --global user.email "真实邮箱"
```
⚠️ 占位符会原样写入：`user.email "你Gitee绑定的邮箱"` 会存字面量。配置后必须 `git config --global user.email` 实测确认，别信命令回显。

## 3. SSH key（Gitee/GitHub 通用）
```bash
ssh-keygen -t ed25519 -C "邮箱" -f ~/.ssh/id_ed25519 -N ""
# 公钥粘贴到 Gitee → 设置 → SSH公钥；标题任意
ssh -T -o StrictHostKeyChecking=accept-new git@gitee.com   # "Hi <用户名>!" 即成功
```

## 4. Windows 路径语法（PowerShell vs git-bash）
- PowerShell：`cd "E:\项目\xxx"`（中文路径必须加引号）
- git-bash（Hermes terminal）：`cd /e/项目/xxx`
- 在 PowerShell 里用 `/e/...` 会报 "找不到路径"——先判断用户在哪个 shell 再给命令

## 5. clone 到非空目录
git clone 目标目录必须为空：先 `mv` 移出文件 → clone → 移回。
`rmdir` 报 "Device or resource busy" = 有终端/资源管理器停在目录里，关掉窗口即可（不影响使用，可留空目录）。

## 6. 本地与远程版本漂移检测（队友让 clone 前先对比）
```bash
git ls-remote git@gitee.com:owner/repo.git              # 远程各分支最新 commit
git fetch origin && git log origin/develop --oneline -5
git merge-base HEAD origin/develop                      # 报错/空 = 本地与远程不同源
```
常见：本地工作目录有**更新**代码但无 remote；远程 develop 落后。先确认权威版本再决定 push 还是 clone，别盲目执行队友的 clone 命令。

## 7. 验证清单
- [ ] `git config --global --list`：身份正确、per-host 代理已设
- [ ] `GIT_TRACE_CURL` 实测 gitee 直连（无 proxy tunnel）
- [ ] `ssh -T git@gitee.com` 通过
