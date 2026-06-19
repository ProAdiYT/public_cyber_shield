import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

print("Loading Dataset...")

df = pd.read_csv(
    "datasets_raw/PhiUSIIL_Phishing_URL_Dataset.csv"
)

# Use only first 50000 rows for now
df = df.head(50000)

X = df.drop(
    columns=[
        "FILENAME",
        "URL",
        "Domain",
        "TLD",
        "Title",
        "label"
    ],
    errors="ignore"
)

y = df["label"]

print("Splitting Dataset...")

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

print("Training Model...")

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)

model.fit(
    X_train,
    y_train
)

pred = model.predict(X_test)

print(
    "Accuracy:",
    accuracy_score(
        y_test,
        pred
    )
)

joblib.dump(
    model,
    "models/advanced_url_model.pkl"
)

print(
    "Advanced URL Model Saved"
)