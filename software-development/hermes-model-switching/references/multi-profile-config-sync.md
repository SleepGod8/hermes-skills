# 多档案（子 profile）配置改写：`HERMES_PROFILE` 是陷阱（2026-10-24 实测）

## 何时看这份

要把某个配置键（模型、`auxiliary.vision`、fallback 链……）**同时应用到多个 Hermes profile** 时。
本机：`default` + `profiles/{athena,eos,hebe,aphrodite,dionysus,artemis,ares,nemesis,hypnos,openvikingtest}`。

## 一、先确认凭据是否共享

```bash
cd "$HOME/AppData/Local/hermes"
for p in default athena eos hebe; do
  f=".env"; [ "$p" != "default" ] && f="profiles/$p/.env"
  len=$(grep -m1 "^DEEPSEEK_API_KEY=" "$f" | sed 's/^DEEPSEEK_API_KEY=//' | tr -d '\r" ' | wc -c)
  echo "$p key_len=$((len-1))"
done
# 只比 md5，不打印密钥本体
md5sum .env profiles/hebe/.env
```

本机结果：所有档案 `DEEPSEEK_API_KEY` 键长 35、md5 完全一致 ⇒ 内置 provider（如 `deepseek`）在每个档案都能直接用，**不需要给子档案重建 custom provider 或复制 .env**。

## 二、❌ `HERMES_PROFILE` 不改变 config 落盘路径

```bash
HERMES_PROFILE=hebe hermes config set auxiliary.vision.provider deepseek
# ✓ Set ... in C:\Users\80704\AppData\Local\hermes\config.yaml   ← 写的是默认档案！
HERMES_PROFILE=hebe hermes config path   # 仍返回默认 config.yaml
HERMES_PROFILE=hebe hermes config get model  # 仍是默认档案的值
```

`HERMES_PROFILE` 只参与部分运行期逻辑。另外 `hermes profile use <name>` 是**粘性把某个档案设为全局默认**，不是「这一条命令作用于该档案」，别拿它做批量改配置。

## 三、✅ 正确姿势：逐档案导出 `HERMES_HOME`

```bash
export HERMES_HOME="C:/Users/80704/AppData/Local/hermes/profiles/hebe"
hermes config path                 # → ...\profiles\hebe\config.yaml
hermes config get model            # default: gpt-5.5 / provider: aslnet-plus ← 确认读对了
hermes config set auxiliary.vision.provider deepseek
hermes config set auxiliary.vision.model deepseek-v4-flash
hermes config set auxiliary.vision.fallback_chain '[{"provider":"custom:ZhipuGLM","model":"glm-4.6v-flash"}]' --force
```

注意：

- **路径必须是原生正斜杠** `C:/Users/...`。MSYS 风格 `$HOME/.../profiles/hebe` 会被拼成 `\c\Users\...`，`hermes config get` 返回空——看着像"成功"，其实配置没读到。
- 自定义键（如 `auxiliary.vision.fallback_chain`）会打印 `⚠ not a recognized config key — saved anyway`，加 `--force` 消警告；不加也会写入。
- 每条 `hermes config set` 有 2~4s 启动开销，批量时写成循环脚本，别手敲。

## 四、批量脚本

`scripts/sync_profile_config.py` 已封装：备份 → 逐档案设 `HERMES_HOME` → `config set` → YAML 读回 → 防呆校验「真的写进了本档案而不是默认档案」。

```bash
python scripts/sync_profile_config.py --key auxiliary.vision.provider --value deepseek
python scripts/sync_profile_config.py --key auxiliary.vision.model --value deepseek-v4-flash
python scripts/sync_profile_config.py --key auxiliary.vision.fallback_chain \
  --value '[{"provider":"custom:ZhipuGLM","model":"glm-4.6v-flash"},{"provider":"custom:DashScope","model":"qwen-vl-plus"}]' --force
# 只挑几个 / 先看
python scripts/sync_profile_config.py --key model.default --value deepseek-v4-flash --profiles athena,eos
python scripts/sync_profile_config.py --key auxiliary.vision.model --value x --dry-run
```

## 五、验证（不验证等于没配）

1. **读回全量**：用 yaml 遍历所有 profile，打印 `auxiliary.vision`，确认每个都是目标值。
2. **抽测端到端**（每类配置至少一个档案）：

```bash
export HERMES_HOME="C:/Users/80704/AppData/Local/hermes/profiles/hebe"
hermes chat -q "调用 vision_analyze 分析 <图路径>，只回答图中数字和汉字。" \
  -m deepseek-v4-pro --provider deepseek -Q
```

3. **查该档案自己的日志**：`profiles/<name>/logs/agent.log`（不是默认档案的 `logs/agent.log`），搜 session id 段的 `tool vision_analyze completed`，并确认没有 `rate limit … trying fallback`。

## 六、本机落地结果（2026-10-24）

10 个档案（default + 9 女仆）统一为 `auxiliary.vision = deepseek / deepseek-v4-flash`，
fallback `custom:ZhipuGLM/glm-4.6v-flash → custom:DashScope/qwen-vl-plus`。
`openvikingtest` 无 `auxiliary` 块（测试档案，未动）。
抽测 hebe(2.36s) / athena(4.64s) 均正确读出图中内容，无 fallback。
备份：各档案 `config.yaml.bak-vision-ds-<ts>`。

## 七、坑清单

- 别把「写成功」当「写对了」：`HERMES_PROFILE` 那条会返回 ✓，但写的是默认档案。
- 改配置前一律 `cp config.yaml config.yaml.bak-<tag>-$(date +%Y%m%d_%H%M%S)`，逐档案各一份。
- 子档案的日志/会话/记忆都在 `profiles/<name>/` 下，验证时别查错位置。
- 运行中的 Hermes 桌面/网关进程可能重写 config.yaml；改完读回验证，被覆盖就以进程写的为准，别反复打架。
