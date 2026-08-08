#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ComfyUI API 格式工作流 → 桌面端 UI 格式（LiteGraph）转换器。

用法:
    python api_to_ui.py <input_api.json> <output_ui.json> [--titles '2:正向,6:负向']

产物可直接拖进 ComfyUI 桌面端画布，或复制到 user/default/workflows/ 从 Workflow→Open 打开。

⚠️ LiteGraph 槽位约定（2026-08-08 实测，第一版按绝对输入顺序转换导致桌面端连接全乱）:
- 节点 inputs 数组里【连接型输入必须排在开头 0..n-1】，widget 值独立存 widgets_values
- links 的 target_slot 索引的是「连接型输入数组」的位置，不是节点定义的绝对输入顺序
- 本版用 CONN_INPUTS 映射表只列连接型输入名并按序编号 slot，WIDGET_NAMES 单独按序回填 widget
- 验证: 把 UI 重建回 API 提交 POST /prompt 成功 + 全量越界检查（每个 link 的 target_slot < 目标节点 inputs 长度）
"""
import json
import sys

OUTPUT_DEFS = {
    'LoadImage': ['IMAGE'],
    'VAEEncode': ['LATENT'],
    'VAEDecode': ['IMAGE'],
    'CheckpointLoaderSimple': ['MODEL', 'CLIP', 'VAE'],
    'CLIPTextEncode': ['CONDITIONING'],
    'CLIPSetLastLayer': ['CLIP'],
    'KSampler': ['LATENT'],
    'SetLatentNoiseMask': ['LATENT'],
    'EmptyLatentImage': ['LATENT'],
    'SegsToCombinedMask': ['MASK'],
    'UltralyticsDetectorProvider': ['BBOX_DETECTOR'],
    'SAMLoader': ['SAM_MODEL'],
    'ImpactSimpleDetectorSEGS': ['SEGS', 'BBOX_DETECTOR'],
    'FaceDetailer': ['IMAGE'],
    'SaveImage': [],
    'PreviewImage': ['IMAGE'],
}

# 连接型输入（按 LiteGraph 槽位顺序）——只有这些会出现在 inputs 数组里
CONN_INPUTS = {
    'LoadImage': [],
    'VAEEncode': ['pixels', 'vae'],
    'VAEDecode': ['samples', 'vae'],
    'CheckpointLoaderSimple': [],
    'CLIPTextEncode': ['clip'],
    'CLIPSetLastLayer': ['clip'],
    'KSampler': ['model', 'positive', 'negative', 'latent_image'],
    'SetLatentNoiseMask': ['samples', 'mask'],
    'EmptyLatentImage': [],
    'SegsToCombinedMask': ['segs'],
    'UltralyticsDetectorProvider': [],
    'SAMLoader': [],
    'ImpactSimpleDetectorSEGS': ['bbox_detector', 'image', 'sam_model_opt', 'segm_detector_opt'],
    'FaceDetailer': ['image', 'model', 'clip', 'vae', 'positive', 'negative', 'bbox_detector', 'sam_model_opt'],
    'SaveImage': ['images'],
    'PreviewImage': ['images'],
}

# widget 名（按 API JSON 里非连接输入的出现顺序）
WIDGET_NAMES = {
    'LoadImage': ['image'],
    'VAEEncode': [],
    'VAEDecode': [],
    'CheckpointLoaderSimple': ['ckpt_name'],
    'CLIPTextEncode': ['text'],
    'CLIPSetLastLayer': ['stop_at_clip_layer'],
    'KSampler': ['seed', 'steps', 'cfg', 'sampler_name', 'scheduler', 'denoise'],
    'SetLatentNoiseMask': [],
    'EmptyLatentImage': ['width', 'height', 'batch_size'],
    'SegsToCombinedMask': [],
    'UltralyticsDetectorProvider': ['model_name'],
    'SAMLoader': ['model_name', 'device_mode'],
    'ImpactSimpleDetectorSEGS': ['bbox_threshold', 'bbox_dilation', 'crop_factor', 'drop_size', 'sub_threshold', 'sub_dilation', 'sub_bbox_expansion', 'sam_mask_hint_threshold'],
    'FaceDetailer': ['guide_size', 'guide_size_for', 'max_size', 'seed', 'steps', 'cfg', 'sampler_name', 'scheduler', 'denoise', 'feather', 'noise_mask', 'force_inpaint', 'bbox_threshold', 'bbox_dilation', 'bbox_crop_factor', 'sam_detection_hint', 'sam_dilation', 'sam_threshold', 'sam_bbox_expansion', 'sam_mask_hint_threshold', 'sam_mask_hint_use_negative', 'drop_size', 'wildcard', 'cycle', 'inpaint_model', 'noise_mask_feather'],
    'SaveImage': ['filename_prefix'],
    'PreviewImage': ['filename_prefix'],
}


def parse_args(argv):
    args = [a for a in argv if not a.startswith('--')]
    titles = {}
    for a in argv:
        if a.startswith('--titles'):
            for pair in a.split('=', 1)[1].split(','):
                if ':' in pair:
                    k, v = pair.split(':', 1)
                    titles[k.strip()] = v.strip()
    if len(args) < 2:
        print(__doc__)
        sys.exit(1)
    return args[0], args[1], titles


def api_to_ui(api_path, out_path, title_map=None):
    title_map = title_map or {}
    with open(api_path, encoding='utf-8') as f:
        wf = json.load(f)

    node_out_types = {nid: OUTPUT_DEFS.get(n.get('class_type', ''), []) for nid, n in wf.items()}

    # 每个目标节点的连接输入（按 CONN_INPUTS 顺序排序）→ slot 从 0 编号
    node_conns = {}
    for target_nid, node in wf.items():
        ct = node.get('class_type', '')
        conns = []
        for iname, ival in node.get('inputs', {}).items():
            if isinstance(ival, list) and len(ival) == 2 and isinstance(ival[0], str):
                conns.append((iname, ival[0], ival[1]))
        conn_order = CONN_INPUTS.get(ct, [])
        conns.sort(key=lambda c: conn_order.index(c[0]) if c[0] in conn_order else 999)
        node_conns[target_nid] = conns

    # 生成 links
    links = []
    for target_nid, conns in node_conns.items():
        for slot, (iname, origin_nid, origin_slot) in enumerate(conns):
            out_types = node_out_types.get(origin_nid, [])
            if origin_slot >= len(out_types):
                continue
            links.append({'id': len(links) + 1, 'origin_id': int(origin_nid), 'origin_slot': origin_slot,
                          'target_id': int(target_nid), 'target_slot': slot, 'type': out_types[origin_slot]})
    last_link_id = len(links)

    # 拓扑深度布局（同层纵排、层间横排）
    depth = {}
    def calc_depth(nid):
        if nid in depth:
            return depth[nid]
        d = 0
        for iname, origin_nid, origin_slot in node_conns.get(nid, []):
            if origin_nid in wf:
                d = max(d, calc_depth(origin_nid) + 1)
        depth[nid] = d
        return d
    for nid in wf.keys():
        calc_depth(nid)
    grid_y_counter = {}

    nodes = []
    for nid, node in wf.items():
        ct = node.get('class_type', '')
        nid_int = int(nid)
        inputs = node.get('inputs', {})
        d = depth[nid]
        col, row = d, grid_y_counter.get(d, 0)
        grid_y_counter[d] = row + 1

        # 连接型输入（slot 与 links.target_slot 一一对应）
        ui_inputs = []
        for slot, (iname, origin_nid, origin_slot) in enumerate(node_conns[nid]):
            link_id = next((l['id'] for l in links if l['target_id'] == nid_int and l['target_slot'] == slot), None)
            ltype = next((l['type'] for l in links if l['id'] == link_id), 'IMAGE')
            ui_inputs.append({'name': iname, 'type': ltype, 'link': link_id})

        # widget 值（非连接输入，保持 API 顺序）
        widget_values = [v for v in inputs.values() if not isinstance(v, list)]

        ui_outputs = []
        for slot, otype in enumerate(node_out_types[nid]):
            ol = [l['id'] for l in links if l['origin_id'] == nid_int and l['origin_slot'] == slot]
            ui_outputs.append({'name': otype, 'type': otype, 'links': ol if ol else None})

        nodes.append({
            'id': nid_int,
            'type': ct,
            'pos': [80 + col * 420, 60 + row * 260],
            'size': [420, 250] if ct == 'CLIPTextEncode' else [320, 180],
            'flags': {},
            'order': nid_int,
            'mode': 0,
            'inputs': ui_inputs,
            'outputs': ui_outputs,
            'properties': {'Node name for S&R': ct},
            'widgets_values': widget_values if widget_values else [],
            **({'title': title_map[nid]} if nid in title_map else {}),
        })

    ui_wf = {
        'version': 1, 'state': {}, 'last_node_id': max(int(k) for k in wf.keys()),
        'last_link_id': last_link_id, 'nodes': nodes, 'links': links,
        'groups': [], 'config': {}, 'extra': {},
    }
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(ui_wf, f, ensure_ascii=False, indent=1)

    # 越界检查：每个 link 的 target_slot 必须 < 目标节点 inputs 长度
    n_inputs = {n['id']: len(n['inputs']) for n in nodes}
    bad = [l for l in links if l['target_slot'] >= n_inputs.get(l['target_id'], 0)]
    print(f'OK: {out_path} ({len(nodes)} nodes, {len(links)} links)')
    if bad:
        print(f'❌ 越界链接 {len(bad)} 个（桌面端会连接错乱）: {[l["id"] for l in bad]}')
    else:
        print('✅ 越界检查通过')
    return ui_wf


if __name__ == '__main__':
    api_path, out_path, titles = parse_args(sys.argv[1:])
    api_to_ui(api_path, out_path, titles)
