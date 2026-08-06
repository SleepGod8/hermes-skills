"""
批量生成 + 手部质量检查裁剪工具（ComfyUI 本地 8189 端口）
用法:
  python batch_hand_screening.py <workflow_api.json> <seed1> [seed2] ... \
      [--node 5] [--prefix athena_maid_detailer_v2] \
      [--crop "0,0.35,0.55,0.72"] [--outdir E:\\Comfy-Desktop\\ComfyUI-Shared\\output]

说明:
- 每个 seed 深拷贝 workflow, 改主采样节点 seed（默认节点 5, --node 指定）;
  FaceDetailer 类节点同步改 seed
- 全部提交后轮询 /history 直到完成（长任务用 terminal background + notify_on_complete 跑）
- 完成后把最新 N 张输出裁剪手部区域, 缩小成 ~800px JPEG 供 vision 模型检查
- 手部裁剪框是构图相关的: 双手交叠身前在 x0~0.55, y0.35~0.72; 构图漂移后先整图定位再调
"""
import json, os, sys, time, argparse
import urllib.request
from PIL import Image

COMFY_URL = os.environ.get("COMFY_URL", "http://127.0.0.1:8189")


def submit(workflow, seed, client_id, sampler_node="5"):
    wf = json.loads(json.dumps(workflow))
    if sampler_node in wf:
        wf[sampler_node]["inputs"]["seed"] = seed
    for node in wf.values():
        if node.get("class_type") == "FaceDetailer" and "seed" in node.get("inputs", {}):
            node["inputs"]["seed"] = seed
    data = json.dumps({"prompt": wf, "client_id": client_id}).encode("utf-8")
    req = urllib.request.Request(f"{COMFY_URL}/prompt", data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))["prompt_id"]
    except urllib.error.HTTPError as e:
        print(f"seed {seed} 提交失败: HTTP {e.code}", e.read().decode()[:400], flush=True)
        return None


def wait_all(ids, timeout=1500):
    """轮询 /history/{pid} 的 status.completed; 返回未完成的 seed 列表"""
    remaining = {s: p for s, p in ids.items() if p}
    start = time.time()
    while remaining and time.time() - start < timeout:
        for seed, pid in list(remaining.items()):
            try:
                with urllib.request.urlopen(f"{COMFY_URL}/history/{pid}", timeout=8) as resp:
                    h = json.loads(resp.read().decode("utf-8"))
                if pid in h and h[pid].get("status", {}).get("completed"):
                    print(f"[{time.time()-start:.0f}s] seed {seed} DONE", flush=True)
                    remaining.pop(seed, None)
            except Exception:
                pass
        if remaining:
            time.sleep(15)
    return list(remaining.keys())


def crop_latest(output_dir, prefix, count, box, crop_dir):
    files = [f for f in os.listdir(output_dir) if f.startswith(prefix) and f.endswith(".png")]
    files.sort()
    newest = files[-count:]
    os.makedirs(crop_dir, exist_ok=True)
    for i, fn in enumerate(newest, 1):
        img = Image.open(os.path.join(output_dir, fn))
        w, h = img.size
        c = img.crop((int(w * box[0]), int(h * box[1]), int(w * box[2]), int(h * box[3])))
        c = c.resize((800, int(800 * c.height / c.width)), Image.LANCZOS).convert("RGB")
        out = os.path.join(crop_dir, f"check_{i}.jpg")
        c.save(out, quality=85)
        print(f"{fn} -> {out}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("workflow", help="API 格式 workflow JSON 路径")
    ap.add_argument("seeds", nargs="+", type=int)
    ap.add_argument("--node", default="5", help="主采样节点 id")
    ap.add_argument("--prefix", default="athena_maid_detailer_v2")
    ap.add_argument("--crop", default="0,0.35,0.55,0.72", help="手部裁剪框 x0,y0,x1,y1 (比例)")
    ap.add_argument("--outdir", default=r"E:\Comfy-Desktop\ComfyUI-Shared\output")
    args = ap.parse_args()

    with open(args.workflow, encoding="utf-8") as f:
        workflow = json.load(f)
    print(f"提交 {len(args.seeds)} 任务: {args.seeds}")
    ids = {s: submit(workflow, s, f"batch-{s}", args.node) for s in args.seeds}
    print("等待完成...")
    unfinished = wait_all(ids)
    print("未完成:", unfinished or "无")
    crop_latest(args.outdir, args.prefix, len(args.seeds),
                tuple(map(float, args.crop.split(","))),
                os.path.join(os.path.dirname(os.path.abspath(args.workflow)), "crops"))


if __name__ == "__main__":
    main()
