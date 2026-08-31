# 视频资产卸载状态（2026-08-30）

用户于 2026-08-30 完成一次大规模清理：**全部视频相关资产已从本机删除**，
只保留动漫画像模型。本文件记录清理范围，防止未来会话误以为视频栈仍可用。

## 已删除

| 类别 | 内容 |
|------|------|
| 模型 | `unet/Wan2.2-TI2V-5B-Q4_K_M.gguf`、`Q5_K_M.gguf`（未下完）、`text_encoders/umt5_xxl_fp16.safetensors`（11G）、`umt5_xxl_fp8_e4m3fn_scaled.safetensors`（6.3G）、`vae/wan2.2_vae.safetensors`、`vae/wan_2.1_vae.safetensors`、`clip_vision/open-clip-..._visual_fp16.safetensors` |
| 图像模型（连带）| `checkpoints/CyberRealisticPony_V18.safetensors`（真人 NSFW）、`checkpoints/Realistic_Vision_V5.1.safetensors`（写实）——用户要求只留动漫 |
| 节点 | `ComfyUI-WanVideoWrapper`、`ComfyUI-GGUF`（custom_nodes/ 下已移除）|
| 工作流 | `wan2.2_ti2v_5b_i2v_8gb_api.json`、`wan2.2_5b_i2v_nsfw_121f.json`、`pony_nsfw_txt2img.json` |
| 测试产物 | input/ 测试图（human.png、realistic_maid.png、rv_nsfw_maid.png）、output/ 视频与 NSFW 图 |

## 保留（当前模型库 = 动漫画像全家）

- checkpoints: NoobAI-XL-v1.1 (6.7G)、animagine-xl-4.0 (6.5G)
- diffusion_models: Anima-2.9B-preview-v1 (5.5G)、anima-base-v1.0 (3.9G)、z_image_turbo_bf16 (12G)
- text_encoders: qwen_3_4b (7.5G)、qwen_3_06b_base (1.2G)
- vae: ae.safetensors (320M)、qwen_image_vae (243M)
- 节点: ComfyUI-AnimateDiff-Evolved、ComfyUI-VideoHelperSuite、ComfyUI-Anima-2.9B、impact-pack/Subpack（仍在，但 animatediff_models/ 为空 → 跑 AnimateDiff 仍需先下 motion module）

## 对未来的影响

- **用户当前意图**：只拍动漫画像，不做视频/真人 NSFW。若用户再提出视频或真人 NSFW
  需求，需先向用户确认是否要重新下载（涉及约 45G+ 模型 + 2 个节点 + 工作流），
  不要假设旧文件还在。
- 恢复路径见本技能 `references/wan2.2-ti2v-5b-8gb.md`（完整配方存档）。
- 删除模型后 `GET /object_info` 的 model 下拉会自然消失——这可以作为"资产已删"的
  快速验证方式。
