import smtplib
from email.mime.text import MIMEText


def send_email(to, msg, subject, use_prefix=True):
    """
  Sends an email to a user. Expects 'to' to be a comma separated string of
  emails, and for 'msg' and 'subject' to be strings.
  """
    msg = MIMEText(msg)

    if use_prefix and '[ASCIT Donut]' not in subject:
        subject = '[ASCIT Donut] ' + subject

    msg['Subject'] = subject
    msg['From'] = 'auto@donut.caltech.edu'
    msg['To'] = to

    with smtplib.SMTP('localhost') as s:
        s.sendmail('auto@donut.caltech.edu', [to], msg.as_string())

def newsgroup_send_email(recipients, group, msg, subject):
    msg = MIMEText(msg)
    msg['Subject'] = subject
    msg['From'] = 'auto@donut.caltech.edu'
    msg['To'] = group.lower().replace(' ', '_')
    with smtplib.SMTP('localhost') as s:
        s.sendmail(
                'auto@donut.caltech.edu', 
                [msg['To']] + recipients, 
                msg.as_string())
