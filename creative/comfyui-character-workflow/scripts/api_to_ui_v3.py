#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
v3: 最终修复 — API 格式 → 桌面端 UI 格式转换
前端 FaceDetailer widgets 数组实际为 29 个（含 control_after_generate 与 tiled_encode/tiled_decode）。
widgets_values 必须按【前端实际生成顺序】排列（浏览器 console: LiteGraph.createNode('FaceDetailer')
读 node.widgets[i].name 是唯一权威来源），缺失 control_after_generate/tiled_* 会导致整体错位、
桌面端报 47 个「输入超出范围/无效输入/类型错误」。
"""
import json

def api_to_ui(api_path, out_path, title_map=None):
    with open(api_path, encoding='utf-8') as f:
        wf = json.load(f)

    title_map = title_map or {}
    nodes = []
    links = []
    next_link_id = 1

    OUTPUT_DEFS = {
        'LoadImage': ['IMAGE'], 'VAEEncode': ['LATENT'],
        'CheckpointLoaderSimple': ['MODEL', 'CLIP', 'VAE'],
        'CLIPTextEncode': ['CONDITIONING'], 'VAEDecode': ['IMAGE'],
        'KSampler': ['LATENT'], 'SetLatentNoiseMask': ['LATENT'],
        'SegsToCombinedMask': ['MASK'],
        'UltralyticsDetectorProvider': ['BBOX_DETECTOR'],
        'SAMLoader': ['SAM_MODEL'],
        'ImpactSimpleDetectorSEGS': ['SEGS', 'BBOX_DETECTOR'],
        'FaceDetailer': ['IMAGE'], 'EmptyLatentImage': ['LATENT'],
        'PreviewImage': [], 'SaveImage': [],
    }

    # ⭐ 前端实际 widget 顺序（含 control_after_generate / tiled_*）
    WIDGET_ORDER = {
        'CheckpointLoaderSimple': ['ckpt_name'],
        'CLIPTextEncode': ['text'],
        'EmptyLatentImage': ['width', 'height', 'batch_size'],
        'KSampler': ['seed', 'control_after_generate', 'steps', 'cfg', 'sampler_name', 'scheduler', 'denoise'],
        'VAEDecode': [],
        'UltralyticsDetectorProvider': ['model_name'],
        'SAMLoader': ['model_name', 'device_mode'],
        'FaceDetailer': ['guide_size', 'guide_size_for', 'max_size', 'seed', 'control_after_generate',
                          'steps', 'cfg', 'sampler_name', 'scheduler', 'denoise', 'feather',
                          'noise_mask', 'force_inpaint', 'bbox_threshold', 'bbox_dilation',
                          'bbox_crop_factor', 'sam_detection_hint', 'sam_dilation', 'sam_threshold',
                          'sam_bbox_expansion', 'sam_mask_hint_threshold',
                          'sam_mask_hint_use_negative', 'drop_size', 'wildcard', 'cycle',
                          'inpaint_model', 'noise_mask_feather', 'tiled_encode', 'tiled_decode'],
        'PreviewImage': [],
        'SaveImage': ['filename_prefix'],
        'LoadImage': ['image'],
        'VAEEncode': [],
        'SetLatentNoiseMask': [],
        'SegsToCombinedMask': [],
        'ImpactSimpleDetectorSEGS': ['bbox_threshold', 'bbox_dilation', 'crop_factor', 'drop_size',
                                      'sub_threshold', 'sub_dilation', 'sub_bbox_expansion',
                                      'sam_mask_hint_threshold'],
    }
    CONTROL_AFTER = {'seed': 'randomize'}

    # 连接型输入（按前端定义顺序；连接型输入排在 inputs 数组开头 0..n-1）
    CONN_INPUTS = {
        'CheckpointLoaderSimple': [],
        'CLIPTextEncode': ['clip'],
        'EmptyLatentImage': [],
        'KSampler': ['model', 'positive', 'negative', 'latent_image'],
        'VAEDecode': ['samples', 'vae'],
        'UltralyticsDetectorProvider': [],
        'SAMLoader': [],
        'FaceDetailer': ['image', 'model', 'clip', 'vae', 'positive', 'negative', 'bbox_detector', 'sam_model_opt'],
        'PreviewImage': ['images'],
        'SaveImage': ['images'],
        'LoadImage': [],
        'VAEEncode': ['pixels', 'vae'],
        'SetLatentNoiseMask': ['samples', 'mask'],
        'SegsToCombinedMask': ['segs'],
        'ImpactSimpleDetectorSEGS': ['bbox_detector', 'image', 'sam_model_opt', 'segm_detector_opt'],
    }

    node_out_types = {nid: OUTPUT_DEFS.get(node.get('class_type',''), []) for nid, node in wf.items()}

    link_records = []
    node_links_in = {}
    for target_nid, node in wf.items():
        conns = []
        for iname, ival in node.get('inputs', {}).items():
            if isinstance(ival, list) and len(ival) == 2 and isinstance(ival[0], str):
                conns.append((iname, ival[0], ival[1]))
        conn_order = CONN_INPUTS.get(node.get('class_type',''), [])
        conns_sorted = sorted(conns, key=lambda c: conn_order.index(c[0]) if c[0] in conn_order else 999)
        node_links_in[target_nid] = conns_sorted
        for slot, (iname, origin_nid, origin_slot) in enumerate(conns_sorted):
            if origin_nid not in node_out_types:
                continue
            out_types = node_out_types[origin_nid]
            if origin_slot >= len(out_types):
                continue
            link_records.append((origin_nid, origin_slot, target_nid, slot, out_types[origin_slot], iname))

    for rec in link_records:
        links.append({
            'id': next_link_id,
            'origin_id': int(rec[0]), 'origin_slot': rec[1],
            'target_id': int(rec[2]), 'target_slot': rec[3], 'type': rec[4],
        })
        next_link_id += 1

    # 深度拓扑布局
    depth = {}
    def calc_depth(nid):
        if nid in depth:
            return depth[nid]
        d = 0
        for iname, origin_nid, origin_slot in node_links_in.get(nid, []):
            if origin_nid in wf:
                d = max(d, calc_depth(origin_nid) + 1)
        depth[nid] = d
        return d
    for nid in wf.keys():
        calc_depth(nid)

    grid_y_counter = {}
    for nid, node in wf.items():
        ct = node.get('class_type', '')
        inputs = node.get('inputs', {})
        nid_int = int(nid)
        d = depth[nid]
        col = d
        row = grid_y_counter.get(col, 0)
        grid_y_counter[col] = row + 1
        pos = [80 + col * 420, 60 + row * 260]
        node_size = [420, 250] if ct == 'CLIPTextEncode' else [340, 200]

        conns = node_links_in[nid]
        ui_inputs = []
        for slot, (iname, origin_nid, origin_slot) in enumerate(conns):
            link_id = None
            ltype = 'IMAGE'
            for l in links:
                if l['target_id'] == nid_int and l['target_slot'] == slot:
                    link_id = l['id']
                    ltype = l['type']
                    break
            ui_inputs.append({'name': iname, 'type': ltype, 'link': link_id})

        # ⭐ widgets_values 按前端顺序
        widget_order = WIDGET_ORDER.get(ct, [])
        widget_values = []
        for wname in widget_order:
            if wname == 'control_after_generate':
                widget_values.append(CONTROL_AFTER.get('seed', 'randomize'))
            elif wname in ('tiled_encode', 'tiled_decode'):
                widget_values.append(False)
            elif wname in inputs and not isinstance(inputs[wname], list):
                widget_values.append(inputs[wname])
            else:
                widget_values.append(None)

        out_types = node_out_types[nid]
        ui_outputs = []
        for slot, otype in enumerate(out_types):
            ol = [l['id'] for l in links if l['origin_id'] == nid_int and l['origin_slot'] == slot]
            ui_outputs.append({'name': otype, 'type': otype, 'links': ol if ol else None})

        node_obj = {
            'id': nid_int, 'type': ct, 'pos': pos, 'size': node_size,
            'flags': {}, 'order': nid_int, 'mode': 0,
            'inputs': ui_inputs, 'outputs': ui_outputs,
            'properties': {'Node name for S&R': ct},
            'widgets_values': widget_values if widget_values else [],
        }
        if nid in title_map:
            node_obj['title'] = title_map[nid]
        nodes.append(node_obj)

    ui_wf = {
        'version': 1, 'state': {},
        'last_node_id': max(int(k) for k in wf.keys()),
        'last_link_id': next_link_id - 1,
        'nodes': nodes, 'links': links,
        'groups': [], 'config': {}, 'extra': {},
    }
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(ui_wf, f, ensure_ascii=False, indent=1)
    print(f'OK {out_path} ({len(nodes)} nodes, {len(links)} links)')
    return ui_wf

if __name__ == '__main__':
    import sys
    src = sys.argv[1] if len(sys.argv) > 1 else r'E:/ai1/comfyui_workflow/iris_maid_detailer_api.json'
    dst = sys.argv[2] if len(sys.argv) > 2 else r'E:/ai1/comfyui_workflow/iris_maid_ui.json'
    api_to_ui(src, dst)
