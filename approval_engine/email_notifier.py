import os
import smtplib
from email.mime.text import MIMEText

LOG_FILE = "logs/notifier.log"

def send_notification(subject, message):
    os.makedirs("logs", exist_ok=True)

    with open(LOG_FILE, "a") as f:
        f.write(f"{subject} - {message}\n")

    print(f"[NOTIFY] {subject}: {message}")

    try:
        SMTP_SERVER = "smtp.gmail.com"
        SMTP_PORT = 587
        EMAIL = "madhangir2005@gmail.com"
        PASSWORD = "bobm eazk ccxu savv"

        msg = MIMEText(message)
        msg["Subject"] = subject
        msg["From"] = EMAIL
        msg["To"] = EMAIL

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)
        server.quit()

    except Exception:
        pass