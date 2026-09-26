#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""镜像同步骨架（加固版）——把 <SRC> 单向镜像到多个副本目录。

把本文件复制成 <skill>/scripts/sync_to_profiles.py 后，只改下面 CONFIG 段。
能力：--dry-run / --diff / --verify-only / --force / --rebuild-baseline / --skip-backup
硬化点（都是踩过的坑，别删）：
  * 无基线 ⇒ 首次镜像分支，不做 DRIFT 拦截（否则首次全部误报）
  * 只有 skipped==0 才落基线（否则中断的同步会污染基线，下次继续误报）
  * 源与副本统一用「忽略只读横幅」的语义哈希（否则永远 diff）
  * 横幅只插一行、不额外加空行（保证「删掉横幅 = 源文件」）
  * 覆盖前一律先备份到 backups/<task>/<ts>/<name>/
  * 语义一致 ⇒ 报告 unchanged 并跳过（幂等）
"""
import argparse, hashlib, json, os, shutil, sys, time

# ============================== CONFIG ==============================
SRC = r'C:\path\to\authoritative\source'          # 权威源目录
DEST_BASE = r'C:\Users\<you>\AppData\Local\hermes\profiles'
NAMES = ['alpha', 'beta']                          # 副本名（档案名）
DEST_REL = os.path.join('skills', 'creative', '<skill-name>')   # 副本内相对路径
REQUIRED = ['SKILL.md']                            # 源侧必须存在的文件，缺失则拒绝同步
BANNER_PREFIX = '> ⛔'
BANNER_TEXT = ('> ⛔ 只读镜像：本副本由同步脚本自动覆盖，请勿在此修改（本地修改会在下次同步丢失）。\n')
BANNER_DIRS = [os.path.join('references', 'state')]  # 需要注入横幅的子目录（相对源根）
MARKER = '_MIRROR_READONLY.md'
MANIFEST = '.sync-manifest.json'
BACKUP_ROOT = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'hermes', 'backups', 'mirror-sync')
SKIP_DIRS = {'__pycache__', '.git'}
SKIP_SUFFIX = ('.pyc', '.pyo')
# ====================================================================


def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 16), b''):
            h.update(c)
    return h.hexdigest()


def semantic_md5(p):
    """文本文件：忽略只读横幅行；二进制文件退回 raw md5。"""
    try:
        with open(p, 'r', encoding='utf-8') as f:
            body = ''.join(l for l in f if not l.startswith(BANNER_PREFIX))
    except (UnicodeDecodeError, OSError):
        return md5(p)
    return hashlib.md5(body.encode('utf-8')).hexdigest()


def snapshot(root, skip_names=()):
    """源与副本都用这一个函数算快照 —— 口径必须一致（坑 #3）。"""
    out = {}
    for r, dirs, fs in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in fs:
            if f.endswith(SKIP_SUFFIX) or f == MANIFEST or f in skip_names:
                continue
            p = os.path.join(r, f)
            out[os.path.relpath(p, root).replace('\\', '/')] = semantic_md5(p)
    return out


def load_manifest(src):
    p = os.path.join(src, MANIFEST)
    if os.path.isfile(p):
        try:
            return json.load(open(p, encoding='utf-8')).get('files', {})
        except (ValueError, OSError):
            print(f'⚠️  manifest 损坏，忽略：{p}')
    return {}


def save_manifest(src, snap):
    json.dump({'version': 1, 'last_sync': time.strftime('%Y-%m-%d %H:%M:%S'),
               'files': snap},
              open(os.path.join(src, MANIFEST), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1, sort_keys=True)


def inject_banner(dst):
    for sub in BANNER_DIRS:
        d = os.path.join(dst, sub)
        if not os.path.isdir(d):
            continue
        for r, _, fs in os.walk(d):
            for f in fs:
                if not f.endswith('.md'):
                    continue
                p = os.path.join(r, f)
                body = open(p, encoding='utf-8').read()
                if body.startswith(BANNER_PREFIX):
                    continue
                lines = body.split('\n')
                if lines and lines[0].startswith('#'):
                    # 只插一行、不额外加空行（坑 #4）
                    body = lines[0] + '\n' + BANNER_TEXT + '\n'.join(lines[1:])
                else:
                    body = BANNER_TEXT + body
                open(p, 'w', encoding='utf-8').write(body)
    open(os.path.join(dst, MARKER), 'w', encoding='utf-8').write(
        '# ⛔ 只读镜像\n\n本目录由同步脚本自动覆盖，请勿修改。源：%s\n' % SRC)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', default=SRC)
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--diff', action='store_true')
    ap.add_argument('--verify-only', action='store_true')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--skip-backup', action='store_true')
    ap.add_argument('--rebuild-baseline', action='store_true')
    a = ap.parse_args()

    src = os.path.abspath(a.src)
    if not os.path.isdir(src):
        print(f'❌ 源不存在: {src}'); return 1
    for req in REQUIRED:
        if not os.path.isfile(os.path.join(src, req)):
            print(f'❌ 源缺少必需文件: {req}（先修源再同步）'); return 1

    src_snap = snapshot(src)
    prev = {} if a.rebuild_baseline else load_manifest(src)
    ts = time.strftime('%Y%m%d_%H%M%S')
    dests = {n: os.path.join(DEST_BASE, n, DEST_REL) for n in NAMES}

    if a.verify_only:
        bad = 0
        for n, d in dests.items():
            if not os.path.isdir(d):
                print(f'  ❌ {n}: 副本缺失'); bad += 1; continue
            cur = snapshot(d, skip_names={MARKER})
            miss = sorted(set(src_snap) - set(cur)); extra = sorted(set(cur) - set(src_snap))
            diff = sorted(k for k in src_snap if k in cur and cur[k] != src_snap[k])
            if miss or extra or diff:
                bad += 1
                print(f'  ❌ {n}: miss={len(miss)} extra={len(extra)} diff={len(diff)} → {(miss+diff+extra)[:3]}')
            else:
                print(f'  ✅ {n}: {len(cur)}/{len(src_snap)} 一致')
        print('✅ verify-only 全部通过' if not bad else f'❌ 失败 {bad} 个')
        return 0 if not bad else 1

    first_sync = not prev
    if first_sync and NAMES:
        print('ℹ️  无同步基线 ⇒ 按「首次镜像」处理，不做 DRIFT 拦截（坑 #1）')
    copied = unchanged = drifted = skipped = 0
    for n, d in dests.items():
        if os.path.isdir(d):
            cur = snapshot(d, skip_names={MARKER})
            drift = [k for k, v in cur.items() if prev.get(k) not in (None, v)] if prev else []
            if drift and not first_sync:
                drifted += 1
                if not a.force:
                    skipped += 1
                    print(f'🛑 {n}: DRIFT 拒绝覆盖 → {len(drift)} 个文件被改过（{drift[:3]}）')
                    continue
                print(f'⚠️  {n}: 覆盖副本侧 DRIFT（{len(drift)} 个文件）')
            if not drift and cur == src_snap:
                unchanged += 1
                print(f'· {n}: unchanged（已与源一致，跳过）')   # 幂等
                continue
        if a.dry_run:
            print(f'• {n}: would-copy {len(src_snap)} files'); copied += 1; continue
        if os.path.isdir(d) and not a.skip_backup:
            b = os.path.join(BACKUP_ROOT, ts, n)
            os.makedirs(os.path.dirname(b), exist_ok=True)
            shutil.copytree(d, b)                                # 覆盖前必备份（坑 #5）
        if os.path.exists(d):
            shutil.rmtree(d)
        shutil.copytree(src, d)
        for junk in (os.path.join(d, MANIFEST), os.path.join(d, '__pycache__')):
            shutil.rmtree(junk, ignore_errors=True) if os.path.isdir(junk) else (os.remove(junk) if os.path.isfile(junk) else None)
        inject_banner(d)
        copied += 1
        print(f'✅ {n}: 已同步')

    if a.dry_run:
        print(f'\n[dry-run] would-copy={copied} unchanged={unchanged}（未写入任何文件）')
        return 0
    if skipped == 0:
        save_manifest(src, src_snap)                             # 只有全绿才落基线（坑 #2）
        print(f'\n✅ 基线已更新（{len(src_snap)} 个文件）')
    else:
        print(f'\n⚠️  有 {skipped} 个副本被 DRIFT 拦截 ⇒ **不更新基线**')
    print(f'完成：同步 {copied} · unchanged {unchanged} · DRIFT {drifted} · 跳过 {skipped}')
    print(f'备份目录：{os.path.join(BACKUP_ROOT, ts)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
