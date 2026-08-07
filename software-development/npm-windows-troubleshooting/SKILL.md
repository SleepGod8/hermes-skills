---
name: npm-windows-troubleshooting
description: "Fix npm global package installs on Windows — postinstall single-quote crashes (use --ignore-scripts), ESM ERR_UNSUPPORTED_ESM_URL_SCHEME (pathToFileURL fix), EPERM cleanup failures, stale .cmd shims. For any npm i -g <pkg> failure on Windows."
version: 1.0.0
author: Hermes Agent
tags: [npm, node, windows, esm, troubleshooting]
---

# npm Windows 安装与 ESM 兼容修复

## 触发条件

- `npm i -g <pkg>` 在 Windows 上报错（SyntaxError / EPERM / command failed）
- 安装后命令找不到，或运行报 `ERR_UNSUPPORTED_ESM_URL_SCHEME`
- 卸载/重装时残留目录删不掉

## 症状 → 根因 → 修复

### 1. postinstall 脚本崩溃：`Unterminated string constant` / SyntaxError

```text
npm error command C:\WINDOWS\system32\cmd.exe /d /s /c node -e 'import(...)...'
npm error [eval]:1 'import(process.cwd()+/src-ext/...'
npm error Unterminated string constant
```

**根因**: 包的 `postinstall` 脚本用 **Unix 风格单引号** 包 JS 代码（如 `node -e 'import(...)'`），Windows `cmd.exe` 不认单引号作字符串定界，代码被截断。这是包在 Windows 上的兼容 bug，不是安装环境问题。

**修复**:
```bash
# 先看 postinstall 干什么（是否只是启动 daemon 之类非必需动作）
npm view @xyagent/cli scripts
# 用 --ignore-scripts 跳过 postinstall
npm i -g @xyagent/cli --ignore-scripts
```
若 postinstall 只是启动后台 daemon，跳过无影响。若必需，则用 git-bash 环境安装或自行 patch 脚本。

### 2. EPERM 清理失败（npm warn cleanup）

```text
npm warn cleanup Failed to remove some directories [
  ... [Error: EPERM: operation not permitted, rmdir '...yargs']
]
```

**根因**: 上次安装中断留下的空壳目录 + 有 node 进程占用文件（Hermes/daemon 等）。

**修复**:
```bash
# 找到残留目录（往往已被清空，只剩空壳）
ls "<npm-prefix>/node_modules/@xyagent"
# 先试重命名（能改名=未被锁），改名成功即可 rm
mv .../@xyagent .../@xyagent_bak && rm -rf .../@xyagent_bak
# 若重命名也失败 → 进程占用，先 tasklist 找 node 进程处理
```

### 3. 运行时报 `ERR_UNSUPPORTED_ESM_URL_SCHEME: Received protocol 'c:'`

```text
Error [ERR_UNSUPPORTED_ESM_URL_SCHEME]: Only URLs with a scheme in: file, data, and node
are supported... Received protocol 'c:'
```

**根因**: 包的源码里 `await import(path.join(__dirname, "relative/path.js"))` —— Windows 下 `path.join` 返回 `C:\...` 绝对路径，而 `import()` 要求 `file://` URL。**任何用 `path.join`/`path.resolve` 拼路径再传给 `import()` 的代码在 Windows 都会炸**。

**修复**（patch node_modules 源码，`pathToFileURL` 包装）:
```js
// 改前
import { fileURLToPath } from "node:url";
const TOML = await import(path.join(__dirname, "../../src-shared/vendor/x.js"));
// 改后
import { fileURLToPath, pathToFileURL } from "node:url";
const TOML = await import(
  pathToFileURL(path.join(__dirname, "../../src-shared/vendor/x.js")).href
);
```
⚠️ 注意 import 行要合并成一条（`import { fileURLToPath, pathToFileURL } from "node:url";`），不要留两条重复 import。

**全局搜一遍**（可能有多个文件同模式）:
```bash
grep -rn -A 3 "await import(" src/ --include="*.mjs" | grep -B 1 -A 2 "path.join\|path.resolve"
```

### 4. 安装成功但命令找不到 / 指向旧路径

- 包的真实 bin 名 ≠ 包名（例：`@xyagent/cli` 的 bin 是 `agentlink` 不是 `xyagent`）→ 看 `package.json` 的 `bin` 字段
- PATH 里有旧 shim（`.cmd`/`.ps1`/无扩展名）指向已删除的旧 node_modules 路径 → `which -a <cmd>` 查全部命中，删旧 shim
- npm prefix 可能指向 Hermes runtime node（`hermes-web-ui\desktop-runtime\...\node`），而残留 shim 在 `AppData\Local\hermes\node` → `npm root -g` 确认实际安装位置

## 验证

```bash
which <cmd>          # 指向新路径
<cmd> --help         # 正常输出（不再报 ESM 错误）
```

## 坑

- **node_modules 里的 patch 重装会被覆盖**：`npm i`/`npm update` 后需重新打补丁。建议把 patch 步骤记下来或写成脚本，重装后重放。
- **postinstall 用 --ignore-scripts 装完的包**，后续 `npm update` 若不带 `--ignore-scripts` 会再次触发崩溃。
