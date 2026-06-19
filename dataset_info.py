import pandas as pd

print("="*50)
print("SMS DATASET")
print("="*50)

sms = pd.read_csv(
    "datasets_raw/SMSSpamCollection",
    sep="\t",
    names=["label", "message"]
)

print(sms.head())
print("\nShape:", sms.shape)
print("\nColumns:", sms.columns)

print("\n\n")

print("="*50)
print("URL DATASET 1")
print("="*50)

url1 = pd.read_csv(
    "datasets_raw/Phishing_Legitimate_full.csv"
)

print(url1.head())
print("\nShape:", url1.shape)
print("\nColumns:", url1.columns)

print("\n\n")

print("="*50)
print("URL DATASET 2")
print("="*50)

url2 = pd.read_csv(
    "datasets_raw/PhiUSIIL_Phishing_URL_Dataset.csv"
)

print(url2.head())
print("\nShape:", url2.shape)
print("\nColumns:", url2.columns)