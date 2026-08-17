# HealthTech PHI/PII Redaction Pipeline

A healthcare privacy and clinical documentation workflow for detecting, masking, and auditing protected health information (PHI) and personally identifiable information (PII) before any clinical content is sent to external AI systems.

This application is designed for secure patient and doctor workflows, with a professional UI and a downloadable PDF report that preserves core clinical context while protecting identifying data.

---

## What the application does

This project performs the following core functions:

- accepts patient or doctor clinical text through a web dashboard
- identifies PHI/PII such as names, emails, phone numbers, dates, and hospital/location references
- redacts sensitive values before safe downstream processing
- keeps the clinical note and doctor recommendations usable for review
- generates a professional PDF report for audit and record keeping
- supports role-aware workflows for patient and doctor users
- provides protected, token-based access to the redaction API

---

## What the application has

### Role-based healthcare dashboard
- Patient workflow for intake and health-note input
- Doctor workflow for clinical note entry and patient guidance notes
- Separate UI states depending on the signed-in role
- Secure authentication using JWT tokens

### PHI/PII detection and masking engine
- Microsoft Presidio integration when available
- Regex-based fallback masking when Presidio is unavailable
- Entity detection for categories including:
  - PERSON
  - EMAIL_ADDRESS
  - PHONE_NUMBER
  - DATE_TIME
  - HOSPITAL_NAME
  - LOCATION

### Protected redaction API
- FastAPI backend with a protected /redact endpoint
- Bearer token validation
- Safe return payload with redacted output and detected entity list
- Optionally includes AI review metadata when available

### Clinical report generation
- Generates a downloadable PDF report for each redaction session
- Includes patient and doctor details in a professional report header/summary
- Preserves doctor advice and recommended actions for the patient
- Lists the clinical note, guidance, and audit sections
- Includes redacted output and compliance-style summary sections

### OTP and registration flow
- Basic registration endpoint
- OTP-based verification flow for demo/local use
- Email-based OTP simulation suitable for local testing

### Modern frontend
- Responsive HTML/CSS/JavaScript dashboard
- Clinical privacy styling with secure workflow look and feel
- Download link for generated PDF reports
- AI review status indicator and redaction summary output

---

## What the application can do

The app can:

- redact names, emails, contact numbers, dates, locations, and hospital references from clinical text
- preserve the useful medical context while removing direct identifiers
- support doctor-patient interactions in a healthcare-like legal/privacy workflow
- create a PDF audit report that looks closer to a real medical document than a demo output
- help reduce re-identification risk before sending text to external AI tools
- generate shareable, downloadable protected output artifacts
- run as a local prototype or demo for privacy-preserving clinical AI workflows

---

## Supported workflow

The application supports a typical clinical privacy workflow like this:

1. User logs in with a demo patient or doctor account.
2. User enters patient information or doctor notes in the dashboard.
3. The system detects sensitive data and creates a redacted version.
4. The backend stores or returns the safe clinical content.
5. A PDF audit report is generated with the protected version and key sections.
6. The user can download the resulting report for review or documentation.

---

## Example use cases

- patient intake form redaction before AI review
- doctor consultation note protection
- clinical summarization workflow with privacy safeguards
- hospital-like report creation with masked PHI and preserved medical instructions
- AI-assisted healthcare documentation without exposing direct identifiers

---

## Current app pages

### Home page
- URL: http://127.0.0.1:8000/
- login and account flow entry point

### Dashboard
- URL: http://127.0.0.1:8000/dashboard
- primary workflow interface for patient and doctor use cases

### Generated report download
- URL pattern: http://127.0.0.1:8000/reports/{filename}.pdf
- downloadable redaction audit report

---

## Tech stack

- Python
- FastAPI
- Jinja2 templates
- JWT authentication
- Microsoft Presidio
- Regex-based fallback redaction
- HTML/CSS/JavaScript
- ReportLab PDF generation
- Optional Groq AI review hook

---

## Project structure

```text
HealthTech---Automated-PHI-PII-Redaction-Pipeline-for-LLMs/
├── app.py
├── auth.py
├── email_service.py
├── otp_service.py
├── redactor.py
├── report_generator.py
├── requirements.txt
├── README.md
├── templates/
│   ├── index.html
│   └── dashboard.html
├── reports/
└── .gitignore
```

---

## Demo credentials

Use these local test accounts:

- Doctor
  - Username: doctor1
  - Password: 1234

- Patient
  - Username: patient1
  - Password: 1234

---

## Local run instructions

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start the application:

```bash
python3 -m uvicorn app:app --host 0.0.0.0 --port 8000
```

3. Open the app in a browser:

```text
http://127.0.0.1:8000/
```

4. After login, open the dashboard:

```text
http://127.0.0.1:8000/dashboard
```

---

## Example clinical input

```text
Patient Name:
John Smith

Doctor Name:
Dr. Emily Carter

Email:
john.smith@example.com

Phone:
+918876072154

Hospital:
St. Mary Hospital

Clinical Note:
Patient reports mild dizziness and fatigue over the last 2 days.

Doctor Recommendation:
Patient should rest, drink fluids, and follow up in 7 days if symptoms continue.
```

The system will redact identifying data such as the email, phone, hospital name, and patient name in the safe output while preserving the clinical guidance and note content.

---

## Privacy and compliance intent

This project is a demonstration/privacy-protection layer meant to reduce risk when clinical or patient information is handled by AI services. It is not a medical compliance system by itself, but it provides a realistic starting point for secure PHI/PII handling in healthcare AI workflows.

---

## Summary

This project is a privacy-first healthcare application that can:

- detect PHI/PII
- redact it safely
- show the result in a clinician-friendly dashboard
- support doctor/patient workflows
- generate a professional PDF report
- help reduce privacy risk before external AI processing

It is best described as a healthcare data redaction and audit workflow built for secure clinical AI use.