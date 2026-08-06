# ComfyUI 质量 Playbook

## 提示词编译

将自然语言拆成稳定字段：`subject`、`count`、`action/pose`、`composition`、`camera`、`lighting`、`materials`、`palette`、`style`、`text`。正向词按这个顺序拼接，重复词只保留一次。负向词只写真实风险，例如 `blurry, low quality, bad anatomy, extra fingers, extra limbs, text, watermark, logo`；不要把正向主体放进负面。

SD1.5 通常更依赖具体英文短语与合理权重；SDXL/现代模型通常应减少 `masterpiece, 4k` 等泛化词，优先描述主体、构图和光线。权重从 1.05–1.25 小步调整，不要同时给十几个词加权。

## 工作流与模型

- API-format workflow 是 `{node_id: {"class_type": ..., "inputs": ...}}`；UI 导出的带 `nodes` 数组的图不能直接提交到 `/prompt`，需要先转换或使用原有 API JSON。
- 核心最小链路是 checkpoint 输出的 MODEL/CLIP/VAE 分别连接采样、文本编码和 VAE decode。每个输出节点都要连接到 `SaveImage` 或其它明确输出。
- Checkpoint 不是可互换的：SD1.5、SDXL、Flux、SD3 的文本编码器、latent 尺寸和采样节点可能不同。看到文件名含 `flux`、`sd3`、`cascade` 时优先找模板，不要自动套 SDXL。
- 二阶段 latent upscale 只在第一阶段构图正确时使用；放大倍率 1.25–1.5、denoise 0.2–0.35。过高会改脸、改服装或引入纹理伪影。

## 参数诊断

- 画面糊：先确认 VAE 与 checkpoint 匹配、尺寸符合模型训练分辨率，再提高 steps；不要先把 CFG 拉高。
- 过饱和/过度锐化：降低 CFG 或移除冲突质量词，尝试 `dpmpp_2m + karras`。
- 主体偏离：减少风格词，明确数量/空间关系和构图；必要时使用 ControlNet/IP-Adapter 模板。
- 重复主体：明确 `one subject, centered`，避免同时出现多个同义主体描述。
- 手脸问题：采用合适分辨率和二阶段/局部修复模板；负向词只能降低概率，不能替代结构条件。

## 安全和可复现

固定 seed 做对照实验，确认改动有效后再随机化。输出旁边保存参数摘要和 workflow JSON；不要下载或执行未经用户同意的自定义节点代码。优先内置节点，只有在本地 inventory 确认存在时才使用第三方节点。
