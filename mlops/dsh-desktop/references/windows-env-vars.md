# Windows 环境变量查询 / 写入 / API key 验证

实战验证过的流程（2026-08，git-bash + Python）。

## 查询（bash 看不到时必用注册表）

```bash
# 用户级环境变量（HKCU）—— git-bash 的 env 可能不显示，必须查注册表
reg query "HKCU\Environment" /v DEEPSEEK_API_KEY
# 系统级环境变量（HKLM）
reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v DEEPSEEK_API_KEY
# 列全部用户变量
reg query "HKCU\Environment"
```

## 写入（用户级，无需管理员）

```bash
setx DEEPSEEK_API_KEY "sk-xxxx"
```

- setx 写入 HKCU\Environment，对**已运行进程不生效**，需重启目标应用；从已开终端启动的程序继承旧环境，要新开终端
- 从 Python subprocess 调 setx：输出是 GBK 中文（如「成功: 指定的值已得到保存」），`text=True` 默认 utf-8 解码会崩
  → 必须 `subprocess.run([...], capture_output=True, text=True, errors="replace")`

## 验证 key 有效性（不打印完整 key）

```python
import subprocess, json, urllib.request
out = subprocess.run(["reg", "query", "HKCU\\Environment", "/v", "DEEPSEEK_API_KEY"],
                     capture_output=True, text=True).stdout
key = out.split("REG_SZ")[-1].strip()

# chat/completions（核心接口）
body = json.dumps({"model": "deepseek-chat",
                   "messages": [{"role": "user", "content": "hi"}],
                   "max_tokens": 5}).encode()
req = urllib.request.Request("https://api.deepseek.com/chat/completions", data=body,
    headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
# 200 = 有效；401 = 失效

# balance（余额接口，DSH 余额小部件用）
req2 = urllib.request.Request("https://api.deepseek.com/user/balance",
    headers={"Authorization": "Bearer " + key})
```

## 坑

- **错误信息只显示 key 后 4 位**（`Your api key: ****54ef is invalid`）。用户常有多把同前缀 key（如 sk-f27... 系列），必须读完整值对比后 6 位 + 长度才能区分哪把失效
- 典型事故：用户换过 key，新 key 只更新到 `ANTHROPIC_API_KEY`（Claude 兼容接口）或 Hermes `.env`，`DEEPSEEK_API_KEY` 还是旧 key → DSH 等读该变量的程序 401
- 环境变量存在时（即使失效），`~/.dsh/.credentials.yaml` 里的 key **不会**被 DSH 使用（优先级：环境变量 > 文件）
