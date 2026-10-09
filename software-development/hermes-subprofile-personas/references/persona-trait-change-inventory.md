# 取消/修改一个既有设定：全库盘点（v2 实战 2026-10 · Hebe「超大音量」项）

> 场景：主人命令「取消 XX 设定」（如「取消 Hebe 的音量巨大」）。
> 本文件是 `hermes-subprofile-personas` 的操作补充。核心教训：**一个「人格特征」往往不止存在于一处**，改之前必须全库 grep 关键词，否则改了 SOUL.md 却漏掉散落的镜像，档案就分叉了。

## 一、特征可能出现的 6 类位置（逐一 grep 关键词）

1. `profiles/<名>/SOUL.md` —— 人格权威（当前多为 slim 版，正文交给 lewd-playbook）
2. `profiles/<名>/config.yaml` —— SOUL 的 YAML 镜像
3. **根 `config.yaml` → `agent.personalities.<名>`** —— ⚠️ **最容易漏！**
   - default 档案的 `/personality` 特性里常存着该女仆的**整份全文镜像**（含色情模块），是一个 YAML 字面块标量（`|`，缩进 6 空格）。
   - 只改 SOUL 不改这里，切换人格时会读到旧设定。
4. 根 `skills/creative/lewd-playbook/references/` 下的散落引用：
   - `女仆专属/<名>.md`（专属机制章节）
   - `声音档案/<名>.md`（声线/情绪水位/台词库，通常改动量最大）
   - `词库/lexicon.md`（各女仆声音变体表一行）
   - `终局玩法/ultimate-moves.md`（Lv.10 大招台词）
   - **兄弟档案的交叉引用**（如 `女仆专属/dionysus.md` 里「× Hebe 拼酒对决」一行）
   - `面板存档/maids/<名>.md`（「专属机制」当前态字段）
5. 8 个子档案的 lewd-playbook 副本（`sync_to_profiles.py` 单向镜像，改完统一跑同步）
6. 长期 memory（`lewd-playbook` / 「女仆家族」摘要条目）

## 二、处理规则（主人钦定）

- **现役设定 vs 历史记录**：只改「今后的设定」；**历史事件不改写**——
  `面板存档/continuity.md` 的「第一次」、`story-log.md` 一行、`maids/<名>.md` 里的 **备注追加X/X** 都是已发生的事，保持原样（改写＝篡改档案）。
  改动处留一句溯源（如「原 X 项已按主人令取消」）便于日后核对。
- **先草案后执行**：先给出「清单(哪些文件) + 每处 before→after + 历史保留项 + 一个待决问题」的草案，主人回「①/②」再动手。
- **留空 vs 替换**：主人说「取消 X」时默认＝删除该特征、不再单列；是否补一个新特征要**问过主人**，不要自作主张改成正向/反向新设定。

## 三、config.yaml（根镜像）的安全改法

- 人物块是 YAML 字面块标量（`|`），缩进 6 空格；删除一小节用**原始文本 replace** 即可。
- **不要** `yaml.safe_load` + `yaml.dump` 整文件回写——会重排/丢结构，两千行的大配置风险高。
- 改前 `shutil.copy2` 备份：`config.yaml.bak-pre-<改动>-<时间戳>`。
- 改后验证：`python -c "import yaml; yaml.safe_load(open('config.yaml',encoding='utf-8'))"` 确认仍能解析；并断言旧特征字符串 `not in` 新文本、其后一节（如「连战无限」）仍在。
- 示例（删除 Hebe 块的「## 超大音量反应」小节）：
  ```python
  old = "      ## 超大音量反应 🆕\n      - 元气系的特点——反应超大，声音压不住\n      - 「…」\n      - …\n\n"
  t = t.replace(old, "", 1)   # 注意 6 空格缩进 + 尾部空行
  ```

## 四、Windows 编辑坑：CRLF 与 patch 工具

- 面板 md 可能是 **CRLF**；`patch` 工具的多行 `old_string` 用 `\n` 会**匹配失败**（单行锚点通常仍可）。
  - 实测：`maids/Hermes.md` 多行 patch 失败、单行成功；`maids/Iris.md`（同批）多行却成功 → 换行符不统一。
- 稳妥做法（`execute_code` 里 Python）：
  ```python
  t = p.read_text(encoding="utf-8")
  nl = "\r\n" if "\r\n" in t else "\n"
  t = t.replace("\r\n", "\n")
  for old, new, label in pairs:
      if old in t: t = t.replace(old, new, 1); print("✔", label)
      else: print("✘ MISS", label)
  with open(p, "w", encoding="utf-8", newline="") as f:
      f.write(t.replace("\n", nl))   # 按原文换行符还原
  ```
  批量多处替换用这一招最稳，还能逐条打印 ✔/✘ 便于核对。

## 五、收尾动作（一条不落）

1. 改完全部现役位置 + 根 config.yaml
2. `python skills/creative/lewd-playbook/scripts/sync_to_profiles.py`（应 DRIFT 0）
3. `python skills/creative/lewd-playbook/scripts/verify_panels.py`（应 PASS）
4. memory 更新一句（memory 常接近上限，条目要短；超限时报错会给出当前条目清单，用 replace 合并/删旧腾地方后再 add）

## 六、本次实录（可作模板）

- 目标：取消 Hebe「音量巨大」→ 留空版（现为「亮、脆、元气、笑声多」，音量默认）。
- 命中：`女仆专属/hebe.md`（音色/破功标记/整节「超大音量反应」）、`声音档案/hebe.md`（9 处）、`词库/lexicon.md`、`终局玩法/ultimate-moves.md`、`女仆专属/dionysus.md`、`面板存档/maids/hebe.md`、根 `config.yaml`；共 7 处现役。
- 保留：`continuity.md`、`story-log.md`、`maids/hebe.md` 历史备注。
- 结果：sync DRIFT 0 / verify PASS；`profiles/hebe/SOUL.md` 本就干净（v1.0 slim）无需改。
