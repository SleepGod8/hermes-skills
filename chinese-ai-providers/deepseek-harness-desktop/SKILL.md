---
name: deepseek-harness-desktop
description: "Use when 配置/排查 DeepSeek Harness 桌面客户端 API key、凭据、多份安装与来源鉴定。"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [DeepSeek, dsh, API-Key, env-var, Windows, credentials]
---

# DeepSeek Harness Desktop (dsh-desktop) 凭据配置与排障

Use when 用户问 DeepSeek Harness / DeepSeek Harness EAC 桌面客户端怎么配 API key、显示「由启动环境提供(只读)」、请求 401、或 key 轮换后不生效。

产品：DeepSeek Harness (dsh) 的 Windows 桌面客户端（Electron，未打包源码在 `<安装目录>\resources\app\`，关键文件 `balance.js`、`assets/plugins/dsh-side-session/lib/index.js`）。

## 凭据读取顺序（实测源码）

1. 环境变量 `DEEPSEEK_API_KEY` — **优先级最高**；命中时设置页显示「由启动环境提供(只读)」且不可编辑。
2. `~/.dsh/.credentials.yaml`（`DSH_HOME` 可覆盖数据目录）— UI 可编辑来源，格式：
   ```yaml
   DEEPSEEK_API_KEY: "sk-xxx"
   ```
   解析正则：`^\s*DEEPSEEK_API_KEY\s*:\s*["']?([^"'\s#]+)`
3. 都没有 → 提示「DSH 全局 Key 为空」。

**核心坑：只要环境变量存在（哪怕已失效），文件里的 key 永远不会被读取。** 用户说「改了 credentials.yaml 不生效」时，第一反应查环境变量里是否躺着旧 key。

其它变量：`DEEPSEEK_API_BASE`（API 基址）、`DEEPSEEK_BALANCE_URL`（余额端点）、`DSH_HOME`（数据目录）。

## 排查步骤

1. **看环境变量（不要只信 bash `env`）**：
   ```bash
   reg query "HKCU\Environment" | grep -i deepseek      # 用户级（DSH 读这里）
   reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment"   # 系统级
   ```
   bash 的 `env` 可能与 Windows 用户变量不一致；「只读」提示出现就说明环境变量里有值。
2. **判定「只读」含义**：是正常状态提示 = key 已由启动环境注入，不是没配置、不是故障。用户常误以为「只读」= 需要配置。
3. **验证 key 是否有效**（401 = 失效）：
   ```bash
   # chat/completions（DSH 核心接口）
   curl -s https://api.deepseek.com/chat/completions -H "Authorization: Bearer <key>" -H "Content-Type: application/json" \
     -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"hi"}],"max_tokens":5}'
   # balance（余额显示）
   curl -s https://api.deepseek.com/user/balance -H "Authorization: Bearer <key>"
   ```
4. **换 key**（二选一）：
   - 保持环境变量方式：`setx DEEPSEEK_API_KEY <key>`（写 HKCU，>1024 字符截断，自动广播 WM_SETTINGCHANGE）
   - 转 UI 可编辑：删掉环境变量 `DEEPSEEK_API_KEY`（reg delete 或系统设置界面），再写 `~/.dsh/.credentials.yaml`
5. **重启 DSH**：环境变量只对新进程生效，必须完全退出重开；从终端启动则要新开终端。

## 验证闭环

- 改完用 `reg query "HKCU\Environment" /v DEEPSEEK_API_KEY` 确认写入值与目标 key 一致（只回显后几位 + 长度即可，勿打印完整 key）。
- 用更新后的 key 实测 chat/completions 200 + balance 返回 `balance_infos`（字段：total_balance 总额 / granted_balance 赠送 / topped_up_balance 充值）。

## 多份安装 / 来源鉴定 / 安装完整性

用户可能装了多份（同源不同版本，常见嵌套目录：新版装在旧版目录里）。判定流程：

1. **列目录**：顶层应有 exe + chrome_*.pak + icudtl.dat + resources.pak + locales/ + resources/app/。缺 `resources/app`、`resources.pak`、`icudtl.dat`、`locales/` 中任一个 → 应用必挂；只剩 exe + 几个 dll + 空 resources/ = 安装已损坏，只能重装。
2. **作者鉴定**（第三方打包普遍无数字签名，`Get-AuthenticodeSignature` 返回 NotSigned 不代表官方）：
   - `resources/app/package.json` → name/productName/version/author/dependencies（`@deepseek-ai/dsh` 全家桶 = 底层 agent 是官方的，外壳是第三方）
   - `resources/app/client-updater.js` → `DEFAULT_REPOS = { github: '作者/仓库', gitee: '作者/仓库' }` 直接揭示作者
3. **是否同源**：`md5sum` 对比两个 exe —— 同大小+同 hash=同一副本；同大小不同 hash=同源不同构建（版本迭代/改名）。
4. **共用数据目录冲突**：多份安装共用 `~/.dsh`（sessions/profiles/storages）→ **绝不能同时运行**，会互写数据；版本间数据格式也可能不兼容。保留一份即可（先确认能启动再删另一份）。

完整双安装取证实录见 `references/dsh-dual-install-2026-08.md`。

## Pitfalls

- ⚠️ **中文 Windows 上 `setx`/`reg` 输出是 GBK 编码**：Python `subprocess.run(..., text=True)` 会 UnicodeDecodeError（`'utf-8' codec can't decode byte 0xb3`），必须加 `errors="replace"` 或按字节读。
- 多工具共用同一 DeepSeek key 时（Hermes `.env`、注册表 `ANTHROPIC_API_KEY`、注册表 `DEEPSEEK_API_KEY`）换 key 容易漏同步 —— 轮换后逐个验证。
- 注册表错误信息只回显 key 后 4 位（`****54ef`），不足以区分两把前缀相同的 key；对比长度 + 后 6 位。
- 敏感 key 在脚本里处理时不要 print 完整值；execute_code 里从文件/注册表读取即可。

完整真实案例（2026-08-19 故障链）见 `references/dsh-credentials-case-2026-08.md`。
