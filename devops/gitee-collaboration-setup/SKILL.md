---
name: gitee-collaboration-setup
description: "Gitee（码云）多人协作环境搭建与使用：开工前清单、git 身份配置、绕过代理直连、SSH key、分支保护与团队规范。含关键坑：git config 命令行空字符串=删除配置项（须编辑 .gitconfig 写空值才能让某 URL 不走代理），以及 GIT_TRACE_CURL 实测验证法。Invoke when user says Gitee/码云/git 多人协作/配 SSH key/git 代理超时/开工前准备。"
version: 1.0.0
tags: [gitee, git, collaboration, china, proxy, ssh]
metadata:
  hermes:
    tags: [gitee, git, collaboration, china, proxy, ssh]
    category: devops
---

# Gitee 多人协作环境搭建与使用

## 触发条件

- 用户提到 Gitee / 码云 / 国内 git 托管
- 用户准备多人/多 agent 协作开发，问「开工前要做什么」「需要了解什么」
- 用户要配 git 身份、SSH key、git 代理绕过
- 用户报 git clone/push 超时或卡死（疑似代理）

## 一、开工前清单（按顺序）

1. **账号与仓库**：注册 Gitee（手机号）→ 新建**私有**仓库（勾 README + `.gitignore` 模板，Python 项目选 Python 模板）→ 邀请成员（角色：管理员/开发者/报告者/观察者；核心成员给「开发者」，负责人留「管理员」）
2. **本地环境**：
   - git 身份（见下节）
   - Gitee 绕过代理（见第三节，**先做这个再 clone**）
   - SSH key（见第四节）
3. **项目骨架文档**（开工前最值钱的部分，能省 80% 协作摩擦）：`README.md`（简介+本地运行步骤）、`CONTRIBUTING.md`（分支/提交/PR 规范）、`docs/架构设计.md`、`docs/接口约定.md`（多人并发冲突集中地，先定死）、`.gitignore`
4. **团队规则**（开工第一天 10 分钟讲清）：`main` 设为保护分支（要求 PR + ≥1 评审）、分支命名 `feat/` `fix/` `docs/`、Conventional Commits、用 Issue 认领任务（PR 里写 `Closes #编号` 自动关）

## 二、git 身份配置

```bash
git config --global user.name "真实姓名"
git config --global user.email "真实邮箱@xxx.com"
```

⚠️ **先 clarify 问出真实邮箱/姓名再给命令**——用户会原样复制占位符（本会话用户把 `"你Gitee绑定的邮箱"` 直接复制进了配置，变成字面量）。命令里永远不要出现占位符文本。

## 三、Gitee 绕过代理（关键！国内直连）

**不要用命令行空串设置**（见 Pitfall 1）。正确姿势：编辑 `~/.gitconfig`（用 read_file + patch，不要 echo 追加），追加：

```ini
[http "https://gitee.com"]
	proxy =
```

git 把**配置文件中的空值**解析为「该 URL 不使用代理」；全局 `http.proxy` 保留给 GitHub 等翻墙场景。

验证（两条都要）：
```bash
git config --global --get http.https://gitee.com.proxy; echo "exit=$?"   # 0=key 存在
GIT_TRACE_CURL=1 git ls-remote https://gitee.com/mirrors/gitee.git HEAD 2>&1 | grep -iE "proxy tunnel|Established connection"
```
成功标志：看到 `Established connection to gitee.com (... port 443)`，**没有** `proxy tunnel` / `port 12450`。
一键脚本：`bash scripts/verify-gitee-proxy.sh`。

## 四、SSH key

```bash
ssh-keygen -t ed25519 -C "邮箱" -f ~/.ssh/id_ed25519 -N ""
# ~/.ssh 不存在会自动创建；-N "" = 无密码短语
```
公钥（`~/.ssh/id_ed25519.pub` 一整行）贴到 **https://gitee.com/profile/sshkeys**（标题任意备注，需输 Gitee 登录密码确认）。
测试：`ssh -T git@gitee.com` → `Hi, 你的名字!`

## Pitfalls

1. **`git config` 命令行传空字符串 = 删除该配置项**（等同 `--unset`），不是「设为空值」！`git config --global http.https://gitee.com.proxy ""`（PowerShell 和 bash 都一样）静默删 key，无报错。想设「某 URL 不用代理」必须编辑 .gitconfig 写 `proxy =` 空值。
2. `git config --get <key>` 对「key 不存在」和「存在但值为空」**都输出空行**——必须看 exit code（0=存在，1=不存在），或 `git config --global --list | grep gitee`。
3. 可粘贴命令里**不要放占位符文本**（`"你的邮箱"` 这类），用户会原样复制。先 clarify 拿真实值。
4. 用户可能在 PowerShell 跑命令，但 `~/.gitconfig` 只有一个——验证时用 terminal(git-bash) 读同一文件即可，注意两条 `git config --global` 写入的是同一份配置。
5. 国内网络 Gitee 直连即可；若机器有全局 git 代理（如 `127.0.0.1:12450`），代理断连会直接导致 clone/push 超时——这就是「Gitee 连不上」的常见根因。

## 支持文件

- `references/gitee-proxy-bypass.md` — 空串删除 key 的原理与 GIT_TRACE_CURL 实测对比记录
- `scripts/verify-gitee-proxy.sh` — 一键验证 Gitee 是否直连（检查 key + 真实连接 trace）
