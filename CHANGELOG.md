# Changelog

All notable changes to the Citizen Cyber Shield project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-06-20

### Added
- **FastAPI API server** (`backend/server.py`) serving endpoints for SMS scanning, URL phishing analysis, OCR screenshot processing, complaint generation, and recovery steps.
- **Unified HTML & JavaScript Web App Frontend** featuring a responsive dark mode styling using glassmorphism and custom CSS variables.
- **EasyOCR and OpenCV integration** for screenshot text scanning and scanning processing.
- **Streamlit Desktop/Dashboard application** (`app.py`) for local testing.
- **XGBoost and Random Forest machine learning models** trained for threat classification.
- **Local history management** to save and load past scan records to/from a CSV file (`scan_history.csv`).
- **Emergency Helpline details** and recovery checklists.
- Added comprehensive repository support files (`.gitignore`, `.env.example`, `LICENSE`, `SETUP.md`, `DEPLOYMENT.md`, `SECURITY.md`, `CONTRIBUTING.md`, `CHANGELOG.md`).
