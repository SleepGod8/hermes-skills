---
name: deepseek-harness-desktop
description: "Use when 配置/排查 DeepSeek Harness 桌面客户端 API key、第三方模型 provider、多份安装。"
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

## 主聊天模型接第三方 OpenAI 兼容 provider（llm-pi-ai，第一方适配器）

主聊天模型（Web UI 模型选择器）接任意 OpenAI 兼容端点（ASLNet/SiliconFlow 等）——编辑 `~/.dsh/settings.yaml`（先备份 `.bak`）：
```yaml
llm-pi-ai:
  providers:
    aslnet-plus:                       # provider 组名（模型选择器里显示）
      displayName: ASLNet Plus
      apiKeyEnv: ASLNET_PLUS_KEY       # 环境变量名；DSH 只读 Windows 环境变量，不读 Hermes .env
      api: openai-completions          # 或 anthropic-messages / openai-responses
      baseURL: https://api.aslnet.cloud/v1
      models:
        - id: gpt-5.5
          name: gpt-5.5
          contextWindow: 128000
          maxTokens: 16384
          input: [text]
```
- schema 权威来源：`<安装目录>\resources\app\node_modules\@deepseek-ai\dsh-llm-pi-ai\lib\index.js`（`Config = z.object({ providers: z.dict(profile) })`；profile 可配 reasoningEfforts/compat/headers/transport 等）
- `apiKeyEnv` 指向的 key 需 `setx` 到 Windows 用户环境变量（DSH 进程不继承 Hermes 的 .env）
- ⚠️ **改完必须重启 DSH**（llm-pi-ai 启动时读 settings.yaml）；日志出现 `[dsh-third-party-thinking] wrapped N third-party adapter(s)` = 第三方适配器已注册
- reasoning_effort 注入默认关闭（dsh-third-party-thinking 插件），严格校验请求体的第三方 API 会 4xx——先别急着开
- 完整 ASLNet 实测配置见 `references/aslnet-provider-2026-08.md`

## IM 桥接第三方端点（openclaw-bridge）

- 设置 → ClawBot/IM 桥接，settings 命名空间 `openclaw-bridge`，provider id `openclaw-custom`
- 字段：customBaseURL / customApiKey / customModel；走 OpenAI 兼容 `/chat/completions`，热生效
- 只作用于微信/飞书消息驱动的 agent（接收模型），**不是** Web UI 主聊天模型

## 运维/排障

- 数据目录：安装版 `%APPDATA%\<productName>\` 各自独立（v0.3.9 = `%APPDATA%\DSH Desktop`；v4.1.0 换皮版 = `%APPDATA%\Deepseek Harness EAC`）；dsh 配置在 `~/.dsh/settings.yaml`。查当前进程数据目录：`powershell Get-CimInstance Win32_Process -Filter "Name='<exe>'" | select ExecutablePath`，再看子进程 node 命令行里的 `--user-data-dir`
- Web UI 端口：`settings.json` 的 `webPort` 可能已过期；以 `logs\dsh-web.log` 的 `dsh web: http://127.0.0.1:<port>` 为准；也可 `netstat -ano | grep <主进程PID>`。UI 是 SPA（`http://127.0.0.1:<port>/`），curl 200 即就绪
- 从 bash 启动 Electron GUI 可能静默退出（exit 0 无窗口）→ **实测可靠方式：`explorer.exe "E:\path\App.exe"`**（2026-08-19 验证，`cmd //c start` 与 `powershell Start-Process` 都可能静默失败——开了 cmd 但进程没起来）；仍不起就让用户桌面双击。启动即退时查 `logs\watchdog.log` 的 `clean exit marker found`（正常退出标记/单实例锁）和 `logs\desktop.log` 尾部；改完环境变量先 `taskkill /IM "<exe>" /T /F` 再启，避免旧进程残留

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
- 第三方 provider 端到端：Web UI 发一条无害消息（如「回复OK」），desktop.log 出现 `[notify] 任务完成: {title: 消息, body: 工作区 · 会话 xxx}` + UI 有回复 = 真实调用成功（2026-08-19 实测 ASLNet gpt-5.4，首轮 ¥0.0103）。模型选择器菜单应按 displayName 分组显示（DeepSeek / ASLNet Plus 等）。

## EAC 内置插件安装（assets/plugins + COMPANION_PLUGINS）

给 DeepSeek Harness EAC 桌面版安装内置/随包分发插件时，不能只把插件目录复制到 `E:\Deepseek Harness EAC\resources\app\assets\plugins\<dir>`，也不能只手改 `~/.dsh/profiles/web-desktop/cordis.patch.yml`。EAC 启动会从 `resources/app/main.js` 的 `COMPANION_PLUGINS` 表同步内置插件到 `~/.dsh/profiles/web-desktop/node_modules`、`.dsh-builtin-plugins.json` 和 `cordis.patch.yml`；手工 patch 行若包未进入 profile 解析链，会报：

```text
plugin tree failed to load ... Cannot find package '<plugin-name>' imported from C:\Users\...\.dsh\profiles\web-desktop\
```

正确流程：

1. 下载/构建插件运行时文件到 `resources/app/assets/plugins/<dir>`，至少包含 `package.json`、`lib/`、`cordis.patch.yml` 以及运行资源。
2. 在 `resources/app/main.js` 的 `COMPANION_PLUGINS` 数组里追加：
   ```js
   { id: '<entry-id>', name: '<package-name>', dir: '<assets-dir>' },
   ```
   `id` 要与插件 `cordis.patch.yml` 中的 loader entry id 一致，`name` 要与插件 `package.json.name` 一致，`dir` 是 `assets/plugins` 下目录名。
3. `node --check 'E:/Deepseek Harness EAC/resources/app/main.js'` 验证语法（不要用 MSYS `/e/...` 路径给 Node，否则可能误解析）。
4. 完全重启 EAC。启动日志应出现 `已同步配套插件/皮肤到 web profile: ... <entry-id>`。
5. 验证：
   ```bash
   grep -n "<entry-id>\|<package-name>" /c/Users/80704/.dsh/profiles/web-desktop/cordis.patch.yml
   grep -n "<package-name>" /c/Users/80704/.dsh/profiles/web-desktop/.dsh-builtin-plugins.json
   test -f /c/Users/80704/.dsh/profiles/web-desktop/node_modules/<package-name>/package.json
   curl -I http://127.0.0.1:<webPort>/
   node --input-type=module -e "import('file:///C:/Users/80704/.dsh/profiles/web-desktop/node_modules/<package-name>/lib/index.js').then(()=>console.log('ok'))"
   ```

失败时守护器会自动回滚 `web-desktop` profile 到最后良好快照；看 `logs/desktop.log` 的 `guard` 与 `logs/dsh-web.log` 的 `ERR_MODULE_NOT_FOUND` 判断原因。

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
