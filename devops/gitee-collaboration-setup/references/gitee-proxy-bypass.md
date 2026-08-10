# Gitee 绕过代理：原理与实测记录

## 为什么命令行空串失败

git config 命令行把空字符串值视为「删除配置项」（等同 `--unset`），而不是「设为空值」。

实测（本机 Windows + git-bash）：
```
PS> git config --global http.https://gitee.com.proxy ""
PS> git config --global --get http.https://gitee.com.proxy
（输出空行）
```
随后验证：`git config --global --get ...; echo $?` → `exit=1`（key 不存在），`git config --global --list | grep gitee` → 无输出。命令无任何报错，静默删除。

而**配置文件里的空值**会被 git 解析为「禁用该 URL 的代理」：
```ini
[http "https://gitee.com"]
	proxy =
```

## 实测对比（GIT_TRACE_CURL）

修改前（全局代理 127.0.0.1:12450 生效，走了代理隧道）：
```
== Info: Establish HTTP proxy tunnel to gitee.com:443
== Info: Established connection to 127.0.0.1 (127.0.0.1 port 12450) from 127.0.0.1 port 10160
```

修改后（直连 Gitee 真实 IP，无任何代理痕迹）：
```
== Info: Established connection to gitee.com (180.76.198.77 port 443) from 192.168.110.17 port 13322
```

## 命令语法说明

- key `http.https://gitee.com.proxy` 解析为：section=`http`，subsection=`https://gitee.com`，key=`proxy`
- 匹配规则：scheme + hostname 匹配 `https://gitee.com/` 下所有路径
- 验证 key 存在性（区分「缺失」和「空值」）：`git config --global --get <key>; echo $?`（0=存在，1=不存在），或 `git config --global --list | grep <key>`
- 修改 `.gitconfig` 用 read_file + patch，不要用 echo 追加（格式错会破坏整个文件）

## 相关环境事实

- 本机全局代理：`http.proxy` / `https.proxy` = `http://127.0.0.1:12450`（用户代理软件，常断）
- 策略：Gitee 直连（本配置），GitHub 等翻墙场景保留全局代理
- 用户终端习惯：PowerShell（`PS C:\Users\...>`），但 git-bash 读同一份 `~/.gitconfig`
