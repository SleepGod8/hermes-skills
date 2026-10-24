# 云端模型版本核对 & DeepSeek ID 台账（2026-10-24 实测）

## 何时看这份

主人问「XX 出了新版，你能更新吗 / 现在用的是哪个模型」时。**先核对，再改配置**——云端厂商普遍保留旧 ID 当别名，「出新版」不等于「还在用旧版」，直接改配置常常是白折腾甚至踩 400。

## 三步核对法（每步都要真跑）

1. **看官方 ID**
   ```bash
   KEY=$(grep -m1 "^DEEPSEEK_API_KEY=" "$HOME/AppData/Local/hermes/.env" | cut -d= -f2- | tr -d '\r"')
   curl -s https://api.deepseek.com/models -H "Authorization: Bearer $KEY"
   ```
   以 API 返回的 `id` / `name` / `context_window` / `input_modalities` 为准，别信搜到的博客或版本号直觉。
2. **看真实路由**：发一条最小 `chat/completions`，读响应体 `"model"` 字段。传旧 ID 却回新 ID ⇒ 旧 ID 已是别名，**配置无需改动**，直接告诉主人「已经在用了」。
3. **跑 Hermes 多轮**：
   ```bash
   hermes chat -q "Use the terminal tool to run: date +%Y. Then tell me the year." -m <id> --provider deepseek -Q
   ```
   单轮 curl 通过 ≠ Hermes 通过；带工具的第二轮才会暴露 thinking / `reasoning_content` 回传类 400。

## DeepSeek 当前 ID（2026-10-24 `/models` 实测）

| ID | 显示名 | 规格 |
|----|--------|------|
| `deepseek-flash` | **DeepSeek-V4.1-Flash** | 1,048,576 ctx / 393,216 max output / 输入 text+image / effort low·high·max（默认 high）/ anthropic_messages 兼容 |
| `deepseek-v4-pro` | DeepSeek-V4-Pro | 1,048,576 ctx / 393,216 max output / 仅 text |

## ID 兼容性坑

- **`deepseek-v4.1-flash` 不存在，硬写必 400**：
  `The supported API model names are deepseek-flash, deepseek-v4-pro, but you passed deepseek-v4.1-flash.`
- **`deepseek-v4-flash` 仍可用**：服务端接受，响应 `"model"` 回 `deepseek-flash` ⇒ 旧名已路由到 V4.1-Flash。
- Hermes 0.20.4 `hermes_cli/model_normalize.py::_normalize_for_deepseek` 只认 `^deepseek-v\d+([-.].+)?$`：
  - `deepseek-flash` → 折叠成 `deepseek-v4-flash`（终端打印 `Normalized model ...`）
  - `deepseek-v4.1-flash` → **原样放行** → 直送 API → 400（最容易踩的一脚：版本号看起来更"精确"，反而炸）
- 结论：**别把 `deepseek-v4.1-flash` 写进 config.yaml**；写 `deepseek-flash` 也会显示旧名。想要界面显示新 ID，等 `hermes update` 支持后再改。
- `agent/model_metadata.py` 已登记 `deepseek-v4-flash: 1_000_000`，不需要再手动加 `context_length`。

## 视觉能力提醒

V4.1-Flash `input_modalities` 含 `image`，理论上可把 `auxiliary.vision` 从 GLM/qwen 切到 deepseek 省额度；**未实测**，切之前先 base64 图跑通再改。

## 操作纪律

- 改配置前：`cp config.yaml config.yaml.bak-<tag>-$(date +%Y%m%d_%H%M%S)`
- 改完如实告知：当前会话模型在启动时固定，新值只对新会话生效
- 若核对结果就是「已是最新」——**不要为了显得干了活而硬改配置**
