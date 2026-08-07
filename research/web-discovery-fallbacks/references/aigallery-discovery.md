# aigallery 发现案例（2026-08-07）

用户问「aigallery 是什么」，线索逐步补充：AI 话题网站 → AI 画图网站 → 无审查的 AI 画图。

## 排查过程

1. Bing cn 搜 `"aigallery"` → 返回完全无关结果（宝可梦道馆、数字 0 的数学讨论、知乎）——query 解析错乱，弃用
2. 百度 → wappass 人机验证跳转，无解
3. Brave → captcha 滑块
4. html.duckduckgo.com / lite.duckduckgo.com → HTML 可拿（14KB）但结果链接解析为 0
5. GitHub API 搜索 → 命中 8 个仓库，最有价值 WYQilin/aigallery（⭐31「帮AI绘画爱好者记录绘图作品的小程序」）——但那是小程序，不是网站
6. 域名 TLD 探测（urllib + title 正则，10 个 TLD）→ 结果：
   - `aigallery.ai` → 域名停放页（"获得此域名"）
   - `aigallery.com` → Atom 域名出售页（$ 出售）
   - `aigallery.io` → 域名出售页
   - `aigallery.cn` → For Sale
   - `aigallery.dev` → Changeboo（AI 换装试穿，不相关）
   - `aigallery.app` → **✅ 真实站点**「AI Gallery - Generate Stunning AI Art」
7. browser_navigate 打开 aigallery.app 确认：浏览器直接用的 AI 画图站，社区驱动，模型列表含 WAI-NSFW-illustrious-SDXL、WAI-ANI-NSFW-PONYXL、Grapefruit Hentai 等 NSFW 模型，Text2Img/Img2Img/Inpainting/ControlNet，免注册，有 Telegram 社区

## 结论

aigallery.app = 无审查 AI 画图网站（社区 worker 算力 + 浏览器端生成，类似去中心化 Stable Diffusion 在线版）。

## 可复用要点

- 用户线索是逐步补全的（话题网站→画图→无审查），每轮用新线索缩小范围
- GitHub API 只找到开源项目，找不到商业网站——「XX 是什么网站」类问题要接着走域名探测
- 域名探测脚本（urllib + title 正则）一次能扫 10+ TLD，几分钟内定位真实站点
