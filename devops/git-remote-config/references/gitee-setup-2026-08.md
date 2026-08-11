# Gitee 配置实战（2026-08）

## 场景
用户（@SleepGod8）团队项目使用 Gitee（`git@gitee.com:hujunxianx/smart-wealth.git`），本机全局代理 `127.0.0.1:12450` 常断，需要 Gitee 直连 + SSH 免密。

## 完成的全流程

### 1. Gitee 绕代理
- 用户按建议跑 `git config --global http.https://gitee.com.proxy ""` → **没生效**（实测 `--get` exit=1，key 不存在）
- 根因：git 命令行空字符串 = 删除配置
- 修复：直接改 `C:\Users\80704\.gitconfig` 加 `[http "https://gitee.com"] proxy =`（空值）
- 验证：`GIT_TRACE_CURL=1 git ls-remote https://gitee.com/mirrors/gitee.git HEAD` 从 `proxy tunnel ... port 12450` 变成 `Established connection to gitee.com (180.76.198.77 port 443)`

### 2. 身份配置
- 用户原样复制了占位符 `git config --global user.email "你Gitee绑定的邮箱"` → email 变成字面量
- 用 clarify 问到真实邮箱 `807047353@qq.com` 后设置成功
- 教训：给命令模板时占位符要标注"替换"，或先问真实值

### 3. SSH key
- `ssh-keygen -t ed25519 -C "807047353@qq.com" -f ~/.ssh/id_ed25519 -N ""`
- 公钥贴 Gitee → https://gitee.com/profile/sshkeys
- 测试：`ssh -T -o StrictHostKeyChecking=accept-new -o ConnectTimeout=15 git@gitee.com` → `Hi SleepGod8(@SleepGod8)!`

### 4. 仓库拉取与版本对齐
- 队友发指令：`git clone git@gitee.com:hujunxianx/smart-wealth.git && cd smart-wealth && git checkout develop`
- 发现本地 `E:\项目\smart-wealth-agent(1)` 有更新代码（5 提交 2325e40）但 Gitee develop 只有初始骨架（829d15b），两线无共同历史
- 用户确认 Gitee 是权威 → 在已有 clone 目录 `git fetch origin && git checkout develop && git pull origin develop`
- 本地已有另一条提交线，pull 产生 merge commit（d5eb137），该 merge 后来被推到远程 → 远程 develop 变为合并版
- 教训：**"先确认哪个是权威版本再动"**——本地代码可能比远程新（未推送），盲目 clone 会拿旧版

### 5. 目录改名（关联 windows-file-ops skill）
- 权威目录中文名 → 英文名：git-bash mv 失败、cmd ren 假成功，最终 Python os.rename 成功
- 嵌套旧 clone 残留（smart-wealth/smart-wealth）通过 Hermes 终端 cwd 锁排查后删除

## 可复用命令集
```bash
# 每天开工
cd /e/项目/smart-wealth && git pull origin develop
git checkout -b feature/xxx

# 日常验证
git status && git branch --show-current && git remote -v
```
