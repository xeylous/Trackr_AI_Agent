import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    def __init__(self):
        self.email = os.getenv("SMTP_EMAIL")
        self.password = os.getenv("SMTP_PASSWORD")

        if not self.email or not self.password:
            raise ValueError("❌ Missing SMTP_EMAIL or SMTP_PASSWORD in .env")

    def send_otp(self, to_email, otp):
        msg = MIMEText(f"🎉 Your Trackr AI Login Code:\n\n👉 {otp}\n\nExpires in 10 minutes.\n\n- Trackr AI")
        msg["Subject"] = "🔐 Your Trackr AI Login Code"
        msg["From"] = self.email
        msg["To"] = to_email

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(self.email, self.password)
                server.send_message(msg)
            print("📨 OTP email sent ✔")
            return True
        except Exception as e:
            print("❌ Email sending failed:", e)
            return False
