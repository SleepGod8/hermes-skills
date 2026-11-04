---
name: windows-disk-cleanup
description: Use when 清理 Windows 磁盘空间. 五阶段确认制+实测扫描+安全删点.
---

# Windows 磁盘清理（五阶段确认制）

用户给「清理 C/D 盘」类任务时，默认走五阶段，每阶段结束停下等确认，全程先只读后动手。

## 五阶段
1. **探测**：容量/已用/剩余/使用率 + 系统版本/用户/是否管理员 + 一级目录归属表 + 紧张度判断（空闲 <15% = 偏紧）。
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
- 虚拟机类：Activity/闲置实例要区分（看 vdi 最后写入时间 + 进程是否在跑）；MuMu `data.vdi` 是只增不减的动态盘，长期占用会持续膨胀。
- 删除时对目录型目标只清子项、保留父目录；不做通配符批量删除。
- 大目录删除用 `cmd /c rd /s /q "<dir>"`，比 `Remove-Item -Recurse -Force` 快一个量级（几十 GB 分钟级 vs 十几 GB 十几分钟）；`Remove-Item` 只留作单个被占用文件的回退手段。删完 `Test-Path` 复核该路径是否真的消失。
- `Export-Csv` / 重定向**不会自动建目录**，`-Out` 路径写错会静默失败：产物写完立即用 `search_files(target='files')` 或 `Test-Path` 核验文件存在，报告里引用的产物必须先确认能列出。
- Steam 的 `steamapps\downloading\<appid>` 是**未完成下载**（体积可达几十 GB，随下载持续增长）：先用 `steamapps\appmanifest_<appid>.acf` 判断该游戏是否真的已安装，删前必须 `Stop-Process -Name steam,steamwebhelper`，否则边写边删必然 PARTIAL。报告要写清「删=放弃本次进度，再装需重下」。
- 模拟器多开：`vms\<实例目录>` 一个子目录 = 一个安卓实例，每个实例一份 ~100 GB 级 `data.vdi`。判定活动性看 `data.vdi` 最后写入时间 + 是否有对应进程；**闲置实例是单块最大可回收项**，但它属于「该实例内所有 App/游戏进度」，只能列为二级需确认。
- **单位只用 1024 进制**：robocopy `/BYTES` 得字节后统一 `/1GB`，不要一处按 1000 换算 MB、另一处按 1024，否则同一项目会给出两个数字（如 9.83 vs 9.60 GB），用户会追问并要求校准。
- **基线在执行时实测**：阶段 5 的报告口径用执行脚本自己打印的 `FREEBEFORE`/`FREEAFTER`，不要复用阶段 1 或上一轮会话的剩余值。动态盘（模拟器 vdi）、日志、下载会在数小时内吃掉几十 GB，跨时段复用旧值必被用户发现对不上。
- 解析扫描 CSV 用 execute_code（内核 python），不要在 bash 里 `python -c`：shell 的 `python` 可能解析到项目桩解释器，直接报 `did not find executable`。

## 大占用项识别

按类型快速判定「这是不是能清的」；深度明细见 `references/big-consumer-identification.md`（Steam 未完成下载、模拟器多开 vdi、微信 file/attach/business 拆分、工程资料 zip、VM vmdk、安装包集合、驱动备份的判定法与优先级）。

- 先扫一级目录拿到 Top 10 再往下钻，**不要一上来全盘递归**；钻到第 2~3 层就能定性时立即停手。
- **盘位预期不同**：C 盘以缓存为主，清缓存能出几十 GB；数据盘（D/E）一级可清量常常 ≈0，大头全是实体数据（工程资料、微信文件、虚拟磁盘、未完成下载、安装包集合）。别承诺「清垃圾」能救数据盘，结论要落到「处理大件 or 迁移」。
- 模拟器实例归属判定（决定「删了会不会断挂机」）：读 `vms\<实例>\configs\vm_config.json` 的 `port_forward` 拿该实例 ADB 端口（典型 16384/16416…），`adb devices` 看当前实际连的是哪个端口，再 grep 挂机工具（MAA/MaaEnd）配置里的 `127.0.0.1:<port>`——三处一对就知道哪台在跑、哪台闲置。
- 「程序安装目录」整体只是 ⛔，但里面常藏可回收子项（模拟器实例、下载中的 depot、旧版本目录）——拆开看，别因为父目录是 Program Files 就整块放过。
- 二级里凡是「删了要重新下载」的（未完成下载、安装包、驱动备份、闲置实例、旧运行时），风险一律写成「可重下/可重建 + 代价」，不要写成「无风险」。

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
