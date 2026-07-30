# Email SMTP Setup

## QQ 邮箱

| 项 | 值 |
|---|-----|
| SMTP 服务器 | `smtp.qq.com` |
| 端口 | `465`（SSL） |
| 账号 | 完整邮箱地址，如 `807047353@qq.com` |
| 密码 | **授权码**（非 QQ 登录密码） |

### 获取授权码
1. 登录 QQ 邮箱 → 设置 → 账户
2. 找到「POP3/SMTP 服务」→ 开启
3. 按指引发送短信获取授权码

### Python 示例

```python
import smtplib
from email.mime.text import MIMEText

mail_host = 'smtp.qq.com'
mail_user = 'your@qq.com'
mail_pass = '你的授权码'
mail_port = 465

sender = 'your@qq.com'
receiver = 'target@qq.com'

message = MIMEText('邮件正文', 'plain', 'utf-8')
message['From'] = sender
message['To'] = receiver
message['Subject'] = '邮件标题'

try:
    smtp = smtplib.SMTP_SSL(mail_host, mail_port)
    smtp.login(mail_user, mail_pass)
    smtp.sendmail(sender, [receiver], message.as_string())
    smtp.quit()
    print("✅ 发送成功")
except Exception as e:
    print(f"❌ 发送失败: {e}")
```

## 163 邮箱

| 项 | 值 |
|---|-----|
| SMTP 服务器 | `smtp.163.com` |
| 端口 | `465`（SSL） |
| 密码 | **授权码**（非登录密码） |

## 安全提醒

- ⚠️ 不要把授权码硬编码在代码里
- 建议改用环境变量：`os.getenv('MAIL_PASS')`
- 设置环境变量：`export MAIL_PASS='你的授权码'`
