# Steam 卸载后的残留排查

触发语：「我把 X 从 Steam 卸载了，看看还有没有残留」「这些游戏的文件还占地方吗」。

铁律：**全部只读查完、汇总成表再问**；不要在排查过程中边查边删。存档类发现先备份并校验，才允许删父目录。

## 排查顺序（按体积收益从大到小）

1. `steamapps\common\<游戏目录>` —— 卸载后最常见的残留地，常剩 **mod 目录 + 加载器 + 用户配置**。
   先判性质：`find <dir> -maxdepth 3 -iname "<GameExecutable>.exe"`
   - 无输出 = 本体已清理，剩下全是 mod/配置 → 可整体清
   - 有输出 = 本体还在，别当残留
   体积用 robocopy 快扫（见 SKILL.md「扫描正确姿势」），不要靠 `du -sh` 估。
2. `steamapps\appmanifest_<appid>.acf` —— 有 manifest = 仍登记为已安装；没有才代表 Steam 认账已卸载。
   **不要手删 manifest**（会让库状态错乱，用户下次启动 Steam 会自愈出怪现象）：让用户在 Steam 里点「卸载」。
3. `steamapps\workshop\content\<appid>` —— 创意工坊订阅内容，卸载游戏通常不会自动清。
4. `steamapps\shadercache\<appid>`、`steamapps\downloading\<appid>`、`steamapps\compatdata\<appid>` —— 着色器缓存 / 未完成下载 / Proton 前缀。
5. `Steam\userdata\<steamid>\<appid>` —— 云存档缓存与本地配置。
6. 模组管理器暂存：`%APPDATA%\Vortex\<game>`（Vortex 把 mod 以**符号链接**部署进游戏目录，源头在这里）、`Vortex Mods\`、Fluffy Mod Manager 的 `Games\`、`%APPDATA%\Nexus Mod Manager`。
   删游戏目录时必须把源头一并列入清单，否则 C 盘还留一份（符号链接只删链接本身）。
7. 应用配置/存档：`%LOCALAPPDATA%\<Publisher>`（如 CD Projekt Red）、`%APPDATA%\<Publisher>`、`Documents\<Game>`、`Documents\My Games\<Game>`。
   注意区分「配置文件（几 KB，随便删）」与「存档（需保留）」。

## 存档必须先备份再删

- 游戏目录里常藏 `savedata_backup\SAVEDATA*`、`profile\`、`*.sav`；这是玩家进度，删了回不来。
- 流程：`Copy-Item` 到 `E:\Hermes workspace\game-backups\<Game>\` → 用**大小 + `Get-FileHash -Algorithm SHA256`** 双比对 → 通过后才删源目录；备份结果写进日志（`Result=OK/FAIL`）。
- 用户说「**存档留着不动，其他删了**」= 备份存档、删掉整个游戏目录，**不是**把整个目录留着；先按这个理解执行，并在报告里点明备份落点。

## 判断「纯 mod 残留」的量级参考

- 大型 3A 打满 mod 后残留可达 10 GB+（如赛博朋克2077 的 `archive\pc\mod\*.archive` + 服装/身形 mod 目录 + 原始 `.zip/.7z` 安装包），极易被误当成「游戏本体没删干净」——先找 exe，再下结论。
- 怪物猎人世界/崛起：`natives\`（mod 资源）、`shader.cache2`（可上百 MB）、Stracker's Loader 的 `dinput8.dll` / `loader.dll`（是符号链接）+ `*.vortex_backup`。
- 暗黑地牢：`mods\<工坊 id 或 mod 名>\`，一个 mod 几百 MB 很常见（高清头像/皮肤）。
- Steam 的「Bonus Content / 奖励内容」类免费 DLC 会单独留一条 `appmanifest_<appid>.acf`，游戏本体卸载后仍在——提示用户在 Steam 内卸载，不要手删。

## 报告口径

输出三张表：①**残留明细**（路径 / 大小 / 里面是什么 / 性质）；②**用户自己的收藏不动**（如 `ZSC\<游戏>mod`、mod 管理器工具本体，只报告不删）；③**Steam 侧状态**（manifest 是否已清、工坊/缓存/云存档有无残留）。最后给合计可清 GB + 空间百分比，再问「备份后全删 / 全删 / 只删最大那块 / 先别动」。
