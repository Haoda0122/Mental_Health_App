import pandas as pd
import numpy as np
from faker import Faker
import random

fake = Faker()

def generate_mental_health_dataset(num_records=1000):
    data = []
    for _ in range(num_records):
        age = random.randint(18, 80)
        duration = random.randint(1, 52)  
        severity = random.choice(['Mild', 'Moderate', 'Severe'])
        symptoms = ', '.join(random.sample(['Sadness', 'Anxiety', 'Fatigue', 'Insomnia', 'Loss of appetite', 'Irritability'], random.randint(2, 5)))
        diagnosis = 'Major Depressive Disorder' if random.random() < 0.6 else 'No Depression'
        treatment = random.choice(['Cognitive Behavioral Therapy', 'Medication', 'Combination therapy', 'No treatment'])
        
        data.append({
            'PatientID': fake.uuid4(),
            'Age': age,
            'Gender': random.choice(['Male', 'Female', 'Other']),
            'Duration(weeks)': duration,
            'Severity': severity,
            'Symptoms': symptoms,
            'Diagnosis': diagnosis,
            'Treatment': treatment
        })
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    df = generate_mental_health_dataset()
    df.to_csv("mental_health_dataset.csv", index=False)
    print("Dataset generated and saved as mental_health_dataset.csv")
