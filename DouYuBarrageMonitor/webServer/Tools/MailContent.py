# File Usage:
#
# Author:

import smtplib
from email.mime.text import MIMEText

from DouYuBarrageMonitor import settings

mail_host = settings.MAIL_HOST
mail_user = settings.MAIL_USER
mail_pass = settings.MAIL_PWD

sender = settings.SEND_FROM_USER
receivers = settings.SEND_TO_USER


def send_email(content, title):
    message = MIMEText(content, 'plain', 'utf-8')
    message['From'] = "{}".format(sender)
    message['To'] = ",".join(receivers)
    message['Subject'] = title

    try:
        smtpObj = smtplib.SMTP(mail_host, 25)
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("mail has been send successfully.")
    except smtplib.SMTPException as e:
        print(e)
