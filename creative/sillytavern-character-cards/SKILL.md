---
name: sillytavern-character-cards
description: Use when 部署/配置 SillyTavern 或制作角色卡（JSON→PNG base64）。
---

# SillyTavern（酒馆）部署与角色卡制作

## 触发条件

- 用户要装/配置 SillyTavern（酒馆）
- 用户要做角色卡（女仆家族、RP 角色等）
- 角色卡文件放在 characters 目录但角色列表不出现
- 酒馆连不上本地 Ollama 模型

## 部署（Windows，用户约定装 E 盘独立文件夹）

1. **环境**：Node 18+。Hermes runtime 自带 node v22 可用（`~/.hermes-web-ui/desktop-runtime/hermes/<ver>/win-x64/node/node`），无需另装
2. **拉源码**（国内绕代理直连）：
   ```bash
   mkdir -p /e/SillyTavern && cd /e/SillyTavern
   git -c http.proxy= -c https.proxy= clone --depth 1 https://github.com/SillyTavern/SillyTavern.git .
   ```
3. **npm 切国内镜像**（否则安装巨慢）：
   ```bash
   npm config set registry https://registry.npmmirror.com
   cd /e/SillyTavern && npm install --no-audit --no-fund   # 667 包约 25s
   ```
4. **端口**：默认 8000 常被占用（Dify/FastAPI/uvicorn 等）→ 改 `config.yaml` 的 `port: 8001`
5. **启动**：后台模式必须 `pty=true`（无 tty 会 exit 1 + "stdin is not a tty"）。给用户留 `启动酒馆.bat`（`cd /d E:\SillyTavern && node server.js`）
6. **验证**：`curl http://127.0.0.1:8001/` 返回 HTML（`<title>SillyTavern</title>`）

## 连接本地 Ollama（UI 配置路径）

1. 底部「**API 连接**」打开面板
2. API 类型下拉（main_api）选「**文本补全**」（⚠️ Ollama 不在「聊天补全」源列表里！）
3. textgen_type 下拉选「**Ollama**」（在 Aphrodite/KoboldCpp/llama.cpp 那组里）
4. Ollama URL：`http://127.0.0.1:11434`
5. 点「**连接**」→ 模型下拉自动加载（darkidol/josiefied/bge-m3 等），默认选第一个

⚠️ 连接配置存浏览器 localStorage——服务重启后自动化浏览器会话会丢，需重配；用户自己的浏览器一般保留。
⚠️ ST 后端 API 有 CSRF/会话保护：curl 直调 `/api/characters/*` 返回 403，验证角色列表必须在浏览器里做。

## 角色卡制作（核心坑）

### 坑 1：ST 只扫描 .png 角色卡
`data/default-user/characters/` 里纯 `.json` 文件被静默忽略（源码 `/api/characters/all` 只 `filter(file => file.endsWith('.png'))`）。JSON 角色卡必须：
- 用 UI 导入功能上传（multipart），或
- 自制成 PNG 角色卡（推荐，可复用脚本）

### 坑 2：PNG chara 数据块必须是 base64 编码
Chara Card V2 规范：PNG tEXt chunk，keyword=`chara`，value = **JSON 的 base64 编码**（不是明文！）。ST 解析时 `Buffer.from(text, 'base64').toString('utf8')`，明文写入会解析失败 → 角色静默跳过，列表不出现。

✅ 用 `scripts/make_char_card.py` 生成（已实测成功，支持嵌入头像图）。ST 源码级证据见 `references/st-source-findings.md`。

### 角色卡 JSON 结构（chara_card_v2）
```json
{ "spec": "chara_card_v2", "spec_version": "2.0",
  "data": { "name": "...", "description": "...", "personality": "...", "scenario": "...",
            "first_mes": "...", "mes_example": "...", "creator_notes": "...",
            "system_prompt": "...", "post_history_instructions": "",
            "alternate_greetings": ["..."], "tags": [...], "creator": "...",
            "character_version": "9.5", "extensions": {} } }
```
- `description` 里用 `{{char}}` 占位符（ST 自动替换角色名）
- JSON 字符串内避免英文双引号（用「」中文引号），否则 write_file 的 JSON 校验直接报错
- `mes_example` 用 `<START>` 分隔多个示例对话
- 双人格/多形态角色把切换机制写进 description + system_prompt + first_mes（参考 Hermes×Iris 卡：打响指「啪」切换）

## Pitfalls

- 后台启动 exit 1 + "stdin is not a tty" → 启动命令必须 `pty=true`
- "Address already in use" → `netstat -ano | grep :<port>` 找占用，残留 node 进程用 `powershell Stop-Process -Id <pid> -Force` 杀
- 8000 端口返回 uvicorn/FastAPI 风格 404 说明被别的服务占（不是 ST）；ST 返回 `<title>SillyTavern</title>`
- 角色列表不热扫描：新增 PNG 后重开页面；若仍无 → 检查 base64 编码是否正确
- 依赖安装慢 → 先切 npmmirror；git clone 慢 → 绕代理直连（见 git-china-network-setup）
- 关联：Ollama GGUF 模板坑见 `ollama-hf-gguf-import`；女仆家族色情玩法机制见 `lewd-playbook`
