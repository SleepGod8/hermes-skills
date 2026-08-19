# Windows 下从 MSYS git-bash 杀进程（重启服务用）

实测（2026-08，GitHub 体检工具重启）：重启服务 = 验 PID → 杀旧进程 → 后台重启 → 健康检查。

## 坑

- ❌ `taskkill //F //PID <pid>`：MSYS 未转换双斜杠时直接报「无效参数/选项 - '//F'」（GBK 乱码显示）
- ❌ `cmd //c "taskkill /F /PID <pid>"`：可能只打开交互式 cmd 而不执行命令（输出 cmd 横幅后命令未跑）

## 可靠写法

```bash
MSYS_NO_PATHCONV=1 powershell -Command "Stop-Process -Id <PID> -Force"
# 或直接 taskkill（已验证同样有效）：
MSYS_NO_PATHCONV=1 taskkill /F /PID <pid>
```

- 杀完用 `netstat -ano | grep ":PORT.*LISTENING"` 确认无残留，再重启新代码
- 后台重启用 terminal(background=true)（`&` 会被拒绝）；起来后先 curl `/api/health` 验证再交付

## 注意

服务 PID 可能中途变化（外部重启过），杀之前先 netstat 拿当前 LISTENING PID，别迷信旧记录。
