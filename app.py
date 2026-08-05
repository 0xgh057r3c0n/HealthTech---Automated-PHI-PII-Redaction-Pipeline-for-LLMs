import os

os.environ["PYTHONUNBUFFERED"] = "1"


from fastapi import FastAPI, Header, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel


from redactor import get_redaction_details, redact_text

# ===== ADDED FOR PDF REPORT =====
from report_generator import generate_report
# ================================


from otp_service import save_otp, verify_otp
from email_service import send_otp_email

from auth import create_token, verify_token



app = FastAPI()



# ---------------- TEMPLATES ---------------- #

templates = Jinja2Templates(
    directory="templates"
)



# ---------------- TEMP USERS DB ---------------- #

users = {

    "doctor1": {
        "password": "1234",
        "role": "doctor",
        "email": "doctor1@clinic.local"
    },

    "patient1": {
        "password": "1234",
        "role": "patient",
        "email": "patient1@clinic.local"
    }

}


# ---------------- REQUEST MODELS ---------------- #

class TextInput(BaseModel):

    text: str



class OTPRequest(BaseModel):

    email: str



class OTPVerify(BaseModel):

    email: str
    otp: str



class LoginRequest(BaseModel):

    username: str
    password: str


class RegisterRequest(BaseModel):

    username: str
    email: str
    password: str
    role: str = "patient"


class RegisterVerify(BaseModel):

    username: str
    email: str
    otp: str
    password: str
    role: str = "patient"





# ---------------- FRONTEND PAGES ---------------- #

@app.get("/")
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request
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


# ---------------- OTP LOGIN ---------------- #

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

    if data.username in users:
        return {
            "error": "Username already exists"
        }

    users[data.username] = {
        "password": data.password,
        "role": data.role,
        "email": data.email
    }

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



    return {


        "error":
        "Invalid OTP"

    }







# ---------------- USER LOGIN ---------------- #

@app.post("/login")
def login(data: LoginRequest):

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

    data: TextInput,

    authorization: str = Header(None)

):


    # AUTH CHECK

    if not authorization:


        return {

            "error":
            "Unauthorized"

        }





    token = authorization.replace(

        "Bearer ",

        ""

    )



    user = verify_token(

        token

    )



    if not user:


        return {

            "error":
            "Invalid token"

        }







    # REDACTION ENGINE


    redaction_details = get_redaction_details(
        data.text
    )

    redacted_text = redaction_details["redacted_text"]
    entities = redaction_details["entities"]



    # ===== ADDED FOR PDF REPORT =====

    report_path = generate_report(

        username=user.get(
            "username",
            user.get("email", "Unknown")
        ),

        original_text=data.text,

        redacted_text=redacted_text,

        entities=entities

    )

    # ================================





    return {


        "user":
        user,


        "original":
        data.text,


        "redacted":
        redacted_text,


        "entities_found":
        len(entities),


        "entity_types":
        list(set(entities)),


        "fallback_redacted":
        redaction_details.get("fallback_redacted_text"),


        "groq_redacted":
        redaction_details.get("llm_redacted_text"),


        "ai_review_enabled":
        redaction_details.get("ai_review_enabled", False),


        # ===== ADDED =====
        "report_path":
        report_path
        # ================

    }