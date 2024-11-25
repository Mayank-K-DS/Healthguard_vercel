import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report
import webbrowser
import urllib.parse
# Load the dataset (replace 'symptoms_dataset.csv' with your actual dataset file)
df = pd.read_csv(r"C:\Users\LENOVO\Desktop\Projects\Healthguard\symbipredict_2022.csv")
# Display the structure of the dataset to understand column names
print(df.head())
# Check the dataset columns (symptoms and prognosis/disease)
symptom_columns = df.columns[:-1]  # Assuming the last column is the 'Prognosis' or 'Disease'
print(f"Symptoms Columns: {symptom_columns}")
# Features (symptoms) and target (disease)
X = df[symptom_columns]  # All columns except the last one, which is the target
y = df[df.columns[-1]]  # Assuming the last column is 'Prognosis' or 'Disease'
# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
# Create and train a Decision Tree model
model = DecisionTreeClassifier()
model.fit(X_train, y_train)
# Test the model
y_pred = model.predict(X_test)
# Model evaluation
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy * 100:.2f}%")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))
# Function to predict disease based on user input symptoms
def predict_disease(model, symptom_columns):
    # Ask the user to input their symptoms
    user_input = input("Enter your symptoms as a comma-separated list (e.g., fever,cough,headache): ").lower().split(',')
    # Create a zeroed-out symptom list
    user_symptoms = {symptom: 0 for symptom in symptom_columns}
    # Mark the symptoms provided by the user as 1 (present)
    for symptom in user_input:
        symptom = symptom.strip()  # Remove any leading/trailing spaces
        if symptom in user_symptoms:
            user_symptoms[symptom] = 1
        else:
            print(f"Warning: Symptom '{symptom}' not recognized.")
    # Convert the user's symptoms into the input format expected by the model
    input_data = list(user_symptoms.values())
    # Convert to a DataFrame and predict the disease
    input_df = pd.DataFrame([input_data], columns=symptom_columns)
    prediction = model.predict(input_df)
    predicted_disease = prediction[0]
    return predicted_disease
def search_disease(disease):
    search_query = urllib.parse.quote(disease)
    search_url = f"https://www.mayoclinic.org/search/search-results?q={search_query}"
    webbrowser.open(search_url)
# Start the symptom checker
predicted_disease = predict_disease(model, symptom_columns)
print(f"The predicted disease based on your symptoms is: {predicted_disease}")
# Search for the disease on Mayo Clinic
search_disease(predicted_disease)