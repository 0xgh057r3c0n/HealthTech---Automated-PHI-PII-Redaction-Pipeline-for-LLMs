import random
from datetime import datetime, timedelta

otp_store = {}
OTP_TTL_SECONDS = 120


def save_otp(email: str):
    otp = str(random.randint(100000, 999999))
    otp_store[email] = {
        "otp": otp,
        "created_at": datetime.utcnow()
    }
    return otp


def verify_otp(email: str, otp: str):
    record = otp_store.get(email)

    if not record:
        return False

    if datetime.utcnow() - record["created_at"] > timedelta(seconds=OTP_TTL_SECONDS):
        otp_store.pop(email, None)
        return False

    is_valid = record["otp"] == str(otp).strip()

    if is_valid:
        otp_store.pop(email, None)

    return is_valid