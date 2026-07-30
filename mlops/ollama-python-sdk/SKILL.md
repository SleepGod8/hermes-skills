---
name: ollama-python-sdk
description: 使用 ollama Python 库调用本地 Ollama 模型，并结合其他 Python 库实现自动化任务
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [ollama, python-sdk, local-llm, automation, gguf]
---

# Ollama Python SDK

使用官方 `ollama` Python 库调用本地 Ollama 服务的模型。

## 何时使用

- 用户想在 Python 脚本中调用本地 Ollama 模型（而非通过 Hermes provider 或 HTTP API）
- 需要将本地模型生成的内容与其它 Python 库（smtplib、requests、pandas 等）集成
- 用户展示或询问 `from ollama import chat` 相关代码

## 安装

```bash
pip install ollama
```

## 基本用法

### 1. 最简调用

```python
from ollama import chat

res = chat(
    model="model-name",       # 本地已下载的模型名，如 "glm-4.7-flash"
    messages=[
        {"role": "user", "content": "你的问题"}
    ]
)
print(res.message.content)    # 获取模型回复
```

### 2. 带类型注解的调用

```python
from ollama import chat, ChatResponse

res: ChatResponse = chat(
    model="model-name",
    messages=[
        {"role": "user", "content": "你的问题"}
    ]
)
# res: ChatResponse 告诉阅读者 res 的类型，纯辅助作用
print(res.message.content)
```

### 3. 结合 SMTP 发送邮件（自动化示例，含错误处理）

```python
from ollama import chat
import smtplib
from email.mime.text import MIMEText

# 生成内容
res = chat(
    model="model-name",
    messages=[{"role": "user", "content": "写一封短信"}]
)

print("✅ AI 生成的内容：", res.message.content)

# 构建邮件
msg = MIMEText(res.message.content, 'plain', 'utf-8')
msg['From'] = 'your@email.com'
msg['To'] = 'target@email.com'
msg['Subject'] = 'AI 自动生成'

# 发送（带错误处理）
try:
    smtp = smtplib.SMTP_SSL('smtp.qq.com', 465)
    smtp.login('your@email.com', '授权码')
    smtp.sendmail('your@email.com', ['target@email.com'], msg.as_string())
    smtp.quit()
    print("✅ 邮件发送成功！")
except Exception as e:
    print(f"❌ 邮件发送失败: {e}")
```

> 完整可运行脚本见 [templates/ollama-send-email.py](templates/ollama-send-email.py)

## API 对比

Ollama 提供三种 API 风格，在 Python 中都可以使用：

| 方式 | 库 | 代码简洁度 | 适用场景 |
|------|-----|-----------|---------|
| **Python SDK** | `ollama`（`pip install ollama`） | ⭐⭐⭐ 最简洁 | 纯 Python 脚本、与其他库集成 |
| **直接 HTTP** | `requests` | ⭐⭐ | 不需要额外安装库时 |
| **OpenAI 兼容** | `openai` | ⭐⭐ | 已有 OpenAI SDK 的项目 |

### Ollama 各端点说明

- `http://localhost:11434/api/generate` — 原生生成端点（`requests.post` 调用）
- `http://localhost:11434/api/chat` — 原生聊天端点（Python SDK 底层用这个）
- `http://localhost:11434/v1/chat/completions` — OpenAI 兼容端点（可配合 OpenAI SDK）

## 注意事项

### ⚠️ 模型首次加载慢

大模型（如 19GB 的 `glm-4.7-flash`）首次调用时需要加载到内存，可能耗时 **1-3 分钟**。后续调用会快很多（模型已缓存在内存中）。

### ⚠️ 密码/授权码安全

不要在代码中硬编码邮箱密码或授权码。建议使用环境变量：

```python
import os
mail_pass = os.getenv('MAIL_PASS')
```

或在终端设置：
```bash
# Windows
set MAIL_PASS=你的授权码
# Linux/macOS
export MAIL_PASS='你的授权码'
```

### ⚠️ QQ邮箱/163邮箱 SMTP 配置

| 邮箱 | SMTP 服务器 | SSL 端口 | 备注 |
|------|------------|---------|------|
| QQ邮箱 | `smtp.qq.com` | 465 | 需开启 SMTP 服务获取授权码 |
| 163邮箱 | `smtp.163.com` | 465 | 需开启 SMTP 服务获取授权码 |

## 常见问题

- **模型名错误**：用 `curl http://localhost:11434/api/tags` 查看本地已下载的模型列表
- **Ollama 未运行**：确保 `ollama serve` 或 Ollama 桌面应用在运行
- **首次调用超时**：增大 timeout，大模型加载需要时间
- **`ModuleNotFoundError: No module named 'ollama'`**：先执行 `pip install ollama`

## 参考资料

- **[api-styles.md](references/api-styles.md)** — Ollama 三种 API 样式的详细对比与代码示例
