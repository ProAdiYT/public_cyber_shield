def generate_report(threat, risk):

    return {
        "Threat Type": threat,
        "Risk Score": risk,

        "Recommendation":
        [
            "Do not click suspicious links",
            "Block sender immediately",
            "Do not share OTP",
            "Report to Cyber Crime Portal"
        ]
    }