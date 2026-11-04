---
name: windows-disk-cleanup
description: Use when 清理 Windows 磁盘空间. 五阶段确认制+实测扫描+安全删点.
---

# Windows 磁盘清理（五阶段确认制）

用户给「清理 C/D 盘」类任务时，默认走五阶段，每阶段结束停下等确认，全程先只读后动手。

## 五阶段
1. **探测**：容量/已用/剩余/使用率 + 系统版本/用户/是否管理员 + 一级目录归属表 + 紧张度判断（空闲 <15% = 偏紧）。
   - 读数与上一轮记录差几十 GB 时，先查根目录 `pagefile.sys`（系统托管、随内存压力伸缩）和动态盘（模拟器 vdi），确认是「没人删东西、只是页面文件缩了」再下结论；这个解释要写进报告，否则用户会怀疑有隐情。
2. **扫描标注**：每项标 `路径/类型/用途/大小/最后修改/优先级/理由/建议操作`。优先级：一级=缓存临时残留（可自动重建）；二级=需确认（旧安装包、闲置实例、未完成下载、可重下运行时）；三级=用户数据/程序数据；不可清理=Windows、Program Files、ProgramData、驱动、运行依赖。
3. **分块汇总+菜单**：每块给「项目数/合计/建议清理量」，然后让用户选「仅一级 / 一+二级 / 指定编号 / 暂不清理」。不执行删除。
4. **最终清单+二次确认**：逐项列出路径/大小/清理方式/风险/前置条件 + 预计释放量，等用户回「确认清理」。
5. **执行+报告**：逐项删除、逐项记日志（before/after/freed/OK|PARTIAL|FAIL），报告前后剩余空间、成功/失败/跳过明细、副作用、后续建议。

产物落在工作区（如 `E:\Hermes workspace\c-drive-cleanup\`）：`inventory.json`、`final_plan.json`、`cleanup_log.csv`、阶段报告 md。

## 扫描正确姿势
- 大目录（几百 GB）**不要**用 `Get-ChildItem -Recurse | Measure-Object`：十几分钟不出结果且可能陷进 junction。
- 用 robocopy 列表模式，秒级出结果、只读、跳过符号链接：
  ```powershell
  robocopy $path 'NULL' /L /S /NJH /BYTES /NFL /NDL /XJ /R:0 /W:0
  # 解析 summary 的 `Bytes :`（中文系统为 `字节 :`）
  ```
  必须**保留** job summary（不要加 `/NJS`，加了就没有 Bytes 行，全是 0）。
- 特殊目录（WinSxS、Windows\Temp、Windows\Logs）普通权限读不到，按约束记录「扫描失败/需管理员」跳过。
- 现成脚本：`scripts/scan-dir-sizes.ps1`（robocopy 快扫 + 根目录散落文件合计 + CSV，自带 `/XJ`、Bytes 解析与「CSV 没写出来就报错」检查）。直接 `-Root 'D:/' -Out '<绝对路径>.csv'` 调用，别每次重写。

## 高危误判（务必逐一核验再列入清单）
- `AppData\Local\hermes\installs\<hash>\environments` = **活动 Python 环境**（十几万文件），不是安装包缓存，删了 Hermes 工具全废。
- `.hermes-web-ui\desktop-runtime`、`AppData\Local\hermes\profiles` = 运行依赖。
- `AppData\Local\b1`、根目录空壳目录（`C:\c`、`C:\XmpCache`）用途不明 → 标「需人工确认」，不主动删。
- `hermes\backups` 里常含技能同步备份，有价值。

## 清理机制与坑
- 包管理器缓存优先用官方命令（`uv cache clean`/`npm cache clean --force`/`pnpm store prune`/`pip cache purge`）；首轮若 PARTIAL，直接对剩余子目录重试 `rm -rf` 往往成功。
- `uv\cache\archive-v0` 常被运行中的 MCP 进程（如 `mcp-server-fetch.exe`）占用 → 首轮报 PARTIAL，重试后可删到 0；uvx 下次启动会自动重建，需在报告里注明首次调用变慢。
- 清浏览器/包管理器缓存前先关进程（`Stop-Process -Name msedge`），否则大批文件被占用。
- `C:\Windows\SoftwareDistribution\Download`、`C:\Windows\Logs` 无管理员必失败，直接标「需提权」跳过，别浪费轮次。
- 用户数据（微信 `xwechat_files`、Documents、工程资料）只能提示大小，禁止手删目录；微信走「设置→存储空间」自带管理，避免破坏数据库索引。
- 私密/成人向收藏目录（盘符下以人名缩写命名的 `ZSC` 类目录）：只读展开到二级结构即停，表格里中性写「个人收藏 + 大小」，**不复述内部文件名、不做价值评价、不主动建议删**，一律三级。
- 回收站里可能出现**不是本次删除**的东西（应用自动更新会把旧版丢进 `$RECYCLE.BIN`，文件名形如 `$R<随机>.<版本后缀>`）：报告里点明归属，别把别人的删除算进本次战果。
- 虚拟机/模拟器类：Activity/闲置实例要区分（看 vdi 最后写入时间 + 进程是否在跑）；MuMu `data.vdi` 是只增不减的动态盘，长期占用会持续膨胀。

## MuMu 模拟器磁盘清理（实测）
- **只能走 GUI**：`nx_main\MuMuManager.exe`（与 `mumu-cli.exe` 同一套）只有 `control/setting/adb/info/...`，**无 disk/compact 子命令**；`setting --all` 里只有 `mini_disk`、`system_disk_readonly`，没有压缩键。别在 CLI 上浪费时间。
- 入口：主窗口实例卡片右侧 `⋮` → **磁盘清理**。
- 机制：**设备必须处于可启动状态**（关着的实例点它会弹「请先启动安卓设备」）；点「继续」后 MuMu **自己关闭设备再清理**，期间无法启动。我早期说「必须手动关机」是错的。
- 实测收益：vdi 95.62 GB → **35.66 GB**（−60 GB），1 分钟内完成，App/账号/存档全保留（清理后重启验证 `pm list packages -3` 15 个包、`/data` 仍 28 GB）。
- 预估可回收量 = **vdi 文件大小 − 客人机 `/data` 实际用量**（`adb shell df -h /data`）；实例 0/1 的 ADB 端口分别是 16384/16416。
- 清醒认识：清理后 vdi 仍会继续涨，是长期运维问题（定期清或迁盘）。

## 雷电模拟器（LDPlayer 9.x）：没有磁盘压缩功能
- 三处确认均无：`ldconsole.exe` 全命令表无 compact（只有 launch/quit/backup/restore/installapp…）、多开器 GUI（实例设置→磁盘页、批量操作菜单、多开设置窗）无入口、对所有 exe 做 UTF-16/UTF-8/GBK 关键字搜索（磁盘清理/磁盘压缩/Compact）**零命中**。
- 目录里只有 `vbox64\*.dll`，**没有 VBoxManage.exe**，无法用 `modifymedium --compact` 压 VMDK。
- 结论：遇到雷电只给两条路——**要么保留，要么删实例**（删除会丢该实例内安卓数据）。别像我一样把 GUI 翻一遍才发现功能不存在；先 grep 二进制关键字再点界面更省时间。
- 删实例用官方命令，别手删 `vms\<实例>` 目录：
  ```powershell
  ldconsole.exe list2                      # 删前：编号,名称,状态
  ldconsole.exe remove --index 0           # 逐个删（0/1/...）
  ldconsole.exe list2                      # 删后应为空
  ```
  实测两实例 104.45 GB，删完卷剩余立即 +104.47 GB，**没有 VSS 差额**（实例删除是直接回收，与逐文件删除不同）。删后安装目录只剩程序本体约 3 GB，仍可新建实例。

## WSL2 / Docker 虚拟磁盘（docker_data.vhdx）压缩的三条路
- `wsl --manage <distro> --set-sparse true`：WSL 2.7.x **主动拒绝**（“由于潜在的数据损坏，目前已禁用稀疏 VHD 支持”），需 `--allow-unsafe` 才强开——官方标注有数据损坏风险，含 Docker 卷数据时不要擅自开，先问用户。
- `diskpart select vdisk → compact vdisk`：**必须管理员**，普通权限直接报“请求的操作需要提升”。
- `Optimize-VHD`：仅在装了 Hyper-V 模块时存在，家用版通常没有。
- 无管理员时的可行替代：`wsl --export` + `--unregister` + `--import` 重建（数据保留、自动紧凑），代价是需要临时空间与时间。

## 窗口被遮挡时 PostMessage 点击失灵 → 临时置顶
- 症状：目标窗口被别的窗口（如 Hermes 自身）盖住时，PostMessage(WM_LBUTTONDOWN) 对某些按钮“没反应”（同坐标换个时间又有效）。
- 解法：先 `SetWindowPos(hwnd, HWND_TOPMOST=-1, …, SWP_NOSIZE|SWP_NOMOVE)` 置顶，再发消息；完事后 `HWND_NOTOPMOST=-2` 恢复。比 `SetForegroundWindow`（常被前台锁拒绝）可靠得多。
- 弹窗可能属于**另一个窗口类名**（本机 MuMu 是 `Q`、雷电弹窗是 `L`/`l` 小写），枚举时按 **pid** 过滤最稳。

## 删除量 ≫ 卷剩余增量：卷影副本
- 实测多次出现：C 盘一次正常，D 盘删除 96.82 GB 只回 87.23 GB，E 盘删除 31.00 GB 只回 17.87 GB。
- 现象稳定、有规律，疑为**卷影副本（VSS）以写时复制保留了被删数据块**；注册表 `SystemRestore\RPSessionInterval=1` 可作为系统保护开启的侧证。
- 普通权限查不了 `vssadmin list shadowstorage /for=<盘>:`，报告中要如实标注差额与验证命令，不要宣称已释放全部。

## 驱动 GUI 应用的可靠姿势（无 computer_use 工具时）
- 坐标系三套（虚拟屏/物理屏/窗口客户区）必须先统一：进程开头调 `SetProcessDpiAwarenessContext(-4)`（或 `SetProcessDPIAware`），之后 `GetWindowRect` 与像素坐标才一致。
- **不要用 `CopyFromScreen` 截图**：目标窗口被前台窗口遮挡时只能拍到遮挡物，会误判「菜单没弹出」。
- 正确做法：`PrintWindow(hwnd, hdc, 2)`（PW_RENDERFULLCONTENT）**只截目标窗口**；Qt 的下拉菜单/弹窗是**独立顶层窗口**，用 `EnumWindows` 按 pid 过滤 + 取窗口矩形，再对弹窗 hwnd 单独 `PrintWindow`。
- 点击：`SetForegroundWindow` 常被 Windows 前台锁拒绝（越点越把别的窗口提到前面）。改用 **`PostMessage(hwnd, WM_LBUTTONDOWN/UP, 1, lParam=(y<<16)|x)` 打客户区坐标**——不抢焦点、不动真实鼠标，Qt 应用响应良好；先用 `ClientToScreen` 求客户区原点把窗口坐标换算成客户区坐标。
- 每步都截图 + 识图确认，再决定下一步；弹窗确认文案要看清楚（本次就是靠读弹窗才发现「需先启动设备」）。
- 现成脚本：`scripts/win-gui-probe.ps1`（DPI 感知 + 按 pid 枚举窗口含矩形 + `PrintWindow` 单窗截图 + `PostMessage` 左/右键 + 临时置顶/恢复），`-Action list|shot|click|top|untop`，别再每次手写 Add-Type 那套 P/Invoke。
- 删除时对目录型目标只清子项、保留父目录；不做通配符批量删除。
- 大目录删除用 `cmd /c rd /s /q "<dir>"`，比 `Remove-Item -Recurse -Force` 快一个量级（几十 GB 分钟级 vs 十几 GB 十几分钟）；`Remove-Item` 只留作单个被占用文件的回退手段。删完 `Test-Path` 复核该路径是否真的消失。
- **自己的 shell 会锁住待删目录**：如果之前的 `cd` 还停在目标目录（或其子目录），`rd /s /q` 会把文件删干净却报「另一个程序正在使用此文件」，只剩下空壳目录。删前先 `cd` 回工作区；撞上这个报错时第一步怀疑自己的 cwd，而不是去翻 Explorer / 杀软，隔十几秒重试一般就过（句柄释放有延迟）。
- `Export-Csv` / 重定向**不会自动建目录**，`-Out` 路径写错会静默失败：产物写完立即用 `search_files(target='files')` 或 `Test-Path` 核验文件存在，报告里引用的产物必须先确认能列出。
- Steam 的 `steamapps\downloading\<appid>` 是**未完成下载**（体积可达几十 GB，随下载持续增长）：先用 `steamapps\appmanifest_<appid>.acf` 判断该游戏是否真的已安装，删前必须 `Stop-Process -Name steam,steamwebhelper`，否则边写边删必然 PARTIAL。报告要写清「删=放弃本次进度，再装需重下」。
- 模拟器多开：`vms\<实例目录>` 一个子目录 = 一个安卓实例，每个实例一份 ~100 GB 级 `data.vdi`。判定活动性看 `data.vdi` 最后写入时间 + 是否有对应进程；**闲置实例是单块最大可回收项**，但它属于「该实例内所有 App/游戏进度」，只能列为二级需确认。
- **单位只用 1024 进制**：robocopy `/BYTES` 得字节后统一 `/1GB`，不要一处按 1000 换算 MB、另一处按 1024，否则同一项目会给出两个数字（如 9.83 vs 9.60 GB），用户会追问并要求校准。
- **基线在执行时实测**：阶段 5 的报告口径用执行脚本自己打印的 `FREEBEFORE`/`FREEAFTER`，不要复用阶段 1 或上一轮会话的剩余值。动态盘（模拟器 vdi）、日志、下载会在数小时内吃掉几十 GB，跨时段复用旧值必被用户发现对不上。
- 解析扫描 CSV 用 execute_code（内核 python），不要在 bash 里 `python -c`：shell 的 `python` 可能解析到项目桩解释器，直接报 `did not find executable`。

## 本机磁盘布局（2026-11 实测；量级会漂移，别当固定值）

- **C:** 300 GB 系统盘 —— 可清的全在 `Users\80704\AppData`（缓存/安装包/浏览器），`Windows`+`Program Files` 约 82 GB 不动。
- **D:** 651 GB —— `Program Files\Netease\MuMu`（两套安卓实例）、`宝深`/`坪深`（工程资料 zip，仅提示）、`xwechat_files`（msg\file 最肥）、`Steam`（常有未完成下载）。
- **E:** 1863 GB —— `SteamLibrary`、`ZSC`（私密收藏）、`leidian\LDPlayer9\vms`（2 实例、长期闲置）、`Hypergryph Launcher`、`docker-data\DockerDesktopWSL\disk\docker_data.vhdx`、`迅雷下载`/`BaiduNetdiskDownload`/`quark`/`迅雷云盘`、`bandzip\BNZ.*`（解压残留，藏十几 GB）、`pagefile.sys`。
- 挂机归属：MAA/MaaEnd 连 `127.0.0.1:16384`（MuMu 实例 0）；实例 1（16416）闲置但保有 WC3/WC4/方舟账号 —— 这类实例优先「压缩」而不是「删除」。

## 大占用项识别

按类型快速判定「这是不是能清的」；深度明细见 `references/big-consumer-identification.md`（Steam 未完成下载/工坊、模拟器多开 vdi、微信 file/attach/business 拆分、WSL/Docker vhdx、解压软件临时目录、pagefile、工程资料 zip、VM vmdk、安装包集合、驱动备份的判定法与优先级，附模拟器与 WSL 虚拟磁盘压缩配方）。

- 先扫一级目录拿到 Top 10 再往下钻，**不要一上来全盘递归**；钻到第 2~3 层就能定性时立即停手。
- **盘位预期不同**：C 盘以缓存为主，清缓存能出几十 GB；数据盘（D/E）一级可清量常常 ≈0，大头全是实体数据（工程资料、微信文件、虚拟磁盘、未完成下载、安装包集合）。别承诺「清垃圾」能救数据盘，结论要落到「处理大件 or 迁移」。
- 模拟器实例归属判定（决定「删了会不会断挂机」）：读 `vms\<实例>\configs\vm_config.json` 的 `port_forward` 拿该实例 ADB 端口（典型 16384/16416…），`adb devices` 看当前实际连的是哪个端口，再 grep 挂机工具（MAA/MaaEnd）配置里的 `127.0.0.1:<port>`——三处一对就知道哪台在跑、哪台闲置。
- 「程序安装目录」整体只是 ⛔，但里面常藏可回收子项（模拟器实例、下载中的 depot、旧版本目录）——拆开看，别因为父目录是 Program Files 就整块放过。
- 二级里凡是「删了要重新下载」的（未完成下载、安装包、驱动备份、闲置实例、旧运行时），风险一律写成「可重下/可重建 + 代价」，不要写成「无风险」。

## 单件删除请求（「X 可以删了吗」）

用户在流程外单独问某个目录能不能删时，仍按「先看后答」：

1. **只读盘点内容并分类**：按扩展名统计数量+合计大小（`for ext in yrm SAV ini exe mix; do ls -l *.$ext | awk ...`），把内容分成三类——可重下的本体（`.mix`/`.bin`/安装包/程序主体）、**私人数据**（存档 `.sav`、自攒的自定义地图/角色卡、键位与配置 ini）、可重建缓存。
2. **先确认是不是唯一副本**（`ls -d <盘>/<同名>*`），唯一副本要在答复里点明「删了只能重下本体，私人数据回不来」。
3. **量化收益**：给出 GB 数 + 占该盘剩余空间的百分比。空间宽松时如实说「删它只多 0.8%，不解决任何问题」——不要让用户以为在解决空间危机。
4. **给三选项**：备份私人数据后删（推荐，往往只有几十 MB）/ 直接删 / 保留。技术上先说清可行性（绿色版=删目录即卸载；装了服务/注册表的程序另说；桌面快捷方式会失效）。
5. 用户回「直接删」就不再走五阶段，一条命令删掉、`Test-Path` 复核、报前后剩余，并在报告里明确写「未备份的私人数据已随之删除」。

## Steam 卸载后的残留排查

用户说「我从 Steam 卸载了 X，还有没有相关文件残留」时，**全部只读查完、汇总成表再问，排查过程中不删任何东西**。固定按七处扫：`steamapps\common\<游戏>`（先 `find` 找 exe 区分「本体真删了只剩 mod」与「本体还在」）→ `appmanifest_<appid>.acf` → `workshop\content\<appid>` → `shadercache` / `downloading` / `compatdata` → `Steam\userdata\<id>\<appid>` → 模组管理器暂存（`%APPDATA%\Vortex\<game>`、`Vortex Mods`、Fluffy Mod Manager）→ `%LOCALAPPDATA%\<发行商>` / `Documents\<Game>`。

两条硬规则：① 游戏目录里的 `savedata_backup` / `*.sav` 是玩家存档，**先 Copy-Item 到 `E:\Hermes workspace\game-backups\<Game>\` 并用大小+SHA256 双校验，通过后才删父目录**；用户说「存档留着、其他删了」就是这个意思，不是把整个目录留着。② **不要手删 `appmanifest`**（库状态会乱），提醒用户在 Steam 内卸载。

清单、量级参考与报告口径见 `references/steam-uninstall-leftovers.md`。

## 阶段推进纪律

- 用户即使已经给出编号选择，也要照常输出该阶段的汇总/菜单，把选择回显成一行「你已选 X+Y（合计 Z GB）」再等一句确认；选择项和「进入阶段 N」同时到达时**不跳步**，阶段 3 依然不删除任何东西。
- 任何需要**改变运行状态**的前置动作（关 Edge、关 Steam、停服务）单独向用户要授权，写进阶段 4 清单的「前置条件」列；不关就跳过该项并把释放量相应下调后告知。
- 不可逆项（闲置模拟器实例、整台虚拟机、微信数据库目录、未完成下载）不能只写一行风险，按四段讲：**能得到的**（释放多少）/ **会失去的**（具体到哪类数据、是否可恢复、重来的代价）/ **不受影响的**（其他实例、正在挂机的进程、程序本体）/ **更稳妥的替代方案**（模拟器自带磁盘压缩、先启动实例看一眼、先不动）。用户会追问「这个到底什么意思、有什么后果」，提前答完省一轮。

## 删除量 ≠ 释放量（两个数都要报）

- 阶段 5 分别记两个数：①逐项 `freed` 之和（文件系统实测减少量，用 robocopy 扫描前后对比）；②卷剩余空间增量（`Win32_LogicalDisk.FreeSpace`）。二者对不上是常态，**不许抹平**。
- 差额首要来源是**卷影副本（VSS）**：写时复制会保留被删文件的旧数据块，快照到期前不释放。注册表 `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\SystemRestore` 里存在 `RPSessionInterval` 即说明系统保护启用。次要来源是执行期间在长的动态盘/日志（模拟器 vdi、挂机脚本、微信）。
- 差额超过约 1 GB 就在报告里单列一节：「文件减少 X GB，卷剩余仅 +Y GB，差 Z GB」，附管理员验证命令 `vssadmin list shadowstorage /for=D:`（普通权限查 `Win32_ShadowCopy` 会报初始化失败）与处置建议（系统保护→删除还原点/调小上限，或等快照过期）。对外口径说「实际可用增加了 Y GB」。
- 收尾再独立核验一次：重扫根目录总量与阶段 1 数值比对，确认「树减少量 ≈ 逐项之和」，把「删干净了」和「空间没回来」两件事分开证。

## shell 坑（Windows + MSYS bash）
- 给 powershell 传 Windows 路径参数用单引号正斜杠：`-Root 'D:/'`。写成 `-Root "D:\"` 时结尾反斜杠会转义引号，bash 报 `unexpected EOF while looking for matching` 且进程秒退（不是「扫描卡住」，别误判）。
- `.ps1` 内容保持**纯 ASCII**：无 BOM 的 UTF-8 中文字符串会被 PowerShell 5.1 按 GBK 读，报「字符串缺少终止符 / MissingExpressionAfterToken」。中文只放在最终 md 报告里。
- 后台任务被 `promoted to background process` 后，不要重复运行同一命令；先等通知或轮询产物文件是否生成。
