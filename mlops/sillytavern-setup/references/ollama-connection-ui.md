# SillyTavern 1.18 Ollama 连接 — UI 元素与排查实录

实测于 2026-08，SillyTavern 1.18.0 release (8172dcd)，中文界面。

## 关键元素 ID / 选择器

| 元素 | 说明 |
|------|------|
| `#main_api` | 顶层 API 类型。选项只有 5 个：`文本补全=textgenerationwebui`、`聊天补全=openai`、`NovelAI=novel`、`AI Horde=koboldhorde`、`KoboldAI=kobold`。**没有独立的 Ollama 项** |
| `#textgen_type` | 「文本补全」下的 API 类型子下拉。含 `Ollama=ollama`（还有 oobabooga、llama.cpp、KoboldCpp、vLLM 等） |
| `#ollama_api_url_text` | Ollama 服务器 URL 输入框（切到 Ollama 后才出现），填 `http://127.0.0.1:11434` |
| `#ollama_model` | 模型下拉。未连接时显示 `-- 连接到 API --`，连接成功后自动加载 `ollama list` 的全部模型 |
| `.api_button` | 「连接」按钮。**页面 DOM 中有 4 个，只有 1 个可见**（`offsetParent !== null`，index 2）。用 querySelectorAll 点第一个会点到隐藏按钮，连接无效 |
| `.online_status_text` | 连接状态文本（`无连接...` / 模型名） |
| `#api_url_text` | 非 Ollama 的通用 URL 输入框（oobabooga 默认 `http://127.0.0.1:5000/api`）——别填错这个 |

## 常见坑

1. **在「聊天补全」里找 Ollama → 找不到**。Ollama 走「文本补全」通道（`textgen_type`），不是 chat completion source（那个列表 25 项：OpenAI/Claude/DeepSeek/自定义… 没有 Ollama）。
2. **URL 填到 `#api_url_text` 而不是 `#ollama_api_url_text`** → 连接仍指向 5000，失败。
3. **点错「连接」按钮**（4 个里只有 1 个可见）→ 无反应。排查：`[...document.querySelectorAll('.api_button')].map(b => b.offsetParent !== null)` 找可见项再 click。
4. 设置值后要 dispatch `change` + `input` 事件让 ST 记录（browser_console 操作时）。
5. 改 `config.yaml` 端口后必须重启 ST 进程（残留进程会继续占旧端口，导致新实例报 already in use）。

## 成功判定

- `#ollama_model` 出现本地模型列表（darkidol / josiefied / bge-m3…）
- `.online_status_text` 从 `无连接...` 变为模型名
- 左侧聊天框可正常对话
