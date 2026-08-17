---
name: hermes-studio-custom-providers
description: Use when Hermes Studio 自定义端点多 profile 显示不一致。
---

# Hermes Studio 自定义供应商 / 端点同步

用于处理 Hermes Studio 中 OpenAI-compatible 自定义端点（如 ASLNet、ASLNetPlus、本地代理、第三方中转）在模型切换器、设置页、多 profile 间显示不一致的问题。

## 触发条件

- 用户说某个模型/供应商在 CLI 能用，但在 Hermes Studio 里看不到
- 用户说 default 档案能看到，自定义子档案看不到
- 用户要把同一个自定义模型池同步到多个 profile
- 用户要让 Studio 模型菜单里出现第三方 OpenAI-compatible 端点

## 核心结论

Hermes 有两套相关配置，不能混用概念：

1. `custom_providers`
   - 主要给 CLI / 兼容层使用
   - 旧格式，常见为 JSON 字符串或 YAML list
   - 仅写这里，不足以保证 Hermes Studio 模型选择器出现该端点

2. `providers`
   - Hermes Studio 自定义端点设置与模型选择器读取的关键配置
   - `GET /api/providers/custom-endpoints` 读取这里
   - Studio 的 `Custom Endpoints` 设置页也是围绕这段配置工作

结论：
**要让 Hermes Studio 稳定看到自定义端点，必须写 `providers`；只写 `custom_providers` 不够。**

## 标准做法

### 1. 先改 default profile 验证格式

主配置：
- `C:/Users/<user>/AppData/Local/hermes/config.yaml`
- `C:/Users/<user>/AppData/Local/hermes/.env`

把密钥放 `.env`，不要明文写进 `config.yaml`。

`providers` 示例：

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
```

可同时保留 `custom_providers` 兼容 CLI。

### 2. 多 profile 同步时，两层都补

对每个子档案 `profiles/<name>/config.yaml`：

- 补 `custom_providers`（CLI 兼容）
- 补 `providers`（Studio 读取）
- 不要顺手改该 profile 的 `model.default/provider/base_url`，除非用户明确要求

### 3. 用 profile 作用域验证，而不是只看 default

验证分三层：

1. `load_config()` 在该 profile 下能读到 `providers.aslnet-plus`
2. `_custom_endpoint_response(load_config())` 在该 profile 下返回该端点，且 `has_api_key=true`
3. `build_model_options_payload(load_picker_context(), explicit_only=True)` 在该 profile 下返回该 provider row

只验证 default 没意义；问题常常出在 profile 作用域。

### 4. 看到后端正常，不等于 Studio 立刻可选

如果以上三层都正常，而 Studio UI 仍看不到，优先判断为：

- Studio 前端/会话网关缓存未刷新
- 当前 profile 的会话仍在吃旧的 model catalog

这时不要继续改 YAML；先做运行时刷新。

## 运行时刷新顺序

按成本从低到高：

1. 切到目标 profile
2. 新开会话
3. 在模型菜单点 `Refresh Models`
4. 若仍无效，完全重启 Hermes Studio
5. 若仍无效，再检查该 profile 的活动会话/网关是否绑了旧 catalog

## 源码定位

排查时重点看这些路径：

- `hermes_cli/web_server.py`
  - `/api/providers/custom-endpoints`
  - `/api/model/options`
- `hermes_cli/inventory.py`
  - `load_picker_context()`
  - `build_model_options_payload()`
- `apps/desktop/src/hermes.ts`
  - `getCustomEndpoints()`
  - `getGlobalModelOptions()`
- `apps/desktop/src/lib/model-options.ts`
  - `requestModelOptions()`

## 关键坑

### 坑 1：以为 Studio 只看 `custom_providers`

错误。Studio 自定义端点展示核心看 `providers`。

### 坑 2：只改 default，不改子档案

每个 profile 都有自己的 `config.yaml` 和 `.env` 可见范围。default 能看到，不代表 `athena/hebe/hypnos/...` 能看到。

### 坑 3：后端已经正常，却继续盲改配置

如果 profile 作用域下：
- `/api/providers/custom-endpoints` 正常
- `/api/model/options` 正常

那问题大概率已经不在配置，而在 Studio 缓存/会话刷新。

### 坑 4：把“设置页能看到端点”和“模型菜单能直接可选”混为一谈

Studio 有两条链路：
- Custom Endpoints 设置页
- Model Picker / 会话模型菜单

后者实际吃的是 `/api/model/options` 聚合结果，不是简单复用设置页列表。

## 推荐交付方式

给用户回报时分开说：

1. 配置是否已写入
2. 后端 profile 作用域是否验证通过
3. 现在剩下的是配置问题还是缓存问题
4. 下一步该做的是刷新还是继续改文件

## 参考

本技能可搭配会话细节参考：
- `references/aslnet-multi-profile-notes.md`
