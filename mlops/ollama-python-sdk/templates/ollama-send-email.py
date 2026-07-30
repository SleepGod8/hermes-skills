"""
Ollama 本地大模型 + QQ邮箱自动发邮件
流程：调用本地模型生成内容 → 清理输出 → 通过QQ邮箱发送

使用方式：
  1. 修改 model 为你本地已下载的模型名（ollama list 查看）
  2. 修改 mail_user/mail_pass 为你的QQ邮箱和授权码
  3. 修改 receiver 为收件人邮箱
  4. 运行：python ollama-send-email.py
"""
from ollama import chat, ChatResponse
import smtplib
from email.mime.text import MIMEText
import os
import re


def clean_model_output(text: str) -> str:
    """清理 qwen2.5 等模型添加的免责声明/注释"""
    # 去掉所有【注：...】或[注：...]及类似注释
    text = re.sub(r'[【\[]\s*[注备注提示此处]+\s*[：:].*?[】\]]', '', text)
    # 去掉所有方括号注释
    text = re.sub(r'\[.*?\]', '', text)
    # 去掉以"注"/"备注"/"提示"开头的行
    text = re.sub(r'\n?\s*(注|备注|提示)[：:].*', '', text)
    # 去掉"纯属虚构"相关文字
    text = re.sub(r'[（(]?纯属虚构[）)]?.*', '', text)
    return text.strip()


# ============================================================
# 1️⃣ 调用本地 Ollama 模型，生成内容
# ============================================================
res: ChatResponse = chat(
    model="qwen2.5:7b",                # 建议：qwen2.5:7b（中文好，速度适中）
    messages=[
        {
            "role": "system",
            "content": "你是秦始皇嬴政。直接输出信件正文，不要包含任何免责声明、虚构声明、安全提示、备注或注释。"
        },
        {
            "role": "user",
            "content": "写一封请求资助50元用于复兴大秦帝国的信件，承诺事成之后册封官职。要求：①正文必须出现'五十'②落款必须是秦始皇③不要加任何'注'等附加文字"
        }
    ]
)

print("✅ AI 生成的内容（原始）：")
print(res.message.content)
print("-" * 50)

# ============================================================
# 1.5️⃣ 清理免责声明和注释
# ============================================================
content = clean_model_output(res.message.content)
print("📮 清理后的正文：")
print(content)
print("-" * 50)

# ============================================================
# 2️⃣ 配置 QQ 邮箱信息
# ============================================================
mail_host = 'smtp.qq.com'
mail_user = 'your@qq.com'
# ⚠️ 使用邮箱授权码（不是登录密码），建议用环境变量
#    os.getenv('MAIL_PASS')
mail_pass = 'your_auth_code'
mail_port = 465

sender = 'your@qq.com'        # 发件人
receiver = 'your@qq.com'      # 收件人（可改）

# ============================================================
# 3️⃣ 构建邮件
# ============================================================
message = MIMEText(content, 'plain', 'utf-8')
message['From'] = sender
message['To'] = receiver
message['Subject'] = 'AI 自动生成的内容'

# ============================================================
# 4️⃣ 发送邮件（带错误处理）
# ============================================================
try:
    smtp = smtplib.SMTP_SSL(mail_host, mail_port)
    smtp.login(mail_user, mail_pass)
    smtp.sendmail(sender, [receiver], message.as_string())
    smtp.quit()
    print("✅ 邮件发送成功！")
except Exception as e:
    print(f"❌ 邮件发送失败: {e}")
