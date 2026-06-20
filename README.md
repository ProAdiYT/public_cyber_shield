# Citizen Cyber Shield

Citizen Cyber Shield is a next-generation AI-powered Cyber Threat Intelligence Platform designed to protect everyday citizens from malicious digital vectors including phishing SMS messages, malicious URLs, and screenshot-based cyber frauds.

---

## Quick Start (Local Run)

To get the application up and running on your local machine instantly, follow these 5 command sets:

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/CitizenCyberShield.git
cd CitizenCyberShield

# 2. Set up virtual environment & activate it (example: Windows PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install required Python and ML packages
pip install -r requirements.txt

# 4. Start the FastAPI backend server (Port 8000)
uvicorn backend.server:app --port 8000 --reload

# 5. Serve the static Web Frontend (Port 8080)
python -m http.server 8080 --directory frontend
```
*Access the Web Frontend dashboard at [http://localhost:8080/sms.html](http://localhost:8080/sms.html) or the backend API Docs at [http://localhost:8000/docs](http://localhost:8000/docs).*

---

## Features

* **AI SMS Scanner**: Detects banking fraud, OTP harvesting, UPI scams, and identity theft using a text vectorizer and an XGBoost classification model.
* **Lexical URL Phishing Analyzer**: Evaluates URL length, SSL security (HTTPS), subdomain ratios, and lexical entropy using a Random Forest classification model.
* **OCR Screenshot Scanner**: Extracts text from images of messages or payment confirmations (EasyOCR + OpenCV) and forwards it automatically to the threat detection engine.
* **National Cyber Incident Complaint Generator**: Pre-populates structured legal reports with victim names, transaction counts, dates, and incident summaries for submission to Cyber Crime cells.
* **Interactive AI Recovery Assistant**: Provides checklists and immediate guides customized for UPI fraud, banking scams, and OTP compromise, complete with bank helpline details.
* **Real-time Incident Dashboard**: Lists scan statistics, threat category breakdown, and logged risk parameters.

---

## Architecture

The application is structured as a decoupled full-stack system:
1. **Frontend**: Static Web App (pure HTML, modern CSS variables with glassmorphism aesthetics, and client-side JavaScript controllers).
2. **Backend**: FastAPI web server that loads pre-trained machine learning models on startup and serves predictive endpoints.
3. **ML Pipeline**: Natural Language Processing (TF-IDF Vectorization) for SMS classification, and regex-based lexical feature extractors for URL threat scores.
4. **OCR Pipeline**: Image processing (OpenCV contrast adjustments, deskewing) and character recognition (EasyOCR).

---

## Folder Structure

```text
CitizenCyberShield/
├── .env.example              # Local environment configuration template
├── .gitignore                # Git exclusions (caches, venv, datasets, logs)
├── CHANGELOG.md              # Document version updates
├── CONTRIBUTING.md           # Instructions for code contributions
├── DEPLOYMENT.md             # Production hosting configurations (Netlify, Render)
├── LICENSE                   # MIT License
├── README.md                 # Primary system manual
├── SECURITY.md               # Incident reporting policy
├── SETUP.md                  # Comprehensive environment initialization manual
├── app.py                    # Main Streamlit Desktop interface
├── requirements.txt          # Python dependencies list
├── backend/                  # Server-side module files
│   ├── server.py             # FastAPI API backend
│   ├── ocr_engine.py         # Screenshot text parser (EasyOCR/OpenCV)
│   ├── extractors.py         # URL feature parsing
│   └── train_*.py            # ML Model training scripts
├── frontend/                 # Client-side static user interface
│   ├── index.html            # Gateway page (Terminal Hub)
│   ├── sms.html              # SMS scanner view
│   ├── url.html              # URL scanner view
│   ├── screenshot.html       # Screenshot scan view
│   ├── dashboard.html        # Scan analytics page
│   ├── recovery.html         # Step-by-step mitigator UI
│   ├── complaint.html        # Automated complaint form
│   ├── js/
│   │   └── app.js            # JavaScript controller calling FastAPI
│   └── css/
│       └── style.css         # Glassmorphism cyber-style sheets
└── models/                   # Serialized ML vectorizer and threat classification models
```

---

## Installation & OS Setup Guide

Ensure Python 3.9+ is installed before starting.

### Windows Setup
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Linux Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Mac Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Running the Components

### Backend Setup (FastAPI)
Run the server using Uvicorn:
```bash
uvicorn backend.server:app --host 127.0.0.1 --port 8000 --reload
```
Interactive Swagger API documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

### Frontend Setup (Web App)
Serve static files using Python's built-in server:
```bash
python -m http.server 8080 --directory frontend
```
Navigate to [http://localhost:8080](http://localhost:8080) to access the dashboard hub.

### Desktop App Setup (Alternative Streamlit Interface)
If you prefer a combined layout in a single interface, run the desktop-themed Streamlit application:
```bash
streamlit run app.py
```
This serves a standalone UI on [http://localhost:8501](http://localhost:8501).

---

## API Documentation

The backend exposes several JSON endpoints:

* **POST** `/api/scan-sms`: Takes an `{"message": "string"}` and returns model categorization, confidence, risk score, severity level, and specific risk indicators.
* **POST** `/api/scan-url`: Takes an `{"url": "string"}` and evaluates active redirection hops, SSL certificate existence, and risk scoring.
* **POST** `/api/scan-screenshot`: Parses multipart form image files, runs EasyOCR extraction, and pipes text through the SMS scanner.
* **POST** `/api/recovery-plan`: Returns specific steps matching threat classifications (e.g. UPI, Bank, OTP) and bank support numbers.
* **POST** `/api/generate-complaint`: Formats a full incident report template based on victim information.

---

## Deployment Guide

* **Backend**: Hosted on cloud platforms (e.g. Render) using a Python environment, installing dependencies via `requirements.txt`, and running the uvicorn start command. Add `OPENBLAS_NUM_THREADS=1` to the environment variables to optimize CPU utilization.
* **Frontend**: Deploy the static `frontend` folder directly to services like Netlify or Vercel. 
* **Important Production Step**: Prior to deploying, open `frontend/js/app.js` and change `const API_BASE_URL = "http://localhost:8000"` (Line 7) to your live backend endpoint.

See [DEPLOYMENT.md](DEPLOYMENT.md) for step-by-step guides.

---

## Troubleshooting & FAQ

### FAQ

**Q: Why does the OCR Scanner take a long time on the first scan?**  
A: EasyOCR downloads the required English language models on its first execution. Subsequent runs occur instantly.

**Q: Can I run this without installing Python locally?**  
A: The frontend can be hosted statically anywhere, but the scanning, machine learning, and OCR logic require the FastAPI python backend to be running.

### Troubleshooting

* **Issue: Connection Refused in the Frontend Interface**  
  *Solution*: Verify that the FastAPI backend is running on `http://localhost:8000`. If it's running on a different port, update the `API_BASE_URL` in `frontend/js/app.js`.
* **Issue: Thread Allocations or Memory Crashing**  
  *Solution*: Ensure you set `OPENBLAS_NUM_THREADS=1` in your environment (preconfigured in `.env.example`).