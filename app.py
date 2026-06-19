import streamlit as st
import joblib
from ai_explainer import explain
from ocr_scanner import scan_image
from report_generator import generate_report
from history_manager import save_scan
from dashboard import load_data
from severity_engine import severity
import styles
from fraud_help import get_help
from recovery_assistant import get_recovery_plan
from evidence_checklist import get_checklist
from complaint_generator import generate_complaint

# Advanced SMS Model
sms_model = joblib.load(
    "models/advanced_sms_model.pkl"
)

sms_vectorizer = joblib.load(
    "models/advanced_sms_vectorizer.pkl"
)

# Advanced URL Model
url_model = joblib.load(
    "models/advanced_url_model.pkl"
)

st.set_page_config(
    page_title="Citizen Cyber Shield"
)

styles.inject_css()

st.title("Citizen Cyber Shield")

st.markdown("""
<div style='text-align:center;padding:20px;'>

<h3 style='color:#00E5FF;'>
Next Generation Cyber Threat Intelligence Platform
</h3>

<p style='font-size:18px;color:white;'>
Protect yourself from phishing attacks,
fraudulent SMS, malicious URLs,
and cyber threats using AI-powered
real-time detection.
</p>

</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "SMS Scanner",
    "URL Scanner",
    "Screenshot Scanner",
    "Dashboard",
    "Fraud Help Center",
    "Recovery Assistant"
])
# ================= SMS TAB =================
with tab1:

    st.subheader("SMS Scam Detection")

    message = st.text_area(
        "Enter SMS Message",
        height=150
    )

    if st.button(
        "Scan SMS",
        key="sms_scan_btn"
    ):

        if message.strip() == "":

            st.warning(
                "Please enter a message"
            )

        else:

            msg_vector = sms_vectorizer.transform(
                [message]
            )

            prediction = sms_model.predict(
                msg_vector
            )

            text = message.lower()

            fraud_keywords = [
                "kyc",
                "otp",
                "verify",
                "verification",
                "account blocked",
                "bank",
                "upi",
                "click here",
                "reward",
                "lottery",
                "suspended",
                "urgent",
                "update account"
            ]

            keyword_detected = False

            for word in fraud_keywords:

                if word in text:
                    keyword_detected = True
                    break

            st.write(
                "Prediction:",
                prediction[0]
            )

            if prediction[0] == "spam" or keyword_detected:

                risk = 95 if keyword_detected else 80

                st.error(
                    "🚨 Fraud SMS Detected"
                )
                
                st.warning(
                    "🚨 Recovery Guide Available"
                )
                
                if st.button(
                    "Open Recovery Assistant",
                    key="sms_recovery_btn"
                ):

                    st.session_state[
                        "recovery_fraud_type"
                    ] = threat_type

                    st.session_state[
                        "open_recovery"
                    ] = True

                st.metric(
                    "Risk Score",
                    f"{risk}%"
                )

                reasons = explain(
                    message
                )

                st.subheader(
                    "AI Explanation"
                )

                for reason in reasons:

                    st.write(
                        "✓",
                        reason
                    )

                # Threat Classification
                threat_type = "Cyber Fraud"

                if "otp" in text:
                    threat_type = "OTP Scam"
                elif "kyc" in text:
                    threat_type = "KYC Fraud"
                elif "upi" in text:
                    threat_type = "UPI Fraud"
                elif "bank" in text:
                    threat_type = "Bank Fraud"
                elif "lottery" in text:
                    threat_type = "Lottery Scam"

                st.subheader(
                    "Threat Classification"
                )

                st.success(
                    threat_type
                )

                # Cyber Safety Report
                report = generate_report(
                    threat_type,
                    risk
                )

                st.subheader(
                    "Cyber Safety Report"
                )

                st.write(
                    report
                )

                save_scan(
                    threat_type,
                    risk,
                    message
                )

                st.success(
                    "History Saved Successfully"
                )

            else:

                st.success(
                    "✅ Safe SMS"
                )

                st.metric(
                    "Risk Score",
                    "10%"
                )

                save_scan(
                    "Safe Message",
                    10,
                    message
                )
# ================= URL TAB =================
with tab2:

    st.subheader(
        "URL Phishing Detection"
    )

    st.info(
        "Advanced URL Model Loaded"
    )

    url = st.text_input(
        "Enter URL"
    )

    if st.button(
        "Scan URL",
        key="url_scan_btn"
    ):

        if url.strip() == "":

            st.warning(
                "Please enter a URL"
            )
        
        else: 

            url_text = url.lower()

            suspicious_keywords = [
                "login",
                "verify",
                "update",
                "bank",
                "otp",
                "kyc",
                "reward",
                "lottery",
                "secure",
                "account"
            ]

            risk = 10
            detected = False

            for word in suspicious_keywords:

                if word in url_text:
                    detected = True
                    risk = 90
                    break

            if "https://" not in url_text:
                risk += 20

            if detected:

                st.error(
                    "🚨 Suspicious URL Detected"
                )

                st.metric(
                    "Risk Score",
                    f"{risk}%"
                )

            else:

                st.success(
                    "✅ URL Appears Safe"
                )

                st.metric(
                    "Risk Score",
                    f"{risk}%"
                )

# ================= SCREENSHOT TAB =================
with tab3:

    st.subheader(
        "Screenshot Scanner"
    )

    uploaded_file = st.file_uploader(
        "Upload Screenshot",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded_file is not None:

        st.image(
            uploaded_file,
            caption="Uploaded Screenshot",
            width="stretch"
        )

        st.success(
            "Screenshot Uploaded Successfully"
        )

        if st.button(
            "Scan Screenshot",
            key="ocr_scan_btn"
        ):

            with open(
                "temp_image.png",
                "wb"
            ) as f:

                f.write(
                    uploaded_file.getbuffer()
                )

            st.write(
                "Starting OCR..."
            )

            extracted_text = scan_image(
                "temp_image.png"
            )

            st.write(
                "OCR Completed"
            )

            st.subheader(
                "Extracted Text"
            )

            st.write(
                extracted_text
            )

            # Fraud Detection on OCR Text
            msg_vector = sms_vectorizer.transform(
                [extracted_text]
            )

            prediction = sms_model.predict(
                msg_vector
            )

            text = extracted_text.lower()

            fraud_keywords = [
                "kyc",
                "otp",
                "verify",
                "verification",
                "account blocked",
                "bank",
                "upi",
                "click here",
                "reward",
                "lottery",
                "suspended"
            ]

            keyword_detected = False

            for word in fraud_keywords:
                if word in text:
                    keyword_detected = True
                    break

            if prediction[0] == "spam" or keyword_detected:

                st.error(
                    "🚨 Fraud Detected in Screenshot"
                )

                st.metric(
                    "Risk Score",
                    "95%"
                )

                save_scan(
                    "Fraud Screenshot",
                    95,
                    extracted_text
                )

                reasons = explain(
                    extracted_text
                )

                st.subheader(
                    "AI Explanation"
                )

                for reason in reasons:
                    st.write(
                        "✓",
                        reason
                    )

            else:

                st.success(
                    "✅ Screenshot Appears Safe"
                )

                st.metric(
                    "Risk Score",
                    "10%"
                )

                save_scan(
                    "Safe Screenshot",
                    10,
                    extracted_text
                )

# ================= DASHBOARD TAB =================
with tab4:

    st.subheader(
        "Threat Dashboard"
    )

    try:

        df = load_data()

        st.dataframe(
            df
        )

        st.metric(
            "Total Scans",
            len(df)
        )

    except:

        st.warning(
            "No history available"
        )
        # ================= FRAUD HELP CENTER =================

with tab5:

    st.subheader(
        "Cyber Emergency Response Center"
    )

    fraud_type = st.selectbox(
        "Select Fraud Type",
        [
            "UPI Fraud",
            "Bank Fraud",
            "OTP Scam"
        ]
    )

    if st.button(
        "Get Recovery Guide"
    ):

        data = get_help(
            fraud_type
        )

        st.error(
            f"Severity: {data['severity']}"
        )

        st.subheader(
            "Immediate Actions"
        )

        for step in data["steps"]:

            st.write(
                "✓",
                step
            )

        st.info(
            "Emergency Helpline: 1930"
        )

        st.link_button(
            "Report Cyber Crime",
            "https://cybercrime.gov.in"
        )
        # ================= RECOVERY TAB =================

with tab6:

    st.subheader(
        "AI Recovery Assistant"
    )

    default_type = st.session_state.get(
        "recovery_fraud_type",
        "UPI Fraud"
    )

    fraud_type = st.selectbox(
        "Fraud Type",
        [
            "UPI Fraud",
            "Bank Fraud",
            "OTP Scam"
        ],
        index=[
            "UPI Fraud",
            "Bank Fraud",
            "OTP Scam"
        ].index(default_type)
        if default_type in [
            "UPI Fraud",
            "Bank Fraud",
            "OTP Scam"
        ]
        else 0
    )

    bank_name = st.selectbox(
        "Bank",
        [
            "SBI",
            "HDFC",
            "ICICI"
        ]
    )

    if st.button(
        "Generate Recovery Plan"
    ):

        result = get_recovery_plan(
            fraud_type,
            bank_name
        )

        st.error(
            "Emergency Actions"
        )
        
        st.subheader(
            "Evidence Checklist"
        )

        for item in get_checklist():

            st.checkbox(
                item
            )

        for step in result["steps"]:

            st.write(
                "✓",
                step
            )

        st.subheader(
            "Bank Information"
        )

        st.write(
            "Helpline:",
            result["bank"]["helpline"]
        )

        st.write(
            "Website:",
            result["bank"]["website"]
        )

        st.info(
            "National Cyber Helpline: 1930"
        )

    st.divider()

    st.subheader(
        "Complaint Generator"
    )

    name = st.text_input(
        "Victim Name"
    )

    amount = st.number_input(
        "Amount Lost",
        min_value=0.0
    )

    if st.button(
        "Generate Complaint"
    ):

        complaint = generate_complaint(
            name,
            fraud_type,
            amount
        )

        st.text_area(
            "Generated Complaint",
            complaint,
            height=250
        )
       