import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.mime.application import MIMEApplication


def send_email(sender, password, receiver, smtp_server,
               smtp_port, email_message, subject, attachment=None):
    message = MIMEMultipart()
    message['To'] = Header(receiver)
    message['From'] = Header(sender)
    message['Subject'] = Header(subject)
    message.attach(MIMEText(email_message, 'plain', 'utf-8'))
    if attachment:
        with open(attachment, 'rb') as file:
            att = MIMEApplication(file.read(), _subtype="zip")
            att.add_header('Content-Disposition', 'attachment',
                           filename=file.name)
            message.attach(att)
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        # server.connect()
        server.ehlo()
        server.login(sender, password)
        text = message.as_string()
        server.sendmail(sender, receiver, text)
        server.quit()