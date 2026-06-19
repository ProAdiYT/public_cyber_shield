def get_help(fraud_type):

    guides = {

        "UPI Fraud": {
            "severity": "Critical",
            "steps": [
                "Call 1930 immediately",
                "Contact your bank",
                "Block UPI services",
                "Save screenshots and UTR number",
                "File complaint on cybercrime portal"
            ]
        },

        "Bank Fraud": {
            "severity": "Critical",
            "steps": [
                "Block debit/credit card",
                "Call bank helpline",
                "Freeze suspicious transactions",
                "Collect transaction details",
                "Report cyber crime"
            ]
        },

        "OTP Scam": {
            "severity": "High",
            "steps": [
                "Change passwords immediately",
                "Contact bank",
                "Enable 2FA",
                "Monitor transactions"
            ]
        }
    }

    return guides.get(
        fraud_type,
        {
            "severity": "Unknown",
            "steps": [
                "Collect evidence",
                "Report incident",
                "Contact support"
            ]
        }
    )