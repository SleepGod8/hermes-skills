# dsh-desktop 凭据故障实录（2026-08-19）

## 环境
- 产品：DeepSeek Harness EAC 桌面客户端 v4.1.0，安装于 `E:\Deepseek Harness EAC\`
- 未打包源码：`resources\app\`（main.js 159KB、balance.js、assets/plugins/dsh-side-session/lib/index.js 等）
- 依赖：`@deepseek-ai/dsh` 0.1.0-rc.6

## 用户问题
「Deepseek Harness EAC 里显示 DeepSeek 的 API 密钥由启动环境提供(只读)，要怎么配？」

## 诊断链

### 1. 确认「只读」来源 = 环境变量已有值
```
reg query "HKCU\Environment" | grep -i deepseek
→ DEEPSEEK_API_KEY  REG_SZ  sk-f27c8…9e54ef   （存在！）
→ ANTHROPIC_BASE_URL  https://api.deepseek.com/anthropic
→ ANTHROPIC_API_KEY  REG_SZ  sk-f27c8…6254ef
```
注意：bash `env | grep -i deepseek` 里**看不到** DEEPSEEK_API_KEY（只有 ANTHROPIC_MODEL），注册表才权威。

### 2. 实测 key 有效性
- 注册表 DEEPSEEK_API_KEY（…9e54ef）→ chat/completions **401**：
  `{"error":{"message":"Authentication Fails, Your api key: ****54ef is invalid","type":"authentication_error"}}`
- Hermes `C:\Users\80704\AppData\Local\hermes\.env` 的 DEEPSEEK_API_KEY（…6254ef，35 字符）→ **200 OK**，model: deepseek-v4-flash

### 3. 根因
用户换过 key：新 key（…6254ef）只同步到了 `ANTHROPIC_API_KEY` 和 Hermes .env，**漏了注册表 `DEEPSEEK_API_KEY`**。DSH 读环境变量（旧 key）→ 界面只读 + 实际请求 401。这正是用户来问「怎么配」的原因。

### 4. 修复
```bash
setx DEEPSEEK_API_KEY "<有效key>"     # 从 Hermes .env 读入，避免用户手输
reg query "HKCU\Environment" /v DEEPSEEK_API_KEY   # 验证后6位 6254ef / 长度 35
```
端到端验证：chat/completions 200 OK；balance 返回 CNY total_balance 61.67（granted_balance 0.00 = 全是充值余额，is_available 字段可能缺失为 None，属正常）。

### 5. 收尾
用户重启 DSH（完全退出）后生效；告知「只读」提示会保留，属正常状态。

## 教训
1. 「由启动环境提供(只读)」= 环境变量注入的 key，UI 只读是设计如此，不是需要配置的提示。
2. 环境变量存在时 credentials.yaml 完全失效 —— 改文件不生效先查环境变量。
3. 多位置共用 key 时（Hermes .env / ANTHROPIC_API_KEY / DEEPSEEK_API_KEY / 第三方工具配置）换 key 必须全量同步。
4. 判断两把 key 是否相同：错误信息只给后 4 位（****54ef），要对比完整长度 + 后 6 位。

## 技术坑：GBK 输出
中文 Windows 上 `setx` 成功输出为 GBK（乱码显示「�ɹ�: ָ����ֵ�ѵõ����档」=「成功: 指定的值已得到保存」）。
Python 读取：`subprocess.run(cmd, capture_output=True, text=True, errors="replace")`，否则 `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xb3`。
