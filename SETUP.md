# Installation & Local Setup Guide

This guide walks you through setting up Citizen Cyber Shield on Windows, Linux, and macOS.

## Prerequisites
* **Python**: Python 3.9 or higher (recommended 3.10+)
* **pip**: Python package manager
* **Git**: To clone the repository
* **Web Browser**: Chrome, Firefox, Safari, or Edge

---

## 1. Get the Code
Clone the repository to your local machine:
```bash
git clone https://github.com/yourusername/CitizenCyberShield.git
cd CitizenCyberShield
```

---

## 2. Virtual Environment Setup

### Windows
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Linux / macOS
```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies
Install all required Python packages and OCR modules:
```bash
pip install -r requirements.txt
```

---

## 4. Run the Project

### Running the API Backend (FastAPI)
Run the backend server on port `8000`:
```bash
# Ensure virtual environment is active
uvicorn backend.server:app --port 8000 --reload
```
Verify the API is active by checking the health/docs endpoint: [http://localhost:8000/docs](http://localhost:8000/docs).

### Running the Web Frontend
You can serve the frontend files locally using Python's built-in HTTP server on port `8080`:
```bash
python -m http.server 8080 --directory frontend
```
Now open your browser and navigate to: [http://localhost:8080/index.html](http://localhost:8080/index.html) or [http://localhost:8080/sms.html](http://localhost:8080/sms.html).

### Running the Standalone Streamlit App (Alternative)
If you prefer to run the standalone Streamlit interface:
```bash
streamlit run app.py
```
This will automatically open the Streamlit interface at [http://localhost:8501](http://localhost:8501).

---

## 5. Verification Checklist
- [ ] Backend starts up on port `8000`.
- [ ] Frontend page loads on port `8080`.
- [ ] Submitting a scan request in the UI triggers a call to `/api/scan-sms` or `/api/scan-url` without errors.
- [ ] Uploading a screenshot successfully runs EasyOCR.
