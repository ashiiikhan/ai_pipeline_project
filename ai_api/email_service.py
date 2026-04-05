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

    # ✅ Validate required config
    if not host or not user or not password:
        raise ValueError("SMTP configuration missing")

    if isinstance(to_emails, str):
        to_list = [e.strip() for e in to_emails.split(",") if e.strip()]
    else:
        to_list = to_emails or []

    if not to_list:
        raise ValueError("No recipient email provided")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = frm
    msg["To"] = ", ".join(to_list)

    msg.set_content(body)
    msg.add_alternative(
        f"<html><body><pre>{body}</pre></body></html>",
        subtype="html"
    )

    # ✅ Safe attachment handling
    for p in attachments or []:
        if not os.path.exists(p):
            print(f"Attachment not found: {p}")
            continue

        ctype, encoding = mimetypes.guess_type(p)
        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"

        maintype, subtype = ctype.split("/", 1)

        try:
            with open(p, "rb") as f:
                msg.add_attachment(
                    f.read(),
                    maintype=maintype,
                    subtype=subtype,
                    filename=os.path.basename(p)
                )
        except Exception as e:
            print(f"Failed to attach {p}: {e}")

    # ✅ More stable SMTP handling
    try:
        with smtplib.SMTP(host, port, timeout=10) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(user, password)
            smtp.send_message(msg)
    except Exception as e:
        print("Email sending failed:", e)