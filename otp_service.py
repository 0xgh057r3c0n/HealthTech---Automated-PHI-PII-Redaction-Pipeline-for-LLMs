import secrets
from datetime import datetime, timedelta

otp_store = {}
OTP_TTL_SECONDS = 120


def _normalize_email(email: str) -> str:
    return (email or "").strip().lower()


def save_otp(email: str):
    normalized_email = _normalize_email(email)
    if not normalized_email:
        raise ValueError("Email is required")

    otp = str(secrets.randbelow(1_000_000)).zfill(6)
    otp_store[normalized_email] = {
        "otp": otp,
        "created_at": datetime.utcnow()
    }
    return otp


def verify_otp(email: str, otp: str):
    normalized_email = _normalize_email(email)
    if not normalized_email:
        return False

    record = otp_store.get(normalized_email)
    if not record:
        return False

    if datetime.utcnow() - record["created_at"] > timedelta(seconds=OTP_TTL_SECONDS):
        otp_store.pop(normalized_email, None)
        return False

    provided_otp = str(otp).strip()
    if not provided_otp or not provided_otp.isdigit():
        return False

    expected_otp = str(record["otp"]).strip()
    is_valid = expected_otp == provided_otp if len(provided_otp) == 6 else expected_otp == provided_otp.zfill(6)

    if is_valid:
        otp_store.pop(normalized_email, None)

    return is_valid