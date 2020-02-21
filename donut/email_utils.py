from email.message import EmailMessage
import smtplib
"""The domain to send emails from"""
DOMAIN = 'beta.donut.caltech.edu'
"""The username @ the domain to send emails as"""
SENDER = 'auto'


def send_email(to, msg, subject, use_prefix=True):
    """
    Sends an email to a user.
    'to' should be an email or list of emails.
    'msg' and 'subject' must be strings.
    """

    message = EmailMessage()
    message.set_content(msg)
    message['Subject'] = '[ASCIT Donut] ' + subject if use_prefix else subject
    message['From'] = SENDER + '@' + DOMAIN
    message['To'] = ', '.join(to) if type(to) in (list, tuple) else to

    with smtplib.SMTP('localhost') as smtp:
        smtp.send_message(message)
