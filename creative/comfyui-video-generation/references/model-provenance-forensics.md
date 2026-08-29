# 模型来源溯源技术（"这个模型是哪来的？"）

用户问本机某个模型文件从哪来时，用文件时间戳 + 下载缓存目录 + 会话历史交叉验证，不要只靠猜测。

## 步骤

1. **文件时间戳三件套**（git-bash 的 stat 支持创建时间）：
   ```bash
   stat -c "%n | 创建:%w | 修改:%y" <file1> <file2> <file3>
   ```
   - 修改时间（%y）= 下载完成时刻（文件写完）
   - 创建时间（%w）= 下载开始/文件创建时刻
   - 同一秒创建的多个文件 = 批量触发下载（模板一键下载的特征）

2. **查下载缓存目录**：ComfyUI Desktop 的 `E:\Comfy-Desktop\ComfyUI-Cache\download-cache` 目录创建时间与模型文件创建时间对齐 = 模型是 ComfyUI 内置下载器在首次安装时拉的。

3. **查会话历史**：`session_search` 搜模型名/关键词，看 Hermes 是否参与过下载。

4. **关键判定**：如果历史会话中 Hermes 曾盘点过该模型但**认错了它的身份**（例如把 Z-Image-Turbo 标成"FLUX 系"），说明模型不是 Hermes 下载的——Hermes 只是事后看到。

## 案例：Z-Image-Turbo 溯源（2026-07 本机）

- 三个文件（diffusion model 12G + qwen_3_4b TE 7.5G + ae VAE 320M）创建时间完全一致：`2026-07-09 03:14:10`，与 `ComfyUI-Cache/download-cache` 目录创建时间（03:14）分秒不差
- 下载完成顺序按大小递增：ae(320M) 03:27 → qwen_3_4b(7.5G) 04:54 → z_image(12G) 05:16
- 结论：7月9日 ComfyUI Desktop v0.20.1 首次安装时，界面内模板/模型下载功能一键拉取，非 Hermes 所为

## 坑

- hf 直连不通时用 hf-mirror 查模型卡（`hf-mirror.com/api/models/<org>/<name>` 拿 tags/siblings，`/raw/main/README.md` 拿说明）
- Windows git-bash 的 `ls -lh --time-style=full-iso` 也能显示时间但默认不显示创建时间；`stat -c "%w"` 才给创建时间
- 会话库只保留有限窗口：查不到下载记录 ≠ 没有下载过，可能是记录已滚动出库——此时时间戳证据更可靠
