#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把角色卡 JSON 打包成 SillyTavern 标准 PNG 角色卡（Chara Card V2）。
用法: python make_char_card.py <input.json> <output.png> [avatar.png]
- 无 avatar.png 时生成占位图（角色名文字）
- chara tEXt 块必须 base64 编码，ST 硬性要求（明文会被静默跳过）
"""
import json
import sys
import os
import base64

from PIL import Image, ImageDraw
from PIL.PngImagePlugin import PngInfo


def main():
    if len(sys.argv) < 3:
        print("用法: python make_char_card.py <input.json> <output.png> [avatar.png]")
        sys.exit(1)

    json_path = sys.argv[1]
    png_path = sys.argv[2]
    avatar_path = sys.argv[3] if len(sys.argv) > 3 else None

    with open(json_path, encoding='utf-8') as f:
        card = json.load(f)

    # 准备图片：优先用头像图，否则生成占位图
    if avatar_path and os.path.exists(avatar_path):
        img = Image.open(avatar_path).convert('RGB')
    else:
        name = card.get('data', {}).get('name', 'Character')
        img = Image.new('RGB', (512, 512), (120, 80, 180))
        draw = ImageDraw.Draw(img)
        draw.text((256, 240), name, fill=(255, 255, 255), anchor='mm')

    # Chara Card V2: tEXt chunk 里 key="chara"，value=JSON 的 base64 编码（ST 硬性要求）
    json_bytes = json.dumps(card, ensure_ascii=False).encode('utf-8')
    b64_data = base64.b64encode(json_bytes).decode('ascii')
    metadata = PngInfo()
    metadata.add_text("chara", b64_data)

    img.save(png_path, pnginfo=metadata)
    print(f"✅ 角色卡 PNG 已生成: {png_path}")
    print(f"   角色名: {card.get('data', {}).get('name', '?')}")
    print(f"   图片尺寸: {img.size}")


if __name__ == '__main__':
    main()
