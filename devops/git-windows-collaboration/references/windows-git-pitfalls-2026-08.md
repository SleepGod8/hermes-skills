# Windows Git 排障实录（2026-08 智能财富管家项目）

## 1. Gitee 绕代理完整过程

背景：全局 git 配置 `http.proxy=http://127.0.0.1:12450`（常断的翻墙代理）。Gitee 国内直连不需要代理，代理断时 clone/push 超时。

### 错误尝试（两个坑）

```bash
git config --global http.https://gitee.com.proxy ""
# ❌ git 把命令行空字符串当 unset！验证：git config --global --get ... 返回 exit=1（key 不存在）
```

PowerShell 里执行时无报错，误导以为成功。`git config --get` 对"空值"和"未配置"都返回空行，无法区分——**要用 exit code**（0=key 存在，1=不存在）。

### 正确做法

直接编辑 `~/.gitconfig`（write_file/patch 工具）添加：

```ini
[http "https://gitee.com"]
	proxy =
```

文件里的空值 = "该 URL 禁用代理"。验证用 GIT_TRACE_CURL：

```bash
GIT_TRACE_CURL=1 git ls-remote https://gitee.com/mirrors/gitee.git HEAD 2>&1 | grep -iE "proxy tunnel|Established connection"
# 修改前: Establish HTTP proxy tunnel to gitee.com:443 + Established connection to 127.0.0.1 (port 12450)
# 修改后: Established connection to gitee.com (180.76.198.77 port 443)   ← 直连成功
```

### 教训

- 命令行设空值 = 删除配置（git 的反直觉行为）
- 代理是"绕过某域名"用 per-URL 配置 `http.<url>.proxy`，不是全局改
- 用真实连接测试（GIT_TRACE_CURL）验证，不要只看配置是否写入

## 2. 中文目录删除被锁（Hermes 终端 cwd 锁）

### 症状演进
1. 早期 clone 残留一个嵌套空壳目录 `smart-wealth/smart-wealth`（旧仓库副本）
2. `rmdir` 报 `Device or resource busy`（有进程 cwd 停在里面）
3. 后来 `rmdir` 报 `Directory not empty`（占用解除但目录非空，里面有 .git 等——是个完整旧仓库）
4. `rm -rf` 报 `Device or resource busy`

### 排查
```bash
python - <<'EOF'
import psutil
target = r"E:\项目\smart-wealth\smart-wealth"
for p in psutil.process_iter(['pid','name','cwd']):
    try:
        cwd = p.info.get('cwd') or ''
        if cwd.lower().startswith(target.lower()):
            print(f"PID={p.info['pid']} NAME={p.info['name']}")
    except Exception: pass
EOF
```

发现 bash.exe × 3 + python.exe cwd 全停在该目录。

### 关键洞察
这些是 **Hermes terminal 工具的后台持久 bash 会话**（之前某条命令 `cd` 进过该目录，会话 cwd 一直停在那）。特征：**kill 一批进程，下一次查询又出现新 PID**（进程池或新会话）。

### 解法（不要 kill）
执行一条 `cd /e/项目/smart-wealth`（父目录）让持久会话 cwd 离开 → 再查 NO_LOCK → `rm -rf` 成功。

### 教训
- 删除/移动目录失败先查 cwd 锁（psutil），不要盲目 kill 进程
- Hermes 环境里"cd 出去"比"杀进程"安全有效
- kill 用户的 bash/python 可能影响其工作，先尝试移动会话 cwd

## 3. 中文目录改名（mv / cmd ren 都失败的最终方案）

- `mv "智能财富管家系统" smart-wealth` → Permission denied（目录锁）
- 释放锁后仍失败？→ 用 `cmd //c 'ren "E:\项目\智能财富管家系统" smart-wealth'` 显示成功但实际无效（中文路径经 git-bash→cmd 编码被破坏，ren 匹配不到）
- **最终方案**：Python os.rename
  ```bash
  python -c "import os; os.rename(r'E:\项目\智能财富管家系统', r'E:\项目\smart-wealth')"
  ```
  输出 True 即成功。改名后 git 完全不受影响（remote/分支跟着 .git 走）。

## 4. 团队分支规范（本项目实测流程）

组长发的规范命令（每个组员自己的功能分支）：
```
git fetch origin
git switch develop
git pull --ff-only origin develop
git switch feature/<名字>
git pull --ff-only origin feature/<名字>
# 修改提交：
git status && git add <自己文件> && git commit -m "feat(scope): ..." && git push origin feature/<名字>
# PR: feature/<名字> -> develop（Gitee 网页）
```

要点：
- `--ff-only` 保证不产生意外 merge commit
- 远程分支通常组长已建好（fetch 后 origin/feature/xxx 存在），首次 pull --ff-only 会成功（空分支）
- 本地分支名不对 → `git branch -m 正确名`（未推送时）
- 提交前检查：branch --show-current / status / diff --cached --name-only
- 工作区有未提交修改（如 docker-compose.yml 本地适配）时 switch 分支会带着走——pull 若远程也改了同文件会拒绝

## 5. PR 描述模板（L3 风控域示例）

```
## 改动
- 规则引擎框架：RiskRule/RuleMatch/EvalStatus 三分状态
- 20 条规则注册，5 条可确定性实现（RW-002/008/009/012/017）

## 验证
- pytest tests/risk/ → 27 passed

## 风险等级
L3（风控域）→ 需要架构组 + 组长审批

## 依赖/影响
- 无契约变更（A1-A15 待冻结项未动）
- docker-compose.yml 修复暂未提交（等组长决定）
```

## 6. 环境细节备忘

- 本机 git 全局身份：user.name=张树灿 / user.email=807047353@qq.com
- Gitee 账号：@SleepGod8（SSH ed25519 已配）
- Gitee 已绕代理（.gitconfig [http "https://gitee.com"] proxy =）
- 项目开发目录：E:\项目\smart-wealth（原中文名"智能财富管家系统"已改英文）
