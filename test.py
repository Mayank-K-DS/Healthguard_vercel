import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
# Load the updated dataset
data = pd.read_csv(r"C:\Users\LENOVO\Desktop\Projects\Healthguard\symbipredict_2022.csv")
# Separate features and labels (symptoms and disease)
X = data.iloc[:, :-2]  # All symptoms columns (132 symptoms)
y = data['prognosis']  # Disease (prognosis)
treatment_data = data['Suggested Treatment']  # Treatment column
# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
# Initialize and train the decision tree classifier
clf = DecisionTreeClassifier()
clf.fit(X_train, y_train)
# Function to get user symptoms and predict disease
def predict_disease(symptoms_input):
    user_symptoms = [0] * len(X.columns)  # Create a list with 0s for each symptom
    # Mark the symptoms provided by the user as 1 in the list
    for symptom in symptoms_input:
        if symptom in X.columns:
            symptom_index = X.columns.get_loc(symptom)
            user_symptoms[symptom_index] = 1
    # Predict the disease
    predicted_disease = clf.predict([user_symptoms])[0]
    # Suggest treatment for the predicted disease
    treatment = data[data['prognosis'] == predicted_disease]['Suggested Treatment'].values[0]
    return predicted_disease, treatment
# Input symptoms from the user
user_input = input("Enter your symptoms separated by commas: ").split(',')
# Strip any extra spaces and ensure lowercase for matching
user_input = [symptom.strip().capitalize() for symptom in user_input]
# Get the disease prediction and treatment suggestion
predicted_disease, suggested_treatment = predict_disease(user_input)
# Output the result
print(f"Based on your symptoms, you may have {predicted_disease}.")
print(f"Suggested treatment: {suggested_treatment}")
