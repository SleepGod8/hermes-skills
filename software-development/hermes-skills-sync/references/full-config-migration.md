# Hermes 完整配置跨机迁移(含多 profile / 多 agent 协作 / 岗位说明)

把本机 Hermes 整套配置搬到另一台电脑,让新机的 Hermes 拥有和本机一样的
身份、记忆、技能、**多 profile 档案**和**多 agent 协作能力**。与 `hermes-skills-sync`
(只同步 skill 目录的持续增量)互补——本文件覆盖**一次性完整搬迁**。

## 配置分布(3 个位置,别漏)

| 位置 | 内容 | 必要度 |
|------|------|--------|
| `C:\Users\<你>\AppData\Local\hermes\` | **主目录**(config.yaml/.env/SOUL.md/skills/profiles/plugins/memories/cron/hooks) | ✅ 核心 |
| `...\hermes\state.db` | 会话历史数据库(本机约 129MB) | ⚠️ 可选(含历史) |
| `C:\Users\<你>\.hermes\` | 另一组 config.yaml/.env/SOUL.md/skills | ✅ 建议 |
| 系统环境变量 | PATH、HERMES_HOME、`HERMES_GIT_BASH_PATH`、`HERMES_WEB_UI_TOKEN`、各 API Key | ✅ 需手动 |

**判定 bind-mount 数据(非命名卷)**:Hermes 数据是普通文件目录,不用 docker,直接复制即可。

## 多 profile 档案(6 个子 agent)——整体迁移

每个 profile 是一个**独立完整的 Hermes 实例**(`profiles/<名>/`),包含:
- `config.yaml`(自己的模型/personality/平台)+ `config.yaml.bak`
- `SOUL.md`(人设:如 artemis/athena/hebe、eos=可爱女仆妹妹、iris=温柔女仆大姐姐、nemesis=雌小鬼女仆)
- `.env`(自己的密钥)+ `memories/` + `skills/` + `state.db`(各自会话历史)

**迁移 = 打包整个 `profiles/` 目录**,6 个档案的身份/人设/技能/记忆全部带走。

## 多 agent 协作机制 + 岗位说明在哪

主配置 `config.yaml` 承载协作核心(不在 profile 里):
| 配置段 | 作用 |
|--------|------|
| `agent.personalities.*` | **多套岗位/人格模板**(engineer=资深编码agent、kawaii、catgirl 等 17 种) |
| `agent.personality: <name>` | 默认工作人格(engineer) |
| `delegation` | 子代理任务分派(max_iterations 等) |
| `moa` | 多模型聚合(fanout + reference_models + aggregator) |
| `model` / `fallback_providers` | 主模型 + 降级链 |

**岗位说明** = 各 profile 的 `SOUL.md`(人设)+ 主 `config.yaml` 的 `agent.personalities`(编码岗位描述)。

## ⚠️ 唯一例外:群聊房间定义

群聊房间的成员关系、@ 配置**不**在 config.yaml 里(实测 grep group_chat/room 无命中),
存在 **Hermes Studio 桌面版的 `state.db`**——属于"全量镜像(含历史)"范围,只有打包
`state.db` 才能带走房间结构。若只要 agent 身份/协作能力,跳过 state.db 即可。

## 打包方案

### 方案 A — 配置归档(轻量,推荐)
只打包核心配置+记忆+技能+多 profile 人格,不含 129MB 会话历史:
```bash
cd /c/Users/<你>/AppData/Local/hermes
tar -czf /d/hermes-migration/hermes-config.tar.gz \
  -C /c/Users/<你>/AppData/Local/hermes \
  config.yaml .env SOUL.md \
  memories skills profiles plugins cron hooks
# 同 Windows 上 git-bash: tar 的路径必须用 /c/... (MSYS) 而非 C:\,否则报
# "Cannot connect to C: resolve failed"
```

### 方案 B — 全量镜像(含历史/群聊房间)
额外把 `state.db`(129MB)+ 可选缓存一并打包。新机 Hermes **版本尽量与新机一致**,
否则 state.db 可能需要迁移。

## 还原(新机)

新机先装好 Hermes(同版或更新版),然后把备份文件放到**对应位置**:
- 主目录文件 → 放 `C:\Users\<新用户名>\AppData\Local\hermes\`
- `.hermes` 组 → 放 `C:\Users\<新用户名>\.hermes\`
- 若新机用户名不同,需**核对 config.yaml 里的绝对路径**(D 盘项目路径、Python 路径等)

若 Hermes 版本不同,启动时可能自动做迁移;做完验证 `hermes` 命令、多 profile(`hermes profile show <名>`)正常。

## 敏感项 & 平台注意

1. **`.env` + `auth.json` 含密钥**(API Key、网关 token、Netlify token)——妥善保管,勿外传。
2. **平台需重新授权**:微信(iLink bot)、飞书、语雀等 pairing/token 可能绑定本机,
   跨机后需在新机重新登录授权(敏感操作用户自己完成,不为用户代输密码)。
3. **多 profile 的 `.env` 各自一份密钥**,6 个 profile 全都有自己独立的 .env。
4. 迁移后建议改管理员密码与各模型 API Key。
5. 若新机用不同用户名,`C:\Users\<新用户名>` 下的路径都要对。

## 传输尺寸参考

主配置(方案 A,含 skills/profiles 但不含 state.db)视 skills+profiles 大小而定,
本机 skills 118MB、6 个 profile 各含 state.db 数 MB~20MB。方案 A tar.gz 通常几十 MB;
方案 B(含主 state.db 129MB)会更大。可 U 盘 / 局域网拷贝。
