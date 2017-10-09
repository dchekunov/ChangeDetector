import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class MailSender:
    def __init__(self, login, password, server, port=25):
        self.login = login
        self.password = password
        self.server = server
        self.port = port

    def send_message(self, to, subject, text):
        msg = MIMEMultipart()
        msg['From'] = self.login
        msg['To'] = to
        msg['Subject'] = subject

        msg.attach(MIMEText(text))

        mailserver = smtplib.SMTP(self.server, self.port)
        mailserver.ehlo()
        mailserver.starttls()
        mailserver.ehlo()
        mailserver.login(self.login, self.password)

        mailserver.sendmail(self.login, to, msg.as_string())

        mailserver.quit()
