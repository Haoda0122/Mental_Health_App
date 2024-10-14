import csv
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()

# Define lists for mental health-related data
symptoms = [
    "Depressed mood", "Anxiety", "Insomnia", "Fatigue", "Loss of interest",
    "Difficulty concentrating", "Irritability", "Panic attacks", "Social withdrawal",
    "Changes in appetite", "Mood swings", "Excessive worry", "Low self-esteem"
]

diagnoses = [
    "Major Depressive Disorder", "Generalized Anxiety Disorder", "Bipolar Disorder",
    "Post-Traumatic Stress Disorder", "Obsessive-Compulsive Disorder",
    "Social Anxiety Disorder", "Panic Disorder", "Eating Disorder",
    "Substance Use Disorder", "Schizophrenia"
]

treatments = [
    "Cognitive Behavioral Therapy", "Medication management", "Group therapy",
    "Mindfulness-based therapy", "Exposure therapy", "Family therapy",
    "Psychodynamic therapy", "Dialectical Behavior Therapy", "Art therapy",
    "Electroconvulsive therapy"
]

def generate_mental_health_data(num_records=1000):
    data = []
    for _ in range(num_records):
        patient_id = fake.unique.random_number(digits=6)
        age = random.randint(18, 80)
        gender = random.choice(["Male", "Female", "Non-binary"])
        symptom = random.choice(symptoms)
        diagnosis = random.choice(diagnoses)
        treatment = random.choice(treatments)
        severity = random.choice(["Mild", "Moderate", "Severe"])
        start_date = fake.date_between(start_date="-2y", end_date="today")
        duration = random.randint(1, 52)  # Duration in weeks
        end_date = start_date + timedelta(weeks=duration)
        
        data.append([
            patient_id, age, gender, symptom, diagnosis, treatment,
            severity, start_date, end_date, duration
        ])
    
    return data

def save_to_csv(data, filename="mental_health_dataset.csv"):
    headers = [
        "PatientID", "Age", "Gender", "PrimarySymptom", "Diagnosis",
        "TreatmentPlan", "Severity", "StartDate", "EndDate", "Duration(weeks)"
    ]
    
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(data)

if __name__ == "__main__":
    num_records = 1000
    print(f"Generating {num_records} mental health records...")
    mental_health_data = generate_mental_health_data(num_records)
    
    filename = "mental_health_dataset.csv"
    save_to_csv(mental_health_data, filename)
    print(f"Dataset saved as {filename}")
