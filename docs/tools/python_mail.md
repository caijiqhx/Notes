# Python Mailer

> [用 Python 实现自动发送邮件](https://zhuanlan.zhihu.com/p/89868804)

在服务器上挂选课脚本需要完成后发送邮件通知，学习一下怎么用 python 发邮件。

```python
import smtplib
import email
# 负责构造文本
from email.mime.text import MIMEText
# 负责构造图片
from email.mime.image import MIMEImage
# 负责将多个对象集合起来
from email.mime.multipart import MIMEMultipart
from email.header import Header

mail_host = "mail.cstnet.cn"
mail_port = 465
mail_sender = "qinhaoxiang20@mails.ucas.ac.cn"
sender_name = "Python Mailer"
mail_passwd = "NOTHING1strue!@#"
mail_receivers = ["qhx_1998@qq.com"]

mm = MIMEMultipart("related");

# 邮件主题
subject_content = """Python Mail Test"""
# 设置发送者,注意严格遵守格式,里面邮箱为发件人邮箱
mm["From"] = sender_name + "<" + mail_sender + ">"
# 设置接受者,注意严格遵守格式,里面邮箱为接受者邮箱
mail_receiver = ""
for i,receiver in enumerate(mail_receivers):
    mail_receiver += "receiver_" + str(i+1) + "_name<" + receiver + ">"
    if i != len(mail_receivers) - 1:
        mail_receiver += ","
print(mail_receiver)
mm["To"] = mail_receiver
# 设置邮件主题
mm["Subject"] = Header(subject_content,'utf-8')

# 邮件正文内容
body_content = """Hello, this is a test for python mailer."""
# 构造文本,参数：正文内容，文本格式，编码方式
message_text = MIMEText(body_content,"plain","utf-8")
# 向MIMEMultipart对象中添加文本对象
mm.attach(message_text)


# # 二进制读取图片
# image_data = open('a.jpg','rb')
# # 设置读取获取的二进制数据
# message_image = MIMEImage(image_data.read())
# # 关闭刚才打开的文件
# image_data.close()
# # 添加图片文件到邮件信息当中去
# mm.attach(message_image)

# # 构造附件
# atta = MIMEText(open('sample.xlsx', 'rb').read(), 'base64', 'utf-8')
# # 设置附件信息
# atta["Content-Disposition"] = 'attachment; filename="sample.xlsx"'
# # 添加附件到邮件信息当中去
# mm.attach(atta)

# 创建SMTP对象
stp = smtplib.SMTP_SSL(mail_host, mail_port)
# stp.starttls()
# stp.connect(mail_host, mail_port)  
stp.set_debuglevel(1)
stp.login(mail_sender, mail_passwd)
stp.sendmail(mail_sender, mail_receivers, mm.as_string())
print("邮件发送成功")
# 关闭SMTP对象
stp.quit()
```