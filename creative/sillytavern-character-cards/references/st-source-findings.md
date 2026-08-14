# SillyTavern 角色卡源码发现（1.18.0，2026-08 实测）

## 为什么纯 .json 角色卡不显示

`src/endpoints/characters.js` → `router.post('/all')`:

```javascript
const files = fs.readdirSync(request.user.directories.characters);
const pngFiles = files.filter(file => file.endsWith('.png'));   // ← 只扫 .png！
const data = (await Promise.all(pngFiles.map(...))).filter(c => c.name);  // ← 解析失败被 name 过滤掉
```

- 纯 `.json` 文件放进 `data/default-user/characters/` 永远不会出现在角色列表
- 导入端点 `/api/characters/import` 接受 multipart 上传（file + file_type=json/png/yaml/charx/byaf），但被 CSRF/会话保护拦截（curl 直调 403）→ 自动化导入走不了，自制成 PNG 最稳

## 为什么明文 chara 块不行

`src/character-card-parser.js`:

```javascript
// 写：base64 编码后写入
chunks.splice(-1, 0, PNGtext.encode('chara', base64EncodedData));
// 读：base64 解码
return Buffer.from(textChunks[charaIndex].text, 'base64').toString('utf8');
```

- PNG tEXt chunk：keyword=`chara`，value 必须是 **base64(JSON)**
- PIL `PngInfo.add_text("chara", 明文JSON)` → ST 解码乱码 → 解析失败 → 角色静默跳过、列表不出现（无报错日志）

## 角色卡 PNG 生成（已实测可用）

```bash
python make_char_card.py input.json output.png [avatar.png]
```

见 skill 的 `scripts/make_char_card.py`。生成后放 `data/default-user/characters/`，重开页面即出现。

## 其他实测事实

- 启动日志 "SillyTavern is listening on IPv4: 127.0.0.1:8001" 即成功
- `node server.js` 在无 tty 后台环境 exit 1（"stdin is not a tty"）→ terminal background 必须 pty=true
- 端口 8000 被 Dify/FastAPI(uvicorn) 占用时返回 JSON `{"detail":"Not Found"}` 而非 ST 页面；ST 根路径返回 `<title>SillyTavern</title>` HTML
- 角色卡默认排序 A-Z；角色列表分页 50/页
- Ollama 模型下拉默认选中列表第一个模型（darkidol:latest 之类）
- browserbase 自动化浏览器会话的 localStorage 不跨 navigate 保留 → 服务重启后 Ollama 连接配置丢失；用户本机浏览器正常保留
