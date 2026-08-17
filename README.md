# HealthTech PHI/PII Redaction Pipeline

A secure healthcare workflow for identifying, masking, and auditing sensitive clinical data before it is processed by external AI systems.

## Overview

This application helps healthcare teams protect patient information while keeping the core clinical context usable for review and documentation.

It supports:

- patient and doctor role-based workflows
- PHI/PII detection and masking
- redacted clinical output
- downloadable PDF reports
- secure token-based API access

## Features

- Role-aware dashboard for patient and doctor flows
- PHI/PII detection for names, emails, phone numbers, dates, and hospital/location data
- Redaction engine with Presidio + regex fallback
- Protected FastAPI API
- PDF report generation for audit and documentation
- OTP-based demo user flow
- Responsive frontend for demo and local testing

## Tech Stack

- Python
- FastAPI
- Jinja2
- JWT authentication
- Microsoft Presidio
- ReportLab
- HTML/CSS/JavaScript

## Run Locally

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start the app:

```bash
python3 -m uvicorn app:app --host 0.0.0.0 --port 8000
```

3. Open:

- http://127.0.0.1:8000/
- http://127.0.0.1:8000/dashboard

## Demo Accounts

- Doctor: `doctor1` / `1234`
- Patient: `patient1` / `1234`

## Project Structure

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

## Example

```text
Patient Name: John Smith
Doctor Name: Dr. Emily Carter
Email: john.smith@example.com
Phone: +918876072154
Hospital: St. Mary Hospital

Clinical Note:
Patient reports dizziness and fatigue over the last 2 days.

Doctor Recommendation:
Patient should rest, hydrate, and follow up in 7 days if symptoms continue.
```

The redacted output protects sensitive identifiers while keeping the medical guidance and documentation usable.

## Purpose

This project is a privacy-first healthcare demo for reducing risk before sending clinical content to AI systems.

It is designed to support safer medical data workflows without exposing direct identifiers.