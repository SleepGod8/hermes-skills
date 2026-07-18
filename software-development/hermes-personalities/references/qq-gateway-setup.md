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

## 调试流程
1. 确认配置 key 是 `qqbot` 不是 `qq`
2. 确认 `app_id` 和 `client_secret` 在 `extra` 嵌套下
3. 重启网关：`hermes gateway run --replace`
4. 查看日志：`tail -f ~/AppData/Local/hermes/logs/gateway.log | grep -i qq`
5. 成功标志：`✓ qqbot connected` + `Gateway running with 2 platform(s)`

## 配对审批
QQ Bot 需要配对才能接收新用户消息：
```bash
hermes pairing approve qqbot <用户ID>
```
