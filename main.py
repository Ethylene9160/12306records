import extractor
import mail_receiver as receiver
import email
import pandas as pd

from email.header import decode_header

IMAP_SERVER = '' # Your IMAP server
EMAIL_ACCOUNT = '' # Your email account
PASSWORD = ''  # Your email password or app password

sender = '12306@rails.com.cn'
file_name = 'tickets.xlsx' # 你希望保存的文件名

mail = receiver.connect_email(IMAP_SERVER, EMAIL_ACCOUNT, PASSWORD)
email_ids = receiver.search_emails(mail, sender)
tickets_list = []

try:
    if not email_ids:
        print("没有找到来自12306的邮件")
    else:
        print(f"找到 {len(email_ids)} 封来自12306的邮件")

        for idx, e_id in enumerate(email_ids[:], 1):  # 只处理最近5封，避免太多
            status, msg_data = mail.fetch(e_id, '(RFC822)')
            msg = email.message_from_bytes(msg_data[0][1])

            subject = email.header.decode_header(msg["Subject"])[0][0]
            subject_format = subject.decode('gbk') if isinstance(subject, bytes) else subject
            from_ = msg.get('From')
            from_format = email.utils.parseaddr(from_)[1]
            print(f'处理第 {idx} 封邮件: {subject_format} 来自: {from_format}')
            body = None
            # 提取邮件正文
            for part in msg.walk():
                body = receiver.extract_body(part)
                date = receiver.get_email_date(msg)

                if isinstance(body, bytes):
                    body = body.decode('gbk', errors='ignore')  # Decode bytes to string

                # 分析邮件正文。
                tickets_info = extractor.extract_tickets(body, subject_format)
                for ticket in tickets_info:
                    tickets_list.append(ticket)
                # 如果你希望保存邮件，可以解注释下一行：
                # receiver.save_email(idx, sender, date, body)
except Exception as e:
    print(f"发生错误: {e}")
finally:
    mail.logout()

df = pd.DataFrame(tickets_list)
print(df)
# df.to_excel(file_name, index=False, sheet_name='车票信息')
# print(f'Successfully saved tickets to {file_name}.')