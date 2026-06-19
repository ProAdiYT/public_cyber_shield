import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

df = pd.read_csv(
    "datasets_raw/SMSSpamCollection",
    sep="\t",
    names=["label", "message"]
)

df.drop_duplicates(inplace=True)
df.dropna(inplace=True)

X = df["message"]
y = df["label"]

vectorizer = TfidfVectorizer(
    max_features=10000
)

X = vectorizer.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

model = LogisticRegression(
    max_iter=1000
)

model.fit(X_train, y_train)

pred = model.predict(X_test)

print(
    "Accuracy:",
    accuracy_score(y_test, pred)
)

joblib.dump(
    model,
    "models/advanced_sms_model.pkl"
)

joblib.dump(
    vectorizer,
    "models/advanced_sms_vectorizer.pkl"
)

print("Advanced SMS Model Saved")