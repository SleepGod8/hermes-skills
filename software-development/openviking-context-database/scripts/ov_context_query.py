#!/usr/bin/env python
"""Query local Docker OpenViking and read back top context snippets.

Designed for the user's Windows Hermes setup where OpenViking runs in the
`openviking` Docker container and the container has `/app/.venv/bin/ov`.
It never prints API keys; it shells into the existing container and uses
`/app/.openviking/ovcli.conf`.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Any


DEFAULT_URI = "viking://resources"
DEFAULT_CONTAINER = "openviking"


@dataclass
class OvResult:
    args: list[str]
    returncode: int
    stdout: str
    stderr: str
    json_data: Any | None


def strip_ov_prefix(text: str) -> str:
    """ov sometimes emits `cmd: ...` before JSON. Strip to first JSON char."""
    if not text:
        return text
    starts = [i for i in (text.find("{"), text.find("[")) if i >= 0]
    if not starts:
        return text
    return text[min(starts):]


def run_ov(args: list[str], *, container: str, timeout: int) -> OvResult:
    cmd = [
        "docker",
        "exec",
        container,
        "sh",
        "-lc",
        "export PATH=/app/.venv/bin:$PATH; ov "
        + " ".join(shell_quote(a) for a in args),
    ]
    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
    raw = proc.stdout.strip()
    data = None
    if raw:
        try:
            data = json.loads(strip_ov_prefix(raw))
        except Exception:
            data = None
    return OvResult(args=args, returncode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr, json_data=data)


def shell_quote(s: str) -> str:
    return "'" + s.replace("'", "'\\''") + "'"


def get_resources(find_json: Any) -> list[dict[str, Any]]:
    result = (find_json or {}).get("result") or {}
    resources = result.get("resources") or []
    return resources if isinstance(resources, list) else []


def read_result_text(read_json: Any) -> str:
    if not isinstance(read_json, dict):
        return ""
    result = read_json.get("result")
    if result is None:
        return ""
    if isinstance(result, str):
        return result
    return json.dumps(result, ensure_ascii=False, indent=2)


def compact_text(text: str, max_chars: int) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "\n...[truncated]"


def grep_matches(grep_json: Any) -> list[dict[str, Any]]:
    result = (grep_json or {}).get("result") or {}
    matches = result.get("matches") if isinstance(result, dict) else None
    return matches if isinstance(matches, list) else []


def main() -> int:
    parser = argparse.ArgumentParser(description="OpenViking find/grep/read helper for Hermes.")
    parser.add_argument("query", nargs="?", help="Semantic query for `ov find`.")
    parser.add_argument("--uri", default=DEFAULT_URI, help=f"Search subtree URI. Default: {DEFAULT_URI}")
    parser.add_argument("-n", "--top", type=int, default=5, help="Number of find results to read. Default: 5")
    parser.add_argument("--read-chars", type=int, default=1800, help="Max chars per read snippet. Default: 1800")
    parser.add_argument("--grep", action="append", default=[], help="Exact grep term; may be repeated.")
    parser.add_argument("--grep-limit", type=int, default=8, help="Max matches per grep term. Default: 8")
    parser.add_argument("--container", default=DEFAULT_CONTAINER, help=f"Docker container name. Default: {DEFAULT_CONTAINER}")
    parser.add_argument("--timeout", type=int, default=180, help="Per ov command timeout seconds. Default: 180")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON instead of Markdown.")
    args = parser.parse_args()

    if not args.query and not args.grep:
        parser.error("provide a query and/or at least one --grep term")

    report: dict[str, Any] = {
        "uri": args.uri,
        "query": args.query,
        "grep_terms": args.grep,
        "find": None,
        "reads": [],
        "greps": [],
        "errors": [],
    }

    # Quick status check gives a clear error if the container/service is unavailable.
    status = run_ov(["status", "-o", "json"], container=args.container, timeout=args.timeout)
    if status.returncode != 0:
        report["errors"].append({"stage": "status", "stderr": status.stderr, "stdout": status.stdout})
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print("OpenViking status check failed. Is the Docker container running?", file=sys.stderr)
            print(status.stderr or status.stdout, file=sys.stderr)
        return 2

    if args.query:
        find_args = ["find", args.query, "-u", args.uri, "-n", str(args.top), "-o", "json"]
        found = run_ov(find_args, container=args.container, timeout=args.timeout)
        report["find"] = found.json_data
        if found.returncode != 0 or not isinstance(found.json_data, dict) or not found.json_data.get("ok"):
            report["errors"].append({"stage": "find", "stdout": found.stdout, "stderr": found.stderr})
        else:
            seen: set[str] = set()
            for item in get_resources(found.json_data)[: args.top]:
                uri = item.get("uri")
                if not uri or uri in seen:
                    continue
                seen.add(uri)
                rr = run_ov(["read", uri, "-o", "json"], container=args.container, timeout=args.timeout)
                text = read_result_text(rr.json_data)
                report["reads"].append(
                    {
                        "uri": uri,
                        "score": item.get("score"),
                        "tags": item.get("tags"),
                        "abstract": item.get("abstract"),
                        "ok": rr.returncode == 0 and bool(text),
                        "chars": len(text),
                        "text": compact_text(text, args.read_chars),
                        "stderr": rr.stderr.strip(),
                    }
                )

    for term in args.grep:
        gr = run_ov(["grep", term, "-u", args.uri, "-n", str(args.grep_limit), "-o", "json"], container=args.container, timeout=args.timeout)
        matches = grep_matches(gr.json_data)
        report["greps"].append({"term": term, "ok": gr.returncode == 0, "matches": matches[: args.grep_limit], "stderr": gr.stderr.strip()})

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if not report["errors"] else 1

    print(f"# OpenViking context query\n")
    print(f"URI: `{args.uri}`")
    if args.query:
        print(f"Query: {args.query}\n")
    if report["errors"]:
        print("## Errors")
        for err in report["errors"]:
            print(f"- {err['stage']}: {(err.get('stderr') or err.get('stdout') or '').strip()[:500]}")
        print()

    if report["greps"]:
        print("## Exact grep matches")
        for g in report["greps"]:
            print(f"### `{g['term']}`")
            if not g["matches"]:
                print("No matches.\n")
                continue
            for m in g["matches"]:
                print(f"- `{m.get('uri')}` line {m.get('line')}: {m.get('content')}")
            print()

    if report["reads"]:
        print("## Semantic find → read snippets")
        for i, r in enumerate(report["reads"], 1):
            score = r.get("score")
            score_s = f" score={score:.3f}" if isinstance(score, (int, float)) else ""
            print(f"### {i}. `{r['uri']}`{score_s}")
            if r.get("tags"):
                print(f"Tags: {', '.join(r['tags'])}")
            if r.get("abstract"):
                print(f"Abstract: {r['abstract']}")
            print("```markdown")
            print(r["text"])
            print("```\n")
    elif args.query:
        print("No readable semantic results.")

    return 0 if not report["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
