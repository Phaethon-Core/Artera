from fastapi import HTTPException
import time
import secrets
import hashlib
import os
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


def otp_rate_limit(email: str, timestamps: dict, max_requests: int, window: int):
    current_time = time.time()

    if email not in timestamps:
        timestamps[email] = []

    timestamps[email] = [t for t in timestamps[email]
                         if current_time - t <= window]

    if len(timestamps[email]) >= max_requests:
        raise HTTPException(
            status_code=429, detail="Too many requests. Please try again later.")

    timestamps[email].append(current_time)


def generate_otp():
    return str(secrets.randbelow(900000)+100000)


def hash_otp(otp: str):
    return hashlib.sha256(otp.encode()).hexdigest()


def send_otp_email(otp_payload):
    subject = f"Your OTP for Login - Artera"

    body = f"""
    <html>
    <body>
        <p>Dear User,</p>
        <p>Your OTP for login is: <strong>{otp_payload['otp']}</strong></p>
        <p>This OTP is valid for 5 minutes.</p>
        <p>Thank you for using Artera!</p>
    </body>
    </html>
    """

    email_sent = send_email(otp_payload["email"], subject, body)

    if not email_sent:
        raise HTTPException(
            status_code=500, detail="Failed to send OTP email")


def send_email(to_email, subject, body):
    try:
        message = MIMEMultipart()
        message["From"] = EMAIL_USER
        message["To"] = to_email
        message["Subject"] = subject

        message.attach(MIMEText(body, "html"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, to_email, message.as_string())

        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
