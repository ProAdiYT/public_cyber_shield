def explain(text):

    text = text.lower()

    reasons = []

    if "otp" in text:
        reasons.append("OTP request detected")

    if "kyc" in text:
        reasons.append("KYC verification request detected")

    if "bank" in text:
        reasons.append("Bank related message")

    if "click here" in text:
        reasons.append("Suspicious link detected")

    if "account blocked" in text:
        reasons.append("Account blocked warning detected")

    return reasons