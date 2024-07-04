import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pydantic import EmailStr
from typing import List


def send_email(email: List[EmailStr], subject: str, body):
    smtp_server = "smtp.gmail.com"
    smtp_port = 465
    smtp_username = "masalasorie@gmail.com"
    smtp_password = "jyyifooudojlescd"

    sender_email = smtp_username

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = ", ".join(email)
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "html"))

    try:
        # Use SMTP_SSL for port 465
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, email, msg.as_string())
            return {"message": "Email sent successfully", "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}
