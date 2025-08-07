# 铁旅纵横

当你打开航旅纵横app，查看自己多年来的飞行轨迹，是否认为这是一个很好的打发时间的东西。
于是你打开了12306，发现自己坐了多年的火车，却没有类似于飞行轨迹的“铁路轨迹”，是否深感遗憾。
如果你也无聊如我，想看自己买的火车票去了哪些地方，那么可以来看看这个脚本：
如果你在12306购票且绑定了邮箱，你的购票信息将会被发送到你的邮箱中。
这个脚本通过登录你的邮箱，在**收件箱**中获取这些邮件，并将火车票信息提取出来，保存到一个Excel表格中。

## 配置

确保你的python满足`requirements.txt`中的要求。

## 使用

去到`main.py`，将：

> ```python
> IMAP_SERVER = '' # IMAP服务i其
> EMAIL_ACCOUNT = '' # 邮箱账号
> PASSWORD = ''  # 邮箱登录授权码
> ```
>

以常用的QQ邮箱为例，例如你的QQ邮箱是your_mail_address@qq.com，授权码是abcdefgh，你的配置应该是：

```python
IMAP_SERVER = 'imap.qq.com'
EMAIl_ACCOUNT = 'your_mail_address@qq.com'
PASSWORD = 'abcdefgh'
```

需要注意的是，**授权码**和邮箱的**登录密码**不同，需要在你的邮箱的“设置”中查看。

此外，你可以修改`file_name = 'tickets.xlsx' # 你希望保存的文件名`以调整想要保存的表格文件名。

最后，运行`main.py`，它会自动登录你的邮箱，获取邮件内容，并将火车票信息保存到当前文件夹下的`tickets.xlsx`中。

> P.S. 如果你的12306邮件没有保存在收件箱而是保留在邮箱的其它文件夹内，可以在`mail_receiver.py`中进行修改：
>
> ```python
> def connect_email(IMAP_SERVER, EMAIL_ACCOUNT, PASSWORD):
>     mail = imaplib.IMAP4_SSL(IMAP_SERVER)
>     mail.login(EMAIL_ACCOUNT, PASSWORD)
>     mail.select('inbox')  # 选择收件箱
>     return mail
> ```
>
> 
