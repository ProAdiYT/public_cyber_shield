import os
# CRITICAL: Prevent OpenBLAS Memory Allocation Errors in restricted environments
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import pandas as pd
import numpy as np
import joblib
from extractors import URLExtractor
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, accuracy_score

def train_model():
    print("Loading URL dataset...")
    # Load first 40,000 rows to prevent Out-Of-Memory inside the sandbox environment
    df = pd.read_csv("datasets_raw/PhiUSIIL_Phishing_URL_Dataset.csv")
    df = df.head(40000)
    
    print("Initializing feature extractor...")
    extractor = URLExtractor()
    
    feature_rows = []
    print("Extracting lexical features from URLs...")
    for idx, row in df.iterrows():
        url = str(row["URL"])
        # Extract features (exclude redirect count from request, copy from dataset to prevent network delay)
        feats = extractor.extract_features(url, skip_lookup=True)
        # Override dynamic redirect count with dataset's pre-computed redirect count
        feats["NoOfURLRedirect"] = int(row["NoOfURLRedirect"])
        feature_rows.append(feats)
        
        if (idx + 1) % 10000 == 0:
            print(f"Processed {idx + 1} URLs...")
            
    X = pd.DataFrame(feature_rows)
    
    # Invert target label so 1 represents Phishing/Danger, and 0 represents Safe
    # original label in dataset: 1 = legitimate, 0 = phishing
    y = 1 - df["label"]
    
    print("Feature columns prepared:\n", X.columns.tolist())
    print("Phishing labels distribution:\n", y.value_counts())
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print("Training XGBoost URL threat model...")
    # Train binary XGBClassifier
    model = XGBClassifier(
        n_estimators=100,
        random_state=42,
        n_jobs=1,
        eval_metric="logloss"
    )
    model.fit(X_train, y_train)
    
    predictions = model.predict(X_test)
    print("Accuracy:", accuracy_score(y_test, predictions))
    print("Classification Report:\n", classification_report(y_test, predictions))
    
    print("Saving URL threat model...")
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/advanced_url_model.pkl")
    print("Advanced XGBoost URL threat model saved successfully!")

if __name__ == "__main__":
    train_model()
