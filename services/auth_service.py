import random
import os
import yagmail
from datetime import datetime, timedelta


class AuthService:
    def __init__(self, memory_service):
        self.memory = memory_service
        self.otp_store = {}

        # Email Config
        self.sender_email = os.getenv("SMTP_EMAIL")
        self.sender_password = os.getenv("SMTP_PASSWORD")

        try:
            self.yag = yagmail.SMTP(self.sender_email, self.sender_password)
            print("📧 Email service connected ✔️")
        except Exception as e:
            print("❌ Failed to connect to email service:", e)
            self.yag = None

    def generate_otp(self):
        return str(random.randint(100000, 999999))

    def start_login(self, email: str) -> bool:
        otp = self.generate_otp()
        expiry = datetime.utcnow() + timedelta(minutes=5)

        self.otp_store[email] = {"otp": otp, "expires": expiry}

        # If email sending works
        # If email sending works
        if self.yag:
            try:
                self.yag.send(
                    email,
                    "Your Trackr AI Login Code",
                    f"👋 Hey!\n\nYour login code is: **{otp}**\n\nIt expires in 5 minutes.\n💛 Trackr AI"
                )
                print(f"📨 OTP sent to {email}")
                return True
            except Exception as e:
                print("❌ Failed to send email:", e)

        # Fallback (debug mode)
        print(f"\n⚠️ EMAIL DEBUG MODE — OTP: {otp}\n")
        return True

    def verify(self, email: str, otp_attempt: str) -> bool:
        record = self.otp_store.get(email)

        if not record:
            return False

        if datetime.utcnow() > record["expires"]:
            del self.otp_store[email]
            return False

        if otp_attempt == record["otp"]:
            del self.otp_store[email]
            return True

        return False
