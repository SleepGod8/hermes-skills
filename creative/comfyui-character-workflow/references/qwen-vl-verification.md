# DashScope qwen-vl-plus 出图视觉验证（2026-08-11 四轮实测）

ComfyUI 角色图交付前用 qwen-vl-plus 逐张验证，通过才给主人。本机免翻墙直连、有免费额度，比 glm-4.6v-flash 稳定（后者偶尔 404）。

## 凭据

- Key：Hermes 根 `.env` 里 `DASHSCOPE_API_KEY`（Hermes 会话里可用 `grep DASHSCOPE "C:/Users/80704/AppData/Local/hermes/.env"` 取，注意是 Hermes 根 .env 不是项目 .env）
- 端点：`https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions`（OpenAI 兼容）
- 模型：`qwen-vl-plus`（看图无内容限制；qwen-vl-max 审查严，别用）

## 调用模式（Python urllib，无第三方依赖）

```python
import base64, json, urllib.request

key = "<DASHSCOPE_API_KEY>"
img_path = r"<绝对路径.png>"
with open(img_path, "rb") as f:
    b64 = base64.b64encode(f.read()).decode()

body = {
    "model": "qwen-vl-plus",
    "messages": [{
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
            {"type": "text", "text": "检查这张动漫图：1)姿势是什么？2)手部：手指数量正常吗？有无畸形/多指/断指？3)发型发色？4)服装/道具元素？5)总体是否可用？先给'通过/不通过'。"}
        ]
    }],
    "max_tokens": 400
}
req = urllib.request.Request(
    "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
    data=json.dumps(body).encode(),
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
)
resp = json.loads(urllib.request.urlopen(req, timeout=60).read().decode())
print(resp["choices"][0]["message"]["content"])
```

## 检查点清单（每次验证都过一遍）

| 项 | 说明 |
|---|---|
| 发型/发色 | 与角色配方表一致（如 Artemis 深紫短发 bob、Hebe 金双马尾粉挑染） |
| 表情 | 是否符合角色气质（傲娇/元气/温柔） |
| 脸部道具 | 创可贴、棒棒糖、发饰等细节是否画出来 |
| 服装元素 | 女仆装/皮夹克/爱心图案等 |
| **手部** | 手指数量、畸形/多指/断指/扭曲、抱臂等姿势自然度——姿势图重点 |
| 画质 | 无模糊/畸形/背景崩坏 |

## 批量验证

5 张姿势图循环调用（每张间隔 0.5s 防限流），输出逐张标注 `通过/不通过`。角色一致性检查：同一角色的姿势变体发型/服装必须与定稿一致，防止模型漂移。

## 已知坑

- 单张图片 base64 后 1.5-2MB PNG 直接发没问题（qwen-vl-plus 能收）；超大的再裁剪/压缩
- 偶尔超时/网络错误 → 重试一次即可
- 验证通过的标准：角色元素齐全 + 手部正常 + 画质无崩坏；主人接受「姿势微偏但质量达标」的图
