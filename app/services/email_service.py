import os
from email.message import EmailMessage
import aiosmtplib

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL") or SMTP_USERNAME
FROM_NAME = os.getenv("SMTP_FROM_NAME", "Hiring Team")
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "true").lower() == "true"


async def send_application_confirmation(
    to_email: str,
    applicant_name: str,
    job_title: str,
):
    if not EMAIL_ENABLED:
        return

    msg = EmailMessage()
    msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
    msg["To"] = to_email
    msg["Subject"] = f"Application received: {job_title}"

    msg.set_content(
        f"Hi {applicant_name},\n\n"
        f"Thanks for applying for {job_title}. We’ve received your application.\n\n"
        "Regards,\n"
        f"{FROM_NAME}\n"
    )

    await aiosmtplib.send(
        msg,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        start_tls=True,
        username=SMTP_USERNAME,
        password=SMTP_PASSWORD,
        timeout=20,
    )
