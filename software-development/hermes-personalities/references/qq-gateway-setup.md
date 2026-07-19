# QQ Bot 网关配置要点

## 平台识别
- Hermes 内置 QQ Bot 平台驱动：`gateway/platforms/qqbot/`
- 平台枚举值：`Platform.QQBOT = "qqbot"`（config.yaml 中用小写 `qqbot`）
- QQ Bot 使用 QQ 开放平台官方 API（`api.sgroup.qq.com`），不是个人 QQ 账号

## 配置格式（易错！）

### ❌ 错误写法
```yaml
platforms:
  qq:                          # ← key 错误！应该是 qqbot
    enabled: true
    uin: "12345678"            # ← QQ Bot 不需要 uin/password
    password: "xxx"
    app_id: "12345678"         # ← 应该嵌套在 extra 下
    client_secret: "xxx"
```

### ✅ 正确写法
```yaml
platforms:
  qqbot:                       # ← 正确的 key
    enabled: true
    extra:
      app_id: "12345678"       # ← 必须在 extra 下
      client_secret: "xxx"
```

配置命令：
```bash
hermes config set platforms.qqbot.enabled "true"
hermes config set platforms.qqbot.extra.app_id "你的AppID"
hermes config set platforms.qqbot.extra.client_secret "你的Secret"
```

## 验证规则
网关验证 QQ Bot 配置时读取 `cfg.extra.get("app_id")` 和 `cfg.extra.get("client_secret")`。
如果这两个值不在 `extra` 嵌套中→验证失败→平台不会加载→日志无任何 QQ 相关信息。

## 已知 Bug：is_reconnect 参数不兼容
**错误日志**：`✗ qqbot error: QQAdapter.connect() got an unexpected keyword argument 'is_reconnect'`

**原因**：`QQAdapter.connect()` 签名是 `async def connect(self) -> bool:`，但网关 runner 调用时传入了 `is_reconnect=True`。其他平台适配器支持此参数，QQ 适配器遗漏了。

**修复**：编辑 `gateway/platforms/qqbot/adapter.py`，将：
```python
async def connect(self) -> bool:
```
改为：
```python
async def connect(self, is_reconnect: bool = False) -> bool:
```

## Open Policy 陷阱（切勿踩坑！）

### 陷阱1：open policy 需要 ALLOW_ALL_USERS
设置 `dm_policy: open` 或 `group_policy: open` 时，网关会检查环境变量。如果没有设置 → 网关**拒绝启动**。

**错误日志**：
```
ERROR: qqbot has dm_policy/group_policy set to 'open' but neither
GATEWAY_ALLOW_ALL_USERS nor QQ_ALLOW_ALL_USERS is enabled.
```

**修复**：在 `~/.hermes/.env` 中添加：
```bash
QQ_ALLOW_ALL_USERS=true
```
⚠️ 注意：`export` 命令只在当前 shell 会话生效，网关读的是 `.env` 文件！

### 陷阱2：open policy 可能意外关闭 enabled
设置 `dm_policy: open` 时，`hermes config` 可能同时把 `enabled` 重置为 `false`。设置完成后务必验证：
```bash
grep -A5 "qqbot" ~/AppData/Local/hermes/config.yaml
# 确认 enabled: true
```

### 陷阱3：GATEWAY_ALLOW_ALL_USERS 对 QQ 不生效
`GATEWAY_ALLOW_ALL_USERS=true` 不会解锁 QQ Bot 的 open policy——必须用平台专属的 `QQ_ALLOW_ALL_USERS=true`。

## 备选方案：配对模式（推荐）
更安全的方式是不用 open policy，保持默认配对模式：
```bash
# 删掉 open policy 配置
hermes config set platforms.qqbot.dm_policy ""
hermes config set platforms.qqbot.group_policy ""
# 用户发消息后用 hermes pairing approve 批准
hermes pairing approve qqbot <用户哈希ID>
```

## 调试流程
1. 确认配置 key 是 `qqbot` 不是 `qq`
2. 确认 `app_id` 和 `client_secret` 在 `extra` 嵌套下
3. 确认 `enabled: true`
4. 如果要用 open policy，确认 `.env` 中有 `QQ_ALLOW_ALL_USERS=true`
5. 重启网关：`hermes gateway run --replace`
6. 查看日志：`tail -f ~/AppData/Local/hermes/logs/gateway.log | grep -i qq`
7. 成功标志：`✓ qqbot connected` + `Gateway running with 2 platform(s)`

## QQ 收不到消息？检查 QQ 开放平台侧
网关一切正常但收不到消息 → 问题在 QQ 开放平台：
- Bot 是否还在**沙盒模式**？需要**发布上线**（https://q.qq.com）
- C2C 私聊权限是否已开通？
- 手机 QQ 上是否已加 Bot 为好友？

## 配对审批
QQ Bot 需要配对才能接收新用户消息：
```bash
hermes pairing approve qqbot <用户ID>
```
