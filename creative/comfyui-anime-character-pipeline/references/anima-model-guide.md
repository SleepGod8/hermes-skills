# Anima Model — ComfyUI 专用参考

## 模型概述

Anima 由 CircleStone Labs × Comfy Org 合作开发，2B 参数动漫文生图模型，2026 年 1 月发布。
- 基座：`nvidia/Cosmos-Predict2-2B-Text2Image` 微调
- 格式：diffusion-single-file (.safetensors)，ComfyUI **原生支持**（无需额外插件）
- 训练数据：几百万动漫图 + ~80 万非动漫艺术图（LAION-POP + DeviantArt），无合成数据，动漫数据截止 2025-09
- 许可证：circlestone-labs-non-commercial-license（**非商用**，私人跑图 OK）
- HF 地址：`circlestone-labs/Anima`（76 万+ 下载，2100+ 点赞）

## 三个版本

| 版本 | 文件名 | 大小 | 特点 |
|------|--------|------|------|
| Base | anima-base-v1.0.safetensors | 4.18 GB | 预训练基础版，多样性/风格遵循最强，**LoRA 训练用此版本** |
| Aesthetic | anima-aesthetic-v1.0/1.0b/1.1.safetensors | 4.18 GB | 高质量画风微调，一致性更好（1.0 > 1.0b，1.1 最新） |
| Turbo | anima-turbo-v1.0/1.1.safetensors | 4.18 GB | 蒸馏版，CFG 1 + 8-12 steps，最快（推荐快速迭代用） |

## 文件清单与安装路径

三个文件放在 ComfyUI 模型目录对应子文件夹：

| 文件 | HF 路径 | 本地路径 |
|------|---------|----------|
| an`ima-base-v1.0.safetensors` | `split_files/diffusion_models/` | `ComfyUI/models/diffusion_models/` |
| `qwen_3_06b_base.safetensors` | `split_files/text_encoders/` | `ComfyUI/models/text_encoders/` |
| `qwen_image_vae.safetensors` | `split_files/vae/` | `ComfyUI/models/vae/` |

⚠️ VAE 文件名是 `qwen_image_vae.safetensors`（不是 `qwen_3_vae.safetensors`）。

### 国内镜像下载

```bash
cd /e/Comfy-Desktop/ComfyUI-Shared/models
curl -L -o diffusion_models/anima-base-v1.0.safetensors \
  "https://hf-mirror.com/circlestone-labs/Anima/resolve/main/split_files/diffusion_models/anima-base-v1.0.safetensors"
curl -L -o text_encoders/qwen_3_06b_base.safetensors \
  "https://hf-mirror.com/circlestone-labs/Anima/resolve/main/split_files/text_encoders/qwen_3_06b_base.safetensors"
curl -L -o vae/qwen_image_vae.safetensors \
  "https://hf-mirror.com/circlestone-labs/Anima/resolve/main/split_files/vae/qwen_image_vae.safetensors"
```

三文件并发下载（用 `&` + `wait`）通常 20~60 分钟完成。

## 生成参数

- 分辨率：512² ~ 1536²
- Steps：30-50（Base/Aesthetic）；8-12（Turbo）
- CFG：4-5（Base/Aesthetic）；1（Turbo）
- 推荐采样器：
  - `er_sde`：中性画风、平涂色、锐利线条（默认推荐）
  - `euler_a`：较柔和线条，稍偏 2.5D，CFG 可稍高
  - `dpmpp_2m_sde_gpu`：类似 er_sde 但更多变/创意
  - `euler`：基础采样器，Turbo/Aesthetic 版用效果好
  - `beta57` scheduler（RES4LYF 节点包）：偏写实/画师感纹理

## 提示词配方

模型训练于 Danbooru 标签 + 自然语言 caption + 混合，两者均可使用。

### Danbooru 标签模式

- **小写标签**，空格分隔（不是下划线）
- `score_*` 标签用下划线（唯一例外）
- 推荐正向前缀：`masterpiece, best quality, score_7, safe, `
- 推荐负向：`worst quality, low quality, score_1, score_2, score_3, artist name, blurry, jpeg artifacts, chromatic aberration`
- 画师用 `@` 前缀：`@big chungus`

### 自然语言模式

- 按标准英语大小写规则（角色/系列名大写）
- 描述要详细（至少 2 句），太短会出意外结果
- 可混用标签和自然语言，任意顺序
- 质量/画师标签可放最前面：`"masterpiece, best quality, @big chungus. An anime girl with medium-length blonde hair is..."`
- 多角色时**必须描述外观**，仅列角色名会混淆模型

### NSFW 安全标签

- Anima 支持 `safe` / `sensitive` / `nsfw` / `explicit` 四档安全标签
- NSFW 内容需要加 `explicit` 标签才会生成（不加可能拒绝或降质）

## 与 animagine-xl-4.0 对比

| 维度 | Anima (2B) | animagine-xl-4.0 (SDXL) |
|------|-----------|--------------------------|
| 参数量 | 2B | ~2.6B (SDXL) |
| 显存需求 | 低（2B 架构） | 中（SDXL 标准） |
| 生成速度 | 快（Turbo 版 8-12 steps） | 中（30-32 steps） |
| 动漫质量 | 极佳（专训动漫+艺术） | 极佳（Danbooru 标签专精） |
| 非动漫能力 | 可（训练含非动漫艺术图） | 弱（动漫特化） |
| LoRA 生态 | 新，生态成长中 | 成熟，大量 LoRA 可用 |
| NSFW | 支持（安全标签控制） | 支持（Danbooru 标签） |
| ComfyUI 支持 | 原生（不同架构，用 ModelSamplingDiscreteDistortion） | 标准 SDXL 流程 |
| 许可证 | 非商用 | openrail++ (商用需遵守) |

## 本机状态

- 本机路径：`E:\Comfy-Desktop\ComfyUI-Shared\models\`
- 已有：`qwen_3_4b.safetensors`（text_encoders）、`ae.safetensors`（vae）、`z_image_turbo_bf16.safetensors`（diffusion_models）
- Anima 需要的 `qwen_3_06b_base.safetensors`（0.6B）和 `qwen_3_4b.safetensors`（4B）是不同的文本编码器，不能混用
- 下载验证：`stat -c '%n %s bytes'` 对比 HF 上的文件大小

## 参考链接

- HF 仓库：https://huggingface.co/circlestone-labs/Anima
- ComfyUI 官方支持：https://github.com/comfyanonymous/ComfyUI
- HF 国内镜像：https://hf-mirror.com/circlestone-labs/Anima
