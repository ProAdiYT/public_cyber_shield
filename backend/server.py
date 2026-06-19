import os
# CRITICAL: Prevent OpenBLAS Memory Allocation Errors in restricted environments
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import shutil
import tempfile
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from extractors import URLExtractor
from ocr_engine import OCREngine

app = FastAPI(title="Citizen Cyber Shield AI API", version="1.0.0")

# Enable CORS for frontend pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load machine learning models on startup
try:
    sms_model = joblib.load("models/advanced_sms_model.pkl")
    sms_vectorizer = joblib.load("models/advanced_sms_vectorizer.pkl")
    sms_encoder = joblib.load("models/advanced_sms_encoder.pkl")
    url_model = joblib.load("models/advanced_url_model.pkl")
    print("AI Threat Models loaded successfully!")
except Exception as e:
    print(f"CRITICAL: Failed to load models. Check if training was run. Error: {str(e)}")

# Initialize helper engines
url_extractor = URLExtractor()
ocr_engine = OCREngine()

# --- Schemas ---
class SMSRequest(BaseModel):
    message: str

class URLRequest(BaseModel):
    url: str

class RecoveryRequest(BaseModel):
    threat_type: str
    bank_name: str

import re

def clean_text(text):
    """Cleans text and normalizes URLs, phone numbers, and UPI handles to tokens."""
    text = str(text).lower()
    url_pattern = r'https?://\S+|www\.\S+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}/\S*'
    text = re.sub(url_pattern, '[URL]', text)
    upi_pattern = r'[a-zA-Z0-9.\-_]+@[a-zA-Z]{3,}'
    text = re.sub(upi_pattern, '[UPI]', text)
    phone_pattern = r'\+?\d[\d -]{8,12}\d'
    text = re.sub(phone_pattern, '[PHONE]', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# --- Endpoints ---

@app.post("/api/scan-sms")
def scan_sms(req: SMSRequest):
    message = req.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Empty message payload.")
        
    try:
        # Apply cleaning/normalization
        cleaned_msg = clean_text(message)
        
        # 1. Transform text using TF-IDF
        vector = sms_vectorizer.transform([cleaned_msg])
        
        # 2. Predict categories and probabilities (XGBoost outputs integer labels)
        pred_encoded = int(sms_model.predict(vector)[0])
        probs = sms_model.predict_proba(vector)[0]
        
        # Decode predicted label
        pred_label = sms_encoder.inverse_transform([pred_encoded])[0]
        
        # Get probability of predicted label
        confidence = float(probs[pred_encoded]) * 100
        
        # Calculate risk score (100% - safe_class probability)
        safe_idx = list(sms_encoder.classes_).index("Safe")
        risk_score = 100.0 - (float(probs[safe_idx]) * 100)
        
        # Heuristic safety override layer
        high_risk_words = [
            "blocked", "verify", "kyc", "otp", "bank", 
            "click here", "suspended", "update account", 
            "reward", "lottery"
        ]
        text_lower = message.lower()
        matched = sum(1 for w in high_risk_words if w in text_lower)
        
        # Determine is_scam
        is_scam = True if pred_label != "Safe" else False
        
        if matched >= 2:
            is_scam = True
            if pred_label == "Safe":
                pred_label = "Banking Fraud"
            risk_score = max(risk_score, 85.0)
            
        # Determine severity
        critical_threats = ["Bank Fraud", "UPI Fraud", "OTP Scam", "Banking Fraud"]
        medium_threats = ["KYC Fraud", "Job Scam", "Investment Scam", "Lottery Scam", "QR Scam"]
        
        if pred_label in critical_threats or matched >= 2:
            severity = "CRITICAL"
        elif pred_label in medium_threats:
            severity = "MEDIUM"
        else:
            severity = "LOW"
            
        # Explanations (extract matched features/keywords)
        reasons = []
        text_lower = message.lower()
        if "otp" in text_lower:
            reasons.append("Solicitation of OTP code.")
        if "upi" in text_lower or "paytm" in text_lower or "phonepe" in text_lower:
            reasons.append("UPI transfer indicators detected.")
        if "kyc" in text_lower or "document" in text_lower or "pan" in text_lower:
            reasons.append("Solicitation of KYC document verifications.")
        if "bank" in text_lower or "blocked" in text_lower or "suspended" in text_lower:
            reasons.append("Bank account warning cues.")
        if "won" in text_lower or "lottery" in text_lower or "prize" in text_lower:
            reasons.append("Lottery/Prize lures present.")
        if "click" in text_lower or "http" in text_lower or "www" in text_lower:
            reasons.append("External hyperlink redirects found.")
            
        if not reasons and is_scam:
            reasons.append("Matched malicious scam text indicators.")
            
        return {
            "is_scam": is_scam,
            "category": pred_label,
            "confidence": f"{confidence:.1f}%",
            "risk_score": f"{risk_score:.1f}%",
            "severity": severity,
            "explainability": reasons
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SMS scan engine error: {str(e)}")

@app.post("/api/scan-url")
def scan_url(req: URLRequest):
    url = req.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="Empty URL payload.")
        
    try:
        # 1. Extract features dynamically (including redirect lookup)
        feats = url_extractor.extract_features(url)
        
        # 2. Formulate input row matching features used in training
        # Features must be in exact training order:
        # ['URLLength', 'IsHTTPS', 'NoOfSubDomain', 'DomainLength', 'DegitRatioInURL', 'SpacialCharRatioInURL', 'Entropy', 'SuspiciousKeywordsCount', 'TLDRisk', 'NoOfURLRedirect']
        feature_order = [
            'URLLength', 'IsHTTPS', 'NoOfSubDomain', 'DomainLength', 'DegitRatioInURL', 
            'SpacialCharRatioInURL', 'Entropy', 'SuspiciousKeywordsCount', 'TLDRisk', 'NoOfURLRedirect'
        ]
        input_row = [feats[col] for col in feature_order]
        
        # 3. Run prediction model
        prediction = int(url_model.predict([input_row])[0])
        probs = url_model.predict_proba([input_row])[0]
        
        # Risk score is probability of class 1 (Phishing)
        risk_score = float(probs[1]) * 100
        
        # Classify severity
        if risk_score > 60:
            severity = "PHISHING HAZARD"
        elif risk_score > 30:
            severity = "SUSPICIOUS"
        else:
            severity = "SAFE"
            
        # Detail findings list
        findings = []
        if feats['IsHTTPS'] == 0:
            findings.append("Missing HTTPS protocol (Unsecured plain HTTP network link).")
        if feats['TLDRisk'] == 1:
            findings.append("Suspicious high-risk top-level domain (TLD).")
        if feats['SuspiciousKeywordsCount'] > 0:
            findings.append(f"Domain contains {feats['SuspiciousKeywordsCount']} phishing keywords.")
        if feats['Entropy'] > 4.5:
            findings.append("High entropy URL string (indicates machine-generated obfuscation).")
        if feats['NoOfURLRedirect'] > 0:
            findings.append(f"Redirect count: {feats['NoOfURLRedirect']} active redirect hops.")
            
        return {
            "risk_score": f"{risk_score:.1f}%",
            "severity": severity,
            "findings": findings,
            "features": feats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"URL analyzer engine error: {str(e)}")

@app.post("/api/scan-screenshot")
async def scan_screenshot(file: UploadFile = File(...)):
    try:
        # 1. Save uploaded file to temp file
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
            
        # 2. Execute preprocessed OCR
        extracted_text = ocr_engine.extract_text(temp_path)
        
        # Clean up temp file
        os.unlink(temp_path)
        
        # 3. Send parsed text payload automatically to the SMS Scanner API
        sms_req = SMSRequest(message=extracted_text)
        sms_report = scan_sms(sms_req)
        
        return {
            "extracted_text": extracted_text,
            "sms_report": sms_report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR scan pipeline error: {str(e)}")

@app.post("/api/recovery-plan")
def recovery_plan(req: RecoveryRequest):
    threat_type = req.threat_type.strip()
    bank_name = req.bank_name.strip()
    
    plans = {
        "UPI Fraud": [
            "Dial Global Cyber Incident Helpline at 1930 immediately.",
            "Log in to your banking app and disable/deregister UPI payment services.",
            "Report transaction dispute UTR numbers to your bank's fraud desk.",
            "Take visual screenshots of payment success pages and WhatsApp logs."
        ],
        "Banking Fraud": [
            "Freeze all netbanking user profiles immediately.",
            "Block debit/credit card modules via bank app or phone hotlines.",
            "Report fraudulent withdrawals to the branch manager to request chargebacks.",
            "Change all secure credentials, pins, and login passwords."
        ],
        "OTP Scam": [
            "Reset passwords and recovery emails for your primary email/bank profiles.",
            "Verify that no unauthorized devices are logged in to your Google/Apple accounts.",
            "Enable App-based 2-Factor Authentication (e.g. Google Authenticator) instead of SMS OTP.",
            "Monitor statements closely for the next 48 hours."
        ],
        "KYC Fraud": [
            "Report identity theft parameters on the national cyber portal.",
            "Contact your credit reporting bureaus to request temporary credit freezes.",
            "Monitor credentials linked to your identity card (Aadhaar/PAN/SSN).",
            "Refuse scanning biometric or scanning face filters on suspicious links."
        ],
        "Job Scam": [
            "Block attackers on Telegram/WhatsApp immediately.",
            "Request bank chargeback for money sent as 'security deposits' or 'task buy-ins'.",
            "Report the attacker's wallet or UPI IDs in your police complaint file.",
            "Do not share resume identity credentials (address, passport copies)."
        ],
        "Investment Scam": [
            "Save wallet transaction hash logs and exchange deposit histories.",
            "Report scam trading platform URLs to domain hosting registrars to initiate blocks.",
            "Do not pay 'withdrawal fees' or 'taxes' demanded to release funds.",
            "File official reports citing cryptocurrency destination addresses."
        ],
        "Lottery Scam": [
            "Do not pay registration taxes or customs duties to release dummy lottery winnings.",
            "Block the caller numbers and scam domain URLs.",
            "Report caller identifiers and banking deposit requests to police.",
            "Secure private identity profiles."
        ],
        "QR Scam": [
            "Contact your bank immediately to block authorization links.",
            "Never scan a QR code to 'receive' money; scanning only 'sends' money.",
            "File UPI dispute reports using payment application portals.",
            "Note transaction receipt references."
        ]
    }
    
    bank_data = {
        "SBI": {
            "helpline": "1800 11 2211 / 1800 425 3800",
            "website": "https://sbi.co.in"
        },
        "HDFC": {
            "helpline": "1800 202 6161 / 1800 22 1006",
            "website": "https://hdfcbank.com"
        },
        "ICICI": {
            "helpline": "1800 1080",
            "website": "https://icicibank.com"
        }
    }
    
    return {
        "steps": plans.get(threat_type, [
            "Preserve all transaction IDs, chat histories, and logs.",
            "Report the threat vectors directly to local police cells.",
            "Update bank profiles and password layers."
        ]),
        "bank": bank_data.get(bank_name, {
            "helpline": "1930 / Contact local branch",
            "website": "Search online"
        })
    }

@app.post("/api/generate-complaint")
def generate_complaint(
    name: str = Form(...),
    scam_type: str = Form(...),
    date: str = Form(...),
    platform: str = Form(...),
    target_info: str = Form(...),
    amount: str = Form(...),
    description: str = Form(...)
):
    complain_date = os.popen('date /t').read().strip() if os.name == 'nt' else "Today"
    
    template = f"""To,
The Cyber Crime Cell,
National Cyber Incident Reporting Center.

SUBJECT: Request for Investigation into Cyber Incident: {scam_type.upper()} FRAUD

Respected Authority,

I am writing to formally report a cyber incident of fraud that occurred on my account. Below are the specific incident diagnostics and facts:

VICTIM INFORMATION:
- Name of Victim: {name}
- Incident Registration Date: {complain_date}

ATTACK PARAMETERS & METRICS:
- Classification of Scam: {scam_type}
- Platform Used by Attacker: {platform}
- Target Identifier (Attacker Account/Phone/URL): {target_info}
- Financial Loss / Amount Disbursed: USD {amount}
- Date and Time of Incident: {date}

INCIDENT CHRONOLOGY & EVIDENCE SUMMATION:
{description}

I have attached all relevant cryptographic hashes, chat logs, URLs, and phone screen snapshots as evidence. I request you to investigate this matter urgently, register an official Complaint Number, and take appropriate action under global cyber laws.

Thank you.

Sincerely,
{name}
(Electronic Signature Verified via Shield ID)"""
    return {"complaint_text": template}
