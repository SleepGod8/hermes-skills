# Kimi (Moonshot AI) API Pricing

> Source: https://platform.kimi.com — scraped 2026-07-27
> Platform: platform.kimi.com (separate from kimi.moonshot.cn desktop/Web product)

## Model Pricing

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Cache Hit |
|-------|----------------------|------------------------|-----------|
| K3 (kimi-k3) | ¥20.00 | ¥100.00 | ¥2.00 |
| K2.7 Code | ¥6.50 | ¥27.00 | ¥1.30 |
| K2.6 | ¥6.50 | ¥27.00 | ¥1.10 |

## Billing Model

- **Pay-as-you-go** (按量付费): Prepaid balance, deducted per API call
- **No free tier** for API (unlike Zhipu GLM which has free models)
- **Cache**: Context caching reduces input cost ~10x on cache hit
- **Token definition**: ~1 token = 1.5-2 Chinese characters (typical)

## Model Capabilities

| Feature | K3 | K2.7 Code | K2.6 |
|---------|:--:|:---------:|:---:|
| Context Window | 1M tokens | 256K tokens | 256K tokens |
| Vision | ✅ | ❌ | ✅ |
| Thinking Mode | ✅ | ✅ | ✅ |
| Function Calling | ✅ | ✅ | ✅ |
| Coding Focus | General | Specialized | General |

## Key Facts

- **Membership ≠ API**: Desktop membership does NOT include API credits
- **OpenAI-compatible**: Standard `/v1/chat/completions` endpoint
- **Registration**: Phone number, Chinese phone required
- **API Key**: Generated in platform.kimi.com user center, NOT the desktop app
- **LiveBench Coding 2026-06-25**: K3 scores 81.4 (#1 open-source), K2.7 Code scores 74.0
