def get_recovery_plan(
    fraud_type,
    bank_name
):

    plans = {

        "UPI Fraud": [
            "Call 1930 immediately",
            "Contact bank",
            "Disable UPI",
            "Save transaction details",
            "Report cyber crime"
        ],

        "Bank Fraud": [
            "Block debit card",
            "Freeze account",
            "Contact bank",
            "Collect evidence",
            "Report cyber crime"
        ],

        "OTP Scam": [
            "Change passwords",
            "Enable 2FA",
            "Contact bank",
            "Monitor account"
        ]
    }

    bank_data = {

        "SBI": {
            "helpline": "1800 1234",
            "website": "https://sbi.co.in"
        },

        "HDFC": {
            "helpline": "1800 202 6161",
            "website": "https://hdfcbank.com"
        },

        "ICICI": {
            "helpline": "1800 1080",
            "website": "https://icicibank.com"
        }
    }

    return {
        "steps": plans.get(
            fraud_type,
            []
        ),
        "bank": bank_data.get(
            bank_name,
            {}
        )
    }