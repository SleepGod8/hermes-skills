# 用户说「基于图片」但上下文里没有图 —— 去哪找

CLI / Studio 会话有时不会把用户粘贴的附件注入模型上下文（消息里只有文字）。
**不要反问用户重发**，先按下面的顺序在磁盘上找，通常 1 分钟内能定位到原图。

## 定位顺序

### 1. Windows Temp（粘贴/拖入的图片会被落盘成 `.tmp`）
```bash
find "$HOME/AppData/Local/Temp" -maxdepth 2 -type f -newermt "<今天的日期>" \
     -printf "%T+ %s %p\n" | sort -r | head -40
file <嫌疑文件>          # .tmp 常其实是 JPEG/PNG/WebP，用 file 判定
```
- 时间戳 ≈ 用户发消息前几分钟；体积 50KB–5MB；`file` 显示 `JPEG image data` / `PNG image data`。
- 微信/QQ 截图落地名形如 `ScreenShot_2026-10-04_131153_100.png`；Office/浏览器粘贴是 UUID `.tmp`。

### 2. Hermes 自己的附件/图片目录
```bash
ls -lt "$HOME/AppData/Roaming/hermes/composer-images"        # Composer 粘贴图
ls -lt "$HOME/AppData/Local/hermes/cache/images"             # 缓存图
ls -lt "$HOME/AppData/Local/hermes/image_cache"
ls -lt "$HOME/AppData/Local/hermes/profiles/<profile>/image_cache"
```

### 3. WeChat 接收文件（国内用户最常见的来源）
```bash
find "D:/xwechat_files" -maxdepth 3 -type d \( -name file -o -name Image \) | head
# 聊天里发出的原图存在临时目录：
#   D:/xwechat_files/<wxid>/temp/RWTemp/<YYYY-MM>/<hash>/<hash>.jpg
find "D:/xwechat_files" -maxdepth 6 -type f -newermt "<今天>" -printf "%T+ %s %p\n" | sort -r
```

### 4. 另一个 Agent 的会话日志（用户可能把同一张图先给了别的 agent）
- Codex：`~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`
  - 每行一个 JSON；`payload.type=="message" && payload.role=="user"` 里能看到**原始提问原文**
    和 `## <filename>: <绝对路径>` 形式的附件路径（含 `Image attachment: true`）。
  - 图片本体也在 `payload.content[].image_url` 里以 `data:image/jpeg;base64,...` 内联 —— 可直接解码落盘。
- 同类：`~/.claude/`、`~/.cursor/`、`~/.trae/` 等目录下的会话/缓存。

### 5. 用户自己的常用目录
`~/Downloads`、`~/Desktop`、`~/Documents`、`~/Pictures`、当前工作区 `E:/Hermes workspace`
```bash
find <dir> -maxdepth 5 -type f \( -iname "*.png" -o -iname "*.jpg" -o -iname "*.jpeg" \) \
     -newermt "<近几天>" -printf "%T+ %s %p\n" | sort -r | head
```

## 注意事项
- **别用 `grep -r` 扫整个 `$HOME` 或 `D:/xwechat_files`**：会超时（本机实测 180s 超时）。先按 maxdepth + mtime 收窄。
- 找到多个候选时，用尺寸/宽高比判断：文档扫描件通常是竖版 A4 比例（如 1280×1812，比值 1.415 ≈ 210/297）。
- 复制到工作区并改回正常扩展名再处理，避免在 Temp 里被系统清理：
  `cp <tmp> "<工作区>/cert_task/source_image.jpg"`，然后 `file` 复核。
- 顺手把原图路径记进当次任务的说明里，便于用户核对是不是他说的那张图。
