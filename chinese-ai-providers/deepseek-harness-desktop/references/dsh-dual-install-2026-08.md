# dsh-desktop 双安装取证实录（2026-08-19）

## 用户问题
「E:\Deepseek Harness EAC 和 E:\Deepseek Harness EAC\DSH Desktop，我是装了 2 个 DeepSeek Harness 桌面端吗？两个都保留有影响吗？」

## 现场事实

| 项 | 外层 `E:\Deepseek Harness EAC\` | 内层 `E:\Deepseek Harness EAC\DSH Desktop\` |
|---|---|---|
| productName | Deepseek Harness EAC | DSH Desktop |
| 版本 | 4.1.0（新） | 0.3.9（旧） |
| exe | Deepseek Harness EAC.exe (225,541,632 B) | DSH Desktop.exe (225,541,632 B) |
| md5 | e72ce0b0… | b5c27db9…（同大小不同 hash = 同源不同构建） |
| 数字签名 | NotSigned | NotSigned（个人打包，无签名） |
| 安装时间 | 8月17日 | 8月16日 |
| 数据目录 | ~/.dsh | ~/.dsh（共用） |

## 作者鉴定链
1. `resources/app/package.json`：两版都是 `name: dsh-desktop`、`author: DSH Desktop`、`license: MIT`，依赖同为 `@deepseek-ai/dsh 0.1.0-rc.6` + 23 个官方包 → 底层 agent 官方、外壳第三方。
2. `resources/app/client-updater.js` 第 31 行：
   ```js
   const DEFAULT_REPOS = { github: 'myYangyunfan/dsh_desktop', gitee: 'my-yang-yunfan/dsh_desktop' };
   ```
   → 作者 = 个人开发者 **myYangyunfan**（GitHub/Gitee 同名仓库）。
3. 结论：**同一个作者的版本迭代**（0.3.9 → 4.1.0 改名 + 大版本跳跃），不是两个不同作者。exe 尺寸完全相同 + author/依赖一致是强证据。

## 安装完整性（关键坑）
第二次排查时发现外层 v4.1.0 已经损坏：
```
顶层只剩：Deepseek Harness EAC.exe + d3dcompiler/dxcompiler/dxil/ffmpeg/libEGL/libGLESv2.dll
resources/ 只剩 node/node.exe
缺失：resources/app（整个源码）、chrome_100/200_percent.pak、resources.pak、icudtl.dat、snapshot_blob.bin、locales/、Uninstall exe
```
Electron 缺 resources.pak + icudtl.dat + resources/app 必然启动失败 → 只能重装。修复判断：先列目录核对完整性清单，别试启动。

## 双安装影响（回答用户）
1. 共用 `~/.dsh` 数据目录 → 同时运行互写 sessions/storages/profiles，数据损坏风险
2. 0.3.9 vs 4.1.0 数据格式可能不兼容（新版升级后旧版再读可能报错）
3. 磁盘浪费 ~1GB（两份各约 500MB）
4. 各自独立自更新，可能互相覆盖文件
5. API key 配置无冲突（都读 DEEPSEEK_API_KEY 环境变量）

## 建议动作
- 保留完好的一份（当时内层 0.3.9 完好且最近运行过），删损坏残留
- 若要新版 4.1.0：重新下载安装包覆盖装，损坏的文件无法修补

## 可复用技巧
- `md5sum a.exe b.exe`：同大小不同 hash → 同源不同构建；同 hash → 同一副本
- `powershell Get-AuthenticodeSignature <exe>` → Signer/Status：个人打包通常 NotSigned，不能据此判官方与否
- exe 里搜字符串找作者：`grep -a github.com exe` 可能命中 node_modules 误报（如 nodejs/undici 文档链接），以 client-updater.js / package.json 为准
