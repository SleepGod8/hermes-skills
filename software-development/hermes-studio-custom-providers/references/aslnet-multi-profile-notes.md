# ASLNet / 多 profile 现场笔记

## 适用场景

Hermes Studio 中：
- default profile 能看到自定义端点
- 其他 profile 看不到或选不到
- CLI 可用，但 Studio 模型菜单不出现

## 本次验证出的稳定事实

### 1. 子档案必须同时有两层配置

- `custom_providers`：CLI / 兼容层
- `providers`：Studio custom-endpoints / model picker 关键来源

只补 `custom_providers` 不够。

### 2. profile 作用域下必须分别验证

需要分别验证：

1. `load_config()` 能读到 `providers.aslnet-plus / aslnet-pro`
2. `_custom_endpoint_response(load_config())` 返回端点，且 `has_api_key=true`
3. `build_model_options_payload(load_picker_context(), explicit_only=True)` 返回 provider rows

本次在 `default / athena / hebe / hypnos / eos` 下都验证通过。

### 3. 即使后端已通过，Studio UI 仍可能看不到

这说明问题已从“磁盘配置”转移到：

- 会话网关缓存
- 模型目录缓存
- 前端未刷新当前 profile 的 model catalog

这时继续改 YAML 通常没有收益。

## 建议的排障顺序

1. 切到目标 profile
2. 新建会话
3. 模型菜单点 `Refresh Models`
4. 若无效，完全退出并重开 Hermes Studio
5. 若仍无效，再查该 profile 当前会话绑定的 model-options 来源

## 典型 provider 配置

```yaml
providers:
  aslnet-plus:
    name: ASLNet Plus (gpt-plus 0.1x)
    base_url: https://api.aslnet.cloud/v1
    model: gpt-5.5
    key_env: ASLNET_PLUS_KEY
    discover_models: true
    models:
      gpt-5.4: {}
      gpt-5.5: {}
      gpt-5.6: {}
      gpt-5.6-sol: {}
      gpt-5.6-terra: {}

  aslnet-pro:
    name: ASLNet Pro (gpt-pro 0.18x)
    base_url: https://api.aslnet.cloud/v1
    model: gpt-5.6-sol
    key_env: ASLNET_API_KEY
    discover_models: true
    models:
      gpt-5.4: {}
      gpt-5.5: {}
      gpt-5.6: {}
      gpt-5.6-sol: {}
      gpt-5.6-terra: {}
```

## 易错点

- 只在 default 写 `providers`
- 只验证 settings/custom-endpoints，不验证 `/api/model/options`
- 看到 default 正常就以为多 profile 也正常
- 在后端已经返回 provider rows 后，仍然不断补 YAML，而不是转向刷新运行时
