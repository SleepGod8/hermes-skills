---
name: image-ocr
description: "Extract text from standalone images (PNG, JPG, etc.) using online APIs and local OCR tools — Chinese, English, and multilingual."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [OCR, Image, Text-Extraction, Chinese, vision]
    related_skills: [ocr-and-documents]
---

# Image OCR — Text Extraction from Images

Extract text from standalone image files (PNG, JPG, WebP, etc.) when the user provides a screenshot, photo, scan, or any image containing text. This skill covers **images only** — for text inside PDFs, see the `ocr-and-documents` skill.

## Quick Decision

| Situation | Approach |
|-----------|----------|
| Network available, no local OCR installed | **OCR.space free API** (no API key needed) |
| Local Tesseract installed | **pytesseract** (fast, offline) |
| No network, no Tesseract, willing to install ~2GB | **easyocr** (pure Python, offline) |
| Need highest accuracy, complex layout | **easyocr** with GPU |

---

## Approach 1: OCR.space Free API (Recommended — No Install)

**Pros:** Works everywhere, supports Chinese (chs) + English, no API key or local install needed.
**Cons:** Requires internet, rate-limited for free tier.

```python
import base64, json, urllib.request, urllib.parse

with open('image.png', 'rb') as f:
    b64 = base64.b64encode(f.read()).decode()

url = 'https://api.ocr.space/parse/image'
data = urllib.parse.urlencode({
    'base64Image': 'data:image/png;base64,' + b64,
    'language': 'chs',           # 'chs' for Chinese, 'eng' for English, 'chs+eng' for both
    'isOverlayRequired': 'false',
    'OCREngine': '2',            # Engine 2 is more accurate
    'apikey': 'helloworld'       # Free tier key (no registration)
}).encode()

req = urllib.request.Request(url, data=data)
req.add_header('Content-Type', 'application/x-www-form-urlencoded')
resp = urllib.request.urlopen(req, timeout=30)
result = json.loads(resp.read().decode())

if result.get('ParsedResults'):
    for r in result['ParsedResults']:
        print(r.get('ParsedText', ''))
else:
    print('Error:', json.dumps(result, ensure_ascii=False, indent=2))
```

**Language codes:** `chs` (Chinese Simplified), `eng` (English), `jpn` (Japanese), `kor` (Korean), `fre` (French), `ger` (German). Combine with `+`: `'chs+eng'`.

---

## Approach 2: pytesseract (Local Tesseract)

Requires Tesseract binary installed on the system.

```bash
pip install pytesseract pillow
```

```python
from PIL import Image
import pytesseract

img = Image.open('image.png')
# Chinese + English
text = pytesseract.image_to_string(img, lang='chi_sim+eng')
print(text)
```

**Windows Tesseract install pitfalls:**
- UB-Mannheim downloads (`https://github.com/UB-Mannheim/tesseract/releases`) may be blocked in some regions (China). Try mirrors or VPN.
- `winget install "Tesseract OCR"` may fail due to interactive prompts that cannot be bypassed with `--disable-interactivity` on some systems.
- If Tesseract is not in PATH, set `pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'`
- After install, Chinese language pack: download `chi_sim.traineddata` to `Tesseract-OCR/tessdata/`

---

## Approach 3: easyocr (Heavy but Fully Offline)

Pure Python OCR using PyTorch. Works without external binaries but requires ~2GB download (PyTorch + models).

```bash
pip install easyocr
```

```python
import easyocr
reader = easyocr.Reader(['ch_sim', 'en'])  # Chinese simplified + English
results = reader.readtext('image.png')
for (bbox, text, confidence) in results:
    print(f'{text} ({confidence:.2f})')
```

**Pitfalls:**
- First install downloads PyTorch (~800MB) and models (~1GB) — slow on limited connections
- GPU not required but CPU mode is slower

---

## Common Pitfalls & Solutions

| Problem | Solution |
|---------|----------|
| OCR.space returns 400 Bad Request | Ensure `base64Image` prefix is included: `data:image/png;base64,` |
| OCR.space timeout on large images | Resize the image first (< 10MB) |
| pytesseract: "Tesseract not installed" | Binary not in PATH. Install tesseract or set `tesseract_cmd` |
| Chinese text garbled | Make sure you have `chi_sim.traineddata` (pytesseract) or use `chs` (OCR.space) |
| Gateway API (vision_analyze) returns 401 | The active model/provider may not have vision configured. Fall back to OCR approaches above. |
| Image downloaded from web can't be read | Save the image locally first: `curl -o image.png URL` |

## Fallback: vision_analyze

When available, try `vision_analyze(image_url=path, question="extract all text")` first — it's the simplest path. Only fall back to the approaches above when vision_analyze is unavailable or fails with auth errors.
