# 实战案例：智能财富管家目录清理（2026-08）

## 背景
- 开发目录 `E:\项目\智能财富管家系统`（中文名）需要改名为 `smart-wealth`
- 目录内嵌套了一个 `smart-wealth\smart-wealth\` 子目录（早期 clone 空壳残留）需要删除

## 排查链（完整过程）

### 1. 改名失败：git-bash mv
```bash
mv "智能财富管家系统" smart-wealth
# → mv: cannot move ... Permission denied
```

### 2. 找锁：psutil 查 cwd
```python
import psutil
for p in psutil.process_iter(['pid','name','cwd']):
    cwd = p.info.get('cwd') or ''
    if cwd.lower().startswith(target.lower()):
        print(p.info['pid'], p.info['name'], cwd)
```
- 第一次查到 4 个进程（python.exe + bash.exe），cwd 全部停在目标目录
- kill 后**又出现新的 PID**（bash 进程池复用）→ 意识到锁源是 Hermes terminal 的持久 bash 会话

### 3. cmd ren 假成功
```bash
cmd //c 'ren "E:\项目\智能财富管家系统" smart-wealth'
# 输出乱码但 echo 显示"成功"——实际目录没变！GBK/UTF-8 编码导致 cmd 拿到乱码路径，静默失败返回 0
```
教训：**cmd ren 的中文路径结果不可信**，必须事后验证（ls 确认）。

### 4. 正解：Python os.rename（一次成功）
```python
import os
os.rename(r"E:\项目\智能财富管家系统", r"E:\项目\smart-wealth")
```
改完验证：`git status` / `git branch --show-current` / `git remote get-url origin` 全部正常（.git 跟着目录走）。

### 5. 嵌套目录删除：Hermes 终端 cwd 锁
```bash
rm -rf /e/项目/smart-wealth/smart-wealth
# → Device or resource busy（反复）
```
- psutil 查到锁进程：bash.exe × 3 + python.exe（PID 每次不同 → 进程池）
- kill 掉一批又出现新一批 → 不能靠 kill
- **解法**：执行 `cd /e/项目/smart-wealth`（让持久 cwd 离开嵌套目录）→ 立即 `NO_LOCK` → `rm -rf` 成功

### 6. 嵌套仓库价值判断
删之前先看它是什么：
```bash
cd smart-wealth/smart-wealth && git log --oneline -3
# fb28168 update haha. / 7495bcf add haha. / 2903557 Initial commit（master 分支）
```
确认是空壳仓库残留（haha/License，历史已包含在主仓库合并历史里）→ 安全删除。

## 关键结论
- 中文路径：Python os.rename / os.rmdir 是最终解法
- 目录锁：先 psutil 定位，再判断锁源；Hermes 终端锁 = cd 出去即释放
- cmd ren 中文路径：假成功陷阱，用完必须验证
