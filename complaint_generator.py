def generate_complaint(
    name,
    fraud_type,
    amount
):

    return f"""
Name: {name}

Fraud Type: {fraud_type}

Amount Lost: ₹{amount}

I request investigation of the
above cyber fraud incident.

Attached:
Screenshots
Transaction Details
Evidence
"""