from datetime import datetime
import imaplib
import email
from email.header import decode_header
import re
import os
from bs4 import BeautifulSoup

# 连接邮箱服务器
def connect_email(IMAP_SERVER, EMAIL_ACCOUNT, PASSWORD):
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_ACCOUNT, PASSWORD)
    mail.select('inbox')  # 选择收件箱
    return mail


# 搜索指定发件人的邮件
def search_emails(mail, sender):
    status, messages = mail.search(None, f'(FROM "{sender}")')
    if status == 'OK':
        return messages[0].split()
    return []

# 解析邮件内容
def parse_email(raw_email):
    msg = email.message_from_bytes(raw_email)
    subject = decode_header(msg["Subject"])[0][0]
    if isinstance(subject, bytes):
        subject = subject.decode()

    # 获取邮件正文
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                body = part.get_payload(decode=True).decode()
                break
    else:
        body = msg.get_payload(decode=True).decode()

    return subject, body

# 获取邮件日期
def get_email_date(msg):
    date_str = msg["Date"]
    if not date_str:
        return 'Invalid Date'
        # return datetime.now().strftime("%Y%m%d")

    # 尝试解析邮件日期
    try:
        date_tuple = email.utils.parsedate_tz(date_str)
        if date_tuple:
            local_date = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
            return local_date.strftime("%Y%m%d")
    except:
        pass

    return datetime.now().strftime("%Y%m%d")


# 提取邮件正文
def get_email_body(msg):
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            # 跳过附件
            if "attachment" in content_disposition:
                continue

            if content_type == "text/html":
                body = part.get_payload(decode=True).decode()
                break
    else:
        body = msg.get_payload(decode=True).decode(errors='ignore')

    return body.strip()


# 保存邮件内容
def save_email(index, sender, date, body, output_dir="emails"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    filename = f"{index}_{sender.split('@')[0]}_{date}.html"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(body)

    print(f"已保存邮件: {filepath}")
def extract_body(part):
    if part.is_multipart():
        # 如果是 multipart，递归处理子部分
        for subpart in part.get_payload():
            result = extract_body(subpart)
            if result:  # 如果找到内容，返回
                return result
    else:
        # 如果不是 multipart，尝试获取内容
        content_type = part.get_content_type()
        if content_type in ["text/plain", "text/html"]:
            try:
                return part.get_payload(decode=True).decode('gbk', errors='ignore')
            except UnicodeDecodeError:
                return part.get_payload(decode=True).decode('gbk', errors='ignore')
        else:
            print(f"无法识别的内容类型: {content_type}")
            # 如果需要，可以在这里处理其他类型的内容
    return None

