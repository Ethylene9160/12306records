from bs4 import BeautifulSoup
import re
import pandas as pd
from enum import Enum
class TicketType(Enum):
    PURCHASE = "购票"
    REFUND = "退票"
    CHANGE = "改签"
    EXCHANGE = "兑票"

def truncate(input_string):
    delimiter = "为了确保旅客人身安全和列车运行秩序"
    truncated_string = input_string.split(delimiter)[0]
    return truncated_string
def extract_tickets_from_text(text, order_type, order_number, mail_date):
    # 匹配票价信息定位有效行（兼容全角/半角符号）
    ticket_lines = re.findall(r'.*票价[\d\.]+元.*', text)
    results = []

    for line in ticket_lines:
        # 统一替换全角符号为半角便于处理
        line = line.replace('，', ',').replace('．', '.').replace('：', ':')
        remark = ''

        match = re.search(
            r'(?:\d+\.)?'  # 可选编号前缀
            r'([^,]+),'  # 乘客姓名 (组1)
            r'(\d{1,2}月\d{1,2}日|\d{4}年\d{1,2}月\d{1,2}日)?'  # 日期 (组2)，兼容无年份
            r'(\d{1,2}:\d{2})(?:开)?,'  # 发车时间 (组3)
            r'([^-—,]+)[-—]([^,]+),'  # 始发站-终到站 (组4,5)
            r'([^,]+)次列车,'  # 车次 (组6)
            r'([^,]+车[^,]+),'  # 座位信息 (组7)
            r'([^,]+),'  # 座位类型 (组8)
            r'(?:成人票|儿童票|学生票)?,?'  # 可选票种
            r'票价([\d\.]+)元'  # 票价 (组9)
            r'(?:,.+)?'  # 忽略后面的所有内容
            r'(?:[，,。\.\s]|$)',  # 边界断言
            line
        )

        if order_type == TicketType.CHANGE:
            remark = re.search(r'改签费([\d\.]+)元', line).group(0) if '改签费' in line else '0' + '元'
        elif order_type == TicketType.REFUND:
            remark = re.search(r'退票费([\d\.]+)元', line).group(0) if '退票费' in line else '0' + '元'
        # TODo: 积分换票

        # 处理日期
        raw_date = match.group(2) if match else None
        full_date = None
        if raw_date:
            if '年' in raw_date:
                # 完整日期格式：2025年05月28日
                full_date = raw_date
            else:
                # 不完整日期格式：05月28日 → 补全年份
                full_date = f"{mail_date[:4]}年{raw_date}"
        if match:
            results.append({
                '乘车人': match.group(1).strip(),
                '日期': full_date,
                '发车时间': match.group(3),
                '始发站': match.group(4).strip(),
                '终到站': match.group(5).strip(),
                '车次': match.group(6),
                '坐席': match.group(8),
                '座位': match.group(7),
                '票价': match.group(9),
                '订单类型': order_type.value,
                '订单号': order_number,
                '备注': remark
            })
        else:
            print(f"无法解析行: {line}")
    return results

def extract_tickets(html_or_text, subject, mail_date):
    # 自动判断输入类型
    # find order number
    html_or_text = html_or_text.replace("\t", "").replace(" ", "")
    order_type = TicketType.PURCHASE
    if '退票' in subject:
        order_type = TicketType.REFUND
    elif '改签' in subject:
        order_type = TicketType.CHANGE
    # TODO： 积分换票
    # elif '' in subject:
    #     order_type = TicketType.EXCHANGE
    # elif not '支付' in subject:
    #     print(f"无法识别邮件标题为【{subject}】中的订单类型，请检查邮件主题或内容。")
    #     return []

    order_pattern = r'订单号码[\s：:]*([A-Za-z0-9]+)'
    match = re.search(order_pattern, html_or_text)

    if not match:  # 尝试更宽松的匹配
        order_pattern = r'14px;">(E[A-Za-z0-9]{9})</span>'
        match = re.search(order_pattern, html_or_text)


    order_number = match.group(1) if match else None
    if '<html' in html_or_text.lower() or '<div' in html_or_text.lower():
        soup = BeautifulSoup(html_or_text, 'html.parser')
        text = soup.get_text('\n')  # 保留换行信息
    else:
        text = truncate(html_or_text).replace("<br/><br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;", "")

    return extract_tickets_from_text(text, order_type, order_number, mail_date)
