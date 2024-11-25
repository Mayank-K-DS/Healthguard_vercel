from flask import Flask, request, render_template, redirect, jsonify, url_for, session, flash
from flask_cors import CORS
import datetime
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
import urllib.parse
import os
import csv

app = Flask(__name__)

CORS(app)

app.secret_key = '12345678'

app.secret_key = os.urandom(24)

patientID = "00000000"
temperature = "N/A"
patient_data = {}
doctor_records = {}
appointments_csv = r"appointments.csv"
emergency_status = {"active": False}


df = pd.read_csv(r"C:\Users\LENOVO\Desktop\Projects\Healthguard\symbipredict_2022.csv")
symptom_columns = df.columns[:-1]
X = df[symptom_columns]
y = df[df.columns[-1]]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = DecisionTreeClassifier()
model.fit(X_train, y_train)

def predict_disease(symptoms):
    user_symptoms = {symptom: 0 for symptom in symptom_columns}
    for symptom in symptoms:
        if symptom in user_symptoms:
            user_symptoms[symptom] = 1
    input_data = list(user_symptoms.values())
    input_df = pd.DataFrame([input_data], columns=symptom_columns)
    prediction = model.predict(input_df)
    return prediction[0]

patients_csv = r"patients.csv"
doctor_records_csv = r"doctor_records.csv"

def load_patient_data():
    patient_data = {}
    if os.path.exists(patients_csv):
        with open(patients_csv, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                patient_data[row['patientID']] = {
                    'name': row['name'],
                    'age': row['age'],
                    'gender': row['gender'],
                    'phone_number': row.get('phone_number', "N/A"),
                    'temperature': row['temperature']
                }
    return patient_data

def load_appointments(patient_id):
    appointments = []
    with open(appointments_csv, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['patientID'] == patient_id:
                appointments.append(row)
    return appointments

def load_doctor_records():
    doctor_records = {}
    if os.path.exists(doctor_records_csv):
        with open(doctor_records_csv, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['patientID'] not in doctor_records:
                    doctor_records[row['patientID']] = []
                doctor_records[row['patientID']].append({
                    'symptom': row['symptom'],
                    'diagnosis': row['diagnosis'],
                    'date': row['date']
                })
    return doctor_records

def save_patient_data():
    with open(patients_csv, mode='w', newline='') as file:
        fieldnames = ['patientID', 'name', 'age', 'gender', 'phone_number', 'temperature']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for pid, info in patient_data.items():
            writer.writerow({
                'patientID': pid,
                'name': info['name'],
                'age': info['age'],
                'gender': info['gender'],
                'phone_number': info.get('phone_number', 'N/A'),
                'temperature': info.get('temperature', "N/A")
            })

patient_data = load_patient_data()
doctor_records = load_doctor_records()

@app.route('/')
def index():
    global patientID, temperature
    patient_info = patient_data.get(patientID, {"name": "Unknown", "age": "Unknown", "gender": "Unknown", "temperature": "N/A"})
    temperature = patient_info.get('temperature', "N/A")

    return render_template('index.html', patientID=patientID, temperature=temperature,
                           name=patient_info['name'], age=patient_info['age'], gender=patient_info['gender'])

@app.route('/predict', methods=['POST'])
def predict():
    symptoms = request.form['symptoms'].lower().split(',')
    symptoms = [symptom.strip() for symptom in symptoms]
    predicted_disease = predict_disease(symptoms)
    
   
    session['symptoms'] = ','.join(symptoms)
    session['prognosis'] = predicted_disease

    return render_template('result.html', disease=predicted_disease)

@app.route('/update_patient', methods=['POST'])
def update_patient():
    if request.is_json:
        global patientID, temperature
        data = request.get_json()
        patientID = data.get('patientID')
        temperature = data.get('temperature')

        if patientID in patient_data:
            patient_data[patientID]['temperature'] = temperature
        else:
            patient_data[patientID] = {"name": "Unknown", "age": "Unknown", "gender": "Unknown", "temperature": temperature}
            
        save_patient_data()

        print(f"Received patientID: {patientID}, Temperature: {temperature} °F")
        return jsonify({"message": "Patient data updated", "patientID": patientID, "temperature": temperature})
    else:
        return jsonify({"error": "Invalid content type, expected JSON"}), 400

@app.route('/change_info', methods=['GET'])
def change_info():
    global patientID
    return render_template('update_info.html', patientID=patientID)

@app.route('/update_patient_info', methods=['POST'])
def update_patient_info():
    name = request.form['name']
    age = request.form['age']
    gender = request.form['gender']
    phone_number = request.form['phone_number']
    password = request.form['password']

    global patientID

    if password != patientID:
        return jsonify({"error": "Incorrect password!"}), 403

    patient_data[patientID] = {
        "name": name,
        "age": age,
        "gender": gender,
        "phone_number": phone_number,
        "temperature": patient_data.get(patientID, {}).get('temperature', "N/A")
    }

    save_patient_data()

    print(f"Updated info for PatientID: {patientID}, Name: {name}, Age: {age}, Gender: {gender}, Phone Number: {phone_number}")

    return redirect(url_for('index'))

@app.route('/search', methods=['POST'])
def search():
    disease = request.form['disease']
    encoded_disease = urllib.parse.quote(disease)
    mayo_clinic_url = f"https://www.mayoclinic.org/search/search-results?q={encoded_disease}"
    return redirect(mayo_clinic_url)

@app.route('/change_patient_info', methods=['GET', 'POST'])
def change_patient_info():
    if request.method == 'POST':
        patient_name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        phone_number = request.form['phone_number']
        password = request.form['password']

        global patientID

        if password != patientID:
            return jsonify({"error": "Incorrect password!"}), 403

        patient_data[patientID] = {
            "name": patient_name,
            "age": age,
            "gender": gender,
            "phone_number": phone_number,
            "temperature": patient_data.get(patientID, {}).get('temperature', "N/A")
        }

        save_patient_data()

        return redirect(url_for('index'))

    return render_template('update_info.html')

def save_appointment_data(appointment_data):
    with open(appointments_csv, mode='a', newline='') as file:
        fieldnames = ['patientID', 'name', 'temperature', 'symptoms', 'prognosis', 'appointment_date', 'appointment_time']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        if os.stat(appointments_csv).st_size == 0:
            writer.writeheader()
        
        writer.writerow(appointment_data)

@app.route('/save_appointment', methods=['POST'])
def save_appointment():
    appointment_date = request.form['appointment_date']
    appointment_time = request.form['appointment_time']
    patient_info = patient_data.get(patientID, {})

    symptoms = session.get('symptoms', "N/A")
    prognosis = session.get('prognosis', "N/A")

    print(f"Symptoms: {symptoms}, Prognosis: {prognosis}")

    appointment_data = {
        'patientID': patientID,
        'name': patient_info.get('name', 'Unknown'),
        'temperature': patient_info.get('temperature', 'N/A'),
        'symptoms': symptoms,
        'prognosis': prognosis,
        'appointment_date': appointment_date,
        'appointment_time': appointment_time
    }

    save_appointment_data(appointment_data)


    session.pop('symptoms', None)
    session.pop('prognosis', None)

    return redirect(url_for('index'))



@app.route('/login_as_doctor', methods=['GET', 'POST'])
def login_as_doctor():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "Doctor_HG" and password == "1234567":
            return redirect(url_for('doctor_appointments'))
        else:
            return render_template('login_as_doctor.html', error="Invalid username or password.")
    
    return render_template('login_as_doctor.html')

@app.route('/doctor_dashboard', methods=['GET', 'POST'])
def doctor_dashboard():
    if request.method == 'POST':
        patient_id = request.form['patient_id']
        symptom = request.form['symptom']
        diagnosis = request.form['diagnosis']
        date = request.form['date']

        if patient_id not in doctor_records:
            doctor_records[patient_id] = []

        doctor_records[patient_id].append({
            'symptom': symptom,
            'diagnosis': diagnosis,
            'date': date
        })

        save_doctor_records()

        print(f"Updated records for PatientID: {patient_id}, Symptom: {symptom}, Diagnosis: {diagnosis}, Date: {date}")

        return redirect(url_for('doctor_dashboard'))
    return render_template('doctor_dashboard.html')

@app.route('/view_patient_dashboard/<patient_id>')
def view_patient_dashboard(patient_id):

    records = doctor_records.get(patient_id, [])

    return render_template('view_patient_dashboard.html', records=records, patient_id=patient_id)

@app.route('/book_appointment')
def book_appointment():
    image_path = r"static\images\Doctor_s_Contact_Number.png"
    symptoms = session.get('symptoms')  
    prognosis = predict_disease(symptoms) if symptoms else "N/A"  
    return render_template('book_appointment.html', image_path=image_path, prognosis=prognosis)

@app.route('/confirm_emergency_help', methods=['GET'])
def confirm_emergency_help():
    return render_template('confirm_emergency_help.html')

@app.route('/emergency_help')
def emergency_help():
    emergency_status["active"] = True
    print("Emergency active status set to:", emergency_status["active"])
    return render_template('emergency_help.html')

@app.route('/emergency_end')
def emergency_end():
    emergency_active = emergency_status["active"]
    print("Current emergency active status:", emergency_active)
    return render_template('emergency_end.html', emergency_active=emergency_active)

@app.route('/reset_emergency', methods=['GET'])
def reset_emergency():
    emergency_status["active"] = False
    return jsonify({"message": "No current emergency call"})

@app.route('/doctor_appointments')
def doctor_appointments():
    appointments = []
    if os.path.exists(appointments_csv):
        with open(appointments_csv, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                appointments.append(row)
    
    return render_template('doctor_appointments.html', appointments=appointments)

def save_doctor_records():
    with open(doctor_records_csv, mode='w', newline='') as file:
        fieldnames = ['patientID', 'symptom', 'diagnosis', 'date', 'appointment_time']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for pid, records in doctor_records.items():
            for record in records:
                writer.writerow({
                    'patientID': pid,
                    'symptom': record['symptom'],
                    'diagnosis': record['diagnosis'],
                    'date': record['date'],
                })


@app.route('/mark_as_done/<int:appointment_index>', methods=['POST'])
def mark_as_done(appointment_index):
    appointments = []
    if os.path.exists(appointments_csv):
        with open(appointments_csv, mode='r') as file:
            reader = csv.DictReader(file)
            appointments = list(reader)

    if 0 <= appointment_index < len(appointments):
        
        appointment = appointments.pop(appointment_index)

       
        patient_id = appointment['patientID']
        symptom = appointment['symptoms']
        diagnosis = appointment['prognosis']
        date = datetime.datetime.now().strftime('%Y-%m-%d')

        
        if patient_id not in doctor_records:
            doctor_records[patient_id] = []
        doctor_records[patient_id].append({
            'symptom': symptom,
            'diagnosis': diagnosis,
            'date': date
        })
        save_doctor_records()

       
        with open(appointments_csv, mode='w', newline='') as file:
            fieldnames = ['patientID', 'name', 'temperature', 'symptoms', 'prognosis', 'appointment_date', 'appointment_time']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            
            filtered_appointments = [{key: appointment[key] for key in fieldnames if key in appointment} for appointment in appointments]
            writer.writerows(filtered_appointments)

    return redirect(url_for('doctor_appointments'))


@app.route('/user_enter', methods=['GET', 'POST'])
def user_enter():
    if request.method == 'POST':
        patient_id = request.form.get('patientID') 
        return redirect(url_for('view_appointments', patient_id=patient_id))
    return render_template('user_enter.html')

@app.route('/user_appointments/<patient_id>')
def view_appointments(patient_id):
    appointments = load_appointments(patient_id)
    return render_template('user_appointments.html', patient_id=patient_id, appointments=appointments)

@app.route('/delete_appointment/<patient_id>/<appointment_date>/<appointment_time>', methods=['POST'])
def delete_appointment(patient_id, appointment_date, appointment_time):
    # Define the expected fieldnames based on appointments.csv
    fieldnames = ['patientID', 'temperature', 'symptoms', 'prognosis', 'appointment_date', 'appointment_time', 'phone_number']

    # Load all appointments from CSV
    appointments = []
    with open('appointments.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            appointments.append(row)

    # Filter out the appointment to delete
    appointments = [
        {key: row[key] for key in fieldnames if key in row}  # Only include valid fields
        for row in appointments
        if not (row['patientID'] == patient_id and row['appointment_date'] == appointment_date and row['appointment_time'] == appointment_time)
    ]

    # Write the updated list back to the CSV
    with open('appointments.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(appointments)

    return redirect(url_for('user_enter'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)