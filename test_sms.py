import joblib

model = joblib.load("models/sms_model.pkl")
vectorizer = joblib.load("models/vectorizer.pkl")

message = input("Enter Message: ")

message_vector = vectorizer.transform([message])

prediction = model.predict(message_vector)

print("Result:", prediction[0])