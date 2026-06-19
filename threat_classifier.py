def classify_threat(text):

    text = text.lower()

    if "kyc" in text:
        return "KYC Fraud"

    elif "otp" in text:
        return "OTP Scam"

    elif "upi" in text:
        return "UPI Fraud"

    elif "bank" in text:
        return "Bank Fraud"

    elif "lottery" in text:
        return "Lottery Scam"

    elif "job" in text:
        return "Job Scam"

    return "Unknown Threat"