#!/usr/bin/env python3
"""Audit foreshadowing registry for overdue/orphaned entries."""
import argparse, json, pathlib, sys

def main():
    ap=argparse.ArgumentParser(description="伏笔状态审计")
    ap.add_argument("registry", help="JSON registry")
    ap.add_argument("--json", action="store_true")
    args=ap.parse_args()
    data=json.loads(pathlib.Path(args.registry).read_text(encoding="utf-8"))
    entries=data.get("foreshadowing", data if isinstance(data,list) else [])
    bad=[]
    for item in entries:
        status=item.get("status", "")
        if status in {"overdue", "orphaned"} or not item.get("id"):
            bad.append(item)
    out={"ok":not bad,"total":len(entries),"issues":bad}
    print(json.dumps(out,ensure_ascii=False,indent=2) if args.json else (f"PASS: {len(entries)} entries" if out["ok"] else f"FAIL: {len(bad)} issues / {len(entries)} entries"))
    return 0 if out["ok"] else 1
if __name__ == "__main__": sys.exit(main())
