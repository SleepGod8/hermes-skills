# DSH EAC `web-desktop` OpenViking plugin validation — 2026-08

## What was learned

DeepSeek Harness EAC desktop may not use the standard DSH `web` profile. In this observed EAC build, the real desktop process ran:

```text
E:/Deepseek Harness EAC/resources/node/node.exe
C:/Users/80704/AppData/Roaming/Deepseek Harness EAC/agent/node_modules/@deepseek-ai/dsh/lib/bin.js
--profile web-desktop --host 127.0.0.1 --port 5936
```

Installing `@openviking/dsh-memory-plugin` into `--profile web` succeeded for a disposable CLI server, but did not make `mcp__openviking__grep` / `mcp__openviking__read` visible inside the EAC desktop UI. The fix was to install and configure the plugin in `C:/Users/80704/.dsh/profiles/web-desktop`.

## Reliable verification sequence

1. Identify the actual profile and port from the live process command line or EAC logs before changing plugin config.
2. Install the OpenViking plugin into that actual profile, not blindly into `web`:

```bash
APP='E:/Deepseek Harness EAC/resources/app'
node "$APP/node_modules/@deepseek-ai/dsh/lib/bin.js" \
  plugin --profile web-desktop add \
  'C:/Users/80704/.dsh/openviking-dsh-memory-plugin-0.2.1.tgz'
```

3. Add `openviking-memory-runtime` config to `C:/Users/80704/.dsh/profiles/web-desktop/cordis.patch.yml`.
4. Verify `--dump-config --profile web-desktop` contains `openviking-memory` and `openviking-memory-runtime`.
5. Fully restart EAC, not just the standalone test server.
6. Verify a child process exists like:

```text
C:/Users/80704/.dsh/profiles/web-desktop/node_modules/@openviking/dsh-memory-plugin/servers/mcp-proxy.mjs
```

This proves the desktop profile loaded the plugin and spawned the MCP proxy. If the model still says no `mcp__openviking__*` tools are available, next suspects are: the current agent preset disables tools, the selected model/provider lacks tool-calling support, or the UI session was created before the plugin reload.

## Pitfall

Do not treat successful `--profile web` install/startup as proof that EAC desktop sessions can see the tools. `web` and `web-desktop` can both exist, and stray test servers/proxies under `web` can confuse process inspection.
