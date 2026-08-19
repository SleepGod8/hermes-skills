# ASLNet provider 配置实录（2026-08-19，DSH v4.1.0 实测）

## ASLNet 基本信息
- 端点：`https://api.aslnet.cloud/v1`（标准 OpenAI 兼容，实测 200 OK）
- 池与 key（Hermes .env 与 Windows 用户环境变量已同步）：
  - `aslnet-plus` = gpt-plus 0.1x 池（≈0.98 元/M，最便宜）→ key env `ASLNET_PLUS_KEY`
  - `aslnet-pro` = gpt-pro 0.18x 池 → key env `ASLNET_API_KEY`
- 模型：`gpt-5.4` / `gpt-5.5` / `gpt-5.6` / `gpt-5.6-sol` / `gpt-5.6-terra`（两池同模型列表，价格档不同）
- 实测：`gpt-5.5` + 两把 key → chat/completions 200

## 写入 `~/.dsh/settings.yaml` 的配置（已验证 schema）
```yaml
llm-pi-ai:
  providers:
    aslnet-plus:
      displayName: ASLNet Plus (gpt-plus 0.1x)
      apiKeyEnv: ASLNET_PLUS_KEY
      api: openai-completions
      baseURL: https://api.aslnet.cloud/v1
      models:
        - {id: gpt-5.4, name: gpt-5.4, contextWindow: 128000, maxTokens: 16384, input: [text]}
        - {id: gpt-5.5, name: gpt-5.5, contextWindow: 128000, maxTokens: 16384, input: [text]}
        - {id: gpt-5.6, name: gpt-5.6, contextWindow: 128000, maxTokens: 16384, input: [text]}
        - {id: gpt-5.6-sol, name: gpt-5.6-sol, contextWindow: 128000, maxTokens: 16384, input: [text]}
        - {id: gpt-5.6-terra, name: gpt-5.6-terra, contextWindow: 128000, maxTokens: 16384, input: [text]}
```
contextWindow 128000 是保守值（gpt-5 系列未实测实际窗口）；maxTokens 16384。

## 配置步骤（可复现）
1. 备份：`cp ~/.dsh/settings.yaml ~/.dsh/settings.yaml.bak`
2. 用 Python yaml 读-合并-写回（保留 agent-presets/agent-default-model 等现有段），勿手写覆盖
3. key 从 `C:\Users\80704\AppData\Local\hermes\.env` 读 → `setx ASLNET_PLUS_KEY <key>`、`setx ASLNET_API_KEY <key>`（不回显完整值）
4. 重启 DSH：`taskkill /IM "Deepseek Harness EAC.exe" /T /F` → 桌面双击 exe
5. 验证：`logs\dsh-web.log` 出现 `[dsh-third-party-thinking] wrapped 1 third-party adapter(s)`；Web UI 模型选择器出现 ASLNet Plus 组

## 排障要点
- 模型选择器没出现新 provider：settings.yaml 被 schema 拒绝（zod 校验）→ 检查字段名/类型；或没重启（llm-pi-ai 启动时读）
- DSH 报 key 空：setx 后未重启 / 从旧终端启动（环境变量未刷新）
- 余额小部件失败：ASLNet 无 `/user/balance`，需 `DEEPSEEK_BALANCE_URL` 指向有效端点或忽略余额显示；聊天不受影响

## 相关源码位置（v4.1.0）
- `resources/app/node_modules/@deepseek-ai/dsh-llm-pi-ai/lib/index.js` — llm-pi-ai provider schema 与注册
- `resources/app/assets/plugins/dsh-openclaw-bridge/lib/index.js` — openclaw-bridge（IM 桥接第三方端点）
- `resources/app/assets/plugins/dsh-third-party-thinking/lib/index.js` — reasoning_effort 注入控制
