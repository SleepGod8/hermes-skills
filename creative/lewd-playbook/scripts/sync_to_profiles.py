#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""同步 lewd-playbook skill 到全部子档案（v2.0 · 带漂移检测/备份/只读镜像）。

背景：子档案会话只扫描自己的 skills 目录（profiles/<name>/skills/），
看不到根级 skills。改根级 lewd-playbook 后必须跑本脚本同步，
否则子档案会话加载的是旧副本。

v2.0 新增（2026-09-26 · P0 单一写入者策略）：
  * .sync-manifest.json 记录上次同步时每个文件的 md5
  * 同步前做**漂移检测**：若某个子档案副本在"上次同步之后"被本地改过（DRIFT），
    默认**拒绝覆盖**（防止抹掉子档案侧真实发生的数据），需 --force 才覆盖，
    且覆盖前一律先备份。
  * 子档案副本里写入 `_MIRROR_READONLY.md` + 面板文件顶部注入「⛔ 只读镜像」横幅，
    明确「面板只由 default（Hermes）会话写」。
  * --dry-run / --diff / --verify-only / --backup-dir 全支持。

用法：
    python sync_to_profiles.py --dry-run --diff     # 预演（不改任何东西）
    python sync_to_profiles.py                     # 正式同步（自动备份）
    python sync_to_profiles.py --force             # 覆盖子档案侧漂移（已自动备份）
    python sync_to_profiles.py --verify-only       # 只校验（应为全部 OK）
"""
import argparse
import hashlib
import json
import os
import shutil
import sys
import time

SRC_DEFAULT = r'C:\Users\80704\AppData\Local\hermes\skills\creative\lewd-playbook'
PROFILES_BASE = r'C:\Users\80704\AppData\Local\hermes\profiles'
NAMES = ['aphrodite', 'ares', 'artemis', 'athena', 'dionysus', 'hebe', 'hypnos', 'nemesis']
MANIFEST_NAME = '.sync-manifest.json'
MARKER = '_MIRROR_READONLY.md'
BANNER_PREFIX = '> ⛔'
SKIP_DIRS = {'__pycache__', '.git'}
SKIP_SUFFIX = ('.pyc', '.pyo')
REQUIRED = ['SKILL.md', 'references/面板存档/panel-records.md',
            'scripts/sync_to_profiles.py', 'scripts/verify_panels.py']

MARKER_TEXT = """# ⛔ 只读镜像（子档案副本）

本目录是 **根级 lewd-playbook 的只读镜像**，由 `scripts/sync_to_profiles.py` 自动覆盖。

- 源：`C:\\Users\\80704\\AppData\\Local\\hermes\\skills\\creative\\lewd-playbook`
- 🔒 **不要在本副本里改任何文件**（含 `references/面板存档/`）。子档案会话结算时只输出
  「本次结算报告」，由 default（Hermes）会话统一落盘。
- 想改玩法/机制：改根级，再跑一次同步脚本。
- 若发现本副本与根级不一致：说明有人在子档案侧写过 = 会上丢的数据，请回报主人。
"""


def md5(path):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 16), b''):
            h.update(chunk)
    return h.hexdigest()


def rel_files(root, skip_names=()):
    out = {}
    for r, dirs, fs in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in fs:
            if f.endswith(SKIP_SUFFIX) or f == MANIFEST_NAME or f in skip_names:
                continue
            p = os.path.join(r, f)
            out[os.path.relpath(p, root).replace('\\', '/')] = md5(p)
    return out


def text_md5_no_banner(path):
    """文本文件：忽略只读横幅行后取 md5（用于 compare 源/副本）。"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            body = ''.join(l for l in f if not l.startswith(BANNER_PREFIX))
    except (UnicodeDecodeError, OSError):
        return md5(path)
    return hashlib.md5(body.encode('utf-8')).hexdigest()


def snapshot_semantic(root, skip_names=()):
    out = {}
    for r, dirs, fs in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in fs:
            if f.endswith(SKIP_SUFFIX) or f == MANIFEST_NAME or f in skip_names:
                continue
            p = os.path.join(r, f)
            rel = os.path.relpath(p, root).replace('\\', '/')
            out[rel] = text_md5_no_banner(p)
    return out


def load_manifest(src):
    p = os.path.join(src, MANIFEST_NAME)
    if os.path.isfile(p):
        try:
            return json.load(open(p, encoding='utf-8'))
        except (ValueError, OSError):
            print(f'⚠️  manifest 损坏，忽略：{p}')
    return {'version': 2, 'files': {}}


def save_manifest(src, snap):
    p = os.path.join(src, MANIFEST_NAME)
    json.dump({'version': 2, 'last_sync': time.strftime('%Y-%m-%d %H:%M:%S'),
               'src': src, 'files': snap},
              open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)


def inject_banner(dst_root):
    """给面板/存档类 md 顶部注入只读横幅（仅副本，源不动）。"""
    targets = []
    pd = os.path.join(dst_root, 'references', '面板存档')
    if os.path.isdir(pd):
        for r, _, fs in os.walk(pd):
            targets += [os.path.join(r, f) for f in fs if f.endswith('.md')]
    for p in targets:
        with open(p, 'r', encoding='utf-8') as f:
            body = f.read()
        if body.startswith(BANNER_PREFIX):
            continue
        head = (f'{BANNER_PREFIX} 只读镜像（子档案副本）· 面板只由 default（Hermes）会话写 · '
                f'本地修改会在下次同步时丢失\n')
        # 放在标题行之后更好读
        lines = body.split('\n')
        if lines and lines[0].startswith('#'):
            # 只在标题行后插一行横幅，不额外插入空行——保证「去掉横幅 = 源文件」
            body = lines[0] + '\n' + head + '\n'.join(lines[1:])
        else:
            body = head + body
        with open(p, 'w', encoding='utf-8') as f:
            f.write(body)
    with open(os.path.join(dst_root, MARKER), 'w', encoding='utf-8') as f:
        f.write(MARKER_TEXT)


def main():
    ap = argparse.ArgumentParser(description='同步 lewd-playbook 到子档案（v2.0）')
    ap.add_argument('--src', default=SRC_DEFAULT)
    ap.add_argument('--profiles', default=PROFILES_BASE)
    ap.add_argument('--dry-run', action='store_true', help='预演，不写入')
    ap.add_argument('--diff', action='store_true', help='显示差异明细')
    ap.add_argument('--verify-only', action='store_true', help='只校验副本与源是否一致')
    ap.add_argument('--force', action='store_true', help='覆盖子档案侧的本地漂移（会先备份）')
    ap.add_argument('--skip-backup', action='store_true', help='同步前不备份（不推荐）')
    ap.add_argument('--rebuild-baseline', action='store_true',
                    help='忽略现有基线，按当前源重建（误报 DRIFT 时用于恢复）')
    ap.add_argument('--backup-dir', default=os.path.join(os.path.expanduser('~'), 'AppData', 'Local',
                                                         'hermes', 'backups', 'lewd-playbook-sync'))
    args = ap.parse_args()

    src = os.path.abspath(args.src)
    if not os.path.isdir(src):
        print(f'❌ 源不存在: {src}')
        return 1
    for req in REQUIRED:
        if not os.path.isfile(os.path.join(src, req)):
            print(f'❌ 源缺少必需文件: {req}（先修源再同步）')
            return 1

    # 统一用「忽略只读横幅」的语义哈希做比较与基线（否则副本横幅会导致永远 diff）
    src_snap = snapshot_semantic(src)
    manifest = load_manifest(src)
    prev = manifest.get('files', {})
    if args.rebuild_baseline:
        prev = {}
    ts = time.strftime('%Y%m%d_%H%M%S')

    if args.verify_only:
        bad = 0
        print(f'🔍 verify-only：源 {len(src_snap)} 个文件')
        for name in NAMES:
            dst = os.path.join(args.profiles, name, 'skills', 'creative', 'lewd-playbook')
            if not os.path.isdir(dst):
                print(f'  ❌ {name}: 副本缺失'); bad += 1; continue
            dst_snap = snapshot_semantic(dst, skip_names={MARKER})
            miss = sorted(set(src_snap) - set(dst_snap))
            extra = sorted(set(dst_snap) - set(src_snap))
            diff = sorted(k for k in src_snap if k in dst_snap and dst_snap[k] != src_snap[k])
            if miss or extra or diff:
                bad += 1
                print(f'  ❌ {name}: miss={len(miss)} extra={len(extra)} diff={len(diff)}')
                for k in (miss + diff + extra)[:5]:
                    print(f'       - {k}')
            else:
                print(f'  ✅ {name}: {len(dst_snap)}/{len(src_snap)} 一致')
        print('✅ verify-only 全部通过' if not bad else f'❌ verify-only 失败：{bad} 个档案有问题')
        return 0 if not bad else 1

    total_drift, total_copy, total_unchanged, skipped = 0, 0, 0, 0
    first_sync = not prev
    if first_sync:
        print('ℹ️  未找到上次同步基线（首次跑 v2.0）：按「首次镜像」处理，不做 DRIFT 拦截；'
              '本次会建立基线，之后才启用漂移检测。')
    for name in NAMES:
        dst = os.path.join(args.profiles, name, 'skills', 'creative', 'lewd-playbook')
        action, detail = 'copy', ''
        if os.path.isdir(dst):
            cur = snapshot_semantic(dst, skip_names={MARKER})
            drift = []
            for rel, h in cur.items():
                if rel in prev and prev[rel] != h:
                    drift.append(rel)
                elif rel not in prev and rel in src_snap and src_snap[rel] != h:
                    drift.append(rel)   # 上次同步没记录（首次升级）但两边不同
            if drift:
                if first_sync:
                    action = 'copy'
                    print(f'ℹ️  {name}: 首次镜像（{len(drift)} 个文件与源不同，属正常，不拦截）')
                else:
                    total_drift += 1
                    action = 'drift'
                    detail = f'{len(drift)} 个文件在子档案侧被改过：{", ".join(drift[:3])}'
                    if not args.force:
                        skipped += 1
                        print(f'🛑 {name}: DRIFT 拒绝覆盖 → {detail}')
                        print(f'      （确认要覆盖就加 --force；覆盖前会自动备份）')
                        continue
            # 幂等：语义一致（忽略只读横幅）则跳过，不重写、不备份
            if not drift and cur == src_snap:
                total_unchanged += 1
                print(f'· {name}: unchanged（已与源一致，跳过）')
                continue
        if args.dry_run:
            n_files = len(src_snap)
            print(f'• {name}: would-copy {n_files} files' + (f' [{detail}]' if detail else ''))
            total_copy += 1
            continue

        # 备份
        if os.path.isdir(dst) and not args.skip_backup:
            bdir = os.path.join(args.backup_dir, ts, name)
            os.makedirs(os.path.dirname(bdir), exist_ok=True)
            shutil.copytree(dst, bdir)
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        # 清掉可能被带过去的 manifest/缓存
        for junk in [os.path.join(dst, MANIFEST_NAME)]:
            if os.path.isfile(junk):
                os.remove(junk)
        shutil.rmtree(os.path.join(dst, '__pycache__'), ignore_errors=True)
        inject_banner(dst)
        print(f'✅ {name}: 已同步{(" · 覆盖了 DRIFT" if action == "drift" else "")}')
        total_copy += 1

    if not args.dry_run:
        # 只有在没有因 DRIFT 跳过任何档案时才落基线——否则基线会与真实镜像不符
        if skipped == 0:
            save_manifest(src, src_snap)
            print(f'\n✅ 基线已更新（{len(src_snap)} 个文件）')
        else:
            print(f'\n⚠️  有 {skipped} 个档案被 DRIFT 拦截，**未更新基线**（避免下次误判）')
        print(f'完成：同步 {total_copy} 个档案 · unchanged {total_unchanged} 个 · '
              f'DRIFT {total_drift} 个 · 跳过 {skipped} 个\n备份目录：{os.path.join(args.backup_dir, ts)}')
    else:
        print(f'\n[dry-run] would-copy={total_copy} unchanged={total_unchanged}（未写入任何文件）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
