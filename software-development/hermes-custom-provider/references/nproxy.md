# nproxy.club — OpenAI 兼容中转站（已验证 2026-08）

备用供应商，模型 ID 为 `vendor/model` 格式。端点 `https://api.nproxy.club/v1`。

## 关键特性

- **免费模型**：`moonshotai/kimi-k3-free`（实测映射到 kimi-k3，可正常对话）
- **模型覆盖**：openai/gpt-5.x、anthropic/claude-opus-4.8、google/gemini-3.5-flash-lite、deepseek/deepseek-v4-*、moonshotai/kimi-k3*、z-ai/glm-5、qwen3.x、图像/视频（seedream-5.0、kling-v3、MiniMax-Hailuo）

## 实测坑（2026-08 踩过）

1. **urllib/原生 Python HTTP 客户端 → HTTP 403 Forbidden**
   `urllib.request` 直接 POST 被 403 拦截（疑似 UA/TLS 指纹检测）。✅ 用 curl 正常；或 requests 带浏览器 UA 测试。

2. **free 模型响应很慢**：`kimi-k3-free` 实测约 82s 才返回（vllm 推理队列）。
   测试/调用要设 `-m 180` 超时，60s 默认会超时。

3. **bash 里直接传中文会乱码**（git-bash 编码问题，模型看到乱码文本）。
   ✅ 把 JSON body 写入临时文件，用 `curl --data-binary @file.json` 传参。

## 命令行测试

```bash
# 1. 模型列表（快速验证 key 有效）
curl -sS -m 30 "https://api.nproxy.club/v1/models" \
  -H "Authorization: Bearer sk-..."

# 2. 对话测试（JSON 文件避免中文乱码）
cat > /tmp/kimi_test.json << 'EOF'
{"model":"moonshotai/kimi-k3-free","messages":[{"role":"user","content":"你好"}],"max_tokens":50}
EOF
curl -sS -m 180 "https://api.nproxy.club/v1/chat/completions" \
  -H "Authorization: Bearer sk-..." -H "Content-Type: application/json" \
  --data-binary @/tmp/kimi_test.json
```

## Hermes 集成（已实测 CLI 可用作主对话模型）

在 config.yaml 的 `custom_providers` 列表追加（必须用 Python+PyYAML 直接编辑，勿用 `hermes config set` 否则覆盖整个列表或存成字符串字面量）：

```yaml
- name: nproxy
  base_url: https://api.nproxy.club/v1
  api_key: sk-...
  models:
    - moonshotai/kimi-k3-free
    - deepseek/deepseek-v4-flash
```

CLI 实测命令（成功）：
```bash
hermes -z "回复：ok" -m "moonshotai/kimi-k3-free" --provider "custom:nproxy" --cli chat
```
注意：`-z` 是全局参数，必须放在子命令 `chat` 之前；交互式 TUI 可用 `--cli` 关闭。

⚠️ 与通用坑"custom provider 作主模型可能认证失败"不同：**nproxy 已实测 CLI 主模型可用**。但 free 模型慢（~80s），适合备用场景而非日常主模型。改回默认：`hermes config set model.provider deepseek && hermes config set model.default deepseek-chat`。
