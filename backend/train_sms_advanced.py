import os
# CRITICAL: Prevent OpenBLAS Memory Allocation Errors in restricted environments
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import re
import pandas as pd
import numpy as np
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

def clean_text(text):
    """Cleans text and normalizes URLs, phone numbers, and UPI IDs to generic tokens."""
    text = str(text).lower()
    
    # 1. Normalize URLs/Domains
    url_pattern = r'https?://\S+|www\.\S+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}/\S*'
    text = re.sub(url_pattern, '[URL]', text)
    
    # 2. Normalize UPI IDs (e.g. pay@upi, handler@okhdfcbank)
    upi_pattern = r'[a-zA-Z0-9.\-_]+@[a-zA-Z]{3,}'
    text = re.sub(upi_pattern, '[UPI]', text)
    
    # 3. Normalize Phone Numbers (8-14 digit numbers)
    phone_pattern = r'\+?\d[\d -]{8,12}\d'
    text = re.sub(phone_pattern, '[PHONE]', text)
    
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def label_scam(message):
    text = str(message).lower()
    if any(word in text for word in ["otp", "one time password", "verification code", "share code", "secure code"]):
        return "OTP Scam"
    elif any(word in text for word in ["upi", "paytm", "gpay", "phonepe", "money transfer", "request money", "vpa"]):
        return "UPI Fraud"
    elif any(word in text for word in ["bank", "card", "debit", "credit", "blocked", "suspended", "sbi", "hdfc", "icici", "pin blocked", "limit expired"]):
        return "Banking Fraud"
    elif any(word in text for word in ["kyc", "know your customer", "pan card", "aadhaar", "update documents", "document verification"]):
        return "KYC Fraud"
    elif any(word in text for word in ["job", "salary", "work from home", "part time", "earn money", "wfh", "telegram job"]):
        return "Job Scam"
    elif any(word in text for word in ["invest", "crypto", "trading", "double your", "bitcoin", "investment"]):
        return "Investment Scam"
    elif any(word in text for word in ["lottery", "prize", "won", "lucky draw", "claims bonus", "crore", "winner"]):
        return "Lottery Scam"
    elif any(word in text for word in ["qr", "quick response", "scan code", "scan to receive", "qr code"]):
        return "QR Scam"
    return "Unknown Threat"

# --- Real-world Phishing / Smishing Templates for Data Augmentation ---
smishing_templates = [
    # Banking Fraud
    ("Banking Fraud", "Your bank account has been suspended due to safety guidelines. Verify here to reactivate: http://secure-bank-login.xyz"),
    ("Banking Fraud", "Alert: Unauthorized withdrawal of USD 450.00 detected on credit card. If not you, block card now: http://card-freeze.info"),
    ("Banking Fraud", "Dear customer, your credit card limit has expired. Login to increase limit and verify bank profile: http://hdfc-limit-update.net"),
    ("Banking Fraud", "SBI Netbanking block notification. Click here to verify user ID and passcode immediately: http://sbi-card-verify.su"),
    ("Banking Fraud", "Account blocked warning! Suspicious login attempt from IP 104.92.1.2. Click to secure: http://login-secure-auth.xyz"),
    ("Banking Fraud", "Dear user, your HDFC bank debit card is locked due to wrong PIN. Reactivate: http://hdfc-pin-reset.xyz"),
    ("Banking Fraud", "Alert! Your card has been deactivated. Click to verify your bank credentials immediately: http://block-verify.net/login"),
    ("Banking Fraud", "Verification required: your account is blocked. Click here to resolve this within 2 hours: http://verify-secure-login-net.xyz"),

    # UPI Fraud
    ("UPI Fraud", "Congratulations! You have received a cash reward of USD 100. Scan QR code or claim UPI request: http://upi-reward-claim.xyz"),
    ("UPI Fraud", "Payment Request: Mahesh has requested USD 150 from your UPI VPA handle. Click link to authorize: upi://pay?pa=scammer@okaxis"),
    ("UPI Fraud", "Your UPI PIN is blocked. Reset your VPA and authorize transactions to reactivate: http://upi-reset-secure.net"),
    ("UPI Fraud", "Important: Disputed UPI transaction of USD 200 detected. Click here to reverse: http://upi-dispute-reverse.xyz"),
    ("UPI Fraud", "GPay Cashback Reward! You won USD 50. Tap here to select your bank account and receive money: http://gpay-cashback.cc"),

    # KYC Fraud
    ("KYC Fraud", "SBI Alert: Your NetBanking access will be suspended today as your KYC documents are pending. Update Aadhaar: http://sbi-kyc-verify.xyz"),
    ("KYC Fraud", "Attention: PAN Card validation has failed. Upload your PAN card photo to restore bank profile: http://pan-verification.info"),
    ("KYC Fraud", "Document verification required: Update your KYC status within 24 hours to prevent account block: http://kyc-update-portal.cc"),
    ("KYC Fraud", "SBI Alert: Aadhaar card not linked with your account. Link now to prevent account suspension: http://sbi-aadhaar-kyc.ru"),

    # OTP Scam
    ("OTP Scam", "Do not share this code. Use OTP 592810 to authorize purchase of USD 300.00 at Maverick store. If not you, click: http://block-otp.xyz"),
    ("OTP Scam", "Verification Code: 928410 is your login code. If you did not request this, share it with support at +1-800-BLOCK-CARD to cancel."),
    ("OTP Scam", "Bank security alert: To block unauthorized login from Chrome, confirm the OTP sent to your phone: http://otp-verify-secure.info"),
    ("OTP Scam", "Security Pin: 104928 is your code to release your lottery funds. Share to claim."),

    # Job Scam
    ("Job Scam", "Part-time job offer! Earn up to USD 50.00 per hour from home. Simple travel tasks. Start immediately via Telegram: http://job-wfh.xyz"),
    ("Job Scam", "We are hiring! Salary up to USD 4,000 monthly. Work from home rating destinations. Contact recruiter: http://recruitment-job-telegram.info"),
    ("Job Scam", "TikTok video likes job! Earn USD 150 daily from home. Join our Telegram recruitment link: http://tiktok-job-wfh.ru"),

    # Investment Scam
    ("Investment Scam", "Earn USD 1,000 daily from a USD 100 crypto investment. Guranteed returns. Free registration: http://crypto-double-returns.xyz"),
    ("Investment Scam", "Bitcoin trading signals! Join our Telegram group and double your investment in 7 days: http://bitcoin-trading-signals.cc"),
    ("Investment Scam", "New IPO launch! Invest USD 200 today and receive 300% return in 14 days. Sign up: http://ipo-invest-scam.xyz"),

    # Lottery Scam
    ("Lottery Scam", "KBC Winner: Congratulations! Your phone number won USD 25,000 in the lucky draw. Contact manager to claim: http://kbc-draw-claim.xyz"),
    ("Lottery Scam", "Lucky winner alert! You have won a brand new car. Pay USD 50 customs duty to release delivery: http://car-draw-claim.cc"),

    # QR Scam
    ("QR Scam", "Scan this QR code to claim your government subsidy cash reward of USD 120 directly to your bank account: http://qr-subsidy-claim.xyz"),
    ("QR Scam", "Tap to scan QR code and receive payment of USD 80 from buyer. No PIN required: http://qr-receive-scam.net")
]

def train_model():
    print("Loading base SMS raw dataset (Kaggle SMSSpamCollection)...")
    df = pd.read_csv(
        "datasets_raw/SMSSpamCollection",
        sep="\t",
        names=["base_label", "message"]
    )
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)

    print("Mapping base dataset and preparing data augmentation...")
    # Map messages: base ham becomes Safe, base spam runs initial label categorization
    labels = []
    for idx, row in df.iterrows():
        if row["base_label"] == "ham":
            labels.append("Safe")
        else:
            labels.append(label_scam(row["message"]))
    df["label"] = labels

    # Create augmentation dataframe from templates
    aug_rows = []
    # Replicate templates to balance classes (add 100 duplicates of each to boost statistical significance)
    for category, text in smishing_templates:
        for _ in range(100):
            aug_rows.append({"base_label": "spam", "message": text, "label": category})
            
    aug_df = pd.DataFrame(aug_rows)
    
    # Merge base dataset with augmented smishing templates
    df = pd.concat([df, aug_df], ignore_index=True)
    
    print("Normalizing SMS text features...")
    df["cleaned_message"] = df["message"].apply(clean_text)

    print("Class distribution after augmentation:\n", df["label"].value_counts())

    X = df["cleaned_message"]
    y = df["label"]

    print("Fitting TF-IDF Vectorizer...")
    # ngram_range (1,2) and max_features=5000 balances quality and memory usage
    vectorizer = TfidfVectorizer(max_features=5000, stop_words="english", ngram_range=(1, 2))
    X_vectorized = vectorizer.fit_transform(X)

    # Encode label strings to integers for XGBoost
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X_vectorized, y_encoded, test_size=0.2, random_state=42, stratify=None
    )

    print("Training XGBoost threat classifier...")
    model = XGBClassifier(
        n_estimators=100,
        random_state=42,
        n_jobs=1,
        eval_metric="mlogloss"
    )
    model.fit(X_train, y_train)

    # Evaluation
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    
    # Map back to original names for evaluation report
    pred_names = label_encoder.inverse_transform(predictions)
    y_test_names = label_encoder.inverse_transform(y_test)
    
    print("\n" + "="*50)
    print("          AI MODEL EVALUATION REPORT")
    print("="*50)
    print(f"Accuracy: {accuracy:.4f}")
    print("-"*50)
    print("Classification Report:\n", classification_report(y_test_names, pred_names))
    print("-"*50)
    
    # Generate Confusion Matrix
    classes = label_encoder.classes_
    cm = confusion_matrix(y_test_names, pred_names, labels=classes)
    cm_df = pd.DataFrame(cm, index=classes, columns=classes)
    print("Confusion Matrix:\n", cm_df.to_string())
    print("="*50 + "\n")

    print("Saving models...")
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/advanced_sms_model.pkl")
    joblib.dump(vectorizer, "models/advanced_sms_vectorizer.pkl")
    joblib.dump(label_encoder, "models/advanced_sms_encoder.pkl")
    print("Production XGBoost SMS model saved successfully!")

if __name__ == "__main__":
    train_model()
