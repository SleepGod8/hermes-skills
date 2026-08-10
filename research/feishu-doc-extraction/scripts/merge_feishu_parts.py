#!/usr/bin/env python3
"""Merge feishu-doc slice files NAME_part1.json..NAME_partN.json into NAME.json
and verify the block count against the collection script's `n`.

Why: the collection script stores blocks in window.__blocks; long docs (many
table cells => 600-1100 blocks) are fetched via browser_console in ~280-block
slices and each slice is written to NAME_partN.json. Merging by hand risks
dropping blocks; this script asserts count == expected so a missing slice
fails loudly.

Usage:
    python merge_feishu_parts.py --name '1产品立项书撰写思路' --expect 1141 [--outdir .]

Exit 0 and writes NAME.json on exact block-count match; exit 1 on mismatch
or missing parts. Does NOT delete the part files (run `rm -f NAME_part*.json`
after a successful merge). Chars may differ ~0.5% from the script's `chars`
(newlines inside code blocks get flattened when transcribing the displayed
result) — block count is the authoritative check, not chars.
"""
import argparse
import json
import pathlib
import sys


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--name', required=True, help='base name, e.g. 1产品立项书撰写思路')
    ap.add_argument('--expect', type=int, required=True, help='block count returned by the collection script (n)')
    ap.add_argument('--outdir', default='.', help='directory containing NAME_partN.json files')
    a = ap.parse_args()

    outdir = pathlib.Path(a.outdir)
    parts: list = []
    i = 1
    while True:
        p = outdir / f'{a.name}_part{i}.json'
        if not p.exists():
            break
        parts.extend(json.loads(p.read_text(encoding='utf-8')))
        i += 1

    if not parts:
        print(f'no part files found for {a.name} in {outdir}', file=sys.stderr)
        return 1

    n = len(parts)
    chars = sum(len(b[1]) for b in parts)
    print(f'merged {i-1} part(s): blocks={n}, chars={chars}')
    if n != a.expect:
        print(f'MISMATCH: expected {a.expect} blocks, got {n}.', file=sys.stderr)
        print(f'Before re-fetching, check for FOREIGN/STALE part files from other agents or earlier runs:', file=sys.stderr)
        print(f'  ls {outdir / (a.name + "_part*.json")}', file=sys.stderr)
        print(f'  (merge scans NAME_part1.json, NAME_part2.json, ... sequentially — a sibling agent writing the same base name inflates the count)', file=sys.stderr)
        print(f'Remove or rename foreign parts, then re-run; only re-fetch the missing slice from window.__blocks if parts are genuinely short.', file=sys.stderr)
        return 1

    (outdir / f'{a.name}.json').write_text(
        json.dumps(parts, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'OK -> {a.name}.json ({n} blocks)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
