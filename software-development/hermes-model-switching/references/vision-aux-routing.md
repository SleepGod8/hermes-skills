# auxiliary.vision 切换与验证（DeepSeek V4.1-Flash 实测，2026-10-24）

## 何时看这份

主人问「模型能看图吗 / 把视觉辅助换成 XX / 少烧点额度」时。核心结论：**能看图的模型很多，但「主模型 native」和「auxiliary.vision」是两条完全不同的通道，必须分开验证**，否则你测到的根本不是你以为的那条路。

## 一、先分清两条通道

`agent/image_routing.py::decide_image_input_mode(provider, model, cfg, requested_provider=...)` 返回 `native` 或 `text`：

- 主模型自身 supports_vision → **`native`**：图片 base64 直接进上下文，agent 亲眼看像素，`auxiliary.vision` 完全不参与。
- 主模型 text-only（如 `deepseek-v4-pro`）→ **`text`**：才走 `auxiliary.vision` 让辅助模型描述成文字。

实测结果（config `agent.image_input_mode: auto`，且有显式 `auxiliary.vision`）：

| 主模型 | 决策 | 现象 |
|--------|------|------|
| `deepseek-v4-flash`（V4.1-Flash，含 image 输入） | `native` | `vision_analyze` 提示 "Image loaded into your context — you can see it natively now"，工具不调 LLM |
| `deepseek-v4-pro`（仅 text） | `text` | 工具结果是一段 JSON `{"success":true,"analysis":"..."}`，`agent.log` 有 `tool vision_analyze completed (2.15s, N chars)` |

**推论（最常见的自欺）**：在主模型本身有视觉的会话里测 aux 配置，看到「成功」也证明不了 aux 配对了。验证 aux 一律用 text-only 主模型跑一遍。

## 二、本机当前配置（已落地）

```yaml
auxiliary:
  vision:
    provider: deepseek
    model: deepseek-v4-flash        # 线上真实 ID deepseek-flash（V4.1-Flash）
    fallback_chain:
      - provider: custom:ZhipuGLM
        model: glm-4.6v-flash       # 零审查兜底（429/1305 常客）
      - provider: custom:DashScope
        model: qwen-vl-plus         # 末位兜底
```

写入方式（config.yaml 不能直接编辑，见下）：

```bash
hermes config set auxiliary.vision.provider deepseek
hermes config set auxiliary.vision.model deepseek-v4-flash
hermes config set auxiliary.vision.fallback_chain '[{"provider":"custom:ZhipuGLM","model":"glm-4.6v-flash"},{"provider":"custom:DashScope","model":"qwen-vl-plus"}]'
```

- 输出会带 `⚠ 'auxiliary.vision.fallback_chain' is not a recognized config key — it was saved anyway`。**可忽略**：YAML 结构写对了，代码确实读该键（历史日志 `Auxiliary vision: rate limit on zhipuglm … fallback_chain[0](custom:DashScope)` 就是它在工作的证据）。
- 改前必做：`cp config.yaml config.yaml.bak-vision-<tag>-$(date +%Y%m%d_%H%M%S)`。

## 三、为什么是「DeepSeek 主 + GLM 兜底」而不是全切

| 维度 | DeepSeek V4.1-Flash | GLM-4.6v-flash |
|------|---------------------|----------------|
| 速度 | 1.0~1.1s（实测） | 慢，且 429/1305 频繁（日志里一堆） |
| 额度 | 走 DeepSeek 主账户 | 免费 |
| 审查 | 官方审查较严，擦边/NSFW 可能拒答 | 近零审查 |
| 上下文 | 1M | 128K |

所以主路径用 DeepSeek 拿速度与稳定，擦边/NSFW 交给兜底 GLM —— 但要注意：**兜底只在「主路径报错/限流」时触发**，主路径「礼貌拒答」未必算错误、不一定 fallback。真要保 NSFW 场景，可临时把 provider 切回 `custom:ZhipuGLM`（或对该会话单独用 GLM 识图）。

## 四、三层验证法（每层都留证据）

1. **直连 API 读图**：base64 塞 `image_url`，图里写可验证内容（数字 + 汉字 + 两个色块），问「读出数字/汉字/颜色」。答对才算过。参考 `scripts/vision_aux_probe.py`。
2. **路由决策**：脚本里调 `decide_image_input_mode`，确认你以为的通道（native/text）与实际一致。
3. **端到端**：`hermes chat -q "调用 vision_analyze 分析 <图>，只回答…" -m deepseek-v4-pro --provider deepseek -Q`，再查 `logs/agent.log` 该 session 段的 `tool vision_analyze completed`，且**不应**出现 `Auxiliary vision: rate limit … trying fallback`。

## 五、坑清单

- `deepseek-v4.1-flash` 不是合法 ID，硬写直接 400；合法名只有 `deepseek-flash` / `deepseek-v4-pro`。Hermes 0.20.4 会把 `deepseek-flash` 折叠回 `deepseek-v4-flash`，服务端接受，所以配置写哪个都能跑，别为此折腾。
- CLI 没有 `-p`，provider 参数是 `--provider`；`--provider custom:XXX` 这种带前缀的写法可能不被接受，能省则省（用 `--provider deepseek` 这类内置名）。
- 不要在一条 terminal 命令里同时做 `wc -l logs/agent.log` + `hermes chat`，会被 gateway 安全拦截（"cannot restart or stop the gateway"）。跑完 chat 另起一次调用查日志。
- 验证用的测试图放 `$LOCALAPPDATA/Temp/`，给主人看时用 `![desc](<C:/.../x.png>)` 尖括号包路径。
