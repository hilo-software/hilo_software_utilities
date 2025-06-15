# projects/utilities/send_mail.py
import smtplib
from email.message import EmailMessage
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def send(from_addr: str, to_addr: str, app_key: str, msg: EmailMessage) -> None:
    '''
    Sends an email via Gmail SMTP.

    Args:
        from_addr (str): Sender's email address
        to_addr (str): Recipient's email address
        app_key (str): App-specific password for Gmail
        msg (EmailMessage): Message to send
    '''
    try:
        logger.info(f'[EMAIL] send')
        smtpobj = smtplib.SMTP('smtp.gmail.com', 587)
        smtpobj.ehlo()
        smtpobj.starttls()
        smtpobj.ehlo()
        smtpobj.login(from_addr, app_key)
        smtpobj.sendmail(from_addr, to_addr, msg.as_string())
        smtpobj.close()
        logger.info(f'[EMAIL] sent')
    except smtplib.SMTPException as e:
        logger.error(f'SMTP ERROR: Unable to send mail: {str(e)}')
    except Exception as e:
        logger.error(f'General ERROR: Unexpected Exception in send: {str(e)}')


def send_text_email(email: str, app_key: str, subject: str, content: str) -> None:
    if not email or not app_key:
        logger.warning('Email or app_key is missing, not sending.')
        return

    msg = EmailMessage()
    msg.set_content(content)
    msg['Subject'] = subject
    msg['From'] = email
    msg['To'] = email
    send(email, email, app_key, msg)


def send_file_email(email: str, app_key: str, subject: str, file_path: str) -> None:
    if not email or not app_key:
        logger.warning('Email or app_key is missing, not sending.')
        return

    try:
        with open(file_path, 'r') as f:
            content = f.read()
        send_text_email(email, app_key, subject, content)
    except IOError:
        logger.error(f'Could not read file: {file_path}')
    except Exception as e:
        logger.error(f'Unexpected error reading file: {str(e)}')
