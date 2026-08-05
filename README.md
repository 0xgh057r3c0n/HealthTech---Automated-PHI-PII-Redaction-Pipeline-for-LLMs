# 🏥 HealthTech PHI/PII Redaction Pipeline

An AI-powered healthcare privacy system that detects and redacts Protected Health Information (PHI) and Personally Identifiable Information (PII) from clinical text before it is sent to external AI systems.

## 📌 Project Overview

Healthcare organizations must protect patient privacy when using AI tools for clinical documentation. This project acts as a secure redaction layer that identifies sensitive information and anonymizes it before processing.

The system currently supports:

- Email redaction
- Phone number redaction
- Date redaction
- Person name detection using NLP
- FastAPI backend
- Interactive web interface

---

## 🎯 Problem Statement

Sending unredacted patient conversations to external AI services can violate privacy regulations such as:

- HIPAA (Health Insurance Portability and Accountability Act)
- PIPEDA (Personal Information Protection and Electronic Documents Act)

This project helps ensure that sensitive patient information is removed before data leaves a secure environment.

---

## 🏗️ System Architecture

```text
User Input
    ↓
FastAPI Backend
    ↓
PII/PHI Detection Layer
    ↓
Redaction Engine
    ↓
Safe Output
```

---

## 🛠️ Technologies Used

- Python
- FastAPI
- spaCy
- Microsoft Presidio
- HTML
- CSS
- JavaScript
- Git & GitHub

---

## 📂 Project Structure

```text
healthtech-redaction/
│
├── app.py
├── redactor.py
├── index.html
├── README.md
├── requirements.txt
├── .gitignore
└── venv/
```

---

## 🚀 Features

### Week 1
- Regex-based PII detection
- Email masking
- Phone number masking
- Date masking

### Week 2
- NLP-based entity recognition
- Person name detection
- FastAPI API development
- Interactive frontend UI

### Week 3 (Completed)

* Enhanced PHI/PII detection using Microsoft Presidio
* Entity counting
* Entity type tracking
* Audit panel support
* Detection of:

  * PERSON
  * PHONE_NUMBER
  * EMAIL_ADDRESS
  * LOCATION
  * DATE_TIME
* Improved frontend integration
* GitHub version control


### Week 4 (Planned)
- Performance optimization
- Deployment
- HIPAA compliance analysis


## 🚀 Live Deployment

The project is deployed and accessible online:

👉 https://healthtech-redaction.onrender.com

### Features:
- Real-time PII/PHI redaction
- FastAPI backend
- NLP-based entity detection
- Web UI interface
- API latency tracking

---

## 🧪 Example

### Input

```text
John Smith visited Apollo Hospital on 12/05/2026.
Contact: johnsmith@gmail.com
```

### Output

```text
<PERSON> visited Apollo Hospital on <DATE_TIME>.
Contact: <EMAIL_ADDRESS>
```

---

## ▶️ Running the Project

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Start Server

```bash
uvicorn app:app --reload
```

### Open Browser

```text
http://127.0.0.1:8000
```

---

## 👨‍💻 Author

**Md Sameer**

HealthTech Privacy & AI Redaction Project