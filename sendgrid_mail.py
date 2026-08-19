import os
import json
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "no-reply@example.com")
SENDGRID_URL = "https://api.sendgrid.com/v3/mail/send"


def _send_via_sendgrid(recipient_email: str, subject: str, text: str, html: str, attachments=None) -> bool:
    if not SENDGRID_API_KEY:
        print("SendGrid API key not set — fallback email payload:\n", text)
        return False

    payload = {
        "personalizations": [{
            "to": [{"email": recipient_email}],
            "subject": subject
        }],
        "from": {"email": SENDER_EMAIL},
        "content": [
            {"type": "text/plain", "value": text},
            {"type": "text/html", "value": html}
        ]
    }

    if attachments:
        payload["attachments"] = attachments

    headers = {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        r = requests.post(SENDGRID_URL, headers=headers, data=json.dumps(payload), timeout=20)
        r.raise_for_status()
        return True
    except Exception as e:
        print("SendGrid send failed:", e)
        try:
            print("Response:", r.status_code, r.text)
        except Exception:
            pass
        return False


def send_otp_email(recipient_email: str, otp: str) -> bool:
    subject = "Your HealthTech OTP"
    body_text = f"Your one-time code is: {otp}\nIt expires in 2 minutes."
    body_html = f"<p>Your one-time code is: <strong>{otp}</strong></p><p>It expires in 2 minutes.</p>"
    return _send_via_sendgrid(recipient_email, subject, body_text, body_html)


def send_report_email(recipient_email: str, subject: str, text: str, html: str, pdf_path: str) -> bool:
    if not SENDGRID_API_KEY:
        print("SendGrid API key not set — report email (dev fallback):", subject)
        return False

    try:
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
    except Exception as e:
        print("Failed to read PDF for attachment:", e)
        return False

    encoded = base64.b64encode(pdf_bytes).decode("ascii")
    attachment = [{
        "content": encoded,
        "type": "application/pdf",
        "filename": pdf_path.split('/')[-1],
        "disposition": "attachment"
    }]

    return _send_via_sendgrid(recipient_email, subject, text, html, attachments=attachment)
