# utils.py
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

def send_email_otp(recipient_email: str, otp_code: str):
    """Securely sends a 6-digit OTP to the user's email."""
    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_APP_PASSWORD")

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = "Group 5 Project - Your Security Code"

    body = f"Hello,\n\nYour Multi-Factor Authentication code is: {otp_code}\n\nThis code will expire in 10 minutes.\n\nSecurely,\nGroup 5 Security"
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls() 
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False