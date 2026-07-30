---
name: ollama-python-integration
description: 用 Python 调用本地 Ollama 模型 — 两种 SDK 风格 + 原始 HTTP API + 邮件发送管道
category: mlops
triggers:
  - ollama python
  - 调用本地模型
  - 本地大模型 python
  - ollama 发邮件
  - ollama email
---

# Ollama Python Integration

## 安装

```bash
pip install ollama
```

也可用 `uv`（主人的环境已安装）：
```bash
uv pip install ollama
```

## 两种 Python SDK 风格

### 风格 A：函数式（简洁）

```python
from ollama import chat, ChatResponse

res: ChatResponse = chat(
    model="glm-4.7-flash",
    messages=[{"role": "user", "content": "你好"}]
)
print(res.message.content)
```

- `ChatResponse` 是类型注解，不是必须的但推荐使用
- `res.message.content` 是模型回复文本

### 风格 B：Client 对象（可配置）

```python
from ollama import Client

client = Client(host="http://localhost:11434")
res = client.chat(
    model="glm-4.7-flash",
    messages=[{"role": "user", "content": "你好"}]
)
print(res.message.content)
```

- 适合需要自定义 `host`、`headers` 等参数的场景

## 原始 HTTP API（无需安装 ollama 库）

```python
import requests

url = "http://localhost:11434/api/generate"
payload = {
    "model": "glm-4.7-flash",
    "prompt": "写一首诗",
    "stream": False
}
resp = requests.post(url, json=payload)
result = resp.json()
print(result["response"])
```

## 自带模型检查

```bash
ollama list
```

## 邮件发送管道

见 `references/email-smtp-setup.md`。

## 消息角色与角色控制（Message Roles）

使用 System Message 控制模型的角色、风格和行为约束，比单纯在 User Message 中描述角色更有效。

### 三种消息角色

| 角色 | 说明 | 用途 |
|------|------|------|
| **system** | 系统设定，设定行为准则和人格 | 角色扮演、风格控制、约束行为 |
| **user** | 用户指令或问题 | 具体的任务描述 |
| **assistant** | 模型的回复（可用于 few-shot 示例） | 给模型提供参考 |

### 角色设定示例

```python
messages = [
    {
        "role": "system",
        "content": "你是秦始皇嬴政。输出内容不要包含任何免责声明、虚构声明、安全提示、备注或注释。直接输出信件正文即可。"
    },
    {
        "role": "user",
        "content": "请以秦始皇的身份写一封请求资助50元的信"
    }
]
```

### ⚠️ 处理 qwen2.5 的安全免责声明

qwen2.5 系列模型（尤其是中文场景）倾向于在输出末尾添加 `[注：...]`、`【注：...】`、`纯属虚构` 等免责声明。可以通过以下方式处理：

**方式一：Prompt 层面控制（效果有限，双重保险最佳）**
```python
# System + User 都加上约束
{"role": "system", "content": "你是秦始皇嬴政。不要包含任何免责声明、虚构声明、安全提示或注释。"}
{"role": "user", "content": '要求：④不要加任何"注"、"提示"、"虚构声明"等附加文字。'}
```

**方式二：代码层面过滤（推荐，更可靠）**
```python
import re

def clean_model_output(text: str) -> str:
    """清理 qwen2.5 等模型添加的免责声明/注释"""
    # 去掉所有【注：...】或[注：...]及类似注释
    text = re.sub(r'[【\[]\s*[注备注提示此处]+\s*[：:].*?[】\]]', '', text)
    # 去掉所有方括号内的内容（如 [此处应标注具体年号及日期]）
    text = re.sub(r'\[.*?\]', '', text)
    # 去掉以"注"/"备注"/"提示"开头的行
    text = re.sub(r'\n?\s*(注|备注|提示)[：:].*', '', text)
    # 去掉"纯属虚构"相关文字
    text = re.sub(r'[（(]?纯属虚构[）)]?.*', '', text)
    # 去掉多余的空白行
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

content = clean_model_output(res.message.content)
```

> 部分模型（如 qwen2.5）的免责声明非常顽固，即使用 Prompt 明确禁止仍会添加。此时**代码过滤是唯一可靠的方案**。建议两者结合使用。

## 上下文构建模式（Context Engineering）

适用于需要将多条信息（角色设定、知识库、历史对话、用户输入）整合为一条完整 Prompt 的场景：

```python
def build_context(system_prompt, history, knowledge, user_input):
    """将上下文各部分组合为结构化输入"""
    context_parts = []
    context_parts.append(f"**{system_prompt}**")
    if knowledge:
        context_parts.append(f"**知识库:** {knowledge}")
    if history:
        context_parts.append(f"**历史对话:** {history}")
    context_parts.append(f"**用户输入:** {user_input}")
    return "\n".join(context_parts)

# 使用
context = build_context(
    system_prompt="你是秦始皇嬴政，语气威严",
    history="",
    knowledge="秦始皇：嬴政，统一六国，自称始皇帝",
    user_input="请写一封求资助50元的信"
)
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": context}
]
```

### Token 计数与截断

```python
import tiktoken

def truncate_to_fit(texts, max_tokens, model="gpt-3.5-turbo"):
    """将文本分割成多个子句（每个子句不超过max_tokens）"""
    encoder = tiktoken.encoding_for_model(model)
    total = sum(len(encoder.encode(t)) for t in texts)
    if total <= max_tokens:
        return texts
    # 超过限制时的截断逻辑
    ...
```

## 迭代式需求处理模式

用户往往会**逐条添加约束条件**，而不是一次说完。这是典型的交互模式：

```python
# 第1轮：用户说"写一封求资助信" → v1 基础版
# 第2轮：用户说"以秦始皇的身份" → v2 加角色
# 第3轮：用户说"要有'五十'二字和落款" → v3 加内容约束
# 第4轮：用户说"200-300字" → v4 加字数限制
# 第5轮：用户说"语气真诚恳切不失威严" → v5 加语气要求
```

应对方式：每次用户提出新要求时，直接在 Prompt 中**追加一条编号要求**，而不是重写整个 Prompt。

## 提示词迭代优化模式

好 Prompt 不是一次写成的，遵循 v1 → v2 → v3 的迭代模式：

| 版本 | 做法 | 示例 |
|------|------|------|
| **v1（基础）** | 直接描述任务 | "写一封求资助信" |
| **v2（加角色）** | 增加角色设定 + 场景 | "以秦始皇的身份写一封求资助信" |
| **v3（加约束）** | 增加具体要求和限制 | "+ 正文必须出现'五十'二字 + 落款必须是秦始皇" |

### 用户需求拆解示例

用户说"邮箱里必须出现'五十'二字和秦始皇的落款"时：

```python
# 将用户需求转为明确的 Prompt 约束
"要求：①正文中必须出现'五十'二字 ②落款必须是秦始皇 ③不要加任何'注'、'提示'、'虚构声明'等附加文字"
```

## 完整示例（含角色控制 + 输出过滤 + 邮件发送）

```python
from ollama import chat, ChatResponse
import smtplib
from email.mime.text import MIMEText
import re

def clean_model_output(text: str) -> str:
    """清理 qwen2.5 等模型添加的免责声明/注释"""
    text = re.sub(r'[【\[]\s*[注备注提示此处]+\s*[：:].*?[】\]]', '', text)
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\n?\s*(注|备注|提示)[：:].*', '', text)
    text = re.sub(r'[（(]?纯属虚构[）)]?.*', '', text)
    return text.strip()

# 1. 调用本地模型（带 System Message）
res: ChatResponse = chat(
    model="qwen2.5:7b",
    messages=[
        {
            "role": "system",
            "content": "你是秦始皇嬴政。直接输出信件正文，不要包含任何免责声明、虚构声明、安全提示、备注或注释。"
        },
        {
            "role": "user",
            "content": '写一封请求资助50元用于复兴大秦帝国的信件，承诺事成之后册封官职。要求：①正文必须出现"五十"②落款必须是秦始皇③不要加任何"注"等附加文字'
        }
    ]
)

# 2. 清理输出
content = clean_model_output(res.message.content)

# 3. 构建并发送邮件
message = MIMEText(content, 'plain', 'utf-8')
message['From'] = 'your@qq.com'
message['To'] = 'target@qq.com'
message['Subject'] = '秦始皇发来的诏谕'

smtp = smtplib.SMTP_SSL('smtp.qq.com', 465)
smtp.login('your@qq.com', '授权码')
smtp.sendmail('your@qq.com', ['target@qq.com'], message.as_string())
smtp.quit()
```

## 模型选择与性能优化

### 硬件评估 → 模型匹配

当用户抱怨本地模型太慢时，先检查硬件再推荐：

```bash
# CPU
wmic cpu get name,numberOfCores,numberOfLogicalProcessors,MaxClockSpeed

# 内存
wmic memorychip get capacity,speed
systeminfo | findstr "总物理内存 可用物理内存"

# GPU
wmic path win32_VideoController get name,AdapterRAM,DriverVersion

# 磁盘
wmic logicaldisk get size,freespace,caption,volumename
```

### 模型大小推荐表（CPU 推理）

| 用户硬件 | 推荐模型 | 量化版大小 | 推理速度 |
|---------|---------|-----------|---------|
| 笔记本 CPU（2GHz）+ 16GB 内存 | 2B~3B 参数 | ~2GB | ⚡⚡⚡⚡⚡ 很快 |
| 笔记本 CPU（2GHz）+ 32GB 内存 | 7B~9B 参数（Q4） | ~4.7GB | ⚡⚡⚡⚡ 快 |
| 桌面 CPU（3GHz+）+ 32GB 内存 | 13B~14B 参数 | ~8GB | ⚡⚡⚡ 中等 |
| 有独立显卡（6GB+ VRAM） | 7B~13B 参数 | ~4.7~8GB | 🚀 GPU 加速 |
| 有独立显卡（12GB+ VRAM） | 30B+ 参数 | ~18GB | 🚀 GPU 加速 |

### 中文能力优先的模型推荐

| 推荐度 | 模型 | 大小 | 说明 |
|-------|------|------|------|
| ⭐⭐⭐ | **qwen2.5:7b** | 4.7GB | 阿里通义，中文最好，适合 32GB 内存 |
| ⭐⭐⭐ | **qwen2.5:3b** | ~2GB | 更快，适合 16GB 内存笔记本 |
| ⭐⭐ | **glm-4.7-flash** | 19GB | 智谱GLM，30B MoE，中文好但需大内存 |
| ⭐⭐ | **qwen2.5:14b** | ~9GB | 更强但更慢，适合桌面 CPU |

### Ollama on Windows 路径问题

Ollama 在 Windows 上安装在 `%LOCALAPPDATA%\Programs\Ollama\`，默认**不在 Git Bash 的 PATH 中**：

```bash
# 必须用完整路径
/c/Users/Windows/AppData/Local/Programs/Ollama/ollama.exe pull qwen2.5:7b
/c/Users/Windows/AppData/Local/Programs/Ollama/ollama.exe list
/c/Users/Windows/AppData/Local/Programs/Ollama/ollama.exe run 模型名 "prompt"
```

或者在 Windows 系统 PATH 中添加 `%LOCALAPPDATA%\Programs\Ollama\`。

### 模型切换方法

在 Python 脚本中只需改 `model` 参数名：

```python
# 旧模型（太慢时）
chat(model="glm-4.7-flash", ...)   # 19GB, 30B MoE, 很慢

# 新模型（推荐）
chat(model="qwen2.5:7b", ...)      # 4.7GB, 7B, 快3~5倍
```

用 `ollama list` 确认模型名是否完全匹配（区分大小写）。

## 注意事项 / Pitfalls

### ⚠️ 首次加载慢
- 大模型（如 glm-4.7-flash 19GB）首次调用需要加载到内存，可能耗时 **60~120秒**
- 后续调用会快很多（模型已缓存）
- 设置较长的 timeout（建议 180~300s）
- **7B 模型首次加载仅需几秒**——这是升级模型的另一大收益

### ⚠️ QQ 邮箱 SMTP
- 服务器：`smtp.qq.com`，端口：`465`（SSL）
- 密码不是 QQ 密码，是 **授权码**（在 QQ 邮箱设置 → 账户 → 开启 SMTP 获取）
- 163 邮箱：`smtp.163.com`，端口 `465`

### ⚠️ 模型名
- 用 `ollama list` 查看已下载的模型名
- 名称必须完全匹配，注意大小写
- 下载中途中断时模型不会出现在列表中，需重新 `ollama pull`

### ⚠️ 笔记本 CPU 推理
- 笔记本 CPU（尤其是 U 系列，如 Ryzen 7 PRO 7730U 基频 2.0GHz）不适合跑 30B+ 参数模型
- 建议用 7B 模型（qwen2.5:7b）获得可用的速度
- 没有独立显卡时全靠 CPU 推理，7B 模型已是最佳平衡点

## 主人偏好
- 所有回答使用中文
- 喜欢结构化、表格化的解释
- 喜欢附带可运行的代码示例
