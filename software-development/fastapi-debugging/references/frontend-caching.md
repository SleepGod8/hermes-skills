# FastAPI SPA 前端缓存问题

## 问题

修改了 `app/static/js/app.js` 或 `app/static/css/app.css`，但浏览器刷新后看不到变化。

## 原因

浏览器强缓存了静态资源（`Cache-Control` 或 `ETag`），尤其是 `index.html` 里引用 JS/CSS 的 `href`/`src` 没变时。

## 解决方法

### 方案 A — 修改版本号（推荐）

```html
<!-- index.html -->
<link rel="stylesheet" href="/static/css/app.css?v=20260716-1">
<script src="/static/js/app.js?v=20260716-1"></script>
```

更改 `v` 参数（如日期+序号），浏览器视为新 URL 重新加载。

### 方案 B — Ctrl+F5 强制刷新

告诉用户按 `Ctrl+F5` 跳过缓存加载最新资源。

### 方案 C — 开发时禁用缓存

浏览器 DevTools → Network → Disable cache（仅 DevTools 打开时有效）。

## 常见陷阱

- 只改了 JS 没改 CSS，但两个的版本号建议统一更新，避免排查时迷惑
- `index.html` 本身可能也被缓存，需要 Ctrl+F5 或版本号变化 + 用户手动刷新
- uvicorn `--reload` 虽然监控文件变化重启服务端，但不影响浏览器缓存
