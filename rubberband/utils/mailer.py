"""Mathods for sending emails."""
import json
import smtplib
from email.mime.text import MIMEText

from tornado.options import options


def sendmail(message, recipient):
    """
    Send an email.

    Parameters:
    message : str -- Message to send.
    recipient : str -- Recipient of mail.
    """
    msg = MIMEText(json.dumps(message))

    msg['Subject'] = "Rubberband file upload: {}".format(message["status"])
    msg['From'] = options.smtp_from_address
    msg['To'] = recipient

    # Send the message via our own SMTP server.
    s = smtplib.SMTP_SSL(options.smtp_host, port=options.smtp_port)
    s.login(options.smtp_username, options.smtp_password)
    s.send_message(msg)
    s.quit()
