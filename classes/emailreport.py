#! /usr/bin/python3

import smtplib
import traceback
import configparser

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

## MAIN EMAIL CONFIGURATION FILE PATH
EMAIL_CONFIG = "configs/email.cfg"

## Changes to the email configuration can be done on the 'configs/email.cfg' file

class EmailReport:
    def __init__(self, subject="ELK Health Alert", body="EMAIL BODY", table=None):
        config = configparser.ConfigParser(delimiters=('='))
        config.read(EMAIL_CONFIG)

        self.smtp_server  = config.get('EMAIL_SERVER_INFO', 'MX_SERVER')
        self.sender_email = config.get('EMAIL_SERVER_INFO', 'SENDING_ADDRESS')
        self.recipients   = config.get('EMAIL_SERVER_INFO', 'RECIPIENTS')
        self.subject      = subject

        message = MIMEMultipart()
        message['From'] = self.sender_email
        message['To'] = self.recipients
        message['Subject'] = self.subject
        message.attach(MIMEText(body, 'plain'))
        if table:
            message.attach(MIMEText(table, 'html'))
        self.content = message.as_string()

    def sendEmail(self):
        try :
            s = smtplib.SMTP(self.smtp_server)
            s.sendmail(self.sender_email, self.recipients.split(','), self.content)
            s.quit()
        except socket_error as err : 
            traceback.print_exc
        except Exception as err :
            traceback.print_exc

