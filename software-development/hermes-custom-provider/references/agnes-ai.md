# Agnes AI (api.agnes-ai.cn) 实测记录

> 2026-08 实测。旧域名 `apihub.agnes-ai.com` 已失效（curl 返回空/无响应），
> 国内版改用 `.cn` 域名：`https://api.agnes-ai.cn/v1`。

## 端点信息

| 项 | 值 |
|---|---|
| Base URL | `https://api.agnes-ai.cn/v1` |
| Provider (Hermes) | `custom:agnes` |
| 认证 | `Authorization: Bearer <AGNES_API_KEY>`（OpenAI 兼容） |
| .env 变量 | `AGNES_API_KEY` |

## 可用模型（GET /v1/models 实测返回）

| 模型 ID | 类型 | supported_endpoint_types |
|---|---|---|
| `agnes-2.0-flash` | 对话（带 reasoning） | - |
| `agnes-2.5-flash` | 对话 | openai |
| `agnes-2.5-pro` | 对话（更强） | - |
| `agnes-2.5-pro-alpha` | 对话（alpha） | openai |
| `agnes-image-2.1-flash` | 文生图 | openai |
| `agnes-video-v2.0` | 视频生成 | openai |

## 响应结构要点

- 对话响应带 `choices[0].message.reasoning_content`（思考过程）+ `content`（正文）
- `usage.completion_tokens_details.reasoning_tokens` 单独统计思考 token
- 有 `provider_specific_fields.matched_stop` 字段

## 验证命令

```bash
# 列模型
curl -s https://api.agnes-ai.cn/v1/models -H "Authorization: Bearer $AGNES_API_KEY"

# 测对话（注意 thinking 模型 max_tokens 要够大，否则 finish_reason=length 看着像坏了）
curl -s https://api.agnes-ai.cn/v1/chat/completions \
  -H "Authorization: Bearer $AGNES_API_KEY" -H "Content-Type: application/json" \
  -d '{"model":"agnes-2.0-flash","messages":[{"role":"user","content":"hi"}],"max_tokens":200}'
```

## 配置进 Hermes

```bash
hermes config set model.provider "custom:agnes"
hermes config set model.base_url "https://api.agnes-ai.cn/v1"
hermes config set model.default "agnes-2.5-pro"
# 或只加入 custom_providers 池（保留当前模型）：
#   config.yaml 的 custom_providers 下加 {name: agnes, base_url: ..., api_key: ...}
```
