#!/usr/bin/env python3
"""同步 lewd-playbook skill 到全部子档案（profiles/<name>/skills/）。

背景：子档案会话只扫描自己的 skills 目录（profiles/<name>/skills/），
看不到根级 skills。改根级 lewd-playbook 后必须跑本脚本同步，
否则子档案会话加载的是旧副本。

用法：python sync_to_profiles.py [--src 根级skill路径]
"""
import shutil, os, sys

SRC = r'C:\Users\80704\AppData\Local\hermes\skills\creative\lewd-playbook'
PROFILES_BASE = r'C:\Users\80704\AppData\Local\hermes\profiles'
NAMES = ['aphrodite', 'ares', 'artemis', 'athena', 'dionysus', 'hebe', 'hypnos', 'nemesis']

def main():
    src = SRC
    if '--src' in sys.argv:
        src = sys.argv[sys.argv.index('--src') + 1]
    if not os.path.isdir(src):
        print(f'❌ 源不存在: {src}')
        sys.exit(1)
    for name in NAMES:
        dst = os.path.join(PROFILES_BASE, name, 'skills', 'creative', 'lewd-playbook')
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print(f'✅ {name}: 已同步')
    print('全部完成')

if __name__ == '__main__':
    main()
