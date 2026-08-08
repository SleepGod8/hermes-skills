---
name: html-to-png-export
description: "Convert any local HTML file (diagrams, dashboards, cards, reports) to a PNG image using headless Chrome/Edge on Windows. Use when the user asks to turn an HTML artifact into an image (png/jpg), export a diagram to picture format, or screenshot a local page for chat/docs."
version: 1.0.0
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [html, png, screenshot, headless-chrome, export, image, diagram]
---

# HTML → PNG Export (headless Chrome)

Turn any local HTML file into a high-resolution PNG. Works for diagrams, architecture views, dashboards, info cards, reports — anything the user wants as an image to send over chat, paste into docs, or share.

## When to use

- User says "转成图片格式" / "export to image" / "save as png" after you produced an HTML artifact
- User wants a diagram as a picture for WeChat/QQ/docs/PPT
- User needs a static screenshot of a local HTML page

## The command (Windows git-bash, verified)

```bash
"/c/Program Files/Google/Chrome/Application/chrome.exe" --headless --disable-gpu \
  --hide-scrollbars --force-device-scale-factor=2 \
  --window-size=1200,1500 --virtual-time-budget=8000 \
  --screenshot="E:/path/out.png" "file:///E:/path/diagram.html"
```

Edge fallback (always present on Win10/11): `/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe`

Ready-made script: `scripts/html_to_png.sh` — `bash scripts/html_to_png.sh input.html [output.png] [width] [height]` (auto-finds Chrome/Edge, verifies output, prints dimensions).

## Key parameters

| Flag | Purpose |
|------|---------|
| `--force-device-scale-factor=2` | 2x hi-dpi output (1200px design → 2400px PNG). Omit for 1x. |
| `--window-size=W,H` | Viewport. MUST exceed page scroll height or bottom content gets cut. |
| `--virtual-time-budget=8000` | Wait for fonts/render before screenshot (Google Fonts need it). |
| `--hide-scrollbars` | Clean capture, no scrollbar artifacts. |
| `--screenshot=path` | Output path. Use Windows-style path. |

## Pitfalls

1. **Chrome exits with code 2 even on success.** Never trust the exit code — check the PNG file exists and its size (`ls -la`). If the file has bytes, it worked.
2. **Truncation**: `--window-size` smaller than the page's real height cuts off the bottom (footer/cards). Check with the browser: load the file, run `document.documentElement.scrollHeight`, and make sure `--window-size` height ≥ that value. If truncated, bump window-size and re-shoot.
3. **Verify dimensions** after export: `python -c "from PIL import Image; print(Image.open('out.png').size)"` (PIL fallback: parse PNG header bytes 16:24 with struct).
4. Fonts: if the page loads Google Fonts and there's no network/proxy, text falls back to system fonts — usually fine, just know it can look slightly different.
5. Use `file:///` URL form for local files (e.g. `file:///E:/ai1/page.html`).

## Workflow

1. Write the HTML file (see `architecture-diagram` / `markdown-viewer` skills for diagram generation).
2. Determine page height first (browser console: `document.documentElement.scrollHeight`) so `--window-size` fits.
3. Run headless Chrome screenshot with 2x scale.
4. Verify: file exists + non-zero size → check PNG dimensions → (optional) re-open in browser to confirm content matches.
5. Deliver the PNG path in the reply using the platform's file-delivery Markdown format.

## Delivery format

Windows paths in replies MUST be forwarded slashes wrapped in angle brackets:

```
![NL2SQL 流程图](<E:/ai1/nl2sql-flowchart.png>)
```
