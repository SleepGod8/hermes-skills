#!/usr/bin/env python3
"""Check a draft against explicit canon rules.

Rules JSON shape:
{"forbidden_claims": ["..."], "required_terms": ["..."]}
This is a narrow guard, not an LLM consistency judge.
"""
import argparse, json, pathlib, re, sys

def main():
    ap = argparse.ArgumentParser(description="正典边界检查")
    ap.add_argument("drafts", nargs="+", help="正文或报告文件")
    ap.add_argument("--rules", required=True, help="规则 JSON")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    rules = json.loads(pathlib.Path(args.rules).read_text(encoding="utf-8"))
    forbidden = rules.get("forbidden_claims", [])
    required = rules.get("required_terms", [])
    results=[]
    for name in args.drafts:
        text=pathlib.Path(name).read_text(encoding="utf-8")
        hits=[x for x in forbidden if x and x in text]
        missing=[x for x in required if x and x not in text]
        results.append({"file":name,"forbidden_hits":hits,"missing_required_terms":missing,"ok":not hits and not missing})
    out={"ok":all(x["ok"] for x in results),"files":results,"scope":"explicit rules only"}
    print(json.dumps(out,ensure_ascii=False,indent=2) if args.json else ("PASS" if out["ok"] else "FAIL") + "\\n" + "\\n".join(f"{x['file']}: forbidden={len(x['forbidden_hits'])}, missing={len(x['missing_required_terms'])}" for x in results))
    return 0 if out["ok"] else 1
if __name__ == "__main__": sys.exit(main())
