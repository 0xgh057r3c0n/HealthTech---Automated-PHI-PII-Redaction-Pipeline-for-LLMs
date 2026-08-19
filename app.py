import os
import requests
from dotenv import load_dotenv

os.environ["PYTHONUNBUFFERED"] = "1"
load_dotenv()

from fastapi import FastAPI, Header, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel


from redactor import get_redaction_details, redact_text

# ===== ADDED FOR PDF REPORT =====
from report_generator import generate_report
# ================================


from otp_service import save_otp, verify_otp
from sendgrid_mail import send_otp_email, send_report_email

from auth import create_token, verify_token



app = FastAPI()



# ---------------- TEMPLATES ---------------- #

templates = Jinja2Templates(
    directory="templates"
)



# ---------------- PERSISTED USERS DB ---------------- #
import sqlite3
import random

DB_PATH = os.path.join(os.getcwd(), "data.db")
# single connection for simplicity; allow cross-thread access for this demo
DB_CONN = sqlite3.connect(DB_PATH, check_same_thread=False)
DB_CONN.execute("""CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY,
    password TEXT,
    role TEXT,
    email TEXT
)""")
DB_CONN.execute("""CREATE TABLE IF NOT EXISTS links(
    from_user TEXT,
    to_user TEXT,
    UNIQUE(from_user,to_user)
)""")
DB_CONN.commit()


def db_add_user(username, password, role, email):
    try:
        DB_CONN.execute(
            "INSERT INTO users(username,password,role,email) VALUES (?,?,?,?)",
            (username, password, role, email),
        )
        DB_CONN.commit()
        return True
    except Exception as e:
        print("db_add_user:", e)
        return False


def db_get_user(username):
    cur = DB_CONN.execute(
        "SELECT username,password,role,email FROM users WHERE username=?", (username,)
    )
    row = cur.fetchone()
    if not row:
        return None
    return {"password": row[1], "role": row[2], "email": row[3]}


def db_get_all_users():
    cur = DB_CONN.execute("SELECT username,password,role,email FROM users")
    return {r[0]: {"password": r[1], "role": r[2], "email": r[3]} for r in cur.fetchall()}


def db_create_link(a, b):
    try:
        DB_CONN.execute(
            "INSERT OR IGNORE INTO links(from_user,to_user) VALUES (?,?)", (a, b)
        )
        DB_CONN.execute(
            "INSERT OR IGNORE INTO links(from_user,to_user) VALUES (?,?)", (b, a)
        )
        DB_CONN.commit()
    except Exception as e:
        print("db_create_link:", e)


def db_load_links():
    cur = DB_CONN.execute("SELECT from_user,to_user FROM links")
    res = {}
    for f, t in cur.fetchall():
        res.setdefault(f, set()).add(t)
    return res


def db_seed_random(doctors=6, patients=20):
    cur = DB_CONN.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] > 0:
        return
    for i in range(1, doctors + 1):
        uname = f"doctor{i}"
        email = f"{uname}@clinic.local"
        db_add_user(uname, "1234", "doctor", email)
    for i in range(1, patients + 1):
        uname = f"patient{i}"
        email = f"{uname}@clinic.local"
        db_add_user(uname, "1234", "patient", email)
    # create random patient->doctor links
    for p in range(1, patients + 1):
        d = random.randint(1, doctors)
        db_create_link(f"patient{p}", f"doctor{d}")


# initialize seed and in-memory caches

def _is_placeholder_value(value: str | None) -> bool:
    if value is None:
        return True
    cleaned = value.strip()
    if not cleaned:
        return True
    lowered = cleaned.lower()
    placeholders = ("your_", "replace_", "demo", "example", "changeme")
    return any(token in lowered for token in placeholders)


def refresh_recaptcha_config():
    global RECAPTCHA_SECRET, RECAPTCHA_SITE_KEY
    load_dotenv(override=True)
    RECAPTCHA_SECRET = (os.getenv("RECAPTCHA_SECRET") or "").strip()
    if _is_placeholder_value(RECAPTCHA_SECRET):
        RECAPTCHA_SECRET = ""
    RECAPTCHA_SITE_KEY = (os.getenv("RECAPTCHA_SITE_KEY") or "").strip()
    if _is_placeholder_value(RECAPTCHA_SITE_KEY):
        RECAPTCHA_SITE_KEY = ""


refresh_recaptcha_config()

db_seed_random()
users = db_get_all_users()
_links = db_load_links()


# ---------------- REQUEST MODELS ---------------- #

class RedactRequest(BaseModel):
    text: str
    # optional: act on behalf of another linked user (doctor <-> patient linking)
    target_username: str = None



class OTPRequest(BaseModel):

    email: str



class OTPVerify(BaseModel):

    email: str
    otp: str



class LoginRequest(BaseModel):
    username: str
    password: str
    # captcha token from client (reCAPTCHA v2)
    captcha: str = None


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    role: str = "patient"
    # captcha token from client (reCAPTCHA v2)
    captcha: str = None


class RegisterVerify(BaseModel):
    username: str
    email: str
    otp: str
    password: str
    role: str = "patient"


class LinkRequest(BaseModel):
    other_username: str


# ---------------- FRONTEND PAGES ---------------- #

@app.get("/")
def home(request: Request):
    refresh_recaptcha_config()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "recaptcha_site_key": RECAPTCHA_SITE_KEY
        }
    )



@app.get("/dashboard")
def dashboard(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "request": request
        }
    )


@app.get("/reports/{filename}")
def download_report(filename: str):
    return FileResponse(
        os.path.join("reports", filename)
    )


# ---------------- EMAIL REPORT ENDPOINT ---------------- #
from pydantic import BaseModel


class EmailReportRequest(BaseModel):
    filename: str
    recipient: str = None


@app.post("/email-report")
def email_report(data: EmailReportRequest, authorization: str = Header(None)):
    """Authenticated endpoint to email a generated PDF report to the report owner or a specified recipient.

    Body: { "filename": "report_xxx.pdf", "recipient": "optional@domain" }
    """
    if not authorization:
        return {"error": "Unauthorized"}
    token = authorization.replace("Bearer ", "")
    user = verify_token(token)
    if not user:
        return {"error": "Invalid token"}

    # determine recipient: explicit or report owner
    recipient = data.recipient
    if not recipient:
        # attempt to map token username/email
        user_email = user.get("email")
        if not user_email:
            # try to map username to email from DB
            current_username = user.get("username")
            if current_username:
                u = db_get_user(current_username)
                user_email = u.get("email") if u else None
        recipient = user_email

    if not recipient:
        return {"error": "No recipient available"}

    report_path = os.path.join("reports", data.filename)
    if not os.path.exists(report_path):
        return {"error": "Report not found"}

    subject = f"HealthTech Audit Report: {data.filename}"
    text = "Please find the attached audit PDF report."
    html = "<p>Please find the attached audit PDF report.</p>"

    ok = send_report_email(recipient, subject, text, html, report_path)
    if ok:
        return {"message": "Email sent", "recipient": recipient}
    else:
        return {"error": "Failed to send email"}


# ---------------- OTP LOGIN ---------------- #

def verify_captcha(token: str) -> bool:
    """
    Verify reCAPTCHA token server-side. Refresh environment values each call so .env edits
    are picked up without restarting the process.
    """
    refresh_recaptcha_config()
    if not RECAPTCHA_SECRET:
        print("RECAPTCHA_SECRET not configured — captcha is disabled on this server")
        return False

    if not token:
        return False

    try:
        resp = requests.post("https://www.google.com/recaptcha/api/siteverify", data={
            "secret": RECAPTCHA_SECRET,
            "response": token
        }, timeout=5)
        data = resp.json()
        return data.get("success", False)
    except Exception as e:
        print("Error verifying captcha:", e)
        return False


@app.post("/send-otp")
def send_otp(data: OTPRequest):

    if not data.email or "@" not in data.email:
        return {
            "error": "Please provide a valid email address"
        }

    otp = save_otp(data.email)
    send_otp_email(data.email, otp)

    return {
        "message": "OTP sent successfully",
        "email": data.email
    }


@app.post("/register")
def register(data: RegisterRequest):

    # captcha check
    if not verify_captcha(data.captcha):
        if not RECAPTCHA_SECRET:
            return {"error": "reCAPTCHA is not configured on this server. Add your Google site key and secret in .env to enable registration."}
        return {"error": "reCAPTCHA verification failed. Please complete the challenge and try again."}

    if not data.username or not data.email or not data.password:
        return {
            "error": "Username, email and password are required"
        }

    if data.username in users:
        return {
            "error": "Username already exists"
        }

    if "@" not in data.email:
        return {
            "error": "Please provide a valid email address"
        }

    otp = save_otp(data.email)
    send_otp_email(data.email, otp)

    return {
        "message": "Registration OTP sent successfully",
        "email": data.email,
        "username": data.username,
        "role": data.role
    }


@app.post("/register/verify")
def register_verify(data: RegisterVerify):

    if not verify_otp(data.email, data.otp):
        return {
            "error": "Invalid or expired OTP"
        }

    # check persisted store for existing username
    existing = db_get_user(data.username)
    if existing:
        return {"error": "Username already exists"}

    success = db_add_user(data.username, data.password, data.role, data.email)
    if not success:
        return {"error": "Failed to create user"}

    # refresh in-memory cache
    users[data.username] = db_get_user(data.username)

    token = create_token({
        "username": data.username,
        "email": data.email,
        "role": data.role
    })

    return {
        "message": "Registration successful",
        "token": token,
        "role": data.role,
        "username": data.username
    }





@app.post("/verify-otp")
def verify_otp_api(data: OTPVerify):


    if verify_otp(
        data.email,
        data.otp
    ):


        role = "patient"


        if "doctor" in data.email.lower():

            role = "doctor"



        token = create_token({

            "email":
            data.email,

            "role":
            role

        })


        return {


            "message":
            "Login successful",


            "token":
            token,


            "role":
            role

        }



    return {"error": "Invalid OTP"}


# Linking endpoints: allows a logged-in user to link with another user (doctor<->patient)
@app.post("/link")
def create_link(data: LinkRequest, authorization: str = Header(None)):
    if not authorization:
        return {"error": "Unauthorized"}
    token = authorization.replace("Bearer ", "")
    user = verify_token(token)
    if not user:
        return {"error": "Invalid token"}
    current_username = user.get("username")
    if not current_username:
        email = user.get("email")
        if email:
            current_username = next((u for u, v in users.items() if v.get("email") == email), None)
    if not current_username:
        return {"error": "Cannot determine username from token"}
    other = data.other_username
    if other not in users:
        return {"error": "Other user does not exist"}
    # create mutual link (persisted)
    db_create_link(current_username, other)
    # also update in-memory cache
    _links.setdefault(current_username, set()).add(other)
    _links.setdefault(other, set()).add(current_username)

    return {"message": f"{current_username} linked with {other}"}


@app.get("/links")
def list_links(authorization: str = Header(None)):
    if not authorization:
        return {"error": "Unauthorized"}
    token = authorization.replace("Bearer ", "")
    user = verify_token(token)
    if not user:
        return {"error": "Invalid token"}
    current_username = user.get("username")
    if not current_username:
        email = user.get("email")
        if email:
            current_username = next((u for u, v in users.items() if v.get("email") == email), None)
    if not current_username:
        return {"error": "Cannot determine username from token"}
    linked = list(_links.get(current_username, set()))
    return {"linked": linked}


# ---------------- USER LOGIN ---------------- #

@app.post("/login")
def login(data: LoginRequest):

    # captcha check
    if not verify_captcha(data.captcha):
        if not RECAPTCHA_SECRET:
            return {"error": "reCAPTCHA is not configured on this server. Add your Google site key and secret in .env to enable login."}
        return {"error": "reCAPTCHA verification failed. Please complete the challenge and try again."}

    user = users.get(data.username)

    if not user:
        return {
            "error": "Invalid credentials"
        }

    if user["password"] != data.password:
        return {
            "error": "Invalid credentials"
        }

    token = create_token({
        "username": data.username,
        "email": user.get("email"),
        "role": user["role"]
    })

    return {
        "token": token,
        "role": user["role"]
    }









# ---------------- PROTECTED REDACT API ---------------- #

@app.post("/redact")
def redact(
    data: RedactRequest,
    authorization: str = Header(None)
):

    # AUTH CHECK
    if not authorization:
        return {"error": "Unauthorized"}

    token = authorization.replace("Bearer ", "")
    user = verify_token(token)

    if not user:
        return {"error": "Invalid token"}

    # resolve current username (token may contain username or only email for OTP flows)
    current_username = user.get("username")
    if not current_username:
        # try to map email back to username in the in-memory users store
        email = user.get("email")
        if email:
            current_username = next((u for u, v in users.items() if v.get("email") == email), None)

    # if acting on behalf of another user, ensure link exists
    target_for_report = None
    if data.target_username:
        if data.target_username not in users:
            return {"error": "Target user does not exist"}
        if not current_username:
            return {"error": "Cannot determine requesting username for delegation"}
        linked = _links.get(current_username, set())
        if data.target_username not in linked:
            return {"error": "Not authorized to act on behalf of that user"}
        target_for_report = data.target_username

    # REDACTION ENGINE
    redaction_details = get_redaction_details(data.text)
    redacted_text = redaction_details["redacted_text"]
    entities = redaction_details["entities"]

    # ===== ADDED FOR PDF REPORT =====
    report_username = target_for_report or current_username or user.get("email", "Unknown")
    report_path = generate_report(
        username=report_username,
        original_text=data.text,
        redacted_text=redacted_text,
        entities=entities
    )
    # ================================

    return {
        "user": user,
        "original": data.text,
        "redacted": redacted_text,
        "entities_found": len(entities),
        "entity_types": list(set(entities)),
        "fallback_redacted": redaction_details.get("fallback_redacted_text"),
        "groq_redacted": redaction_details.get("llm_redacted_text"),
        "ai_review_enabled": redaction_details.get("ai_review_enabled", False),
        "report_path": report_path
    }