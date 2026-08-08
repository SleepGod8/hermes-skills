#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ComfyUI API 格式工作流 → 桌面端 UI 格式（LiteGraph）转换器。

用法:
    python api_to_ui.py <input_api.json> <output_ui.json> [--titles '2:正向,6:负向']

产物可直接拖进 ComfyUI 桌面端画布，或复制到 user/default/workflows/ 从 Workflow→Open 打开。

关键点:
- 每个 class_type 的输出/输入端口名靠硬编码映射表还原（API 引用是 [node_id, slot]）
- widgets_values 必须是有值数组，None 会让前端加载异常 -> 统一改 []
- 验证: 把 UI 重建回 API 提交 POST /prompt, 成功即桌面端可用
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
INPUT_DEFS = {
    'LoadImage': ['image'],
    'VAEEncode': ['pixels', 'vae'],
    'VAEDecode': ['samples', 'vae'],
    'CheckpointLoaderSimple': ['ckpt_name'],
    'CLIPTextEncode': ['text', 'clip'],
    'CLIPSetLastLayer': ['stop_at_clip_layer', 'clip'],
    'KSampler': ['seed', 'steps', 'cfg', 'sampler_name', 'scheduler', 'denoise', 'model', 'positive', 'negative', 'latent_image'],
    'SetLatentNoiseMask': ['samples', 'mask'],
    'EmptyLatentImage': ['width', 'height', 'batch_size'],
    'SegsToCombinedMask': ['segs'],
    'UltralyticsDetectorProvider': ['model_name'],
    'SAMLoader': ['model_name', 'device_mode'],
    'ImpactSimpleDetectorSEGS': ['bbox_threshold', 'bbox_dilation', 'crop_factor', 'drop_size', 'sub_threshold', 'sub_dilation', 'sub_bbox_expansion', 'sam_mask_hint_threshold', 'bbox_detector', 'image', 'sam_model_opt', 'segm_detector_opt'],
    'FaceDetailer': ['guide_size', 'guide_size_for', 'max_size', 'seed', 'steps', 'cfg', 'sampler_name', 'scheduler', 'denoise', 'feather', 'noise_mask', 'force_inpaint', 'bbox_threshold', 'bbox_dilation', 'bbox_crop_factor', 'sam_detection_hint', 'sam_dilation', 'sam_threshold', 'sam_bbox_expansion', 'sam_mask_hint_threshold', 'sam_mask_hint_use_negative', 'drop_size', 'bbox_detector', 'wildcard', 'cycle', 'image', 'model', 'clip', 'vae', 'positive', 'negative', 'sam_model_opt', 'segm_detector_opt', 'inpaint_model', 'noise_mask_feather'],
    'SaveImage': ['filename_prefix', 'images'],
    'PreviewImage': ['images'],
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

    # node_id -> 输出端口类型
    node_out_types = {nid: OUTPUT_DEFS.get(n.get('class_type', ''), []) for nid, n in wf.items()}

    # 收集链接: (origin_nid, origin_slot, target_nid, target_slot, type)
    link_records = []
    for target_nid, node in wf.items():
        ct = node.get('class_type', '')
        t_inputs = INPUT_DEFS.get(ct, [])
        for iname, ival in node.get('inputs', {}).items():
            if isinstance(ival, list) and len(ival) == 2 and isinstance(ival[0], str):
                origin_nid, origin_slot = ival[0], ival[1]
                out_types = node_out_types.get(origin_nid, [])
                if origin_slot >= len(out_types):
                    continue
                try:
                    target_slot = t_inputs.index(iname)
                except ValueError:
                    continue
                link_records.append((origin_nid, origin_slot, target_nid, target_slot, out_types[origin_slot]))

    links = []
    for i, rec in enumerate(link_records, start=1):
        links.append({'id': i, 'origin_id': int(rec[0]), 'origin_slot': rec[1],
                      'target_id': int(rec[2]), 'target_slot': rec[3], 'type': rec[4]})
    last_link_id = len(links)

    nodes = []
    for order, (nid, node) in enumerate(wf.items()):
        ct = node.get('class_type', '')
        nid_int = int(nid)
        inputs = node.get('inputs', {})

        # 连接型输入
        ui_inputs = []
        for iname, ival in inputs.items():
            if isinstance(ival, list):
                slot = len(ui_inputs)
                link_id = next((l['id'] for l in links if l['target_id'] == nid_int and l['target_slot'] == slot), None)
                ui_inputs.append({'name': iname, 'type': INPUT_DEFS.get(ct, [])[slot] if slot < len(INPUT_DEFS.get(ct, [])) else '*', 'link': link_id})

        # widget 值（非连接输入，保持 API 顺序）
        widget_values = [v for v in inputs.values() if not isinstance(v, list)]

        # 输出端口
        ui_outputs = []
        for slot, otype in enumerate(node_out_types[nid]):
            ol = [l['id'] for l in links if l['origin_id'] == nid_int and l['origin_slot'] == slot]
            ui_outputs.append({'name': otype, 'type': otype, 'links': ol if ol else None})

        col, row = order // 3, order % 3
        nodes.append({
            'id': nid_int,
            'type': ct,
            'pos': [50 + col * 480, 50 + row * 320],
            'size': [400, 250] if ct == 'CLIPTextEncode' else [280, 150],
            'flags': {},
            'order': order + 1,
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
    print(f'OK: {out_path} ({len(nodes)} nodes, {len(links)} links)')
    return ui_wf


if __name__ == '__main__':
    api_path, out_path, titles = parse_args(sys.argv[1:])
    api_to_ui(api_path, out_path, titles)
