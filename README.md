# 🏥 HealthTech PHI/PII Redaction Pipeline

A secure healthcare workflow for identifying, masking, and auditing sensitive clinical data before it is processed by external AI systems.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Privacy-Healthcare-red?style=for-the-badge" alt="Privacy" />
  <img src="https://img.shields.io/badge/PDF-Reports-4B5563?style=for-the-badge" alt="PDF" />
</p>

## 📌 Overview

This application helps healthcare teams protect patient information while keeping the core clinical context usable for review and documentation.

It supports:

- 👩‍⚕️ patient and doctor role-based workflows
- 🔒 PHI/PII detection and masking
- 🩺 redacted clinical output
- 📄 downloadable PDF audit reports
- 🔐 secure token-based API access

---

## ✨ Features

- 🧑‍⚕️ Role-aware dashboard for patient and doctor workflows
- 🛡️ PHI/PII detection for names, emails, phone numbers, dates, and hospital/location values
- 🧠 Redaction engine with Presidio + regex fallback
- 🚀 Protected FastAPI API
- 📄 PDF report generation for audit and documentation
- 🔁 OTP-based demo user flow
- 📱 Responsive frontend for local testing and demo use

---

## 🏗️ Tech Stack

- Python
- FastAPI
- Jinja2 Templates
- JWT Authentication
- Microsoft Presidio
- ReportLab
- HTML / CSS / JavaScript

---

## ▶️ Run Locally

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the app

```bash
python3 -m uvicorn app:app --host 0.0.0.0 --port 8000
```

### 3. Open the app

- http://127.0.0.1:8000/
- http://127.0.0.1:8000/dashboard

---

## 👤 Demo Accounts

- Doctor: `doctor1` / `1234`
- Patient: `patient1` / `1234`

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
├── reports/
└── .gitignore
```

---

## 🧪 Example Clinical Input

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

---

## 🎯 Purpose

This project is a privacy-first healthcare demo for reducing risk before sending clinical content to AI systems.

It is designed to support safer medical data workflows without exposing direct identifiers.

---

## ✅ Summary

This project can:

- detect PHI/PII in healthcare text
- redact it safely
- support doctor/patient workflows
- generate a professional PDF report
- reduce privacy risk before external AI processing

It is best described as a healthcare data redaction and audit workflow built for secure clinical AI use.