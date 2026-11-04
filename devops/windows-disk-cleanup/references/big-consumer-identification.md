# 大占用项识别表（按类型判定 → 优先级 → 处置）

用于阶段 2 标注时的定性参考。原则：**先看类型再看体积**——体积最大的不一定是能删的。

| 类型 | 识别特征 | 优先级 | 处置与代价 |
|---|---|---|---|
| Steam 未完成下载 | `steamapps\downloading\<appid>`，几十 GB 且持续增长；`steamapps` 下没有对应 `appmanifest_<appid>.acf` | 二级 | 删=放弃这次进度；先关 `steam`/`steamwebhelper`。若用户想装，反而要提示先腾出足够空间，否则永远下不完 |
| Steam 已装游戏 | `steamapps\common\<game>` + 有 appmanifest（`ls steamapps/appmanifest_*.acf \| wc -l` 即已装数量） | 三级 | 走 Steam 客户端卸载，别手删。注意在别的盘下可能只装了几个小游戏、几百 GB 全在 `downloading` 里 |
| Steam 创意工坊 | `steamapps\workshop` | 二级 | 取消订阅/清缓存可回收；删后对应游戏 mod 失效 |
| 模拟器活动实例 | `vms\<实例>\data.vdi` 最后写入=今天，且有 VMM/Player 进程 | ⛔ | 运行中，删了实例报废 |
| 模拟器闲置实例 | 另一个 `vms\<实例>` 的 vdi 数天未写、无对应进程 | 二级 | 单块最大可回收项（可达 ~100 GB），代价=该实例内所有 App/游戏进度丢失 |
| 模拟器动态盘膨胀 | 同一 vdi 数小时内涨几十 GB | — | 只增不减，用模拟器自带磁盘压缩（见下）或迁实例 |
| 雷电/其他安卓模拟器 | `LDPlayer9\vms\leidian0|1` 等实例目录，各几十~上百 GB | 二级 | 与 MuMu 同理：自带磁盘压缩保数据；长期未启动（半年以上）可整实例删除 |
| Docker Desktop / WSL2 磁盘 | `<docker-data>\DockerDesktopWSL\disk\docker_data.vhdx`，几十 GB；Docker 未运行也照样占 | 二级 | 停 WSL 后压 vhdx（见下）；回收量 ≈ vhdx 大小 − 容器内实际用量 |
| 解压软件临时目录 | `Bandizip\BNZ.*`（每个 1~1.6 GB，内含未清掉的 .rar/.zip） | 一级 | 解压完成后的残留，直接删；批量前确认没有解压任务在跑 |
| 页面文件 | 根目录 `pagefile.sys`（十几~几十 GB），随内存压力伸缩 | ⛔ | 系统托管，禁止手删。它会让卷剩余在数小时内跳变几十 GB，读到异常波动先查它 |
| 微信聊天文件 | `xwechat_files\<wxid>\msg\file`（文档/压缩包）、`msg\attach`（图片附件）、`msg\video` | 二级/三级 | 禁止手删目录；引导「微信→设置→存储空间→管理」按时间/类型清，保住数据库索引与文字记录 |
| 微信缓存 | `<wxid>\business`（公众号/视频号）、`db_storage` | 二级 | business 属纯缓存可重下；db_storage 是索引，别动 |
| 工程/项目资料 | 目录名带 竣工资料/图纸/方案/监理，内含超大 zip | 三级 | 只提示大小；报告里禁止复述内部敏感文件名 |
| 保密资料目录 | 名称含「保密」 | 三级 | **不展开扫描**，只报总量；需要用户明确授权才看结构 |
| 私密/成人向收藏 | 盘符下以人名缩写命名的目录（如 `ZSC`），内含大量整合包/游戏 | 三级 | 只展开两级看结构就停；报告中性写「个人收藏 + 大小」，不复述内部文件名、不评价、不建议删 |
| VMware 虚拟机 | `*.vmdk` + `*.vmx` 同目录 | 二级 | 数月未启动的实验机可清；确认不是唯一副本 |
| 软件安装包集合 | `D:\软件` 这类目录，内含历年 `*Setup.exe`/`*.iso` | 二级 | 同款已装即可清；重装需重下 |
| 驱动包备份 | `Drivers\{AMDVGA,NVVGA,NVGFE}` 等整机迁移备份 | 二级 | 驱动已装好，备份可重下；保留最近一代更稳 |
| 旧运行时/旧版本工具 | `.cache\codex-runtimes`、`MAA-v*`（新版本已装） | 二级 | 可重下；旧版留新版删旧版 |
| 包管理器缓存 | uv/npm/pnpm/pip 缓存 | 一级 | 官方命令清，自动重建 |
| 显卡着色器缓存 | `NVIDIA\DXCache`、`GLCache` | 一级 | 驱动重建，仅首启变慢 |
| 系统更新残留 | `Windows\SoftwareDistribution\Download`、`Windows\Logs` | 一级（需管理员） | 无提权必失败，直接标跳过 |
| 未完成临时文件 | `AppData\Local\Temp`、`%TEMP%` | 一级 | 占用中的子项会失败，属正常 PARTIAL |

## 虚拟磁盘压缩配方（保数据回收空间，优先于删除）

先算可回收量 = **磁盘文件大小 − 客户机实际用量**。这个差值就是「删了文件但块没还回来」的空洞，压缩只吃掉这部分，不影响数据。

**安卓模拟器（MuMu / 雷电）**
1. 客户机在跑时取 `adb shell df -h /data`（实例 ADB 端口见 `vms\<实例>\configs\vm_config.json` 的 `port_forward`，典型 16384/16416…）。
2. MuMu：主窗口实例卡片 `⋮` → 磁盘清理；设备关着时会提示「请先启动安卓设备」，先开机再点，它会自己关机再清理。
3. 压缩后必须**重新启动客户机验证**：`pm list packages -3 | wc -l` 数量不变、`/data` 用量不变——这是唯一能证明「数据没丢」的证据，报告里要贴出来。

**WSL2 / Docker Desktop**
```powershell
wsl --shutdown                     # Docker Desktop 先退出，否则 vhdx 被占用
# 管理员 diskpart：
#   select vdisk file="E:\docker-data\DockerDesktopWSL\disk\docker_data.vhdx"
#   attach vdisk readonly
#   compact vdisk
#   detach vdisk
```
压缩前向用户要「停容器」的授权（会影响 Dify/Milvus 等在跑的服务），并在报告里说明重启后需重新拉起容器。

## 判断顺序

1. 一级目录 Top 10 → 只盯 ≥1 GB 的项，小于 0.5 GB 的合并成一行「其余 N 项」。
2. 对每个大项问三句：**在跑吗？删了会怎样？能重建吗？** 三句都有答案才给优先级。
3. 父目录是 Program Files / ProgramData 时，往下拆一层找「实例/下载缓存/旧版本」这类可回收子项。
4. 拿不准用途（`b1`、空壳目录、陌生命名）→ 标「需人工确认」，不主动删，也不做猜测性建议。
5. 体积大且「删了心疼、压了不疼」的（模拟器实例、WSL/Docker 磁盘、虚拟机盘）→ 一律先给**压缩**方案，把删除列为次选。
