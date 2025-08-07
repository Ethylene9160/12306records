import extractor
import mail_receiver as receiver
import email
import pandas as pd

from email.header import decode_header

IMAP_SERVER = '' # IMAP服务器
EMAIL_ACCOUNT = '' # 邮箱账号
PASSWORD = ''  # 邮箱登录授权码

sender = '12306@rails.com.cn'
file_name = 'tickets.xlsx' # 你希望保存的文件名

tickets_list = []
mail = None
try:
    mail = receiver.connect_email(IMAP_SERVER, EMAIL_ACCOUNT, PASSWORD)
    email_ids = receiver.search_emails(mail, sender)
    if not email_ids:
        print("没有找到来自12306的邮件")
    else:
        print(f"找到 {len(email_ids)} 封来自12306的邮件")

        for idx, e_id in enumerate(email_ids[:], 1):
            status, msg_data = mail.fetch(e_id, '(RFC822)')
            msg = email.message_from_bytes(msg_data[0][1])

            subject = email.header.decode_header(msg["Subject"])[0][0]
            subject_format = subject.decode('gbk') if isinstance(subject, bytes) else subject
            from_ = msg.get('From')
            from_format = email.utils.parseaddr(from_)[1]
            print(f'处理第 {idx} 封邮件: {subject_format} 来自: {from_format}')

            # 提取邮件正文
            body = None
            date = None
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    body = receiver.extract_body(part)
                    date = receiver.get_email_date(msg)

                if isinstance(body, bytes):
                    body = body.decode('gbk', errors='ignore')  # Decode bytes to string
            if not body:
                print(f"未识别到【{subject_format}】邮件的正文内容。")
                continue
            tickets_info = extractor.extract_tickets(body, subject_format, date)
            for ticket in tickets_info:
                tickets_list.append(ticket)
            # 如果你希望保存邮件正文，可以解注释下一行：
            # receiver.save_email(idx, sender, date, body)
except Exception as e:
    print(f"发生错误: {e}")
finally:
    if mail:
        mail.logout()

df = pd.DataFrame(tickets_list)
print(df)
df.to_excel(file_name, index=False, sheet_name='车票信息')
print(f'Successfully saved tickets to {file_name}.')