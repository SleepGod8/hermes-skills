#!/usr/bin/env python
"""Inspect a Hermes maid-profile SOUL.md / config.yaml line-ending structure before editing.

Why: profile SOUL.md files are CRLF, but sometimes DOUBLE-SPACED CRLF (a blank
`\r\n` line between every content line). Inserting a single-spaced module into a
double-spaced file produces inconsistent formatting; and `replace('\n','\r\n')`
on the wrong base produces the wrong variant entirely. Check bytes first.

Usage:
  python check_profile_soul.py <profile_name> [anchor_text]
    profile_name : folder under ~/AppData/Local/hermes/profiles/
                   ('default' reads the root ~/AppData/Local/hermes/SOUL.md)
    anchor_text  : optional substring counted in SOUL.md and config system_prompt

Example:
  python check_profile_soul.py dionysus "## 共通色情机制 🆕"
"""
import os
import sys

try:
    import yaml
except ImportError:
    yaml = None

HOME = os.path.expanduser('~')
HERMES = os.path.join(HOME, 'AppData', 'Local', 'hermes')
PROFILES = os.path.join(HERMES, 'profiles')


def line_stats(raw: bytes) -> dict:
    crlf = raw.count(b'\r\n')
    lf = raw.count(b'\n')
    crcrlf = raw.count(b'\r\r\n')
    lines = raw.split(b'\n')
    empties = sum(1 for ln in lines if ln in (b'', b'\r'))
    content = len(lines) - empties
    return {
        'crlf': crlf,
        'lf': lf,
        'crcrlf': crcrlf,
        'content_lines': content,
        'empty_lines': empties,
        'double_spaced_crlf': crlf == lf and crcrlf == 0 and empties >= content and content > 1,
    }


def find_system_prompt(cfg: dict) -> str:
    agent = cfg.get('agent', {})
    if isinstance(agent, dict) and 'system_prompt' in agent:
        return agent['system_prompt']
    if isinstance(agent, dict) and isinstance(agent.get('personalities'), dict):
        for v in agent['personalities'].values():
            if isinstance(v, dict) and 'system_prompt' in v:
                return v['system_prompt']
    return ''


def main() -> None:
    if len(sys.argv) < 2:
        print('usage: check_profile_soul.py <profile_name> [anchor_text]')
        return
    name = sys.argv[1]
    anchor = sys.argv[2] if len(sys.argv) > 2 else None

    if name == 'default':
        soul_p = os.path.join(HERMES, 'SOUL.md')
        cfg_p = os.path.join(HERMES, 'config.yaml')
    else:
        base = os.path.join(PROFILES, name)
        soul_p = os.path.join(base, 'SOUL.md')
        cfg_p = os.path.join(base, 'config.yaml')

    print(f'== {name} ==')
    print('SOUL.md:', soul_p, '| exists:', os.path.exists(soul_p))
    print('config  :', cfg_p, '| exists:', os.path.exists(cfg_p))

    if os.path.exists(soul_p):
        with open(soul_p, 'rb') as f:
            raw = f.read()
        st = line_stats(raw)
        print(f'SOUL bytes={len(raw)} CRLF={st["crlf"]} LF={st["lf"]} CRCRLF={st["crcrlf"]} '
              f'content={st["content_lines"]} empty={st["empty_lines"]} '
              f'DOUBLE-SPACED-CRLF={st["double_spaced_crlf"]}')
        print('first lines repr:', [repr(x) for x in raw.split(b'\n')[:4]])
        if anchor:
            with open(soul_p, encoding='utf-8', newline='') as f:
                text = f.read()
            print(f'SOUL anchor count={text.count(anchor)}')

    if os.path.exists(cfg_p) and yaml is not None:
        with open(cfg_p, encoding='utf-8') as f:
            cfg = yaml.safe_load(f)
        sp = find_system_prompt(cfg)
        print(f'config system_prompt len={len(sp)} first={sp.split(chr(10))[0]!r} '
              f'hasCRLF={"\\r\\n" in sp}')
        if anchor:
            print(f'cfg anchor count={sp.count(anchor)}')


if __name__ == '__main__':
    main()
