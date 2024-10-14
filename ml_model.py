import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report


if not os.path.exists("mental_health_dataset.csv"):
    print("Error: mental_health_dataset.csv not found. Please generate the dataset first.")
    exit(1)


df = pd.read_csv("mental_health_dataset.csv")


df['Depression'] = df['Diagnosis'].apply(lambda x: 1 if x == 'Major Depressive Disorder' else 0)


features = ['Age', 'Duration(weeks)', 'Severity']
X = df[features]
y = df['Depression']


X = pd.get_dummies(X, columns=['Severity'])


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)


model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)


y_pred = model.predict(X_test_scaled)


accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.2f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))


def predict_depression(age, duration, severity):

    input_data = pd.DataFrame([[age, duration, severity]], columns=['Age', 'Duration(weeks)', 'Severity'])
    input_data = pd.get_dummies(input_data, columns=['Severity'])
    

    for col in X.columns:
        if col not in input_data.columns:
            input_data[col] = 0
    

    input_data = input_data[X.columns]
    

    input_scaled = scaler.transform(input_data)
    

    prediction = model.predict(input_scaled)
    probability = model.predict_proba(input_scaled)[0][1]
    
    return prediction[0], probability


age = 35
duration = 12
severity = "Moderate"
prediction, probability = predict_depression(age, duration, severity)
print(f"\nPrediction for Age: {age}, Duration: {duration} weeks, Severity: {severity}")
print(f"Depression: {'Yes' if prediction == 1 else 'No'}")
print(f"Probability of Depression: {probability:.2f}")
