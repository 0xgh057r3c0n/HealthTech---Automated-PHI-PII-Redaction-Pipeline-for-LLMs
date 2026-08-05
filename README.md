# 🏥 HealthTech PHI/PII Redaction Pipeline

A secure healthcare privacy workflow for detecting, masking, and reviewing Protected Health Information (PHI) and Personally Identifiable Information (PII) before any clinical text is sent to external AI systems.

Built and maintained by: 0xgh057r3c0n

---

## 📌 Project Overview

This project is a FastAPI-based healthcare privacy application that gives doctors and patients a protected interface for:

- entering clinical or patient-related text
- generating a safe redacted output
- reviewing fallback and AI-assisted results
- downloading a PDF report of the redaction process

The application is designed to help healthcare teams reduce privacy exposure when working with LLM-based processing pipelines.

---

## 🎯 Core Problem

Healthcare organizations often need to use AI helpers for summarization, documentation, or triage. Sending raw patient information to an external model can create privacy, compliance, and governance risks.

This project introduces a controlled layer that:

- detects sensitive fields such as names, emails, phone numbers, dates, and locations
- masks them in the protected output
- keeps the workflow role-aware for doctor and patient use cases
- optionally uses an AI review model for a separate review-only experience

---

## ✨ Features Included

### Authentication and Access Control
- JWT-based login workflow
- Role-aware user access for doctor and patient flows
- Protected redaction endpoint using bearer-token authentication
- Demo in-memory user store for local testing

### Registration and OTP Workflow
- User registration flow
- OTP generation and verification
- Email-based OTP simulation for local demo use
- Expiry handling for OTP tokens

### Redaction Engine
- Microsoft Presidio-powered entity detection
- Regex fallback masking for missing NLP coverage
- Support for detection and masking of:
  - PERSON
  - EMAIL_ADDRESS
  - PHONE_NUMBER
  - DATE_TIME
  - LOCATION
  - HOSPITAL_NAME

### AI Review Integration
- Optional Groq-based review hook
- Separate AI-review output panel in the dashboard
- Review-only behavior to keep the primary workflow masked and protected
- AI badge state to show whether the review feature is enabled or unavailable

### Dashboard Experience
- Doctor dashboard and patient dashboard role split
- Modern glassmorphism / healthcare-style UI
- Interactive form generation and action buttons
- Separate panels for:
  - redacted output
  - fallback redaction output
  - Groq AI review output
  - detected entity summary
  - report download link

### Reporting
- PDF report generation for each redaction run
- Downloadable result artifact stored in the reports folder

### UX and Workflow
- Responsive frontend
- FastAPI backend with templated HTML pages
- Clean login and dashboard flow
- Demo login credentials for manual testing

---

## 🏗️ System Architecture

```text
User Browser
    ↓
FastAPI App
    ├── Auth Layer
    ├── OTP Registration Flow
    ├── Protected Redaction API
    ├── PDF Report Generator
    └── Optional Groq Review Hook
    ↓
Redaction Engine
    ├── Presidio NLP Detection
    └── Regex Fallback Masking
    ↓
Safe Dashboard Output
```

---

## 🛠️ Technologies Used

- Python
- FastAPI
- Jinja2 Templates
- JWT / jose
- Microsoft Presidio
- Regex-based privacy masking
- HTML / CSS / JavaScript
- PDF report generation
- Optional Groq API integration

---

## 📁 Project Structure

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
└── reports/
```

---

## 🚀 Demo Credentials

Use these demo accounts for local manual testing:

- Doctor
  - Username: `doctor1`
  - Password: `1234`

- Patient
  - Username: `patient1`
  - Password: `1234`

---

## 🧪 Example Test Input

```text
Contact Dr. John Smith at john.smith@example.com or (555) 123-4567 on 2026-08-05.
```

### Expected Protected Output

```text
Contact Dr. <PERSON> at <EMAIL_ADDRESS> or <PHONE_NUMBER> on <DATE_TIME>.
```

### Expected AI Review Panel

The AI review section is designed to show the raw review payload or original input in a separate non-masking review view, while the main output remains protected.

---

## ▶️ How to Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the app

```bash
uvicorn app:app --reload
```

### 3. Open the app

```text
http://127.0.0.1:8000/
```

### 4. Open the dashboard after login

```text
http://127.0.0.1:8000/dashboard
```

---

## 📦 What This Project Delivers

This project provides a complete healthcare privacy redaction MVP with:

- secure masked output generation
- role-specific doctor/patient workflow
- OTP-based account registration flow
- protected redaction API
- dashboard-driven user experience
- PDF report generation
- optional AI review integration
- a modern polished frontend experience

---

## 👨‍💻 Author

**0xgh057r3c0n**

HealthTech Privacy + AI Redaction Pipeline