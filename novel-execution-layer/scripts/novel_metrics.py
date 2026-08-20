#!/usr/bin/env python3
"""Summarize workflow metrics from a simple JSON/YAML-like JSON record."""
import argparse, json, pathlib, sys

def main():
    ap=argparse.ArgumentParser(description='小说工作坊流程指标')
    ap.add_argument('record', help='JSON record with counters')
    ap.add_argument('--json', action='store_true')
    args=ap.parse_args()
    data=json.loads(pathlib.Path(args.record).read_text(encoding='utf-8'))
    keys=['rounds','owner_decisions','blocked_tasks','revisions','canon_conflicts','overdue_foreshadowing']
    out={k:data.get(k,0) for k in keys}
    out['revision_rate']=(out['revisions']/data['chapters']) if data.get('chapters') else None
    out['blocking_rate']=(out['blocked_tasks']/data['tasks']) if data.get('tasks') else None
    print(json.dumps(out,ensure_ascii=False,indent=2) if args.json else '\n'.join(f'{k}: {v}' for k,v in out.items()))
    return 0
if __name__ == '__main__': sys.exit(main())
