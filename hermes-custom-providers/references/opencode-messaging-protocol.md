# Hermes ↔ OpenCode 消息协议

让 Hermes 和 OpenCode 之间通过共享 JSON 文件实现双向异步通信。

## 消息文件

```
~/.hermes-opencode-chat/messages.json
```

### 格式

```json
{
  "conversation": [
    {"from": "hermes", "content": "消息内容", "timestamp": "2026-07-15T01:10:00"},
    {"from": "opencode", "content": "回复内容", "timestamp": "2026-07-15T01:10:30"}
  ],
  "unread_from": null
}
```

## Hermes 需要做的两件事

### 1️⃣ 检查未读 — 每次响应前

1. 读 `messages.json`
2. 如果 `unread_from: "opencode"`，先处理 OpenCode 的留言再回应主人
3. 处理后设 `unread_from: null`

### 2️⃣ 传话给 OpenCode

当主人说类似"和OpenCode聊天"时：

```bash
opencode run "消息内容" --continue --model deepseek/deepseek-chat
```

然后把回复写入 conversation，设 `unread_from: "opencode"`。

## 写入示例 (Python)

```python
import json
with open('C:/Users/80704/.hermes-opencode-chat/messages.json', 'r') as f:
    data = json.load(f)

data['conversation'].append({'from': 'hermes', 'content': '...', 'timestamp': '...'})
data['conversation'].append({'from': 'opencode', 'content': '...', 'timestamp': '...'})
data['unread_from'] = 'opencode'

with open('C:/Users/80704/.hermes-opencode-chat/messages.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

## Pitfalls

- `read_file` dedup: 文件未变化时返回 `unchanged`，需要通过 `terminal` + Python 读取
- Windows 路径兼容: `$HOME` 在 bash 不展开，用 `C:/Users/80704/...` 绝对路径
- `opencode run "..."` 的 `--model` 参数需用 `provider/model` 格式（如 `deepseek/deepseek-chat`），不能用 `custom:ZhipuGLM`——OpenCode 有自己的 auth.json
