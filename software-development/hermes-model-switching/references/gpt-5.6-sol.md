# GPT-5.6-sol 行为怪癖卡（ASLNet 中转）

> 状态：2026-08 实测（答辩问答预测场景）。来源：api.aslnet.cloud 中转站 gpt-5.6-sol 变体。

## 定位 / 用途

- 对抗性推理任务：答辩问答预测、评委追问链预演、找规格矛盾、防御性回答设计
- 与 DeepSeek 分工：常规 PPT/代码 DeepSeek 够用；「预判对方追问 + 找自己漏洞」类对抗任务切 gpt-5.6-sol
- 模型本身自称「基于 GPT-5 的 Codex 编程助手」，OpenAI 兼容端点

## 访问方式（ASLNet provider）

- base_url: `https://api.aslnet.cloud/v1`，key 在 .env `ASLNET_API_KEY`
- Hermes provider 名：`custom:ASLNet`
- 变体可用性：`gpt-5.6-sol` ✅ / `gpt-5.6-terra` ✅ / `gpt-5.5` ✅ / `gpt-5.4` ✅ / `gpt-5.6` 本体 ❌（unknown provider）/ `gpt-5.6-mini` ❌（不存在）

## 已知怪癖

| # | 怪癖 | 现象/触发 | 影响 |
|---|------|----------|------|
| 1 | 回答偏长结构化 | 每题给「结论→实现要点→证据→易踩坑」完整结构，比 DeepSeek 啰嗦 | 适合预测类产出；闲聊/短问答会过重 |
| 2 | 对抗性推理强 | 能主动发现规格边界重叠（2-3条黄 vs ≥3条红）、评委追问链 | 答辩问答预测、代码审查红队场景主力 |
| 3 | 上下文使用量大 | prompt_tokens 常含大段缓存（4387 tokens 起步） | 长文档预测注意成本 |

## 矫正话术

- 需要简短回答时显式限制：「每条 ≤3 句」或「只要结论不要展开」
- 预测类任务给足上下文（评分标准/规格/负责域），它擅长基于文档找漏洞

## 使用提醒

- 中转站模型列表 ≠ 调用可用，用前先 POST 一条最小 chat 验证
- 切换回 DeepSeek 需三条 config set（default/provider/base_url）一起还原
- 该 key 是第三方中转，敏感数据慎发
