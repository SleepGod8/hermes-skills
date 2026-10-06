# -*- coding: utf-8 -*-
"""扫描件/文档照片的版式测量：行 band、字符分组、下划线、缩进、页边距。

用法:
    python measure_doc_layout.py <image> [--red-seal]

输出（供与渲染图逐行比对，也供推出 Word 参数）:
    BAND 行号 y0 y1 h 左沿 右沿 宽度        每一行文本带
    UL   行号 y  x0 x1 宽度                 检测到的下划线横 run
    CHAR 行号 x0 x1 宽度                    行内字符分组（可算单字宽→字号）
    PAGE W H                                图像尺寸
    换算提示：1pt = (21/W)*72/2.54 px；1cm = W/21 px（A4 竖版）
运行环境只需 Pillow + numpy。
"""
import sys

import numpy as np
from PIL import Image


def masks(img_path):
    im = Image.open(img_path).convert("RGB")
    a = np.asarray(im).astype(float)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    redness = r - (g + b) / 2.0
    black = (lum < 180) & (redness < 30)          # 黑字（含下划线）
    red = redness > 24                            # 红章/红字
    return im, black, red


def row_bands(mask, min_h=4, min_px=3):
    rows = mask.sum(axis=1)
    bands, s = [], None
    for y, v in enumerate(rows):
        if v > min_px and s is None:
            s = y
        elif v <= min_px and s is not None:
            if y - s >= min_h:
                bands.append((s, y))
            s = None
    return bands


def col_groups(mask, y0, y1, gap=3, min_w=4):
    cols = mask[y0:y1].sum(axis=0)
    xs = np.nonzero(cols > 0)[0]
    if len(xs) == 0:
        return []
    out, start, prev = [], xs[0], xs[0]
    for x in xs[1:]:
        if x - prev > gap:
            out.append((int(start), int(prev) + 1))
            start = x
        prev = x
    out.append((int(start), int(prev) + 1))
    return [o for o in out if o[1] - o[0] >= min_w]


def underline_runs(mask, y0, y1, min_len=12):
    """在某行文本带内找横向长 run —— 下划线（可能因扫描倾斜出现在多行 y）。"""
    best = (None, 0, [])
    for y in range(y0, y1):
        row = mask[y]
        runs, s = [], None
        for x, v in enumerate(row):
            if v and s is None:
                s = x
            elif not v and s is not None:
                if x - s >= min_len:
                    runs.append((int(s), int(x), int(x - s)))
                s = None
        if s is not None and len(row) - s >= min_len:
            runs.append((int(s), int(len(row)), int(len(row) - s)))
        tot = sum(r[2] for r in runs)
        if tot > best[1]:
            best = (y, tot, runs)
    return best


def main():
    img = sys.argv[1]
    im, black, _red = masks(img)
    w, h = im.size
    print(f"PAGE {w} {h}")
    print(f"SCALE 1pt = {21 / w * 72 / 2.54:.3f}px ; 1cm = {w / 21:.2f}px")
    bands = row_bands(black)
    for i, (y0, y1) in enumerate(bands, 1):
        g = col_groups(black, y0, y1)
        if not g:
            continue
        left, right = g[0][0], g[-1][1]
        print(f"BAND {i:02d} y {y0}-{y1} h={y1 - y0} x {left}-{right} w={right - left}")
        yy, tot, runs = underline_runs(black, y0, y1)
        for (s, e, ln) in runs:
            if ln >= 25:  # 长 run 更可能是下划线而非汉字横画
                print(f"UL   {i:02d} y={yy} x {s}-{e} w={ln} ({ln:.1f}px)")
        # 字符分组：每字宽 ≈ 字号*2.15 (1280px 宽时)
        if len(g) <= 60:
            print("CHAR ", " ".join(f"{e - s}" for s, e in g))
            print("     ", " ".join(f"{s}-{e}" for s, e in g))


if __name__ == "__main__":
    main()
