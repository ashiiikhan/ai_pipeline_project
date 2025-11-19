import os
import smtplib
import mimetypes
from email.message import EmailMessage

def send_email(subject, body, to_emails, attachments=None):
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT") or 587)
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    frm = os.getenv("SMTP_FROM") or user

    if isinstance(to_emails, str):
        to_list = [e.strip() for e in to_emails.split(",") if e.strip()]
    else:
        to_list = to_emails or []

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = frm
    msg["To"] = ", ".join(to_list)
    msg.set_content(body)
    msg.add_alternative(f"<html><body><pre>{body}</pre></body></html>", subtype="html")

    for p in attachments or []:
        ctype, encoding = mimetypes.guess_type(p)
        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        with open(p, "rb") as f:
            msg.add_attachment(
                f.read(), maintype=maintype, subtype=subtype, filename=os.path.basename(p)
            )

    with smtplib.SMTP(host, port) as smtp:
        smtp.starttls()
        smtp.login(user, password)
        smtp.send_message(msg)
