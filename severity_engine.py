def severity(threat):

    critical = [
        "Bank Fraud",
        "UPI Fraud",
        "OTP Scam"
    ]

    medium = [
        "Lottery Scam",
        "Job Scam",
        "KYC Fraud"
    ]

    if threat in critical:
        return "CRITICAL 🔴"

    elif threat in medium:
        return "MEDIUM 🟡"

    else:
        return "LOW 🟢"