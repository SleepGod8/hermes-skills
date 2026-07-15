# AI API 中转站 (Chinese API Proxy Services)

Centralized proxy services that provide a single API key with access to multiple AI providers (GPT, Claude, Gemini, etc.) via OpenAI-compatible endpoints. Useful in mainland China for direct access without VPN.

## Surveyed Services (2026-07)

### API2D (api2d.com)

- **Status**: ✅ Active
- **Pricing**: ~1.5× OpenAI official prices
- **Models**: GPT, Claude, StableDiffusion, Tencent Cloud
- **Format**: OpenAI-compatible, "fill Key and go"
- **Best for**: Stable production use, mature platform
- **Signup**: Register, top up, copy key

### ChatAnywhere (api.chatanywhere.tech)

- **Status**: ✅ Active
- **Pricing**: CA-coin based, ~90% of official with recharge bonus
- **Model coverage (most comprehensive)**:
  - GPT-5.6-sol/terra/luna (latest OpenAI)
  - Claude Sonnet 5, Opus 4-8
  - DeepSeek v4-pro/flash, v3.2, R1
  - Qwen 3.5-plus/max, Qwen3 Coder
  - Kimi K2.5/2.6/2.7
  - GLM-5.2/5.1
  - Gemini (listed in docs)
- **Best for**: One key for all models, widest selection
- **Pitfall**: No free tier; models from third-party suppliers may occasionally error

### AIHubMix (aihubmix.com)

- **Status**: ❌ Connection timeout (may be offline/shut down)

## Hermes Integration

To use a proxy service in Hermes, add it as a custom provider:

```yaml
custom_providers:
  - name: ChatAnywhere
    base_url: https://api.chatanywhere.tech/v1
    api_key: <your-key>
```

Then reference as `custom:ChatAnywhere` for chat or auxiliary tasks.

## Recommendation

For users who already have DeepSeek + GLM free models, a proxy service is only needed when wanting GPT-5.6 or Claude. ChatAnywhere is the best option for that use case.
