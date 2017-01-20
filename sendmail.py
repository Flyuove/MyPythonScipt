# -*- coding: utf-8 -*-

####################################################################
# Script    : mail_util
# PURPOSE   : Send email via smtp , for plain text and attachments
#
# CREATED:    2016-10-28    Eric Hu
#
#
# MODIFIED
# DATE        AUTHOR            DESCRIPTION
# -------------------------------------------------------------------
#
#####################################################################


import smtplib
import poplib
import os.path
import re
import base64
import quopri
import time
import datetime

import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.header import Header
from email.parser import Parser
from email import encoders


class MailUtil(object):
    __doc__ = """
    MIME Explained
    Multipart MIME email is in a tree structure

    MIMEMultipart
     ├──MIMEText (plain/html)
     ├──MIMEBase (base64 encoding attachment)
     ...
     └──MIMEBase ...

    This implementation actually wrap up MIMEMultipart and MIMEText into get_message
    If you want to add attachment, just simply use get_attachment_msg()

    Usage:
        m = MailUtil({
            "smtp": M_163_SMTP_SERVER,
            "smtp_port": 25,
            "pop3": M_163_POP3_SERVER,
            "pop3_port": 110,
            "email": "email@163.com",
            "password": "password"})
        msg = m.get_msg("subject", "body")
        msg.attach(m.get_attachment_msg("/home/user/test.png"))
        m.send(["email1@163.com"],msg)
    """
    mail_account = None
    pop3_conn = None

    def __init__(self, mail_account):
        self.mail_account = mail_account

    def send(self, to_addrs, msg):
        msg['From'] = self.mail_account["email"]
        msg['To'] = ';'+''.join(to_addrs)

        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+'   create smtp object and login')
        server = smtplib.SMTP(
            self.mail_account["smtp"],
            self.mail_account["smtp_port"])
        try:
            # server.set_debuglevel(1)
            server.login(
                self.mail_account["email"],
                self.mail_account["password"])
            time.sleep(3)
        except:
            pass
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+'   sendemail')
        server.sendmail(
            from_addr=self.mail_account["email"],
            to_addrs=to_addrs,
            msg=msg.as_string())

        time.sleep(5)
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+'   quit')
        server.quit()

    def get_msg(self, subject, body):
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+'   create message body')
        msg = MIMEMultipart('related')
        msg["Subject"] = Header(subject, 'utf-8')
        msg.preamble = 'This is a multi-part message in MIME format.'
        msgBody = MIMEText(body, 'plain', 'utf-8')
        msg.attach(msgBody)
        return msg

    def get_attachment_msg(self, filename):
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+'   attach ' + filename)

        # open file for read
        data = open(filename, 'rb')

        # guess main type and subtype
        ctype, encoding = mimetypes.guess_type(filename)
        if ctype is None or encoding is not None:
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)

        attachment_msg = MIMEBase(maintype, subtype)
        attachment_msg.set_payload(data.read())
        data.close()
        # encode as base64
        encoders.encode_base64(attachment_msg)

        basename = os.path.basename(filename)
        attachment_msg.add_header('Content-Disposition', 'attachment', filename=basename)
        return attachment_msg

    def guess_html(self, body):
        if (body.lower().find("</body>") >= 0 or
                    body.lower().find("</html>") >= 0 or
                    body.lower().find("</span>") >= 0 or
                    body.lower().find("</div>") >= 0 or
                    body.lower().find("</a>") >= 0):
            return True
        else:
            return False

    # refers to https://www.douban.com/group/topic/3573819/
    def resolve_base64(self, line):
        # print(line)
        # everything starting from = and ending with ?=
        result = ""
        while len(line) > 0:
            m = re.search(r"(=[?][uU][tT][fF].*[?]=)+", line)
            if (m != None):
                if (m.start() > 0):
                    result = result + line[0:m.start()]
                s = line[m.start():m.end()]
                flag = s[8:9]
                s = s[10:len(s) - 2]

                if (flag.lower() == "b"):
                    s = base64.decodebytes(s.encode('utf_8'))
                    s = s.decode("utf-8")
                else:
                    s = quopri.decodestring(s.encode("utf-8")).decode("utf-8")
                result = result + s

                line = line[m.end():]
            else:
                result = result + line
                line = ""

        # if starts with UTF-8
        if (result.find("=?UTF-8?") == 0):
            flag = result[8:9]
            result = result[10:]
            # print(result)
            if (flag.lower() == "b"):
                # For the robustness, ignore the incorrect base64 and unicode encoding
                result = result[0:len(result) // 4 * 4]
                result = base64.decodebytes(result.encode(encoding='utf_8', errors="ignore")).decode(encoding="utf-8",
                                                                                                     errors="ignore")
            else:
                result = quopri.decodestring(result.encode("utf-8")).decode("utf-8")

        return result

    def process_mail(self, lines):
        msg_content = ""
        for i in range(len(lines[1])):
            msg_content = msg_content + lines[1][i].decode("utf-8") + "\r\n"

        # 稍后解析出邮件:
        msg = Parser().parsestr(msg_content)
        mail_obj = {}

        if (msg.is_multipart()):
            parts = msg.get_payload()
            for n, part in enumerate(parts):
                content_type = part.get_content_type()
                if (content_type == "text/plain" or
                            content_type == "plain" or
                            content_type == "text/html" or
                            content_type == "html"):

                    mail_obj["subject"] = self.resolve_base64(msg.get("Subject"))
                    mail_obj["from_addr"] = self.resolve_base64(msg.get("From"))
                    mail_obj["to_addr"] = self.resolve_base64(msg.get("To"))

                    mail_obj["received"] = self.resolve_base64(msg.get("received"))
                    mail_obj["date"] = self.resolve_base64(msg.get("date"))

                    try:
                        mail_obj["body"] = part.get_payload(decode=True).decode(encoding="utf-8", errors="strict")
                    except:
                        mail_obj["body"] = part.get_payload(decode=True).decode(encoding="gbk", errors="strict")

                    if (self.guess_html(mail_obj["body"])):
                        mail_obj["body"] = re.sub("<[^>]+>", "", mail_obj["body"])
                    return mail_obj
        else:
            content_type = msg.get_content_type()
            if (content_type == "text/plain" or
                        content_type == "plain" or
                        content_type == "text/html" or
                        content_type == "html"):

                mail_obj["subject"] = self.resolve_base64(msg.get("Subject"))
                mail_obj["from_addr"] = self.resolve_base64(msg.get("From"))
                mail_obj["to_addr"] = self.resolve_base64(msg.get("To"))
                mail_obj["received"] = self.resolve_base64(msg.get("received"))
                mail_obj["date"] = self.resolve_base64(msg.get("date"))

                try:
                    mail_obj["body"] = msg.get_payload(decode=True).decode(encoding="utf-8", errors="strict")
                except:
                    mail_obj["body"] = msg.get_payload(decode=True).decode(encoding="gbk", errors="strict")

                if (self.guess_html(mail_obj["body"])):
                    mail_obj["body"] = re.sub("<[^>]+>", "", mail_obj["body"])
                return mail_obj

    def connect_pop3(self):
        self.pop3_conn = poplib.POP3(self.mail_account["pop3"])
        # self.pop3_conn.set_debuglevel(1)
        self.pop3_conn.user(self.mail_account["email"])
        self.pop3_conn.pass_(self.mail_account["password"])

    def disconnect_pop3(self):
        self.pop3_conn.quit()

    def list_pop3(self):
        l = self.pop3_conn.list()[1]
        list = []
        for i in range(len(l)):
            s = l[i].decode("utf-8")
            s = s.split(" ")
            list.append({"id": int(s[0]), "size": int(s[1])})
        return list

    def receive_pop3(self, id):
        lines = self.pop3_conn.retr(id)
        return self.process_mail(lines)




mail_account = {
        # 发送账户
        "smtp": 'smtp.163.com',
        "smtp_port": 25,
        "pop3": 'pop.163.com',
        "pop3_port": 110,
        "email": 'steamyu@163.com',
        "password": "a1111111"
        }

content = "您的账号为:\n\n" \
          "账号: var1 \n" \
          "密码: pass0117 \n" \
          "请在登陆后修改默认密码 \n\n" \
          "舆情系统地址: http://10.3.207.170:2443 \n\n" \
          "==================== \n" \
          "余生华 \n" \
          "[Talkingeyes]-舆情系统系统管理员 \n"

receives = ['steamyu@163.com']

def _send_mail(msg, to_addr):
    m = MailUtil(mail_account)
    for addr in to_addr:
        content = msg.replace("var1",addr)
        key = "Talkingeyes-舆情系统-账号 sid: " + str(int(time.time()))
        msg_struct = m.get_msg(key, content)
        m.send(addr, msg_struct)

_send_mail(content, receives)
