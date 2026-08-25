/**
 * DSH EAC 内置插件批量更新脚本（复现 plugin-updater.js 的 applyBuiltinPluginUpdate 流程）
 *
 * 用法：
 *   "E:/Deepseek Harness EAC/resources/node/node.exe" <path>/update-builtin-plugins.js
 *
 * 流程：npm install 到 staging → 复制到覆盖层(%APPDATA%/Deepseek Harness EAC/builtin-plugin-updates/)
 * 重启 EAC 后 syncCompanionPlugins 自动从覆盖层读取新版本。
 *
 * 仅适用于在 PLUGIN_UPDATE_SOURCES 中登记的内置 companion 插件（npm 源）。
 * GitHub 源插件（如 dsh-undo）或用户插件不适用本脚本。
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

// ── 路径 ──────────────────────────────────────────────────────
const userDataDir = path.join(os.homedir(), 'AppData', 'Roaming', 'Deepseek Harness EAC');
const overlayDir  = path.join(userDataDir, 'builtin-plugin-updates');
const stagingDir  = path.join(userDataDir, 'plugin-update-staging');

const nodeExe = 'E:/Deepseek Harness EAC/resources/node/node.exe';
const npmCli  = 'E:/Deepseek Harness EAC/resources/npm/bin/npm-cli.js';

// ── 要更新的插件 ─────────────────────────────────────────────
// id = cordis.patch.yml 中的 id（也是覆盖层目录名）
// pkg = npm 包名
const PLUGINS = [
  { id: 'dsh-market-plugin',  pkg: '@sanqi-normal/dsh-webui-market-plugin' },
  { id: 'better-sidebar',     pkg: 'dsh-better-sidebar' },
  { id: 'dsh-pet',            pkg: 'dsh-pet' },
  { id: 'dsh-session-manager',pkg: 'dsh-session-manager' },
  { id: 'soul-md',            pkg: 'dsh-soul-md' },
  // 按需增删
];

// ── 工具 ──────────────────────────────────────────────────────
function runNpm(args, cwd) {
  const cmd = `"${nodeExe}" "${npmCli}" ${args}`;
  console.log('  > ' + cmd);
  return execSync(cmd, { cwd, timeout: 300_000, encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] });
}

fs.mkdirSync(overlayDir, { recursive: true });
fs.mkdirSync(stagingDir, { recursive: true });

// ── 批量更新 ──────────────────────────────────────────────────
let ok = 0, fail = 0;

for (const p of PLUGINS) {
  console.log(`\n=== ${p.pkg} ===`);

  const installDir = path.join(stagingDir, 'tmp-' + p.id);
  try {
    // 1. 准备临时 package.json
    if (fs.existsSync(installDir)) fs.rmSync(installDir, { recursive: true, force: true });
    fs.mkdirSync(installDir, { recursive: true });
    fs.writeFileSync(path.join(installDir, 'package.json'), JSON.stringify({
      name: 'tmp', version: '0.0.0', dependencies: { [p.pkg]: 'latest' }
    }));

    // 2. npm install（--ignore-scripts 安全）
    console.log('  Installing...');
    runNpm('install --ignore-scripts --no-audit --no-fund', installDir);

    // 3. 读取安装后的版本
    const srcDir = path.join(installDir, 'node_modules', ...p.pkg.split('/'));
    const pkgJson = path.join(srcDir, 'package.json');
    if (!fs.existsSync(pkgJson)) { console.log('  FAILED: package.json not found'); fail++; continue; }
    const pkg = JSON.parse(fs.readFileSync(pkgJson, 'utf8'));
    console.log('  Version: ' + pkg.version);

    // 4. 复制到覆盖层
    const dest = path.join(overlayDir, p.id);
    if (fs.existsSync(dest)) fs.rmSync(dest, { recursive: true, force: true });
    fs.cpSync(srcDir, dest, { recursive: true });
    console.log('  → Overlay: ' + p.id);

    ok++;
  } catch (err) {
    console.error('  ERROR: ' + (err.message || err));
    fail++;
  } finally {
    if (fs.existsSync(installDir)) fs.rmSync(installDir, { recursive: true, force: true });
  }
}

console.log(`\n=== Done: ${ok} ok, ${fail} fail ===`);
console.log('Restart EAC to apply.');
